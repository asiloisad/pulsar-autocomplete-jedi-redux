import os
import io
import re
import sys
import json
import traceback

import jedi

WORD_RE = re.compile(r'\w')
ARGUMENT_RE = re.compile(r'[a-zA-Z0-9_=\*"\']+')


class JediCompletion(object):
    basic_types = {
        'module': 'import',
        'instance': 'variable',
        'statement': 'value',
        'param': 'variable',
    }

    def __init__(self):
        self.default_sys_path = sys.path
        self._input = io.open(sys.stdin.fileno(), encoding='utf-8')
        self._devnull = open(os.devnull, 'w')
        self.stdout, self.stderr = sys.stdout, sys.stderr

    def _get_definition_type(self, definition):
        is_built_in = definition.in_builtin_module
        if definition.type not in ['import', 'keyword'] and is_built_in():
            return 'builtin'
        if definition.type in ['statement'] and definition.name.isupper():
            return 'constant'
        return self.basic_types.get(definition.type, definition.type)

    def _additional_info(self, completion):
        try:
            if not hasattr(completion, '_definition') or completion._definition is None:
                return ''
            if completion.type == 'statement':
                nodes_to_display = ['InstanceElement', 'String', 'Node', 'Lambda', 'Number']
                return ''.join(
                    c.get_code() for c in completion._definition.children
                    if type(c).__name__ in nodes_to_display
                ).replace('\n', '')
        except Exception:
            pass
        return ''

    @classmethod
    def _get_top_level_module(cls, path):
        """Recursively walk through directories looking for top level module.

        Jedi will use current filepath to look for another modules at same
        path, but it will not be able to see modules **above**, so our goal
        is to find the higher python module available from filepath.
        """
        _path, _ = os.path.split(path)
        if _path != path and os.path.isfile(os.path.join(_path, '__init__.py')):
            return cls._get_top_level_module(_path)
        return path

    def _generate_signature(self, completion):
        if completion.type in ['module'] or not hasattr(completion, 'params'):
            return ''
        return '%s(%s)' % (
            completion.name,
            ', '.join(p.description for p in completion.params if p)
        )

    def _get_call_signatures(self, script, line, column):
        _signatures = []
        try:
            call_signatures = script.get_signatures(line, column)
        except KeyError:
            call_signatures = []
        for signature in call_signatures:
            for pos, param in enumerate(signature.params):
                if not param.name:
                    continue
                if param.name == 'self' and pos == 0:
                    continue
                if WORD_RE.match(param.name) is None:
                    continue
                description = re.sub('param ', '', param.description)
                try:
                    name, value = description.split('=')
                except ValueError:
                    name = description
                    value = None
                if name.startswith('*'):
                    continue
                _signatures.append((signature, name, value))
        return _signatures

    def _serialize_completions(self, script, line, column, identifier=None, prefix=''):
        _completions = []

        for signature, name, value in self._get_call_signatures(script, line, column):
            if not self.fuzzy_matcher and not name.lower().startswith(prefix.lower()):
                continue
            _completion = {
                'type': 'property',
                'rightLabel': self._additional_info(signature)
            }
            if value:
                _completion['snippet'] = '%s=${1:%s}$0' % (name, value)
                _completion['text'] = '%s=%s' % (name, value)
            else:
                _completion['snippet'] = '%s=$1$0' % name
                _completion['text'] = name
                _completion['displayText'] = name
            if self.show_doc_strings:
                _completion['description'] = signature.docstring()
            else:
                _completion['description'] = self._generate_signature(signature)
            _completions.append(_completion)

        try:
            completions = script.complete(line, column)
        except KeyError:
            completions = []
        for completion in completions:
            if self.show_doc_strings:
                description = completion.docstring()
            else:
                description = self._generate_signature(completion)
            _completion = {
                'text': completion.name,
                'type': self._get_definition_type(completion),
                'description': description,
                'rightLabel': self._additional_info(completion)
            }
            if any(c['text'].split('=')[0] == _completion['text'] for c in _completions):
                continue
            _completions.append(_completion)
        return json.dumps({'id': identifier, 'results': _completions})

    def _serialize_methods(self, script, line, column, identifier=None, prefix=''):
        _methods = []
        try:
            completions = script.complete(line, column)
        except KeyError:
            return []

        for completion in completions:
            if completion.name == '__autocomplete_python':
                instance = completion.parent().name
                break
        else:
            instance = 'self.__class__'

        for completion in completions:
            params = []
            if hasattr(completion, 'params'):
                params = [p.description for p in completion.params
                          if ARGUMENT_RE.match(p.description)]
            if completion.parent().type == 'class':
                _methods.append({
                    'parent': completion.parent().name,
                    'instance': instance,
                    'name': completion.name,
                    'params': params,
                    'moduleName': completion.module_name,
                    'fileName': os.fspath(completion.module_path),
                    'line': completion.line,
                    'column': completion.column,
                })
        return json.dumps({'id': identifier, 'results': _methods})

    def _top_definition(self, definition):
        for d in definition.goto():
            if d == definition:
                continue
            if d.type == 'import':
                return self._top_definition(d)
            else:
                return d
        return definition

    def _serialize_definitions(self, definitions, identifier=None):
        _definitions = []
        for definition in definitions:
            if definition.module_path:
                if definition.type == 'import':
                    definition = self._top_definition(definition)
                if not definition.module_path:
                    continue
                _definitions.append({
                    'text': definition.name,
                    'type': self._get_definition_type(definition),
                    'fileName': os.fspath(definition.module_path),
                    'line': definition.line - 1,
                    'column': definition.column
                })
        return json.dumps({'id': identifier, 'results': _definitions})

    def _serialize_usages(self, usages, identifier=None):
        _usages = []
        for usage in usages:
            _usages.append({
                'name': usage.name,
                'moduleName': usage.module_name,
                'fileName': os.fspath(usage.module_path),
                'line': usage.line,
                'column': usage.column,
            })
        return json.dumps({'id': identifier, 'results': _usages})

    def _deserialize(self, request):
        return json.loads(request)

    def _set_request_config(self, config):
        sys.path = self.default_sys_path
        self.show_doc_strings = config.get('showDocStrings', True)
        self.fuzzy_matcher = config.get('fuzzyMatching', False)
        jedi.settings.case_insensitive_completion = config.get('caseInsensitive', True)
        self.extra_paths = []
        for path in config.get('extraPaths', []):
            if path and path not in sys.path:
                self.extra_paths.append(path)

    def _process_request(self, request):
        request = self._deserialize(request)
        self._set_request_config(request.get('config', {}))

        path = self._get_top_level_module(request.get('path', ''))
        if path not in sys.path:
            sys.path.insert(0, path)
        lookup = request.get('lookup', 'completions')

        script = jedi.Script(
            code=request['source'], path=request.get('path', ''),
            project=jedi.Project(path, added_sys_path=self.extra_paths),
        )
        line = request['line'] + 1
        column = request['column']

        if lookup == 'definitions':
            return self._write_response(self._serialize_definitions(
                script.goto(line, column), request['id']))
        elif lookup == 'usages':
            return self._write_response(self._serialize_usages(
                script.get_references(line, column), request['id']))
        elif lookup == 'methods':
            return self._write_response(self._serialize_methods(
                script, line, column, request['id'], request.get('prefix', '')))
        else:
            return self._write_response(self._serialize_completions(
                script, line, column, request['id'], request.get('prefix', '')))

    def _write_response(self, response):
        sys.stdout = self.stdout
        sys.stdout.write(response + '\n')
        sys.stdout.flush()

    def watch(self):
        while True:
            try:
                sys.stdout, sys.stderr = self._devnull, self._devnull
                request = self._input.readline()
                if not request:
                    return
                self._process_request(request)
            except Exception:
                sys.stderr = self.stderr
                sys.stderr.write(traceback.format_exc() + '\n')
                sys.stderr.flush()


if __name__ == '__main__':
    if sys.argv[1:]:
        for s in sys.argv[1:]:
            JediCompletion()._process_request(s)
    else:
        JediCompletion().watch()
