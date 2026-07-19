# 雅思真题语境词书内容集合导入说明

## 文件

- `content_topics.json`：30 条，JSONL。
- `content_lines.json`：1,423 条，JSONL。
- `content_line_words.json`：4,068 条，JSONL。
- `word_learning_content.json`：1,352 条，JSONL。
- `word_relations.json`：984 条，JSONL。
- `word_relation_groups.json`：200 条，JSONL。
- `translation_review_queue.json`：机器译文的重点人工复核队列。

## 当前状态

- 已有中文翻译：1,423 / 1,423。
- 待机器翻译：0 条。
- 机器翻译待人工复核：1,365 条。
- AI 二次校订待人工复核：25 条。
- 第一篇编辑译文待人工复核：33 条。
- 完整编辑学习内容：66 条（第一篇命中词）。
- 词典基线学习内容：1,286 条；未生成不可靠的正文窗口搭配。

## 约束

- 所有 `content_line_words` 均满足 `_id = lineId:wordId`，重复词位置聚合进 `positions[]`。
- 所有 `word_learning_content._id = wordId`，与新词书的 1,352 条关联一一对应。
- 所有 `wordbook_words.sourceStats.primaryLineId` 均存在于 `content_lines`。
- 未把机器生成或未审核内容标记为 `reviewed/published`。
