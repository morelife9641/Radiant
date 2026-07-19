# 数据库与语料系统设计 v4 review

针对 [数据库与语料系统设计-v4执行版.md](数据库与语料系统设计-v4执行版.md) 的修改建议。

按严重度分四级。每条包含 **问题 / 影响 / 建议**。

---

## P0 — 真矛盾，必改

### 1. §4.2 `audioPolicy` 默认值"示例"与"规则"自相冲突

**问题**：
- 第 155 行示例：`audioPolicy: { provider: "rule", baseUrl: "...", fileName: "accurate.mp3", signFunctionName: "" }`（非 null）
- 第 185 行规则："`audioPolicy` 默认 `null`，只用于覆盖默认音频拼接规则"
- 第 189 行又说："`audioPolicy` 可为 `null`。非空时结构如下"

**影响**：导入脚本到底默认写 null 还是写完整对象？两种都符合文档字面。

**建议**：把示例改成 `audioPolicy: null`。多数词不需要 audioPolicy。同时确保 §11 默认拼接规则（`encodeURIComponent(normalized) + '.mp3'`）写清楚。

---

## P1 — 关键细节

### 2. §8.1 词书列表 cursor 与排序未给

**问题**：list 接口只有 `category: "exam"` 过滤，没有分页、排序规则。

**影响**：未来词书超过 20 本时分页不了。

**建议**：

```text
排序：order by createdAt asc，或新增 wordbooks.order 字段
分页：MVP 词书数 < 100，可先全返不分页
```

### 3. §8.1 详情 cursor 用 `lastOrder` 不能处理 order 相等情况

**问题**：若两条 `wordbook_words.order` 相等（导入数据 bug 或重排过渡期），分页会丢词或重复。

**建议**：

```text
cursor = base64({ lastOrder: 123, lastWordId: "word_x" })
查询条件：order > lastOrder OR (order == lastOrder AND wordId > lastWordId)
```

### 4. §4.10 `app_config` 配置变更生效时机未定

**问题**："configVersion 变化时刷新本地缓存"——已渲染的页面要不要重新拉数据？还是下次启动才生效？

**建议**：二选一明确写出来：

```text
A. 立即生效：emit 配置变更事件，services 层重新走对应数据源
B. 下次启动生效：写本地缓存，本进程沿用旧值
```

倾向 B，简单、稳定。

### 5. §8.2 `bulkImport` 重复调用幂等性未定义

**问题**：迁移失败重试时，同一个词的 progress 是覆盖、合并、还是跳过？

**影响**：首次部分成功后第二次重跑会丢已迁移的最新数据。

**建议**：按 (userId, wordId) upsert：

```text
本次 progress.updatedAt > 现有 -> 覆盖
否则 -> 跳过
```

---

## P2 — 字段语义

### 6. §4.5 `lastResult` 枚举值未列

**问题**：当前代码只有 `known / vague / unknown`，文档未注明。

**建议**：在 §4.5 注明 enum 范围。

### 7. §4.6 `masteredCount` 来源未说

**问题**：`learnedCount` 已有公式，`masteredCount` 没说。

**建议**：

```text
masteredCount = count(user_word_progress
  where userId AND wordId in book AND status = 'mastered')
```

### 8. §11 现状提醒与 §4.2 audioPolicy 描述并存导致困惑

**问题**：§4.2 已经引入 `audioPolicy`，§11 又说"默认桶是 ielts-word-audio"。新人会困惑两套规则的关系。

**建议**：§11 改为：

```text
默认拼接规则在 audio.js 与 audioPolicy 配置中维护。
当前 CET4 没有自己的桶，CET4 词在默认桶里会 404。
长期方案：CET4 写自己的 audioPolicy，或补 words.audio。
```

---

## P3 — 细节

### 9. §4.5 `_id` 示例视觉混淆

**问题**：`_id: "openid_xxx:word_accurate"` 中 `openid_xxx` 自带下划线，与 `:` 分隔符混排，读者乍看以为分隔符不一致。

**建议**：在 §4.5 旁注："示例 `openid_xxx` 是 placeholder，真实 openid 不含分隔语义下划线"。

### 10. §6 tokenize 正则缺中划线 / 破折号

**问题**：当前正则 `/[\s,;.!?:()"""]+/`，但 Valorant lines 可能有 `—`（U+2014）和 `–`（U+2013）。

**建议**：正则补 `—–`：

```js
text.split(/[\s,;.!?:()"""—–]+/).filter(Boolean)
```

### 11. §13 搜索"前缀匹配"性能未提

**问题**：微信云数据库 `regex` 不走索引，全文搜大表会很慢。

**建议**：补一行：

```text
前缀匹配 limit 20。
禁止开放给搜全文。
content_lines.normalizedText 全文搜需要 ES / 自建倒排，MVP 不做。
```

### 12. §14 步骤 2 "写导入脚本" 与步骤 4 "运行" 之间没说本地 dry-run

**建议**：在步骤 3 与 4 之间加：

```text
3.5 本地 dry-run：脚本输出 JSON 到本地文件，确认条数与 schema 后再写云端。
```

---

## 总结

| 级别 | 数量 | 必须本阶段处理 |
|------|------|------|
| P0 | 1 | 是，§4.2 audioPolicy 示例与规则矛盾 |
| P1 | 4 | 是，影响接口契约与迁移幂等性 |
| P2 | 3 | 推荐，写云函数前补 |
| P3 | 4 | 可在迭代中补 |

**唯一阻塞动手的只有 P0-1**：把 §4.2 示例的 `audioPolicy` 改成 `null` 即可。其余写脚本、写云函数时增量补 patch。

整体已达"可开工实现"成熟度，不必再出 v5，遇到细节直接在 v4 上打 patch。
