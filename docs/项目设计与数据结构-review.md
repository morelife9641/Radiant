# 项目设计与数据结构 review 清单

针对 [项目设计与数据结构.md](项目设计与数据结构.md) 的逐条问题清单。已排除"CET4 走 IELTS 音频桶 404"（属数据整理问题，单独处理）。

每条包含：**问题** / **影响** / **建议**。

---

## 一、设计矛盾或与现状不符

### 1. §5.2 `words.audio` 与 §2.3 拼接策略冲突

**问题**：目标模型让每个词存 `audio.us / audio.uk` 完整 URL，但当前 [utils/audio.js](../miniprogram/utils/audio.js) 是按 `word.toLowerCase()` 直接拼接 CDN 路径。文档没说清两者关系。

**影响**：迁移到云端时不知道该全量落库 URL，还是继续拼接、字段只在"非默认 CDN / 例外覆盖"时使用。

**建议**：明确策略，二选一：
- A. `audio` 字段为空时按规则拼接，非空时使用字段值（推荐）
- B. 全量落库，loader 不再拼接

### 2. §5.4 `wordbook_words._id` 用 `'ielts_0001'` 是错的

**问题**：示例用 `bookId + order` 拼 `_id`，但 `order` 会因重排、插入新词而变化，`_id` 不可改。

**影响**：一旦词书重排，所有 `_id` 全部失效；外部引用（如 `study_sessions.wordIds`）也会断链。

**建议**：改为 `bookId_wordId`（与 §5.5 `openid_wordId` 一致），`order` 单独作为字段。

### 3. §5.6 `user_book_progress` 与 §7 跨词书共享冲突

**问题**：进度按 `wordId` 共享，但聚合表按 `bookId` 计数。两个未回答的关键问题：
- 用户在 IELTS 学了 `accurate`，TOEFL 也有这词，TOEFL 的 `learnedCount` 要不要 +1？何时计入？
- `dueCount` 实时变化，存聚合表如何保持新鲜？

**影响**：云端同步阶段必踩坑，会出现"切换词书后进度不一致"的体验问题。

**建议**：在 §7 明确两条规则：
- 聚合表 `learnedCount` 只统计"在本书内被学过的词"，由 `learn-submit` 写入时按 `bookId` 计数
- `dueCount` 不入聚合表，查询时按 `userId + nextReviewAt` 索引旁路计算

### 4. §5.2 同形异义词未处理

**问题**：`lead`（铅 / 领导）、`bank`（银行 / 河岸）共用一个 `word_lead` 还是按词性拆？`normalized` 只能解决大小写。

**影响**：未来加入"按义项学习"或词义辨析时，数据模型撑不住。

**建议**：MVP 阶段一词一记录、`senses[]` 内并列；文档明确"暂不区分同形异义词"，作为已知限制。

### 5. §1 流程图把"发音"画在"单词详情"之后

**问题**：实际 [learn/index.js:109](../miniprogram/pages/learn/index.js#L109) 在卡片即支持发音。

**建议**：流程图把发音节点上移到单词卡片层级。

---

## 二、字段语义不清

### 6. §2.2 today key 描述与代码不符

**问题**：文档写 `today.${bookId}.${date}`，代码用 `new Date().toDateString()`，实际是 `"Mon May 25 2026"` 格式，不是 ISO 日期。

**建议**：文档改为 `today.${bookId}.${dateString}` 并注明格式来自 `Date.toDateString()`，或修代码统一为 ISO（推荐后者，便于跨端解析）。

### 7. §3 词书 schema 不统一未说明

**问题**：示例只展示了 IELTS 的简化结构。CET4 实际有 `collins_definition`、`synonyms[]`（含 nuance / example）、`antonyms`、`gaming_link`，schema version 是 v2，IELTS 是 v1。

**建议**：在 §3 加一段说明"两本词书 schema 不一致，loader 不感知差异，UI 兼容缺失字段"，并列出 v1 / v2 的字段差异表。

### 8. §5.5 `lastBookId` 语义不明

**问题**：未说明用途。

**建议**：要么删除；要么注明用于"展示该词最近一次在哪本词书被学到"，并定义谁写入。

### 9. §5.4 `bookSenseOverride` 语义模糊

**问题**：未说明覆盖粒度——整个 `senses[]`、按 `pos` 合并、还是仅覆盖 `translation`？

**建议**：明确为"整段替换 `senses[]`，非空即覆盖"，避免合并语义带来的实现复杂度。

---

## 三、漏掉的关键话题

### 10. 音频本地持久缓存策略

**问题**：当前 `wx.downloadFile` 拿到的 `tempFilePath` 重启即失效，同一个词反复下载。

**建议**：新增小节"音频缓存"，规划：
- 首次下载后 `wx.saveFile` 到 `USER_DATA_PATH`
- 设置 LRU 上限（建议 50MB）
- 命中本地直接 `playUrl(localPath)`，不再走网络

### 11. `_todayDone` 生命周期未定义

**问题**：[learn/index.js:145](../miniprogram/pages/learn/index.js#L145) 写入 `_todayDone: true`，跨天后无人重置。当前靠 `today.${bookId}.${date}` key 隔离能工作，但字段语义混乱。

**建议**：在 §2.2 进度结构里注明 "`_todayDone` 仅在当天有效，跨天读取时忽略"，或干脆删字段、完全用 today 缓存判定。

### 12. 微信云数据库批量查询上限

**问题**：§7 写"批量查 `user_word_progress`"，但小程序端单次 20 条、云函数 100 条/批。3000 词的词书切换时怎么处理？

**建议**：在 §6.2 / §7 明确：
- 切换词书时优先读 `user_book_progress` 聚合表
- 详细进度按需懒加载（卡片显示前才查单条）
- 不做整本预拉

### 13. 时区基准

**问题**：`toDateString()` 用设备本地时区，跨时区或云端 UTC 聚合会出现打卡日期不一致。

**建议**：定一条规则——"所有日期相关 key 与统计统一用东八区"，提供工具函数 `getLocalDateKey()`。

### 14. 小程序包体预算

**问题**：§9 阶段 1 没给词书静态打包的体积上限。主包 2MB、整包 20MB 是硬约束。

**建议**：在 §9 阶段 1 加一行"静态词书总体积预算 ≤ 8MB，超出即必须进入阶段 3 云端化"。当前 CET4 + IELTS 已经接近多少要核一下。

### 15. 词书切换的写入路径未定义

**问题**：当前只有 onboarding 流程写 `onboarding.wordbook`。settings 页要做"切换词书"时改哪个 key？云端化后本地与 `users.activeBookId` 如何同步？

**建议**：
- 本地阶段：统一用 `onboarding.wordbook`（或重命名为 `currentBookId`），settings 直接写
- 云端阶段：`users.activeBookId` 为权威，本地缓存只作离线兜底，登录后从云端覆盖本地

### 16. 本地 progress 迁移到云端

**问题**：§9 阶段 2 说"learn-submit 写 user_word_progress、本地 storage 作离线缓存"，但没说**首次登录如何把已有本地 progress 推上云**。

**建议**：新增 §9.x"本地数据迁移"，定方案：
- 首次登录后扫描所有 `progress.${bookId}`
- 调用 `learn-submit` 的 `action: 'bulkImport'`，按 `wordId` 合并写入 `user_word_progress`
- 冲突策略：取 `easiness / interval` 较高者（云端为准 or 本地为准要选一个）
- 完成后写本地标记 `progress.migratedAt`，避免重复迁移

### 17. 云函数实现状态标注缺失

**问题**：§6.3 描述 learn-submit 完整职责，但 [cloudfunctions/learn-submit/index.js](../cloudfunctions/learn-submit/index.js) 实际是空 stub（只 return `{ words: [] }`）。文档读起来像"已完成"。

**建议**：每个云函数小节末尾加一行：

```text
当前实现：stub / partial / done
```

让文档可作为 source of truth。

---

## 四、建议补充的章节

### 18. 音频资源治理

- 哪个 COS 桶覆盖哪些词书
- 覆盖率核对脚本（输入词表、输出缺词列表）
- 缺词补录流程（TTS 生成 → 上传 → 验证）

### 19. 降级策略

| 场景 | 兜底 |
|------|------|
| 弱网 / 下载超时 | toast 提示，保留上次成功播放的音频 |
| 云函数不可用 | 本地 storage 继续运转，记录待同步队列 |
| CDN 404 | 显式提示"该词暂无音频"而非"播放失败" |

### 20. 隐私与权限

- `users` 集合默认权限：仅本人可读写
- `user_word_progress` / `user_book_progress` / `study_sessions`：仅本人可读写
- `words` / `wordbooks` / `wordbook_words`：所有用户可读、仅管理端可写
- 文档应注明在云开发控制台手动配置规则

### 21. 数据迁移脚本说明

把 §9 阶段 2 / 阶段 3 的数据迁移脚本（本地 → 云端、静态 js → 云数据库）单列一节，给出脚本位置、运行方式、回滚方法。

---

## 优先级建议

| 优先级 | 条目 | 理由 |
|--------|------|------|
| P0 | 2, 3, 16 | 影响云端阶段数据结构，先定下来后面少返工 |
| P1 | 1, 6, 7, 11, 17 | 文档与现状不符，读者会被误导 |
| P2 | 10, 12, 13, 14, 15 | 漏掉的话题，云端阶段开始前补齐即可 |
| P3 | 4, 5, 8, 9, 18-21 | 完善性问题，可慢慢迭代 |
