# autocomplete-jedi-redux

Python packages, variables, methods and functions with their arguments autocompletion powered by [Jedi](https://github.com/davidhalter/jedi).

## Features

- **Autocomplete**: complete packages, variables, methods and functions with their arguments.
- **Go-to-definition**: navigate to the definition of any symbol.
- **Show usages**: list all usages of the symbol under cursor across the project.
- **Rename**: rename a symbol across multiple files in the project.
- **Method override**: insert method overrides from parent classes.
- **Hyperclick integration**: click on any symbol to go-to-definition when [Hyperclick](https://web.pulsar-edit.dev/packages/hyperclick) is installed.
- **Virtual environment support**: set the `Python Command` to the interpreter inside your virtualenv, e.g. `.venv/Scripts/python.exe`, or use `$PROJECT/.venv/Scripts/python.exe` for project-relative paths.
- **Cross-platform**: works on macOS, Linux and Windows.

## Installation

To install `autocomplete-jedi-redux` search for [autocomplete-jedi-redux](https://web.pulsar-edit.dev/packages/autocomplete-jedi-redux) in the Install pane of the Pulsar settings or run `ppm install autocomplete-jedi-redux`. Alternatively, you can run `ppm install asiloisad/pulsar-autocomplete-jedi-redux` to install a package directly from the GitHub repository.

The package requires [Jedi](https://pypi.org/project/jedi/) to be installed.

## Commands

Commands available in `atom-workspace`:

- `autocomplete-jedi-redux:add-roots-to-extra-paths`: add all current project root directories to the `Extra Paths` setting.

Commands available in `atom-text-editor[data-grammar~=python]:not([mini])`:

- `autocomplete-jedi-redux:go-to-definition`: navigate to the definition of the symbol under cursor,
- `autocomplete-jedi-redux:show-usages`: list all usages of the symbol under cursor,
- `autocomplete-jedi-redux:override-method`: insert a method override from a parent class,
- `autocomplete-jedi-redux:rename`: rename a symbol across all files in the project.

## Contributing

Got ideas to make this package better, found a bug, or want to help add new features? Just drop your thoughts on GitHub. Any feedback is welcome!
