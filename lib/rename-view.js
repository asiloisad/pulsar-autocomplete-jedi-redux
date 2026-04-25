const { CompositeDisposable } = require("atom");

class RenameView {
  constructor(usages) {
    const n = usages.length;
    const { name } = usages[0];

    this.disposables = new CompositeDisposable();

    this.element = document.createElement("div");

    const label = document.createElement("div");
    label.textContent = `Type new name to replace ${n} occurrences of ${name} within project:`;
    this.element.appendChild(label);

    this.editor = atom.workspace.buildTextEditor({ mini: true, placeholderText: name });
    const editorElement = atom.views.getView(this.editor);
    this.element.appendChild(editorElement);

    this.panel = atom.workspace.addModalPanel({ item: this.element, visible: true });
    editorElement.focus();

    this.disposables.add(atom.commands.add(this.element, "core:cancel", () => this.destroy()));
  }

  destroy() {
    this.panel.hide();
    this.panel.destroy();
    this.editor.destroy();
    this.disposables.dispose();
  }

  onInput(callback) {
    const editorElement = atom.views.getView(this.editor);
    this.disposables.add(
      atom.commands.add(editorElement, {
        "core:confirm": () => {
          callback(this.editor.getText());
          this.destroy();
        },
      }),
    );
  }
}

module.exports = RenameView;
