const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

// 输入：{ fileID } 微信云存储中的音频文件
// 输出：{ text }
exports.main = async (event, context) => {
  return {
    ok: false,
    code: 'FEATURE_DISABLED',
    message: '语音识别功能尚未开放。'
  };
};
