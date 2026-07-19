const POS_ALIASES = {
  a: 'adj',
  adj: 'adj',
  adjective: 'adj',
  ad: 'adv',
  adv: 'adv',
  adverb: 'adv',
  n: 'n',
  noun: 'n',
  v: 'v',
  verb: 'v',
  vi: 'vi',
  vt: 'vt',
  prep: 'prep',
  preposition: 'prep',
  conj: 'conj',
  conjunction: 'conj',
  pron: 'pron',
  pronoun: 'pron',
  num: 'num',
  numeral: 'num',
  int: 'int',
  interj: 'int',
  article: 'art',
  art: 'art'
};

export function formatPos(pos) {
  const raw = String(pos || '')
    .replace(/[\uFF10-\uFF19\uFF21-\uFF3A\uFF41-\uFF5A\uFF0E]/g, char => String.fromCharCode(char.charCodeAt(0) - 0xFEE0))
    .replace(/\u3000/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/\.$/, '');
  if (!raw) return '';
  const normalized = POS_ALIASES[raw] || raw;
  return `${normalized}.`;
}
