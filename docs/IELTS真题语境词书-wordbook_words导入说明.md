# 雅思真题语境词书 wordbook_words 导入说明

## 产物

- `tmp/cloud_import_ielts_content_words/wordbooks.json`：更新 `totalWords` 后的词书文档（JSONL）。
- `tmp/cloud_import_ielts_content_words/wordbook_words.json`：词书与单词关联记录（JSONL，每行一条）。
- `tmp/cloud_import_ielts_content_words/wordbook_words.pretty.json`：同一批记录的格式化 JSON 数组，便于检查。
- `tmp/cloud_import_ielts_content_words/articles.json`：30 篇正文的 title、topicId 与句子 ID 前缀映射。

## 统计

- 词书 ID：`ielts_content_words`
- 阅读文章：30 篇
- 独立词条：1,352 条
- important：695 条
- 正文累计命中：4,166 次
- 出现在多篇文章中的词：655 条

## 口径

- 只匹配 30 篇 Reading Passage 正文，不统计目录、题目、选项、答案和页眉页脚。
- 精确匹配忽略大小写；常见复数、过去式和现在分词采用保守词形还原。
- 句中大写专名匹配会被排除，例如 `Franks`、`Curry`、`Storey` 不会误算成普通词条。
- `order` 按词条首次在正文出现的顺序生成；`chapter` 为首次出现的文章标题。
- `important` 继承现有 IELTS 词库；`bookSenseOverride` 显式写入 `null`。
- `primaryLineId` 使用对应文章的句子顺序，可与后续 `content_lines` 导入保持一致。

## 首次出处分布

| Test | Passage | 文章 | topicId | 首次出现词条 |
|---:|---:|---|---|---:|
| 1 | 1 | Ants Could Teach Ants | `ielts-reading-ants-could-teach-ants` | 66 |
| 1 | 2 | Wealth in a cold climate | `ielts-reading-wealth-in-a-cold-climate` | 98 |
| 1 | 3 | Compliance or Noncompliance for children | `ielts-reading-compliance-or-noncompliance-for-children` | 67 |
| 2 | 1 | Plant Scents | `ielts-reading-plant-scents` | 108 |
| 2 | 2 | The Development of Plastics | `ielts-reading-the-development-of-plastics` | 57 |
| 2 | 3 | Global Warming in New Zealand | `ielts-reading-global-warming-in-new-zealand` | 72 |
| 3 | 1 | Grey Workers | `ielts-reading-grey-workers` | 52 |
| 3 | 2 | The history of salt | `ielts-reading-the-history-of-salt` | 43 |
| 3 | 3 | Designed to Last | `ielts-reading-designed-to-last` | 55 |
| 4 | 1 | William Gilbert and Magnetism | `ielts-reading-william-gilbert-and-magnetism` | 51 |
| 4 | 2 | Seed Hunting | `ielts-reading-seed-hunting` | 47 |
| 4 | 3 | The Power of Nothing | `ielts-reading-the-power-of-nothing` | 64 |
| 5 | 1 | Going Bananas | `ielts-reading-going-bananas` | 46 |
| 5 | 2 | Computer Provides More Questions Than Answers | `ielts-reading-computer-provides-more-questions-than-answers` | 36 |
| 5 | 3 | Save Endangered Language | `ielts-reading-save-endangered-language` | 35 |
| 6 | 1 | Eco-Resort Management Practices | `ielts-reading-eco-resort-management-practices` | 52 |
| 6 | 2 | TV Addiction | `ielts-reading-tv-addiction` | 50 |
| 6 | 3 | Music: Language We All Speak | `ielts-reading-music-language-we-all-speak` | 42 |
| 7 | 1 | California’s age of Megafires | `ielts-reading-california-s-age-of-megafires` | 36 |
| 7 | 2 | European Heat Wave | `ielts-reading-european-heat-wave` | 25 |
| 7 | 3 | The concept of childhood in the western countries | `ielts-reading-the-concept-of-childhood-in-the-western-countries` | 21 |
| 8 | 1 | Natural Pesticide in India | `ielts-reading-natural-pesticide-in-india` | 29 |
| 8 | 2 | Numeracy: Can animals tell numbers? | `ielts-reading-numeracy-can-animals-tell-numbers` | 26 |
| 8 | 3 | Multitasking Debate | `ielts-reading-multitasking-debate` | 22 |
| 9 | 1 | Organic farming and chemical fertilisers | `ielts-reading-organic-farming-and-chemical-fertilisers` | 29 |
| 9 | 2 | The Pearl | `ielts-reading-the-pearl` | 24 |
| 9 | 3 | Scent of success | `ielts-reading-scent-of-success` | 29 |
| 10 | 1 | Coastal Archaeology of Britain | `ielts-reading-coastal-archaeology-of-britain` | 31 |
| 10 | 2 | Activities for Children | `ielts-reading-activities-for-children` | 24 |
| 10 | 3 | Mechanisms of Linguistic Change | `ielts-reading-mechanisms-of-linguistic-change` | 15 |

## 样例

```json
{
  "_id": "ielts_content_words:word_transform",
  "bookId": "ielts_content_words",
  "wordId": "word_transform",
  "word": "transform",
  "normalized": "transform",
  "order": 1,
  "chapter": "Ants Could Teach Ants",
  "important": true,
  "bookSenseOverride": null,
  "sourceStats": {
    "occurrenceCount": 2,
    "articleCount": 2,
    "firstTopicId": "ielts-reading-ants-could-teach-ants",
    "primaryLineId": "line_ants_02"
  },
  "createdAt": null,
  "updatedAt": null
}
```
