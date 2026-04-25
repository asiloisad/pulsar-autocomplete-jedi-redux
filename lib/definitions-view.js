const {SelectListView} = require('@asiloisad/select-list');

class DefinitionsView {
  constructor() {
    this.selectList = new SelectListView({
      className: 'symbols-view',
      loadingMessage: 'Looking for definitions',
      emptyMessage: 'No definition found',
      filterKeyForItem: (item) => item.fileName,
      elementForItem: ({text, fileName, line, type}) => {
        const [, relativePath] = atom.project.relativizePath(fileName);
        return {primary: `${type} ${text}`, secondary: `${relativePath}, line ${line + 1}`};
      },
      didConfirmSelection: (item) => {
        this.navigate(item);
      },
      didCancelSelection: () => {
        this.selectList.hide();
      }
    });
    this.selectList.show();
  }

  setItems(items) {
    this.selectList.update({items, loadingMessage: null});
  }

  confirmed(item) {
    this.navigate(item);
  }

  navigate({fileName, line, column}) {
    this.selectList.hide();
    atom.workspace.open(fileName).then(editor => {
      editor.setCursorBufferPosition([line, column]);
      editor.scrollToCursorPosition({center: true});
    });
  }

  destroy() {
    this.selectList.destroy();
  }
}

module.exports = DefinitionsView;
