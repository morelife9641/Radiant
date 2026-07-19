# 数据库与语料系统设计 review 清单

针对 [数据库与语料系统设计.md](数据库与语料系统设计.md) 的逐条问题清单。

按严重程度分四级。每条包含 **问题 / 影响 / 建议**。

---

## P0 — 必改

### 1. §3.9 `content_line_words._id` 同句重复词冲突

**问题**：示例 `_id: lineId + wordId`，但 `"the the the"` 这种句子同一词出现多次时 `_id` 会重。`positions[]` 已是数组，与 `_id` 拼法逻辑矛盾。

**影响**：导入脚本写入第二次出现时直接覆盖前一次；或抛唯一性冲突。

**建议**：选一种：
- A. `_id = lineId + wordId`，`positions[]` 容纳所有出现位置（推荐，简单）
- B. `_id = lineId + wordId + occurrenceIndex`，每次出现独立一行

### 2. §4 详情页查询触发微信云数据库 `in` 限制

**问题**：`content_line_words` 按 `topicId in preferredTopicIds AND wordId = X` 查。微信云数据库 `command.in()` 与等值查询组合性能差，复合索引加速有限。

**影响**：用户配多个偏好主题时单词详情打开慢。

**建议**：在云函数 `topic-fetch.wordExamples` 里按 topic 逐个查再合并，每次单 topic + wordId 走 `wordId + topicId` 索引；或前端只允许选 1 个 active topic 简化路径。

### 3. §9.1 progress 迁移 `updatedAt` 缺失没兜底

**问题**：冲突策略写"以 updatedAt 更新的一方为准"，但旧版本本地数据可能没 updatedAt——[learn/index.js:147](../miniprogram/pages/learn/index.js#L147) 是后加字段。

**影响**：早期用户迁移时分支判断失败、可能丢数据或错误回退。

**建议**：补一句兜底规则：

```text
本地 updatedAt 缺失 -> 用 lastReviewedAt / firstSeenAt
都缺失 -> 丢弃本地，以云端为准
```

---

## P1 — 设计矛盾或字段未使用

### 4. §3.1 users 同字段四重冗余

**问题**：`_id` / `userId` / `openid` / `accountId` 全是同一个 openid 值。

**建议**：保留 `_id` + `openid`。`accountId` 等真要做跨平台时再引入；`userId` 删除。

### 5. §3.8 `content_lines._id` 生成规则未统一

**问题**：Valorant 示例按音频文件名拼，美剧示例按 `s03e15_001234` 拼。两套规则不通用。

**影响**：二次导入或新 topic 接入时 `_id` 冲突或不可预测。

**建议**：明确统一规则：

```text
line_${topicId}_${stableHash(text + speaker.name + scene)}
```

或

```text
line_${topicId}_${importBatch}_${csvRow}
```

### 6. §3.2 `audioPolicy` 字段实际不会被用到

**问题**：§10.1 只说"有 audio 用 audio，否则按规则拼接"，拼接逻辑在 [audio.js](../miniprogram/utils/audio.js) 全局共用。`audioPolicy` 写在 words 里没人读。

**建议**：删除；或明确语义为"覆盖默认拼接规则的特例（私有桶、特殊文件名）"，注明默认情况下不写入。

### 7. §7 users 索引重复

**问题**：`userId unique` + `openid unique` 是同一字段，且 `_id` 本身已唯一。

**建议**：删 `userId unique`，仅保留 `openid` 索引（如果 `_id == openid`，连这个都可以省）。

### 8. §8 权限规则与微信云数据库实际能力不对齐

**问题**：微信云数据库集合权限四选一：所有人可读、仅创建者可读写、仅管理端、所有人可读写。文档写的"本人可读、仅云函数可写"不是直接选项。

**建议**：在 §8 加一段：

```text
实现方式：
集合权限选"仅创建者可读写"
所有写操作走云函数（用 cloud.callFunction，云函数以管理身份写）
本人读：客户端按 _id 直接读
```

### 9. §9 `currentBookId` vs `users.activeBookId` 语义混淆

**问题**：第 808 行说"统一为 currentBookId 或 users.activeBookId"，但前者是本地字段、后者是云端字段。

**建议**：改写为：

```text
云端权威字段 users.activeBookId
本地缓存字段 currentBookId（替代 onboarding.wordbook 命名）
登录后云端覆盖本地
```

### 10. §11.1 `normalized` 函数定义不精确

**问题**：示例只给了"normalized = word.trim().toLowerCase()"，没说是否处理标点、连字符、内部空格。但 §11.1 又说"不合并 easy-going / easy going"，暗示保留所有标点。

**影响**：导入脚本和运行时分词如果实现不一致，会导致 `content_line_words` 命中率虚低。

**建议**：在 §3.2 写明：

```js
normalized(s) = s.trim().toLowerCase()
// 不去标点、不归一空格、不替换连字符
// "easy-going" 与 "easy going" 视为不同词
```

并提供共用工具函数 `utils/normalize.js`，导入脚本与运行时同源。

---

## P2 — 漏掉的关键话题

### 11. CET4 v2 schema 的复杂 senses 怎么落库

**问题**：§3.2 `words.senses[]` 示例只有 `pos / translation / definitionEn / definitionZh`。CET4 实际有：

```text
collins_definition.{en, zh}
synonyms[].{word, nuance_explanation, example_en, example_zh}
antonyms[]
gaming_link.{game, context, zh}
```

**影响**：直接决定 `wordbook-fetch` 的输出结构。先不定，后续要重写。

**建议**：在 §3.2 增加"扩展 senses 字段"小节。建议直接展开放在 senses 内：

```js
senses: [{
  pos: "n.",
  translation: "...",
  definitionEn: "",
  definitionZh: "",
  collinsEn: "",
  collinsZh: "",
  synonyms: [{ word, nuanceEn, exampleEn, exampleZh }],
  antonyms: [],
  gamingLink: { game, contextEn, contextZh }
}]
```

### 12. 词书的 `tags / important` 导入映射

**问题**：当前 IELTS json 里 `tags` / `important` 在词级别。云端 `important` 在 `wordbook_words`（§3.4）——同一个词在不同词书 `important` 不同时怎么处理？

**建议**：在 §11.1 明确：

```text
导入时
  tags / important 从 word 取出
  写入 wordbook_words（按本书内）
  words 集合不存这两个字段
```

### 13. `content_lines` 没有翻译字段

**问题**：英文台词没翻译。中文学习者很难用。

**建议**：选一种并写入文档：
- A. 加 `translationZh` 字段，导入时空，后续 AI 批量翻译入库
- B. 不入库，详情页打开时由 AI 即时翻译并缓存

倾向 A——可控、可缓存、可校对。

### 14. 词书内容更新流程未规划

**问题**：CET4 修订（错音标、加词、改释义）怎么走？

**影响**：MVP 之后第一次词书修订时会卡住。

**建议**：补一节 §14 词书更新：
- `wordbooks.version` 升级
- 客户端启动比对版本，按需失效本地缓存
- 修订脚本：导入新版词书 → diff → 增量更新 `words` / `wordbook_words`

### 15. 搜索功能未规划

**问题**：用户想搜词，没定义入口与查询路径。

**建议**：补一节：
- 全局搜：`words.normalized` 前缀匹配（云函数 + `regex`）
- 本书内搜：`wordbook_words.normalized` 前缀匹配，限定 `bookId`
- 优先做全局搜，用户从详情结果回到当前词书

---

## P3 — 次要 / 可后续

### 16. 聚合 stats 字段更新时机不明

**字段**：`words.contextStats` / `content_topics.stats.lineCount`

**建议**：明确"由导入脚本写入，运行时不更新"。或干脆删除，查询时聚合算。

### 17. 多集合内嵌冗余字段

**字段**：
- `wordbook_words.word + normalized`
- `user_word_progress.normalized`
- `content_line_words.normalized + surface`

**建议**：在各集合定义末尾标注"冗余字段、仅作展示快照、不保证与源同步"。避免读者误以为是 source of truth。

### 18. §7 `content_line_words` 索引方向重复

**问题**：`wordId + topicId` 和 `topicId + wordId` 同时建，主查询路径只用前者。

**建议**：删 `topicId + wordId`，保留 `wordId + topicId` + `lineId`。

### 19. `users.localMigration.progressMigratedAt` 跨设备未理顺

**问题**：§3.1 字段定义在云端，§9.1 又说"本地写 progress.migratedAt"。

**建议**：

```text
权威字段在云端 users.localMigration.progressMigratedAt
本地不写
换设备登录时读云端字段，已存在则跳过迁移
```

### 20. topic-detail 页分页策略未提

**问题**：14000+ Valorant lines 全拉不可能。

**建议**：补一段"分页 + filter"：默认按 speaker 分组、cursor 分页、每页 50 条。

### 21. `_todayDone` 实际是死字段

**问题**：[learn/index.js:84](../miniprogram/pages/learn/index.js#L84) 只在 today key 命中时才用 `_todayDone` 过滤；首次或换 key 时根本不读它。当前已经基本无用。

**建议**：直接删除字段，统一靠 today key 隔离。比"云端化时再处理"更早做掉。

### 22. 灰度与回滚未提

**问题**：§13 执行顺序全是单向操作。

**建议**：
- 测试环境跑通整链路再切生产
- 前端 service 层做数据源开关，能 storage 与云端切换
- 云函数保留旧路径一段时间（比如 2 周），完全切换后再删

---

## 总结

| 级别 | 数量 | 必须本阶段处理 |
|------|------|------|
| P0 | 3 | 是，影响数据结构正确性 |
| P1 | 7 | 是，落表前定下来 |
| P2 | 5 | 推荐，否则后面要返工 |
| P3 | 7 | 可在迭代中补 |

最值得优先解决的是 **P0 三条**和 **P1 第 11 条**（CET4 复杂 senses 怎么落库）—— 后者直接决定 `wordbook-fetch` 输出结构，先不定后面会重写。

---

# v2 追加 review（针对当前文档第 2 版）

第 2 版已纳入 v1 review 的 P0/P1/P2 大部分条目。重读后发现以下新问题。

## P0 — 矛盾，必须先解决

### N1. §11.2 分词"去标点" vs §3.2 normalize"不去标点" 冲突

**问题**：
- §3.2 `normalized = trim().toLowerCase()`，保留标点和撇号
- §11.2 Valorant 导入流程：分词 → lowercase → **去标点** → exact match `words.normalized`

**影响**：句子里 `"We're"` 去标点后变 `we` / `re`，但 `words.normalized` 存的是 `we're`，命中率严重下降。Valorant 14000 条 lines 大量例句拿不出。

**建议**：统一两套 normalize：
- 共用 `tokenize()` + `normalize()` 函数
- 分词只切空格、保留撇号 + 连字符
- 或者 `normalize` 也去撇号——二选一，必须一致

### N2. §3.8 `stableHash` 算法 / 序列化规则未指定

**问题**：示例只写 `stableHash(text + speaker.name + scene + audio.fileName)`，未明确：
- 哪个算法（md5 / sha1 / fnv32）
- 截断几位
- `scene` 是对象，`JSON.stringify` 不保证 key 顺序
- `scene.timestampMs: null` 与字段缺失是否等价
- Python 导入脚本与 JS 客户端如何保持一致

**影响**：重导 `_id` 变化，`content_lines` 出现重复行。

**建议**：明确规则：

```text
md5(
  text + '|' +
  speaker.name + '|' +
  (audio.fileName || '') + '|' +
  (scene.section || '') + '|' +
  (scene.timestampMs || '')
).slice(0, 12)
```

并提供 Python 与 JS 双语言参考实现。

## P1 — 设计未闭环

### N3. §4 `wordExamples` 排序与返回结构未定

**问题**："preferred topic 命中 → 优先展示 3 条"，但同一 topic 内 50 条都命中时按什么排？

**建议**：
- 排序规则：`audio.url` 存在优先 → speaker 多样性 → `lineId` 稳定排序
- 返回结构明确：

```js
{
  ok: true,
  primary: [{ line, words[] }],   // preferred topic 命中
  secondary: [{ line, words[] }], // 其他 topic 命中
  topics: [{ id, name, cover }]   // 命中 topic 元数据
}
```

### N4. §12.1 `wordbooks.version` 与 §3.3 `schemaVersion` 命名冲突

**问题**：两件不同的事用了同一个名字：
- §3.3 `schemaVersion`：数据结构版本，决定 migrate
- §12.1 `version + 1`：内容修订版本，用于客户端缓存失效

**建议**：

```text
schemaVersion   - 数据结构版本，schema 变了才升
contentVersion  - 内容修订版本，词条增删改就升
```

客户端只关心 `contentVersion` 做缓存失效；schema 升级走单独 migrate 流程。

### N5. §9.1 `bulkImport` 输入/输出不完整

**问题**：输入示例 `progress: {}` 是空，输出未定义。

**建议**：

输入：

```js
{
  action: "bulkImport",
  items: [{
    bookId, word,
    progress: {
      easiness, interval, nextReviewAt,
      correctCount, wrongCount, status,
      lastReviewedAt, firstSeenAt, updatedAt
    }
  }]
}
```

输出：

```js
{
  ok: true,
  importedCount: 120,
  skippedWords: ["roll film", "in addition to"], // 云端 words 没匹配
  failedItems: []
}
```

明确"找不到 wordId 的词跳过、不报错"。

## P2 — 语义不清 / 易出 bug

### N6. §3.6 `todayDone` 缺重置规则

**问题**：跨天后如何归零？读取时按当天日期判断、还是定时重置？

**建议**：

```text
user_book_progress.todayDone 字段配合 lastStudiedAt
读取时若 lastStudiedAt 不在今天 -> todayDone 视为 0
写入时若 lastStudiedAt 不在今天 -> 先清零再加 1
```

### N7. §3.5 vs §3.6 命名不一致

**字段**：`user_word_progress.lastReviewedAt` vs `user_book_progress.lastStudiedAt`

**建议**：统一为 `lastReviewedAt`（或 `lastStudiedAt`），二选一。

### N8. §12.3 灰度开关存哪里未指定

**问题**：`wordbookDataSource = local | cloud` 写在哪？没明确就没法切流。

**建议**：远程配置存于云数据库新建集合 `app_config`：

```js
{
  _id: "default",
  wordbookDataSource: "local",
  progressDataSource: "local",
  topicDataSource: "cloud",
  updatedAt: 1779700000000
}
```

启动时拉一次、缓存到本地。出问题改云端值即可秒回滚。

### N9. §9.2 时区工具实现未给

**问题**：小程序里没 `moment-timezone`。

**建议**：给最小实现：

```js
function getDateKeyAsiaShanghai() {
  const utc = Date.now();
  const shanghai = new Date(utc + 8 * 3600 * 1000);
  return shanghai.toISOString().slice(0, 10);
}
```

放 `utils/date.js`，导入脚本对齐。

### N10. §3.4 `wordbook_words.tags` 在 IELTS 全是 `["ielts"]`

**问题**：IELTS 当前所有词 tags 都是 `["ielts"]`，与 bookId 重复无信息密度。

**建议**：导入规则改为"仅当词条 tags ≠ [bookId] 时写入"。或干脆删除 `tags`，按 `chapter` 字段分类即可。

## P3 — 细节

### N11. 撤回 v1 review P1-4 中"userId 冗余"的建议

**说明**：v1 review §4 我建议删除 `users.userId`。这版已删（对的）。但 `user_word_progress.userId` 不能删——`_id = "openid_xxx_word_accurate"` 无法做"按 userId 查所有进度"的范围查询，必须独立 `userId` 字段配合索引。这版保留是正确的。

### N12. §3.8 `wordCount` 字段语义模糊

**问题**：是源文本按空格切的数量、还是 normalize 后命中 `words` 表的数量？

**建议**：拆成两个字段：

```text
tokenCount         源文本切词数
matchedWordCount   命中 words 表的数量
```

后者由 `build_content_line_words.py` 写入。

### N13. §13.2 引用编号错位

**问题**：表格里 "5 发音流程图位置" 引用首版 review 的条目编号，第 2 版 review 没有第 5 条。读者困惑。

**建议**：删掉 §13 整章；或在小标题注明"以下编号引用 v1 review"。

### N14. §14 索引建立时机未提

**问题**：建集合 → 导入大数据 → 建索引；还是先建索引再导入？大数据量边导入边建索引会慢。

**建议**：在 §14 第一步与第二步之间加一行：

```text
第一步：手动创建集合
第二步：导入数据（不建索引）
第三步：建索引
第四步：写云函数
```

### N15. §3.4 `bookSenseOverride` 与 §12.1 词书更新交互

**问题**：词书新版本把某词的 `bookSenseOverride` 改回 `null` 时，diff 流程要 unset 字段而非保留旧值。

**建议**：在 §12.1 词书更新规则补一行：

```text
bookSenseOverride 从有值改为 null
  -> wordbook_words 集合该字段必须显式 set 为 null
  -> 不能因为新版数据没这个字段就忽略
```

---

## v2 总结

| 级别 | 数量 | 重点 |
|------|------|------|
| P0 | 2 | N1 分词冲突、N2 hash 算法 —— 导入脚本一动手就踩坑 |
| P1 | 3 | N3-5 接口契约缺失，云函数实现前必须定 |
| P2 | 5 | 字段语义/规则补全 |
| P3 | 5 | 细节优化和文档清理 |

第 2 版相比 v1 进步明显，剩下问题大多是**实现层面的算法一致性**和**接口契约细节**，已不在数据建模层面。修完 N1/N2 即可开始写导入脚本。
