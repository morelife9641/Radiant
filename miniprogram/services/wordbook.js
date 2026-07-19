import { callFn } from '../utils/request';

export const wordbookService = {
  list(category) {
    return callFn('wordbook-fetch', { action: 'list', category });
  },
  detail(id, options = {}) {
    return callFn('wordbook-fetch', {
      action: 'detail',
      id,
      ...options
    });
  },
  word(id, word, options = {}) {
    return callFn('wordbook-fetch', {
      action: 'word',
      id,
      word,
      ...options
    });
  },
  words(id, words) {
    return callFn('wordbook-fetch', {
      action: 'words',
      id,
      words
    });
  },
  search(id, keyword, options = {}) {
    return callFn('wordbook-fetch', {
      action: 'search',
      id,
      keyword,
      ...options
    });
  },
  relations(wordId, options = {}) {
    return callFn('wordbook-fetch', {
      action: 'relations',
      wordId,
      ...options
    });
  },
  learningContent(wordId, options = {}) {
    return callFn('wordbook-fetch', {
      action: 'learningContent',
      wordId,
      ...options
    });
  }
};
