const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

// TODO: 接入 DeepSeek-V3 / 通义千问
// 输入：{ messages, role, scene }
// 输出：{ reply, suggestion, tokensUsed }
exports.main = async (event, context) => {
  return {
    ok: false,
    code: 'FEATURE_DISABLED',
    message: 'AI 对话功能尚未开放。'
  };
};
