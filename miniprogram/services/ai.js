import { callFn } from '../utils/request';

export const aiService = {
  chat(payload) {
    return callFn('ai-chat', payload);
  }
};
