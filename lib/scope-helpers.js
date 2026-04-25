function selectorsMatchScopeChain(selectorString, scopeChain) {
  return selectorString.split(',').some(selector =>
    selector.trim().split(/\s+/).every(part => scopeChain.includes(part))
  );
}

module.exports = {selectorsMatchScopeChain};
