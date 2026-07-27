import { callFn } from '../utils/request';

export const aiService = {
  chat(payload) {
    return callFn('ai-chat', payload);
  },
  wordMemoryGuide(word) {
    return callFn('ai-chat', {
      action: 'wordMemoryGuide',
      word
    });
  }
};
