module.exports = {
  prefix: "autocomplete-jedi-redux:",
  debug(...msg) {
    if (atom.config.get("autocomplete-jedi-redux.debugLogs")) {
      console.debug(this.prefix, ...msg);
    }
  },

  warning(...msg) {
    console.warn(this.prefix, ...msg);
  },
};
