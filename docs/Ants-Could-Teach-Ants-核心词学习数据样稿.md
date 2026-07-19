# Ants Could Teach Ants：核心词学习数据样稿

## 范围与状态

- 文章标题：**Ants Could Teach Ants**
- 有效命中词：**66** 个；命中原句：**33** 个。
- 已排除误匹配：人名 `Franks` 不作为单词 `frank`。
- 不保存 PDF 页码。真实原句按 `content_lines` 去重，再通过 `content_line_words` 与单词关联。
- 词形来自 ECDICT；基础例句、搭配、辨析与错误提示为编辑草稿。无可靠内容时数组或字符串保持为空。
- 音标沿用并规范化现有词库主音标；`uk/us` 当前共用该值，仍列入词典编辑复核项。音频按既定 schema 保持空值。
- 当前统一状态：`draft / pending_human_review`，不能直接标记为已人工审核或 published。
- 字段覆盖：构词说明 66/66，搭配 66/66，语法模式 66/66，常见错误 18/66，场景辨析 28/66。后两项只在有学习价值时提供。

## 数据结构

```js
{
  words: { _id, word, normalized, type, phonetic, audio, senses, inflections },
  word_learning_content: { wordId, morphology, derivatives, collocations, usageNotes, commonErrors, examProfile, provenance },
  content_lines: { _id, articleTitle, text, translationZh, sourceType, tags, status },
  content_line_words: { lineId, wordId, surfaceForms, matchType },
  word_relations: { fromWordId, toWord, relationType, explanationZh, status }
}
```

## 文章原句语料

### line_ants_02

> Transformed into research subjects at the University of Bristol, they raced along a tabletop foraging for food - and then, remarkably, returned to guide others.

它们被转移到布里斯托大学作为研究对象，在桌面上竞相觅食，随后又出人意料地返回去引导其他蚂蚁。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_02_word_transform","lineId":"line_ants_02","wordId":"word_transform","surfaceForms":["Transformed"],"matchType":"lemma"},{"_id":"line_ants_02_word_subject","lineId":"line_ants_02","wordId":"word_subject","surfaceForms":["subjects"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_03

> Time and again, followers trailed behind leaders, darting this way and that along the route, presumably to memorise landmarks.

一次又一次，跟随者尾随领路者，沿途来回穿行，似乎是为了记住沿途的地标。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_03_word_route","lineId":"line_ants_03","wordId":"word_route","surfaceForms":["route"],"matchType":"exact"},{"_id":"line_ants_03_word_presumably","lineId":"line_ants_03","wordId":"word_presumably","surfaceForms":["presumably"],"matchType":"exact"},{"_id":"line_ants_03_word_memorise","lineId":"line_ants_03","wordId":"word_memorise","surfaceForms":["memorise"],"matchType":"exact"},{"_id":"line_ants_03_word_landmark","lineId":"line_ants_03","wordId":"word_landmark","surfaceForms":["landmarks"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_04

> Once a follower got its bearings, it tapped the leader with its antennae, prompting the lesson to literally proceed to the next step.

一旦跟随者辨清方向，它就用触角轻触领路者，促使这一教学过程真正进入下一步。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_04_word_tap","lineId":"line_ants_04","wordId":"word_tap","surfaceForms":["tapped"],"matchType":"lemma"},{"_id":"line_ants_04_word_proceed","lineId":"line_ants_04","wordId":"word_proceed","surfaceForms":["proceed"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_05

> The ants were only looking for food, but the researchers said the careful way the leaders led followers, thereby turning them into leaders in their own right, marked the Temnothorax albipennis ant as the very first example of a non-human animal exhibiting teaching behaviour.

这些蚂蚁只是在寻找食物，但研究人员表示，领路者谨慎地带领跟随者、进而把它们也变成领路者的方式，使白扁胸蚁成为首个表现出教学行为的非人类动物实例。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_05_word_thereby","lineId":"line_ants_05","wordId":"word_thereby","surfaceForms":["thereby"],"matchType":"exact"},{"_id":"line_ants_05_word_exhibit","lineId":"line_ants_05","wordId":"word_exhibit","surfaceForms":["exhibiting"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_06

> "Tandem running is an example of teaching, to our knowledge the first in a non-human animal, that involves bidirectional feedback between teacher and pupil” remarks Nigel Franks, professor of animal behaviour and ecology, whose paper on the ant educators was published last week in the journal Nature.

奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_06_word_involve","lineId":"line_ants_06","wordId":"word_involve","surfaceForms":["involves"],"matchType":"lemma"},{"_id":"line_ants_06_word_feedback","lineId":"line_ants_06","wordId":"word_feedback","surfaceForms":["feedback"],"matchType":"exact"},{"_id":"line_ants_06_word_remark","lineId":"line_ants_06","wordId":"word_remark","surfaceForms":["remarks"],"matchType":"lemma"},{"_id":"line_ants_06_word_ecology","lineId":"line_ants_06","wordId":"word_ecology","surfaceForms":["ecology"],"matchType":"exact"},{"_id":"line_ants_06_word_journal","lineId":"line_ants_06","wordId":"word_journal","surfaceForms":["journal"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_07

> No sooner was the paper published, of course, than another educator questioned it.

当然，这篇论文刚一发表，就遭到另一位教育研究者的质疑。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_07_word_course","lineId":"line_ants_07","wordId":"word_course","surfaceForms":["course"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_08

> Marc Hauser, a psychologist and biologist and one of the scientists who came up with the definition of teaching, said it was unclear whether the ants had learned a new skill or merely acquired new information.

心理学家兼生物学家马克·豪瑟是提出教学定义的科学家之一；他说，目前尚不清楚蚂蚁是学会了一项新技能，还是仅仅获得了新信息。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_08_word_definition","lineId":"line_ants_08","wordId":"word_definition","surfaceForms":["definition"],"matchType":"exact"},{"_id":"line_ants_08_word_merely","lineId":"line_ants_08","wordId":"word_merely","surfaceForms":["merely"],"matchType":"exact"},{"_id":"line_ants_08_word_acquire","lineId":"line_ants_08","wordId":"word_acquire","surfaceForms":["acquired"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_10

> With the guidance of leaders, ants could find food faster.

在领路者的引导下，蚂蚁能够更快地找到食物。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_10_word_guidance","lineId":"line_ants_10","wordId":"word_guidance","surfaceForms":["guidance"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_11

> But the help comes at a cost for the leader, who normally would have reached the food about four times faster if not hampered by a follower.

但这种帮助会让领路者付出代价：如果不受跟随者拖累，它通常能快约四倍到达食物所在地。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_11_word_hamper","lineId":"line_ants_11","wordId":"word_hamper","surfaceForms":["hampered"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_12

> This means the hypothesis that the leaders deliberately slowed down in order to pass the skills on to the followers seems potentially valid.

这意味着，领路者为了把技能传给跟随者而有意放慢速度这一假说，似乎可能是成立的。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_12_word_hypothesis","lineId":"line_ants_12","wordId":"word_hypothesis","surfaceForms":["hypothesis"],"matchType":"exact"},{"_id":"line_ants_12_word_valid","lineId":"line_ants_12","wordId":"word_valid","surfaceForms":["valid"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_13

> His ideas were advocated by the students who carried out the video project with him.

与他一起完成视频项目的学生支持他的观点。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_13_word_advocate","lineId":"line_ants_13","wordId":"word_advocate","surfaceForms":["advocated"],"matchType":"lemma"},{"_id":"line_ants_13_word_carry","lineId":"line_ants_13","wordId":"word_carry","surfaceForms":["carried"],"matchType":"lemma"},{"_id":"line_ants_13_word_project","lineId":"line_ants_13","wordId":"word_project","surfaceForms":["project"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_14

> Opposing views still arose, however.

然而，反对意见依然出现了。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_14_word_oppose","lineId":"line_ants_14","wordId":"word_oppose","surfaceForms":["Opposing"],"matchType":"lemma"},{"_id":"line_ants_14_word_however","lineId":"line_ants_14","wordId":"word_however","surfaceForms":["however"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_15

> Hauser noted that mere communication of information is commonplace in the animal world.

豪瑟指出，单纯的信息交流在动物界十分常见。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_15_word_mere","lineId":"line_ants_15","wordId":"word_mere","surfaceForms":["mere"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_16

> Consider a species, for example, that uses alarm calls to warn fellow members about the presence.

例如，设想有一种动物会发出警报声，提醒同类有危险存在。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_16_word_species","lineId":"line_ants_16","wordId":"word_species","surfaceForms":["species"],"matchType":"exact"},{"_id":"line_ants_16_word_alarm","lineId":"line_ants_16","wordId":"word_alarm","surfaceForms":["alarm"],"matchType":"exact"},{"_id":"line_ants_16_word_presence","lineId":"line_ants_16","wordId":"word_presence","surfaceForms":["presence"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`
- `sourceNote`: PDF 原文止于 'the presence.'，句子疑似缺词；中文仅按上下文作保守补译，需回源复核。

### line_ants_17

> Sounding the alarm can be costly, because the animal may draw the attention of the predator to itself.

发出警报可能代价高昂，因为这只动物可能会把捕食者的注意力吸引到自己身上。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_17_word_alarm","lineId":"line_ants_17","wordId":"word_alarm","surfaceForms":["alarm"],"matchType":"exact"},{"_id":"line_ants_17_word_attention","lineId":"line_ants_17","wordId":"word_attention","surfaceForms":["attention"],"matchType":"exact"},{"_id":"line_ants_17_word_predator","lineId":"line_ants_17","wordId":"word_predator","surfaceForms":["predator"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_18

> But it allows others flee to safety.

但这能让其他动物逃到安全地带。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_18_word_flee","lineId":"line_ants_18","wordId":"word_flee","surfaceForms":["flee"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`
- `sourceNote`: PDF 原文为 'allows others flee'；标准英语通常写作 'allows others to flee'。

### line_ants_20

> “The caller incurs a cost.

发出叫声的动物要承担代价。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_20_word_incur","lineId":"line_ants_20","wordId":"word_incur","surfaceForms":["incurs"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_21

> The naive animals gain a benefit and new knowledge that better enables them to learn about the predator’s location than if the caller had not called.

这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_21_word_naive","lineId":"line_ants_21","wordId":"word_naive","surfaceForms":["naive"],"matchType":"exact"},{"_id":"line_ants_21_word_benefit","lineId":"line_ants_21","wordId":"word_benefit","surfaceForms":["benefit"],"matchType":"exact"},{"_id":"line_ants_21_word_enable","lineId":"line_ants_21","wordId":"word_enable","surfaceForms":["enables"],"matchType":"lemma"},{"_id":"line_ants_21_word_predator","lineId":"line_ants_21","wordId":"word_predator","surfaceForms":["predator’s"],"matchType":"lemma"},{"_id":"line_ants_21_word_location","lineId":"line_ants_21","wordId":"word_location","surfaceForms":["location"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_22

> This happens throughout the animal kingdom, but we don’t call it teaching, even though it is clearly transfer of information.

这种情况遍及整个动物界，但我们并不称之为教学，尽管它显然属于信息传递。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_22_word_throughout","lineId":"line_ants_22","wordId":"word_throughout","surfaceForms":["throughout"],"matchType":"exact"},{"_id":"line_ants_22_word_transfer","lineId":"line_ants_22","wordId":"word_transfer","surfaceForms":["transfer"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_24

> He found that cheetah mothers that take their cubs along on hunts gradually allow their cubs to do more of the hunting —going, for example, from killing a gazelle and allowing young cubs to eat merely tripping the gazelle and letting the cubs finish it off.

他发现，猎豹母亲带幼崽狩猎时，会逐渐让幼崽承担更多捕猎任务，例如从杀死羚羊后让幼崽进食，过渡到只把羚羊绊倒，再让幼崽完成捕杀。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_24_word_merely","lineId":"line_ants_24","wordId":"word_merely","surfaceForms":["merely"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_25

> At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.

从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_25_word_level","lineId":"line_ants_25","wordId":"word_level","surfaceForms":["level"],"matchType":"exact"},{"_id":"line_ants_25_word_except","lineId":"line_ants_25","wordId":"word_except","surfaceForms":["except"],"matchType":"exact"},{"_id":"line_ants_25_word_merely","lineId":"line_ants_25","wordId":"word_merely","surfaceForms":["merely"],"matchType":"exact"},{"_id":"line_ants_25_word_facilitate","lineId":"line_ants_25","wordId":"word_facilitate","surfaceForms":["facilitating"],"matchType":"lemma"},{"_id":"line_ants_25_word_various","lineId":"line_ants_25","wordId":"word_various","surfaceForms":["various"],"matchType":"exact"},{"_id":"line_ants_25_word_stage","lineId":"line_ants_25","wordId":"word_stage","surfaceForms":["stages"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_26

> In another instance, birds watching other birds using a stick to locate food such as insects and so on, are observed to do the same thing themselves while finding food later.

另一个例子是，鸟类看到其他鸟用树枝寻找昆虫等食物后，后来觅食时也会做出同样的行为。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_26_word_stick","lineId":"line_ants_26","wordId":"word_stick","surfaceForms":["stick"],"matchType":"exact"},{"_id":"line_ants_26_word_locate","lineId":"line_ants_26","wordId":"word_locate","surfaceForms":["locate"],"matchType":"exact"},{"_id":"line_ants_26_word_observe","lineId":"line_ants_26","wordId":"word_observe","surfaceForms":["observed"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_28

> The challenge in understanding whether other animals truly teach one another, he added, is that human teaching involves a “theory of mind”: teachers are aware that students don’t know something.

他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_28_word_challenge","lineId":"line_ants_28","wordId":"word_challenge","surfaceForms":["challenge"],"matchType":"exact"},{"_id":"line_ants_28_word_understanding","lineId":"line_ants_28","wordId":"word_understanding","surfaceForms":["understanding"],"matchType":"exact"},{"_id":"line_ants_28_word_involve","lineId":"line_ants_28","wordId":"word_involve","surfaceForms":["involves"],"matchType":"lemma"},{"_id":"line_ants_28_word_theory","lineId":"line_ants_28","wordId":"word_theory","surfaceForms":["theory"],"matchType":"exact"},{"_id":"line_ants_28_word_aware","lineId":"line_ants_28","wordId":"word_aware","surfaceForms":["aware"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_29

> He questioned whether Franks’ leader ants really knew that the follower ants were ignorant.

他质疑弗兰克斯的领路蚂蚁是否真的知道跟随者对此一无所知。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_29_word_ignorant","lineId":"line_ants_29","wordId":"word_ignorant","surfaceForms":["ignorant"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_30

> Could they simply have been following an instinctive rule to proceed when the followers tapped them on the legs or abdomen?

它们是否只是遵循一种本能规则：当跟随者轻触它们的腿或腹部时便继续前进？

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_30_word_proceed","lineId":"line_ants_30","wordId":"word_proceed","surfaceForms":["proceed"],"matchType":"exact"},{"_id":"line_ants_30_word_tap","lineId":"line_ants_30","wordId":"word_tap","surfaceForms":["tapped"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_31

> And did leaders that led the way to food - only to find that it had been removed by the experimenter - incur the wrath of followers?

如果领路者带路去寻找食物，却发现食物已被实验人员移走，它会招致跟随者的愤怒吗？

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_31_word_remove","lineId":"line_ants_31","wordId":"word_remove","surfaceForms":["removed"],"matchType":"lemma"},{"_id":"line_ants_31_word_incur","lineId":"line_ants_31","wordId":"word_incur","surfaceForms":["incur"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_32

> That, Hauser said, would suggest that the follower ant actually knew the leader was more knowledgeable and not merely following an instinctive routine itself.

豪瑟说，这将表明跟随者确实知道领路者掌握更多信息，而不只是自己在遵循本能程序。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_32_word_suggest","lineId":"line_ants_32","wordId":"word_suggest","surfaceForms":["suggest"],"matchType":"exact"},{"_id":"line_ants_32_word_merely","lineId":"line_ants_32","wordId":"word_merely","surfaceForms":["merely"],"matchType":"exact"},{"_id":"line_ants_32_word_routine","lineId":"line_ants_32","wordId":"word_routine","surfaceForms":["routine"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_33

> The controversy went on, and for a good reason.

这场争论仍在继续，而且理由充分。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_33_word_controversy","lineId":"line_ants_33","wordId":"word_controversy","surfaceForms":["controversy"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_34

> The occurrence of teaching in ants, if proven to be true, indicates that teaching can evolve in animals with tiny brains.

如果蚂蚁的教学行为得到证实，就表明教学能够在脑容量很小的动物中演化出来。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_34_word_indicate","lineId":"line_ants_34","wordId":"word_indicate","surfaceForms":["indicates"],"matchType":"lemma"},{"_id":"line_ants_34_word_evolve","lineId":"line_ants_34","wordId":"word_evolve","surfaceForms":["evolve"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_35

> It is probably the value of information in social animals that determines when teaching will evolve, rather than the constraints of brain size.

决定教学行为何时演化的，可能是信息对群居动物的价值，而不是脑容量的限制。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_35_word_determine","lineId":"line_ants_35","wordId":"word_determine","surfaceForms":["determines"],"matchType":"lemma"},{"_id":"line_ants_35_word_evolve","lineId":"line_ants_35","wordId":"word_evolve","surfaceForms":["evolve"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_36

> Bennett Galef Jr., a psychologist who studies animal behaviour and social learning at McMaster University in Canada, maintained that ants were unlikely to have a "theory of mind” - meaning that leaders and followers may well have been following instinctive routines that were not based on an understanding of what was happening in another ant’s brain.

研究动物行为和社会学习的心理学家小贝内特·盖利夫认为，蚂蚁不太可能具有‘心智理论’；这意味着领路者和跟随者很可能只是在遵循本能程序，并非基于对另一只蚂蚁脑中活动的理解。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_36_word_maintain","lineId":"line_ants_36","wordId":"word_maintain","surfaceForms":["maintained"],"matchType":"lemma"},{"_id":"line_ants_36_word_theory","lineId":"line_ants_36","wordId":"word_theory","surfaceForms":["theory"],"matchType":"exact"},{"_id":"line_ants_36_word_routine","lineId":"line_ants_36","wordId":"word_routine","surfaceForms":["routines"],"matchType":"lemma"},{"_id":"line_ants_36_word_understanding","lineId":"line_ants_36","wordId":"word_understanding","surfaceForms":["understanding"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_37

> He warned that scientists may be barking up the wrong tree when they look not only for examples of humanlike behaviour among other animals but humanlike thinking that underlies such behaviour.

他警告说，当科学家不仅在其他动物中寻找类似人类的行为，还寻找支撑这种行为的类人思维时，可能找错了方向。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_37_word_bark","lineId":"line_ants_37","wordId":"word_bark","surfaceForms":["barking"],"matchType":"lemma"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

### line_ants_38

> Animals may behave in ways similar to humans without a similar cognitive system, he said, so the behaviour is not necessarily a good guide into how humans came to think the way they do.

他说，动物可能在没有相似认知系统的情况下表现出与人类相似的行为，因此，行为未必能很好地说明人类如何形成如今的思维方式。

- `articleTitle`: `Ants Could Teach Ants`
- `contentLineWords`: [{"_id":"line_ants_38_word_behave","lineId":"line_ants_38","wordId":"word_behave","surfaceForms":["behave"],"matchType":"exact"},{"_id":"line_ants_38_word_necessarily","lineId":"line_ants_38","wordId":"word_necessarily","surfaceForms":["necessarily"],"matchType":"exact"}]
- `sourceType`: `ielts_reading_pdf`
- `status`: `source_verified_translation_draft`

## 核心词数据

### acquire

```json
{
  "_id": "word_acquire",
  "word": "acquire",
  "normalized": "acquire",
  "type": "word",
  "phonetic": {
    "uk": "/əˈkwaɪə(r)/",
    "us": "/əˈkwaɪə(r)/",
    "default": "/əˈkwaɪə(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "acquire_v_01",
      "pos": "v.",
      "translation": "获得；习得",
      "definitionEn": "To gain or obtain something, especially through effort or experience.",
      "definitionZh": "通过努力、学习或经历获得某物，尤指知识、技能或信息。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "acquired"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "acquired"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "acquiring"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "acquires"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_acquire",
  "wordId": "word_acquire",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_08"
  ],
  "primaryExampleLineId": "line_acquire_basic_001",
  "ieltsContextLineIds": [
    "line_ants_08"
  ],
  "morphology": {
    "segments": [
      {
        "form": "acquire",
        "type": "base",
        "meaningZh": "获得；习得",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "acquire 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_acquisition",
        "word": "acquisition",
        "pos": "n",
        "translationZh": "获得；收购",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "acquire knowledge",
      "translationZh": "获得知识"
    },
    {
      "text": "acquire a skill",
      "translationZh": "掌握技能"
    },
    {
      "text": "acquire information",
      "translationZh": "获取信息"
    },
    {
      "text": "acquire property",
      "translationZh": "获得财产"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "acquire + object",
      "exampleEn": "Children acquire language through interaction.",
      "exampleZh": "儿童通过互动习得语言。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_acquisition",
      "word": "acquisition",
      "pos": "n",
      "translationZh": "获得；收购",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_acquire_basic_001",
    "text": "Children acquire language through interaction.",
    "translationZh": "儿童通过互动习得语言。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_08",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Marc Hauser, a psychologist and biologist and one of the scientists who came up with the definition of teaching, said it was unclear whether the ants had learned a new skill or merely acquired new information.",
    "translationZh": "心理学家兼生物学家马克·豪瑟是提出教学定义的科学家之一；他说，目前尚不清楚蚂蚁是学会了一项新技能，还是仅仅获得了新信息。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_acquire_basic_001_word_acquire",
    "lineId": "line_acquire_basic_001",
    "wordId": "word_acquire",
    "surfaceForms": [
      "acquire"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_08_word_acquire",
    "lineId": "line_ants_08",
    "wordId": "word_acquire",
    "surfaceForms": [
      "acquired"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_acquire",
    "toWordId": "word_obtain",
    "toWord": "obtain",
    "relationType": "contrast",
    "explanationZh": "obtain 泛指取得；acquire 常强调逐步获得知识、技能或财产。",
    "exampleEn": "Students acquire language gradually, while researchers obtain data from experiments.",
    "exampleZh": "学生逐渐习得语言，而研究人员从实验中获得数据。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### advocate

```json
{
  "_id": "word_advocate",
  "word": "advocate",
  "normalized": "advocate",
  "type": "word",
  "phonetic": {
    "uk": "/ˈædvəkeɪt/",
    "us": "/ˈædvəkeɪt/",
    "default": "/ˈædvəkeɪt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "advocate_v_01",
      "pos": "v.",
      "translation": "提倡；拥护；主张",
      "definitionEn": "To publicly support or recommend a policy, idea, or course of action.",
      "definitionZh": "公开支持或提倡某种政策、观点或行动方式。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "advocated"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "advocates"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "advocating"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "advocated"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "advocates"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_advocate",
  "wordId": "word_advocate",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_13"
  ],
  "primaryExampleLineId": "line_advocate_basic_001",
  "ieltsContextLineIds": [
    "line_ants_13"
  ],
  "morphology": {
    "segments": [
      {
        "form": "advocate",
        "type": "base",
        "meaningZh": "提倡；拥护；主张",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "advocate 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_advocacy",
        "word": "advocacy",
        "pos": "n",
        "translationZh": "拥护；倡导",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "advocate reform",
      "translationZh": "提倡改革"
    },
    {
      "text": "strongly advocate",
      "translationZh": "大力提倡"
    },
    {
      "text": "advocate doing sth.",
      "translationZh": "主张做某事"
    },
    {
      "text": "an advocate of equality",
      "translationZh": "平等的倡导者"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "advocate + noun / doing sth.",
      "exampleEn": "Many doctors advocate regular exercise.",
      "exampleZh": "许多医生提倡规律运动。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_advocacy",
      "word": "advocacy",
      "pos": "n",
      "translationZh": "拥护；倡导",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "动词重音通常在末音节；名词重音通常在首音节。动词常接名词或动名词，不接 advocate sb. to do。"
  ],
  "commonErrors": [
    {
      "wrong": "advocate people to recycle",
      "correct": "advocate recycling / encourage people to recycle",
      "explanationZh": "advocate 不使用 sb. to do 结构。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_advocate_basic_001",
    "text": "Many doctors advocate regular exercise.",
    "translationZh": "许多医生提倡规律运动。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_13",
    "articleTitle": "Ants Could Teach Ants",
    "text": "His ideas were advocated by the students who carried out the video project with him.",
    "translationZh": "与他一起完成视频项目的学生支持他的观点。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_advocate_basic_001_word_advocate",
    "lineId": "line_advocate_basic_001",
    "wordId": "word_advocate",
    "surfaceForms": [
      "advocate"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_13_word_advocate",
    "lineId": "line_ants_13",
    "wordId": "word_advocate",
    "surfaceForms": [
      "advocated"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_advocate",
    "toWordId": "word_recommend",
    "toWord": "recommend",
    "relationType": "contrast",
    "explanationZh": "advocate 强调公开支持某种政策或做法；recommend 强调给出具体建议。",
    "exampleEn": "The report advocates stricter rules but recommends a gradual timetable.",
    "exampleZh": "报告主张制定更严格的规则，但建议采用渐进式时间表。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### alarm

```json
{
  "_id": "word_alarm",
  "word": "alarm",
  "normalized": "alarm",
  "type": "word",
  "phonetic": {
    "uk": "/əˈlɑːm/",
    "us": "/əˈlɑːm/",
    "default": "/əˈlɑːm/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "alarm_n_01",
      "pos": "n.",
      "translation": "警报；警报声；惊恐",
      "definitionEn": "A warning of danger, often given by a sound or signal.",
      "definitionZh": "对危险发出的警告，常以声音或信号呈现。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "alarms"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "alarmed"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "alarmed"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "alarming"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "alarms"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_alarm",
  "wordId": "word_alarm",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_16",
    "line_ants_17"
  ],
  "primaryExampleLineId": "line_alarm_basic_001",
  "ieltsContextLineIds": [
    "line_ants_16",
    "line_ants_17"
  ],
  "morphology": {
    "segments": [
      {
        "form": "alarm",
        "type": "base",
        "meaningZh": "警报；警报声；惊恐",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "alarm 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "sound the alarm",
      "translationZh": "发出警报"
    },
    {
      "text": "raise the alarm",
      "translationZh": "拉响警报"
    },
    {
      "text": "alarm call",
      "translationZh": "警报声"
    },
    {
      "text": "cause alarm",
      "translationZh": "引起恐慌"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "sound / raise + the alarm",
      "exampleEn": "The smoke alarm woke everyone.",
      "exampleZh": "烟雾报警器惊醒了所有人。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_alarm_basic_001",
    "text": "The smoke alarm woke everyone.",
    "translationZh": "烟雾报警器惊醒了所有人。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_16",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Consider a species, for example, that uses alarm calls to warn fellow members about the presence.",
    "translationZh": "例如，设想有一种动物会发出警报声，提醒同类有危险存在。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft",
    "sourceNote": "PDF 原文止于 'the presence.'，句子疑似缺词；中文仅按上下文作保守补译，需回源复核。"
  },
  {
    "_id": "line_ants_17",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Sounding the alarm can be costly, because the animal may draw the attention of the predator to itself.",
    "translationZh": "发出警报可能代价高昂，因为这只动物可能会把捕食者的注意力吸引到自己身上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_alarm_basic_001_word_alarm",
    "lineId": "line_alarm_basic_001",
    "wordId": "word_alarm",
    "surfaceForms": [
      "alarm"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_16_word_alarm",
    "lineId": "line_ants_16",
    "wordId": "word_alarm",
    "surfaceForms": [
      "alarm"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_17_word_alarm",
    "lineId": "line_ants_17",
    "wordId": "word_alarm",
    "surfaceForms": [
      "alarm"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### attention

```json
{
  "_id": "word_attention",
  "word": "attention",
  "normalized": "attention",
  "type": "word",
  "phonetic": {
    "uk": "/əˈtenʃn/",
    "us": "/əˈtenʃn/",
    "default": "/əˈtenʃn/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "attention_n_01",
      "pos": "n.",
      "translation": "注意；注意力",
      "definitionEn": "The act of directing thought or awareness towards something.",
      "definitionZh": "把思想或意识集中到某事物上的状态或行为。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "attentions"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_attention",
  "wordId": "word_attention",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_17"
  ],
  "primaryExampleLineId": "line_attention_basic_001",
  "ieltsContextLineIds": [
    "line_ants_17"
  ],
  "morphology": {
    "segments": [
      {
        "form": "attention",
        "type": "base",
        "meaningZh": "注意；注意力",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "attention 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "pay attention to",
      "translationZh": "注意"
    },
    {
      "text": "draw attention to",
      "translationZh": "引起对……的注意"
    },
    {
      "text": "attract attention",
      "translationZh": "吸引注意"
    },
    {
      "text": "public attention",
      "translationZh": "公众关注"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "pay attention to + noun",
      "exampleEn": "Please pay attention to the instructions.",
      "exampleZh": "请注意这些说明。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [
    {
      "wrong": "pay attention on the details",
      "correct": "pay attention to the details",
      "explanationZh": "固定搭配是 pay attention to。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_attention_basic_001",
    "text": "Please pay attention to the instructions.",
    "translationZh": "请注意这些说明。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_17",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Sounding the alarm can be costly, because the animal may draw the attention of the predator to itself.",
    "translationZh": "发出警报可能代价高昂，因为这只动物可能会把捕食者的注意力吸引到自己身上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_attention_basic_001_word_attention",
    "lineId": "line_attention_basic_001",
    "wordId": "word_attention",
    "surfaceForms": [
      "attention"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_17_word_attention",
    "lineId": "line_ants_17",
    "wordId": "word_attention",
    "surfaceForms": [
      "attention"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### aware

```json
{
  "_id": "word_aware",
  "word": "aware",
  "normalized": "aware",
  "type": "word",
  "phonetic": {
    "uk": "/əˈweə(r)/",
    "us": "/əˈweə(r)/",
    "default": "/əˈweə(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "aware_adj_01",
      "pos": "adj.",
      "translation": "意识到的；知道的",
      "definitionEn": "Knowing or realising that something exists or is true.",
      "definitionZh": "知道或意识到某事存在或属实。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_aware",
  "wordId": "word_aware",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_28"
  ],
  "primaryExampleLineId": "line_aware_basic_001",
  "ieltsContextLineIds": [
    "line_ants_28"
  ],
  "morphology": {
    "segments": [
      {
        "form": "aware",
        "type": "base",
        "meaningZh": "意识到的；知道的",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "aware 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_awareness",
        "word": "awareness",
        "pos": "n",
        "translationZh": "意识",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_unaware",
        "word": "unaware",
        "pos": "adj",
        "translationZh": "未意识到的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "be aware of",
      "translationZh": "意识到"
    },
    {
      "text": "become aware that",
      "translationZh": "意识到……"
    },
    {
      "text": "fully aware",
      "translationZh": "充分意识到"
    },
    {
      "text": "raise awareness",
      "translationZh": "提高认识"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "be aware of + noun / be aware that + clause",
      "exampleEn": "She was aware of the risk.",
      "exampleZh": "她意识到了风险。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_awareness",
      "word": "awareness",
      "pos": "n",
      "translationZh": "意识",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_unaware",
      "word": "unaware",
      "pos": "adj",
      "translationZh": "未意识到的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "通常作表语：be aware of/that；一般不放在名词前表示“有意识的某人”。"
  ],
  "commonErrors": [
    {
      "wrong": "I aware the risk.",
      "correct": "I am aware of the risk.",
      "explanationZh": "aware 通常作表语，需要 be，并用 of 接名词。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_aware_basic_001",
    "text": "She was aware of the risk.",
    "translationZh": "她意识到了风险。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_28",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The challenge in understanding whether other animals truly teach one another, he added, is that human teaching involves a “theory of mind”: teachers are aware that students don’t know something.",
    "translationZh": "他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_aware_basic_001_word_aware",
    "lineId": "line_aware_basic_001",
    "wordId": "word_aware",
    "surfaceForms": [
      "aware"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_28_word_aware",
    "lineId": "line_ants_28",
    "wordId": "word_aware",
    "surfaceForms": [
      "aware"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_aware",
    "toWordId": "word_conscious",
    "toWord": "conscious",
    "relationType": "contrast",
    "explanationZh": "aware 表示知道某事实；conscious 还可表示有意识、未昏迷。",
    "exampleEn": "She was aware of the danger and remained conscious throughout the rescue.",
    "exampleZh": "她意识到了危险，并在救援过程中始终保持清醒。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### bark

```json
{
  "_id": "word_bark",
  "word": "bark",
  "normalized": "bark",
  "type": "word",
  "phonetic": {
    "uk": "/bɑːk/",
    "us": "/bɑːk/",
    "default": "/bɑːk/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "bark_v_01",
      "pos": "v.",
      "translation": "吠叫；厉声说",
      "definitionEn": "To make the short, loud cry typical of a dog.",
      "definitionZh": "发出狗所特有的短促响亮叫声；文中用于习语 bark up the wrong tree。"
    }
  ],
  "inflections": [
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "barked"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "barking"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "barks"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "barked"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "barks"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_bark",
  "wordId": "word_bark",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_37"
  ],
  "primaryExampleLineId": "line_bark_basic_001",
  "ieltsContextLineIds": [
    "line_ants_37"
  ],
  "morphology": {
    "segments": [
      {
        "form": "bark",
        "type": "base",
        "meaningZh": "吠叫；厉声说",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "bark 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "bark loudly",
      "translationZh": "大声吠叫"
    },
    {
      "text": "bark at sb.",
      "translationZh": "朝某人吠叫"
    },
    {
      "text": "tree bark",
      "translationZh": "树皮"
    },
    {
      "text": "bark up the wrong tree",
      "translationZh": "找错对象"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "bark at + person / bark up the wrong tree",
      "exampleEn": "The dog barked at the stranger.",
      "exampleZh": "狗冲着陌生人叫。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_bark_basic_001",
    "text": "The dog barked at the stranger.",
    "translationZh": "狗冲着陌生人叫。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_37",
    "articleTitle": "Ants Could Teach Ants",
    "text": "He warned that scientists may be barking up the wrong tree when they look not only for examples of humanlike behaviour among other animals but humanlike thinking that underlies such behaviour.",
    "translationZh": "他警告说，当科学家不仅在其他动物中寻找类似人类的行为，还寻找支撑这种行为的类人思维时，可能找错了方向。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_bark_basic_001_word_bark",
    "lineId": "line_bark_basic_001",
    "wordId": "word_bark",
    "surfaceForms": [
      "bark"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_37_word_bark",
    "lineId": "line_ants_37",
    "wordId": "word_bark",
    "surfaceForms": [
      "barking"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### behave

```json
{
  "_id": "word_behave",
  "word": "behave",
  "normalized": "behave",
  "type": "word",
  "phonetic": {
    "uk": "/bɪˈheɪv/",
    "us": "/bɪˈheɪv/",
    "default": "/bɪˈheɪv/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "behave_v_01",
      "pos": "v.",
      "translation": "表现；行为",
      "definitionEn": "To act in a particular way.",
      "definitionZh": "以某种特定方式行动或表现。"
    }
  ],
  "inflections": [
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "behaving"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "behaved"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "behaved"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "behaves"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_behave",
  "wordId": "word_behave",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_38"
  ],
  "primaryExampleLineId": "line_behave_basic_001",
  "ieltsContextLineIds": [
    "line_ants_38"
  ],
  "morphology": {
    "segments": [
      {
        "form": "behave",
        "type": "base",
        "meaningZh": "表现；行为",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "behave 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_behaviour",
        "word": "behaviour",
        "pos": "n",
        "translationZh": "行为",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_behavioural",
        "word": "behavioural",
        "pos": "adj",
        "translationZh": "行为的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "behave well",
      "translationZh": "表现良好"
    },
    {
      "text": "behave badly",
      "translationZh": "表现不佳"
    },
    {
      "text": "behave differently",
      "translationZh": "表现不同"
    },
    {
      "text": "behave like",
      "translationZh": "表现得像"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "behave + adverb / behave like + noun",
      "exampleEn": "The children behaved well.",
      "exampleZh": "孩子们表现得很好。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_behaviour",
      "word": "behaviour",
      "pos": "n",
      "translationZh": "行为",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_behavioural",
      "word": "behavioural",
      "pos": "adj",
      "translationZh": "行为的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_behave_basic_001",
    "text": "The children behaved well.",
    "translationZh": "孩子们表现得很好。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_38",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Animals may behave in ways similar to humans without a similar cognitive system, he said, so the behaviour is not necessarily a good guide into how humans came to think the way they do.",
    "translationZh": "他说，动物可能在没有相似认知系统的情况下表现出与人类相似的行为，因此，行为未必能很好地说明人类如何形成如今的思维方式。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_behave_basic_001_word_behave",
    "lineId": "line_behave_basic_001",
    "wordId": "word_behave",
    "surfaceForms": [
      "behave"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_38_word_behave",
    "lineId": "line_ants_38",
    "wordId": "word_behave",
    "surfaceForms": [
      "behave"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### benefit

```json
{
  "_id": "word_benefit",
  "word": "benefit",
  "normalized": "benefit",
  "type": "word",
  "phonetic": {
    "uk": "/ˈbenɪfɪt/",
    "us": "/ˈbenɪfɪt/",
    "default": "/ˈbenɪfɪt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "benefit_v_01",
      "pos": "n.",
      "translation": "益处；好处",
      "definitionEn": "An advantage or helpful effect.",
      "definitionZh": "某事带来的优势、帮助或积极效果。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "benefits"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "benefited"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "benefits"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "benefited"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "benefiting"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_benefit",
  "wordId": "word_benefit",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_21"
  ],
  "primaryExampleLineId": "line_benefit_basic_001",
  "ieltsContextLineIds": [
    "line_ants_21"
  ],
  "morphology": {
    "segments": [
      {
        "form": "benefit",
        "type": "base",
        "meaningZh": "益处；好处",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "benefit 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_beneficial",
        "word": "beneficial",
        "pos": "adj",
        "translationZh": "有益的",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_beneficiary",
        "word": "beneficiary",
        "pos": "n",
        "translationZh": "受益者",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "benefit from",
      "translationZh": "从……中受益"
    },
    {
      "text": "bring benefits",
      "translationZh": "带来益处"
    },
    {
      "text": "mutual benefit",
      "translationZh": "互惠"
    },
    {
      "text": "health benefits",
      "translationZh": "健康益处"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "benefit + object / benefit from + noun",
      "exampleEn": "Exercise benefits both body and mind.",
      "exampleZh": "锻炼有益于身心。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_beneficial",
      "word": "beneficial",
      "pos": "adj",
      "translationZh": "有益的",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_beneficiary",
      "word": "beneficiary",
      "pos": "n",
      "translationZh": "受益者",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "benefit sb./sth. 表示“使……受益”；benefit from 表示“从……受益”。"
  ],
  "commonErrors": [
    {
      "wrong": "Regular exercise benefits from people.",
      "correct": "People benefit from regular exercise.",
      "explanationZh": "benefit from 的主语应是受益者。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_benefit_basic_001",
    "text": "Exercise benefits both body and mind.",
    "translationZh": "锻炼有益于身心。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_21",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The naive animals gain a benefit and new knowledge that better enables them to learn about the predator’s location than if the caller had not called.",
    "translationZh": "这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_benefit_basic_001_word_benefit",
    "lineId": "line_benefit_basic_001",
    "wordId": "word_benefit",
    "surfaceForms": [
      "benefit"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_21_word_benefit",
    "lineId": "line_ants_21",
    "wordId": "word_benefit",
    "surfaceForms": [
      "benefit"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_benefit",
    "toWordId": "word_advantage",
    "toWord": "advantage",
    "relationType": "contrast",
    "explanationZh": "benefit 是获得的益处；advantage 是使人占优的条件。",
    "exampleEn": "Clean air is a public benefit, while a central location gives the shop a commercial advantage.",
    "exampleZh": "清洁空气是一项公共福祉，而中心位置给商店带来商业优势。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### carry

```json
{
  "_id": "word_carry",
  "word": "carry",
  "normalized": "carry",
  "type": "word",
  "phonetic": {
    "uk": "/ˈkærɪ/",
    "us": "/ˈkærɪ/",
    "default": "/ˈkærɪ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "carry_v_01",
      "pos": "v.",
      "translation": "携带；运送；执行",
      "definitionEn": "To take something from one place to another; in carry out, to perform a task.",
      "definitionZh": "把某物带到另一处；在 carry out 中表示执行或完成。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "carried"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "carrying"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "carried"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "carries"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_carry",
  "wordId": "word_carry",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_13"
  ],
  "primaryExampleLineId": "line_carry_basic_001",
  "ieltsContextLineIds": [
    "line_ants_13"
  ],
  "morphology": {
    "segments": [
      {
        "form": "carry",
        "type": "base",
        "meaningZh": "携带；运送；执行",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "carry 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "carry out",
      "translationZh": "执行"
    },
    {
      "text": "carry information",
      "translationZh": "传递信息"
    },
    {
      "text": "carry a risk",
      "translationZh": "带有风险"
    },
    {
      "text": "carry weight",
      "translationZh": "有影响力"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "carry out + task / research",
      "exampleEn": "This pipe carries water to the village.",
      "exampleZh": "这条管道把水输送到村庄。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_carry_basic_001",
    "text": "This pipe carries water to the village.",
    "translationZh": "这条管道把水输送到村庄。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_13",
    "articleTitle": "Ants Could Teach Ants",
    "text": "His ideas were advocated by the students who carried out the video project with him.",
    "translationZh": "与他一起完成视频项目的学生支持他的观点。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_carry_basic_001_word_carry",
    "lineId": "line_carry_basic_001",
    "wordId": "word_carry",
    "surfaceForms": [
      "carry"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_13_word_carry",
    "lineId": "line_ants_13",
    "wordId": "word_carry",
    "surfaceForms": [
      "carried"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### challenge

```json
{
  "_id": "word_challenge",
  "word": "challenge",
  "normalized": "challenge",
  "type": "word",
  "phonetic": {
    "uk": "/ˈtʃælɪndʒ/",
    "us": "/ˈtʃælɪndʒ/",
    "default": "/ˈtʃælɪndʒ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "challenge_n_01",
      "pos": "n.",
      "translation": "挑战；难题",
      "definitionEn": "A difficult task or problem that tests ability or understanding.",
      "definitionZh": "检验能力或理解力的困难任务或问题。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "challenges"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "challenged"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "challenged"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "challenging"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "challenges"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_challenge",
  "wordId": "word_challenge",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_28"
  ],
  "primaryExampleLineId": "line_challenge_basic_001",
  "ieltsContextLineIds": [
    "line_ants_28"
  ],
  "morphology": {
    "segments": [
      {
        "form": "challenge",
        "type": "base",
        "meaningZh": "挑战；难题",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "challenge 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "face a challenge",
      "translationZh": "面临挑战"
    },
    {
      "text": "pose a challenge",
      "translationZh": "构成挑战"
    },
    {
      "text": "meet a challenge",
      "translationZh": "应对挑战"
    },
    {
      "text": "challenge an assumption",
      "translationZh": "质疑假设"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "pose / face + a challenge",
      "exampleEn": "Finding clean water is a major challenge.",
      "exampleZh": "获得清洁用水是一项重大挑战。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_challenge_basic_001",
    "text": "Finding clean water is a major challenge.",
    "translationZh": "获得清洁用水是一项重大挑战。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_28",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The challenge in understanding whether other animals truly teach one another, he added, is that human teaching involves a “theory of mind”: teachers are aware that students don’t know something.",
    "translationZh": "他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_challenge_basic_001_word_challenge",
    "lineId": "line_challenge_basic_001",
    "wordId": "word_challenge",
    "surfaceForms": [
      "challenge"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_28_word_challenge",
    "lineId": "line_ants_28",
    "wordId": "word_challenge",
    "surfaceForms": [
      "challenge"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### controversy

```json
{
  "_id": "word_controversy",
  "word": "controversy",
  "normalized": "controversy",
  "type": "word",
  "phonetic": {
    "uk": "/ˈkɔntrəvɜːsɪ/",
    "us": "/ˈkɔntrəvɜːsɪ/",
    "default": "/ˈkɔntrəvɜːsɪ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "controversy_n_01",
      "pos": "n.",
      "translation": "争议；公开辩论",
      "definitionEn": "Prolonged public disagreement about an issue.",
      "definitionZh": "围绕某一问题持续发生的公开分歧或争论。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "controversies"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_controversy",
  "wordId": "word_controversy",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_33"
  ],
  "primaryExampleLineId": "line_controversy_basic_001",
  "ieltsContextLineIds": [
    "line_ants_33"
  ],
  "morphology": {
    "segments": [
      {
        "form": "controversy",
        "type": "base",
        "meaningZh": "争议；公开辩论",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "controversy 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_controversial",
        "word": "controversial",
        "pos": "adj",
        "translationZh": "有争议的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "cause controversy",
      "translationZh": "引发争议"
    },
    {
      "text": "a major controversy",
      "translationZh": "重大争议"
    },
    {
      "text": "surrounding controversy",
      "translationZh": "围绕……的争议"
    },
    {
      "text": "controversy over",
      "translationZh": "关于……的争议"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "controversy over / surrounding + noun",
      "exampleEn": "The decision caused public controversy.",
      "exampleZh": "这一决定引发了公众争议。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_controversial",
      "word": "controversial",
      "pos": "adj",
      "translationZh": "有争议的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_controversy_basic_001",
    "text": "The decision caused public controversy.",
    "translationZh": "这一决定引发了公众争议。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_33",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The controversy went on, and for a good reason.",
    "translationZh": "这场争论仍在继续，而且理由充分。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_controversy_basic_001_word_controversy",
    "lineId": "line_controversy_basic_001",
    "wordId": "word_controversy",
    "surfaceForms": [
      "controversy"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_33_word_controversy",
    "lineId": "line_ants_33",
    "wordId": "word_controversy",
    "surfaceForms": [
      "controversy"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_controversy",
    "toWordId": "word_debate",
    "toWord": "debate",
    "relationType": "contrast",
    "explanationZh": "controversy 强调广泛而持续的争议；debate 可指有组织的讨论。",
    "exampleEn": "The policy caused controversy, and Parliament held a formal debate about it.",
    "exampleZh": "这项政策引发争议，议会就此举行了正式辩论。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### course

```json
{
  "_id": "word_course",
  "word": "course",
  "normalized": "course",
  "type": "word",
  "phonetic": {
    "uk": "/kɔːs/",
    "us": "/kɔːs/",
    "default": "/kɔːs/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "course_n_01",
      "pos": "n.",
      "translation": "过程；路线；课程",
      "definitionEn": "A direction, sequence of events, or series of lessons; of course is a fixed expression meaning naturally or certainly.",
      "definitionZh": "路线、事情发展的过程或系列课程；of course 是表示“当然”的固定表达。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "courses"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "coursing"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "coursed"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "courses"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "coursed"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_course",
  "wordId": "word_course",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_07"
  ],
  "primaryExampleLineId": "line_course_basic_001",
  "ieltsContextLineIds": [
    "line_ants_07"
  ],
  "morphology": {
    "segments": [
      {
        "form": "course",
        "type": "base",
        "meaningZh": "过程；路线；课程",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "course 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "a training course",
      "translationZh": "培训课程"
    },
    {
      "text": "course of action",
      "translationZh": "行动方针"
    },
    {
      "text": "in the course of",
      "translationZh": "在……过程中"
    },
    {
      "text": "of course",
      "translationZh": "当然"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "in the course of + noun / of course",
      "exampleEn": "The river changed its course.",
      "exampleZh": "河流改变了流向。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "of course 是固定话语标记；course 单独还可表示课程、路线或过程，需依语境判断。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_course_basic_001",
    "text": "The river changed its course.",
    "translationZh": "河流改变了流向。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_07",
    "articleTitle": "Ants Could Teach Ants",
    "text": "No sooner was the paper published, of course, than another educator questioned it.",
    "translationZh": "当然，这篇论文刚一发表，就遭到另一位教育研究者的质疑。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_course_basic_001_word_course",
    "lineId": "line_course_basic_001",
    "wordId": "word_course",
    "surfaceForms": [
      "course"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_07_word_course",
    "lineId": "line_ants_07",
    "wordId": "word_course",
    "surfaceForms": [
      "course"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### definition

```json
{
  "_id": "word_definition",
  "word": "definition",
  "normalized": "definition",
  "type": "word",
  "phonetic": {
    "uk": "/ˏdefɪˈnɪʃn/",
    "us": "/ˏdefɪˈnɪʃn/",
    "default": "/ˏdefɪˈnɪʃn/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "definition_n_01",
      "pos": "n.",
      "translation": "定义；释义",
      "definitionEn": "A statement that explains the exact meaning of a word or concept.",
      "definitionZh": "说明某个词语或概念确切含义的陈述。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "definitions"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_definition",
  "wordId": "word_definition",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_08"
  ],
  "primaryExampleLineId": "line_definition_basic_001",
  "ieltsContextLineIds": [
    "line_ants_08"
  ],
  "morphology": {
    "segments": [
      {
        "form": "definition",
        "type": "base",
        "meaningZh": "定义；释义",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "definition 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_define",
        "word": "define",
        "pos": "v",
        "translationZh": "定义",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_definite",
        "word": "definite",
        "pos": "adj",
        "translationZh": "明确的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "a precise definition",
      "translationZh": "精确定义"
    },
    {
      "text": "dictionary definition",
      "translationZh": "词典释义"
    },
    {
      "text": "definition of success",
      "translationZh": "成功的定义"
    },
    {
      "text": "by definition",
      "translationZh": "按照定义"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the definition of + noun",
      "exampleEn": "The term has a clear definition.",
      "exampleZh": "这个术语有明确的定义。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_define",
      "word": "define",
      "pos": "v",
      "translationZh": "定义",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_definite",
      "word": "definite",
      "pos": "adj",
      "translationZh": "明确的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_definition_basic_001",
    "text": "The term has a clear definition.",
    "translationZh": "这个术语有明确的定义。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_08",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Marc Hauser, a psychologist and biologist and one of the scientists who came up with the definition of teaching, said it was unclear whether the ants had learned a new skill or merely acquired new information.",
    "translationZh": "心理学家兼生物学家马克·豪瑟是提出教学定义的科学家之一；他说，目前尚不清楚蚂蚁是学会了一项新技能，还是仅仅获得了新信息。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_definition_basic_001_word_definition",
    "lineId": "line_definition_basic_001",
    "wordId": "word_definition",
    "surfaceForms": [
      "definition"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_08_word_definition",
    "lineId": "line_ants_08",
    "wordId": "word_definition",
    "surfaceForms": [
      "definition"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### determine

```json
{
  "_id": "word_determine",
  "word": "determine",
  "normalized": "determine",
  "type": "word",
  "phonetic": {
    "uk": "/dɪˈtɜːmɪn/",
    "us": "/dɪˈtɜːmɪn/",
    "default": "/dɪˈtɜːmɪn/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "determine_v_01",
      "pos": "v.",
      "translation": "决定；确定；查明",
      "definitionEn": "To cause a result or establish something through evidence or calculation.",
      "definitionZh": "决定某种结果，或通过证据、计算查明某事。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "determined"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "determining"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "determines"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "determined"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_determine",
  "wordId": "word_determine",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_35"
  ],
  "primaryExampleLineId": "line_determine_basic_001",
  "ieltsContextLineIds": [
    "line_ants_35"
  ],
  "morphology": {
    "segments": [
      {
        "form": "determine",
        "type": "base",
        "meaningZh": "决定；确定；查明",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "determine 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_determination",
        "word": "determination",
        "pos": "n",
        "translationZh": "决定；决心",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_determined",
        "word": "determined",
        "pos": "adj",
        "translationZh": "坚定的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "determine whether",
      "translationZh": "确定是否"
    },
    {
      "text": "determine the cause",
      "translationZh": "查明原因"
    },
    {
      "text": "determine the outcome",
      "translationZh": "决定结果"
    },
    {
      "text": "largely determine",
      "translationZh": "很大程度上决定"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "determine + object / determine whether + clause",
      "exampleEn": "Tests determine the quality of the water.",
      "exampleZh": "检测可以确定水质。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_determination",
      "word": "determination",
      "pos": "n",
      "translationZh": "决定；决心",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_determined",
      "word": "determined",
      "pos": "adj",
      "translationZh": "坚定的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_determine_basic_001",
    "text": "Tests determine the quality of the water.",
    "translationZh": "检测可以确定水质。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_35",
    "articleTitle": "Ants Could Teach Ants",
    "text": "It is probably the value of information in social animals that determines when teaching will evolve, rather than the constraints of brain size.",
    "translationZh": "决定教学行为何时演化的，可能是信息对群居动物的价值，而不是脑容量的限制。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_determine_basic_001_word_determine",
    "lineId": "line_determine_basic_001",
    "wordId": "word_determine",
    "surfaceForms": [
      "determine"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_35_word_determine",
    "lineId": "line_ants_35",
    "wordId": "word_determine",
    "surfaceForms": [
      "determines"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_determine",
    "toWordId": "word_decide",
    "toWord": "decide",
    "relationType": "contrast",
    "explanationZh": "determine 可表示查明事实或决定结果；decide 更常表示作出选择。",
    "exampleEn": "The evidence will determine the cause, and the committee will decide what to do next.",
    "exampleZh": "证据将查明原因，委员会将决定下一步行动。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### ecology

```json
{
  "_id": "word_ecology",
  "word": "ecology",
  "normalized": "ecology",
  "type": "word",
  "phonetic": {
    "uk": "/iːˈkɔlədʒɪ/",
    "us": "/iːˈkɔlədʒɪ/",
    "default": "/iːˈkɔlədʒɪ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "ecology_n_01",
      "pos": "n.",
      "translation": "生态学；生态关系",
      "definitionEn": "The study of relationships between organisms and their environment.",
      "definitionZh": "研究生物与其环境之间关系的学科。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "ecologies"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_ecology",
  "wordId": "word_ecology",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_06"
  ],
  "primaryExampleLineId": "line_ecology_basic_001",
  "ieltsContextLineIds": [
    "line_ants_06"
  ],
  "morphology": {
    "segments": [
      {
        "form": "eco-",
        "type": "combining_form",
        "meaningZh": "生态；环境",
        "origin": "Greek"
      },
      {
        "form": "-logy",
        "type": "suffix",
        "meaningZh": "……学；研究",
        "origin": "Greek"
      }
    ],
    "explanationZh": "eco-（生态、环境）+ -logy（……学）→ 生态学",
    "relatedWords": [
      {
        "wordId": "word_ecological",
        "word": "ecological",
        "pos": "adj",
        "translationZh": "生态的",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_ecologist",
        "word": "ecologist",
        "pos": "n",
        "translationZh": "生态学家",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "local ecology",
      "translationZh": "当地生态"
    },
    {
      "text": "marine ecology",
      "translationZh": "海洋生态"
    },
    {
      "text": "ecological balance",
      "translationZh": "生态平衡"
    },
    {
      "text": "ecology research",
      "translationZh": "生态学研究"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the ecology of + place / species",
      "exampleEn": "The project may damage the local ecology.",
      "exampleZh": "这个项目可能破坏当地生态。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_ecological",
      "word": "ecological",
      "pos": "adj",
      "translationZh": "生态的",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_ecologist",
      "word": "ecologist",
      "pos": "n",
      "translationZh": "生态学家",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_ecology_basic_001",
    "text": "The project may damage the local ecology.",
    "translationZh": "这个项目可能破坏当地生态。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_06",
    "articleTitle": "Ants Could Teach Ants",
    "text": "\"Tandem running is an example of teaching, to our knowledge the first in a non-human animal, that involves bidirectional feedback between teacher and pupil” remarks Nigel Franks, professor of animal behaviour and ecology, whose paper on the ant educators was published last week in the journal Nature.",
    "translationZh": "奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_ecology_basic_001_word_ecology",
    "lineId": "line_ecology_basic_001",
    "wordId": "word_ecology",
    "surfaceForms": [
      "ecology"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_06_word_ecology",
    "lineId": "line_ants_06",
    "wordId": "word_ecology",
    "surfaceForms": [
      "ecology"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### enable

```json
{
  "_id": "word_enable",
  "word": "enable",
  "normalized": "enable",
  "type": "word",
  "phonetic": {
    "uk": "/ɪˈneɪbl/",
    "us": "/ɪˈneɪbl/",
    "default": "/ɪˈneɪbl/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "enable_v_01",
      "pos": "v.",
      "translation": "使能够；使成为可能",
      "definitionEn": "To give someone the ability or opportunity to do something.",
      "definitionZh": "给予某人做某事的能力或条件。"
    }
  ],
  "inflections": [
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "enables"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "enabled"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "enabling"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "enabled"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_enable",
  "wordId": "word_enable",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_21"
  ],
  "primaryExampleLineId": "line_enable_basic_001",
  "ieltsContextLineIds": [
    "line_ants_21"
  ],
  "morphology": {
    "segments": [
      {
        "form": "en-",
        "type": "prefix",
        "meaningZh": "使成为；使处于",
        "origin": "French/Latin"
      },
      {
        "form": "able",
        "type": "base",
        "meaningZh": "能够的",
        "origin": "Latin"
      }
    ],
    "explanationZh": "en-（使成为）+ able（能够的）→ 使能够",
    "relatedWords": [
      {
        "wordId": "word_disable",
        "word": "disable",
        "pos": "v",
        "translationZh": "使失去能力",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_ability",
        "word": "ability",
        "pos": "n",
        "translationZh": "能力",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "enable sb. to do sth.",
      "translationZh": "使某人能够做某事"
    },
    {
      "text": "enable access",
      "translationZh": "使访问成为可能"
    },
    {
      "text": "technology enables",
      "translationZh": "技术使……成为可能"
    },
    {
      "text": "help enable",
      "translationZh": "帮助实现"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "enable + object + to do sth.",
      "exampleEn": "The app enables users to work remotely.",
      "exampleZh": "这款应用使用户能够远程工作。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_disable",
      "word": "disable",
      "pos": "v",
      "translationZh": "使失去能力",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_ability",
      "word": "ability",
      "pos": "n",
      "translationZh": "能力",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [
    {
      "wrong": "enable people do this",
      "correct": "enable people to do this",
      "explanationZh": "enable 后用 object + to-infinitive。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_enable_basic_001",
    "text": "The app enables users to work remotely.",
    "translationZh": "这款应用使用户能够远程工作。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_21",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The naive animals gain a benefit and new knowledge that better enables them to learn about the predator’s location than if the caller had not called.",
    "translationZh": "这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_enable_basic_001_word_enable",
    "lineId": "line_enable_basic_001",
    "wordId": "word_enable",
    "surfaceForms": [
      "enable"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_21_word_enable",
    "lineId": "line_ants_21",
    "wordId": "word_enable",
    "surfaceForms": [
      "enables"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_enable",
    "toWordId": "word_allow",
    "toWord": "allow",
    "relationType": "contrast",
    "explanationZh": "enable 强调提供能力或条件；allow 强调许可或不加阻止。",
    "exampleEn": "The ramp enables wheelchair users to enter; the guard allows access after checking identification.",
    "exampleZh": "坡道使轮椅使用者能够进入；警卫核验身份后准许通行。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### evolve

```json
{
  "_id": "word_evolve",
  "word": "evolve",
  "normalized": "evolve",
  "type": "word",
  "phonetic": {
    "uk": "/ɪˈvɔlv/",
    "us": "/ɪˈvɔlv/",
    "default": "/ɪˈvɔlv/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "evolve_v_01",
      "pos": "v.",
      "translation": "演化；逐渐发展",
      "definitionEn": "To develop gradually, especially from a simpler form.",
      "definitionZh": "逐渐发展变化，尤指从较简单的形态演变而来。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "evolved"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "evolved"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "evolving"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "evolves"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_evolve",
  "wordId": "word_evolve",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_34",
    "line_ants_35"
  ],
  "primaryExampleLineId": "line_evolve_basic_001",
  "ieltsContextLineIds": [
    "line_ants_34",
    "line_ants_35"
  ],
  "morphology": {
    "segments": [
      {
        "form": "evolve",
        "type": "base",
        "meaningZh": "演化；逐渐发展",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "evolve 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_evolution",
        "word": "evolution",
        "pos": "n",
        "translationZh": "演化",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_evolutionary",
        "word": "evolutionary",
        "pos": "adj",
        "translationZh": "演化的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "gradually evolve",
      "translationZh": "逐渐演变"
    },
    {
      "text": "evolve into",
      "translationZh": "演变成"
    },
    {
      "text": "evolve from",
      "translationZh": "从……演变而来"
    },
    {
      "text": "continue to evolve",
      "translationZh": "继续发展"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "evolve from A into B",
      "exampleEn": "Languages evolve over time.",
      "exampleZh": "语言会随时间演变。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_evolution",
      "word": "evolution",
      "pos": "n",
      "translationZh": "演化",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_evolutionary",
      "word": "evolutionary",
      "pos": "adj",
      "translationZh": "演化的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_evolve_basic_001",
    "text": "Languages evolve over time.",
    "translationZh": "语言会随时间演变。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_34",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The occurrence of teaching in ants, if proven to be true, indicates that teaching can evolve in animals with tiny brains.",
    "translationZh": "如果蚂蚁的教学行为得到证实，就表明教学能够在脑容量很小的动物中演化出来。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_35",
    "articleTitle": "Ants Could Teach Ants",
    "text": "It is probably the value of information in social animals that determines when teaching will evolve, rather than the constraints of brain size.",
    "translationZh": "决定教学行为何时演化的，可能是信息对群居动物的价值，而不是脑容量的限制。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_evolve_basic_001_word_evolve",
    "lineId": "line_evolve_basic_001",
    "wordId": "word_evolve",
    "surfaceForms": [
      "evolve"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_34_word_evolve",
    "lineId": "line_ants_34",
    "wordId": "word_evolve",
    "surfaceForms": [
      "evolve"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_35_word_evolve",
    "lineId": "line_ants_35",
    "wordId": "word_evolve",
    "surfaceForms": [
      "evolve"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_evolve",
    "toWordId": "word_develop",
    "toWord": "develop",
    "relationType": "contrast",
    "explanationZh": "evolve 强调逐渐演变；develop 泛指发展、成长或开发。",
    "exampleEn": "Species evolve over generations, while individual skills develop through practice.",
    "exampleZh": "物种经过世代演化，而个人技能通过练习得到发展。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### except

```json
{
  "_id": "word_except",
  "word": "except",
  "normalized": "except",
  "type": "word",
  "phonetic": {
    "uk": "/ɪkˈsept/",
    "us": "/ɪkˈsept/",
    "default": "/ɪkˈsept/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "except_v_01",
      "pos": "prep./conj.",
      "translation": "除……之外",
      "definitionEn": "Not including a particular person or thing.",
      "definitionZh": "不把某个特定的人或事物包括在内。"
    }
  ],
  "inflections": [
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "excepting"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "excepted"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "excepted"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "excepts"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_except",
  "wordId": "word_except",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_25"
  ],
  "primaryExampleLineId": "line_except_basic_001",
  "ieltsContextLineIds": [
    "line_ants_25"
  ],
  "morphology": {
    "segments": [
      {
        "form": "except",
        "type": "base",
        "meaningZh": "除……之外",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "except 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "except for",
      "translationZh": "除……之外"
    },
    {
      "text": "all except",
      "translationZh": "除……外全部"
    },
    {
      "text": "with the exception of",
      "translationZh": "除……以外"
    },
    {
      "text": "nothing except",
      "translationZh": "除了……什么也没有"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "except + noun / except for + noun",
      "exampleEn": "Everyone came except Tom.",
      "exampleZh": "除了汤姆，所有人都来了。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "except 排除同类中的个体；except for 常用于对整体陈述作局部修正。"
  ],
  "commonErrors": [
    {
      "wrong": "Everyone except of Tom came.",
      "correct": "Everyone except Tom came.",
      "explanationZh": "except 直接接被排除对象，不加 of。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_except_basic_001",
    "text": "Everyone came except Tom.",
    "translationZh": "除了汤姆，所有人都来了。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_25",
    "articleTitle": "Ants Could Teach Ants",
    "text": "At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.",
    "translationZh": "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_except_basic_001_word_except",
    "lineId": "line_except_basic_001",
    "wordId": "word_except",
    "surfaceForms": [
      "except"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_25_word_except",
    "lineId": "line_ants_25",
    "wordId": "word_except",
    "surfaceForms": [
      "except"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### exhibit

```json
{
  "_id": "word_exhibit",
  "word": "exhibit",
  "normalized": "exhibit",
  "type": "word",
  "phonetic": {
    "uk": "/ɪgˈzɪbɪt/",
    "us": "/ɪgˈzɪbɪt/",
    "default": "/ɪgˈzɪbɪt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "exhibit_n_01",
      "pos": "v.",
      "translation": "表现出；展示",
      "definitionEn": "To show a quality, behaviour, or characteristic clearly.",
      "definitionZh": "清楚地表现出某种性质、行为或特征。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "exhibited"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "exhibits"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "exhibiting"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "exhibited"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "exhibits"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_exhibit",
  "wordId": "word_exhibit",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_05"
  ],
  "primaryExampleLineId": "line_exhibit_basic_001",
  "ieltsContextLineIds": [
    "line_ants_05"
  ],
  "morphology": {
    "segments": [
      {
        "form": "exhibit",
        "type": "base",
        "meaningZh": "表现出；展示",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "exhibit 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_exhibition",
        "word": "exhibition",
        "pos": "n",
        "translationZh": "展览",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_exhibitor",
        "word": "exhibitor",
        "pos": "n",
        "translationZh": "参展者",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "exhibit behaviour",
      "translationZh": "表现出行为"
    },
    {
      "text": "exhibit symptoms",
      "translationZh": "表现出症状"
    },
    {
      "text": "exhibit evidence",
      "translationZh": "展示证据"
    },
    {
      "text": "museum exhibit",
      "translationZh": "博物馆展品"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "exhibit + behaviour / symptom / quality",
      "exampleEn": "The patient exhibited clear symptoms.",
      "exampleZh": "患者表现出明显症状。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_exhibition",
      "word": "exhibition",
      "pos": "n",
      "translationZh": "展览",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_exhibitor",
      "word": "exhibitor",
      "pos": "n",
      "translationZh": "参展者",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_exhibit_basic_001",
    "text": "The patient exhibited clear symptoms.",
    "translationZh": "患者表现出明显症状。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_05",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The ants were only looking for food, but the researchers said the careful way the leaders led followers, thereby turning them into leaders in their own right, marked the Temnothorax albipennis ant as the very first example of a non-human animal exhibiting teaching behaviour.",
    "translationZh": "这些蚂蚁只是在寻找食物，但研究人员表示，领路者谨慎地带领跟随者、进而把它们也变成领路者的方式，使白扁胸蚁成为首个表现出教学行为的非人类动物实例。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_exhibit_basic_001_word_exhibit",
    "lineId": "line_exhibit_basic_001",
    "wordId": "word_exhibit",
    "surfaceForms": [
      "exhibit"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_05_word_exhibit",
    "lineId": "line_ants_05",
    "wordId": "word_exhibit",
    "surfaceForms": [
      "exhibiting"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_exhibit",
    "toWordId": "word_display",
    "toWord": "display",
    "relationType": "contrast",
    "explanationZh": "两者都可表示展示；exhibit 更正式，也常指表现出症状或行为。",
    "exampleEn": "The patient exhibited unusual symptoms, and the chart displayed the test results.",
    "exampleZh": "患者表现出异常症状，图表则展示了检测结果。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### facilitate

```json
{
  "_id": "word_facilitate",
  "word": "facilitate",
  "normalized": "facilitate",
  "type": "word",
  "phonetic": {
    "uk": "/fəˈsɪlɪteɪt/",
    "us": "/fəˈsɪlɪteɪt/",
    "default": "/fəˈsɪlɪteɪt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "facilitate_v_01",
      "pos": "v.",
      "translation": "促进；使便利",
      "definitionEn": "To make an action or process easier.",
      "definitionZh": "使某项行动或过程更容易进行。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "facilitated"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "facilitates"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "facilitating"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "facilitated"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_facilitate",
  "wordId": "word_facilitate",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_25"
  ],
  "primaryExampleLineId": "line_facilitate_basic_001",
  "ieltsContextLineIds": [
    "line_ants_25"
  ],
  "morphology": {
    "segments": [
      {
        "form": "facilitate",
        "type": "base",
        "meaningZh": "促进；使便利",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "facilitate 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_facilitation",
        "word": "facilitation",
        "pos": "n",
        "translationZh": "促进；便利",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "facilitate learning",
      "translationZh": "促进学习"
    },
    {
      "text": "facilitate communication",
      "translationZh": "促进交流"
    },
    {
      "text": "facilitate access",
      "translationZh": "便利获取"
    },
    {
      "text": "facilitate the process",
      "translationZh": "推动进程"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "facilitate + noun / process",
      "exampleEn": "The new system facilitates communication.",
      "exampleZh": "新系统促进了沟通。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_facilitation",
      "word": "facilitation",
      "pos": "n",
      "translationZh": "促进；便利",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_facilitate_basic_001",
    "text": "The new system facilitates communication.",
    "translationZh": "新系统促进了沟通。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_25",
    "articleTitle": "Ants Could Teach Ants",
    "text": "At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.",
    "translationZh": "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_facilitate_basic_001_word_facilitate",
    "lineId": "line_facilitate_basic_001",
    "wordId": "word_facilitate",
    "surfaceForms": [
      "facilitate"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_25_word_facilitate",
    "lineId": "line_ants_25",
    "wordId": "word_facilitate",
    "surfaceForms": [
      "facilitating"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_facilitate",
    "toWordId": "word_enable",
    "toWord": "enable",
    "relationType": "contrast",
    "explanationZh": "facilitate 是让过程更容易；enable 是让某事成为可能。",
    "exampleEn": "Clear instructions facilitate learning, while internet access enables students to study remotely.",
    "exampleZh": "清晰的说明促进学习，而网络接入使学生能够远程学习。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### feedback

```json
{
  "_id": "word_feedback",
  "word": "feedback",
  "normalized": "feedback",
  "type": "word",
  "phonetic": {
    "uk": "/ˈfiːdbæk/",
    "us": "/ˈfiːdbæk/",
    "default": "/ˈfiːdbæk/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "feedback_n_01",
      "pos": "n.",
      "translation": "反馈；反馈信息",
      "definitionEn": "Information about a response or performance used to guide later action.",
      "definitionZh": "关于反应或表现的信息，可用于指导后续行动。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "feedbacks"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_feedback",
  "wordId": "word_feedback",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_06"
  ],
  "primaryExampleLineId": "line_feedback_basic_001",
  "ieltsContextLineIds": [
    "line_ants_06"
  ],
  "morphology": {
    "segments": [
      {
        "form": "feed",
        "type": "base",
        "meaningZh": "输入；供给"
      },
      {
        "form": "back",
        "type": "base",
        "meaningZh": "返回"
      }
    ],
    "explanationZh": "feed（输入、供给）+ back（返回）→ 返回的信息，即反馈",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "provide feedback",
      "translationZh": "提供反馈"
    },
    {
      "text": "receive feedback",
      "translationZh": "收到反馈"
    },
    {
      "text": "positive feedback",
      "translationZh": "积极反馈"
    },
    {
      "text": "feedback on",
      "translationZh": "关于……的反馈"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "feedback on + noun",
      "exampleEn": "Students need clear feedback.",
      "exampleZh": "学生需要明确的反馈。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_feedback_basic_001",
    "text": "Students need clear feedback.",
    "translationZh": "学生需要明确的反馈。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_06",
    "articleTitle": "Ants Could Teach Ants",
    "text": "\"Tandem running is an example of teaching, to our knowledge the first in a non-human animal, that involves bidirectional feedback between teacher and pupil” remarks Nigel Franks, professor of animal behaviour and ecology, whose paper on the ant educators was published last week in the journal Nature.",
    "translationZh": "奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_feedback_basic_001_word_feedback",
    "lineId": "line_feedback_basic_001",
    "wordId": "word_feedback",
    "surfaceForms": [
      "feedback"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_06_word_feedback",
    "lineId": "line_ants_06",
    "wordId": "word_feedback",
    "surfaceForms": [
      "feedback"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### flee

```json
{
  "_id": "word_flee",
  "word": "flee",
  "normalized": "flee",
  "type": "word",
  "phonetic": {
    "uk": "/fliː/",
    "us": "/fliː/",
    "default": "/fliː/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "flee_v_01",
      "pos": "v.",
      "translation": "逃离；逃跑",
      "definitionEn": "To leave a dangerous place quickly.",
      "definitionZh": "迅速离开危险的地方。"
    }
  ],
  "inflections": [
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "fled"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "fled"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "fleeing"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "flees"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_flee",
  "wordId": "word_flee",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_18"
  ],
  "primaryExampleLineId": "line_flee_basic_001",
  "ieltsContextLineIds": [
    "line_ants_18"
  ],
  "morphology": {
    "segments": [
      {
        "form": "flee",
        "type": "base",
        "meaningZh": "逃离；逃跑",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "flee 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "flee the scene",
      "translationZh": "逃离现场"
    },
    {
      "text": "flee from",
      "translationZh": "逃离"
    },
    {
      "text": "be forced to flee",
      "translationZh": "被迫逃亡"
    },
    {
      "text": "flee to safety",
      "translationZh": "逃到安全地带"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "flee + place / flee from + danger",
      "exampleEn": "Residents fled the burning building.",
      "exampleZh": "居民逃离了着火的大楼。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_flee_basic_001",
    "text": "Residents fled the burning building.",
    "translationZh": "居民逃离了着火的大楼。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_18",
    "articleTitle": "Ants Could Teach Ants",
    "text": "But it allows others flee to safety.",
    "translationZh": "但这能让其他动物逃到安全地带。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft",
    "sourceNote": "PDF 原文为 'allows others flee'；标准英语通常写作 'allows others to flee'。"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_flee_basic_001_word_flee",
    "lineId": "line_flee_basic_001",
    "wordId": "word_flee",
    "surfaceForms": [
      "flee"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_18_word_flee",
    "lineId": "line_ants_18",
    "wordId": "word_flee",
    "surfaceForms": [
      "flee"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_flee",
    "toWordId": "word_escape",
    "toWord": "escape",
    "relationType": "contrast",
    "explanationZh": "flee 强调迅速逃离危险地点；escape 强调成功摆脱控制或危险。",
    "exampleEn": "Residents fled the town before the fire reached it, and all of them escaped safely.",
    "exampleZh": "居民在大火蔓延到城镇前便逃离了，所有人都安全脱险。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### guidance

```json
{
  "_id": "word_guidance",
  "word": "guidance",
  "normalized": "guidance",
  "type": "word",
  "phonetic": {
    "uk": "/ˈgaɪdns/",
    "us": "/ˈgaɪdns/",
    "default": "/ˈgaɪdns/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "guidance_n_01",
      "pos": "n.",
      "translation": "指导；引导",
      "definitionEn": "Advice or direction that helps someone act or decide.",
      "definitionZh": "帮助某人行动或作决定的建议和指引。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_guidance",
  "wordId": "word_guidance",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_10"
  ],
  "primaryExampleLineId": "line_guidance_basic_001",
  "ieltsContextLineIds": [
    "line_ants_10"
  ],
  "morphology": {
    "segments": [
      {
        "form": "guide",
        "type": "base",
        "meaningZh": "引导；指导"
      },
      {
        "form": "-ance",
        "type": "suffix",
        "meaningZh": "行为、状态或结果",
        "origin": "French/Latin"
      }
    ],
    "explanationZh": "guide（引导）+ -ance（名词后缀）→ 指导、指引",
    "relatedWords": [
      {
        "wordId": "word_guide",
        "word": "guide",
        "pos": "v./n",
        "translationZh": "引导；指南",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "seek guidance",
      "translationZh": "寻求指导"
    },
    {
      "text": "provide guidance",
      "translationZh": "提供指导"
    },
    {
      "text": "under the guidance of",
      "translationZh": "在……指导下"
    },
    {
      "text": "official guidance",
      "translationZh": "官方指引"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "guidance on + noun / under the guidance of + person",
      "exampleEn": "Ask your teacher for guidance.",
      "exampleZh": "向老师寻求指导。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_guide",
      "word": "guide",
      "pos": "v./n",
      "translationZh": "引导；指南",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_guidance_basic_001",
    "text": "Ask your teacher for guidance.",
    "translationZh": "向老师寻求指导。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_10",
    "articleTitle": "Ants Could Teach Ants",
    "text": "With the guidance of leaders, ants could find food faster.",
    "translationZh": "在领路者的引导下，蚂蚁能够更快地找到食物。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_guidance_basic_001_word_guidance",
    "lineId": "line_guidance_basic_001",
    "wordId": "word_guidance",
    "surfaceForms": [
      "guidance"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_10_word_guidance",
    "lineId": "line_ants_10",
    "wordId": "word_guidance",
    "surfaceForms": [
      "guidance"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### hamper

```json
{
  "_id": "word_hamper",
  "word": "hamper",
  "normalized": "hamper",
  "type": "word",
  "phonetic": {
    "uk": "/ˈhæmpə(r)/",
    "us": "/ˈhæmpə(r)/",
    "default": "/ˈhæmpə(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "hamper_v_01",
      "pos": "v.",
      "translation": "妨碍；阻碍",
      "definitionEn": "To make movement, progress, or action difficult.",
      "definitionZh": "使移动、进展或行动变得困难。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "hampered"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "hampered"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "hampers"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "hampering"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "hampers"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_hamper",
  "wordId": "word_hamper",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_11"
  ],
  "primaryExampleLineId": "line_hamper_basic_001",
  "ieltsContextLineIds": [
    "line_ants_11"
  ],
  "morphology": {
    "segments": [
      {
        "form": "hamper",
        "type": "base",
        "meaningZh": "妨碍；阻碍",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "hamper 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "hamper progress",
      "translationZh": "阻碍进展"
    },
    {
      "text": "hamper development",
      "translationZh": "妨碍发展"
    },
    {
      "text": "severely hamper",
      "translationZh": "严重阻碍"
    },
    {
      "text": "be hampered by",
      "translationZh": "受到……妨碍"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "hamper + progress / effort",
      "exampleEn": "Heavy rain hampered the rescue effort.",
      "exampleZh": "大雨妨碍了救援工作。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_hamper_basic_001",
    "text": "Heavy rain hampered the rescue effort.",
    "translationZh": "大雨妨碍了救援工作。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_11",
    "articleTitle": "Ants Could Teach Ants",
    "text": "But the help comes at a cost for the leader, who normally would have reached the food about four times faster if not hampered by a follower.",
    "translationZh": "但这种帮助会让领路者付出代价：如果不受跟随者拖累，它通常能快约四倍到达食物所在地。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_hamper_basic_001_word_hamper",
    "lineId": "line_hamper_basic_001",
    "wordId": "word_hamper",
    "surfaceForms": [
      "hamper"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_11_word_hamper",
    "lineId": "line_ants_11",
    "wordId": "word_hamper",
    "surfaceForms": [
      "hampered"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_hamper",
    "toWordId": "word_hinder",
    "toWord": "hinder",
    "relationType": "contrast",
    "explanationZh": "两者均指阻碍；hamper 常指外部条件使进展变慢。",
    "exampleEn": "Fog hampered the rescue operation, while fallen trees hindered traffic.",
    "exampleZh": "大雾妨碍了救援行动，倒下的树木则阻碍了交通。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### however

```json
{
  "_id": "word_however",
  "word": "however",
  "normalized": "however",
  "type": "word",
  "phonetic": {
    "uk": "/hauˈevə(r)/",
    "us": "/hauˈevə(r)/",
    "default": "/hauˈevə(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "however_conj_01",
      "pos": "adv./conj.",
      "translation": "然而；不过；无论怎样",
      "definitionEn": "Used to introduce a contrast, or before an adjective or adverb to mean regardless of degree.",
      "definitionZh": "用于引出转折；也可置于形容词或副词前表示“无论多么”。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_however",
  "wordId": "word_however",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_14"
  ],
  "primaryExampleLineId": "line_however_basic_001",
  "ieltsContextLineIds": [
    "line_ants_14"
  ],
  "morphology": {
    "segments": [
      {
        "form": "however",
        "type": "base",
        "meaningZh": "然而；不过；无论怎样",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "however 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "however difficult",
      "translationZh": "无论多困难"
    },
    {
      "text": "however small",
      "translationZh": "无论多小"
    },
    {
      "text": "however, the results",
      "translationZh": "然而，结果……"
    },
    {
      "text": "however much",
      "translationZh": "无论多少"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "however, + clause / however + adjective",
      "exampleEn": "The task was difficult; however, we finished it.",
      "exampleZh": "任务很困难；不过，我们完成了。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "表示转折时通常用标点与句子隔开；however + adj./adv. 表示“无论多么……”。"
  ],
  "commonErrors": [
    {
      "wrong": "However the plan failed.",
      "correct": "However, the plan failed.",
      "explanationZh": "句首表示转折时通常需要逗号。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_however_basic_001",
    "text": "The task was difficult; however, we finished it.",
    "translationZh": "任务很困难；不过，我们完成了。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_14",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Opposing views still arose, however.",
    "translationZh": "然而，反对意见依然出现了。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_however_basic_001_word_however",
    "lineId": "line_however_basic_001",
    "wordId": "word_however",
    "surfaceForms": [
      "however"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_14_word_however",
    "lineId": "line_ants_14",
    "wordId": "word_however",
    "surfaceForms": [
      "however"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### hypothesis

```json
{
  "_id": "word_hypothesis",
  "word": "hypothesis",
  "normalized": "hypothesis",
  "type": "word",
  "phonetic": {
    "uk": "/haɪˈpɔθəsɪs/",
    "us": "/haɪˈpɔθəsɪs/",
    "default": "/haɪˈpɔθəsɪs/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "hypothesis_n_01",
      "pos": "n.",
      "translation": "假说；假设",
      "definitionEn": "A proposed explanation that can be tested against evidence.",
      "definitionZh": "一种可以利用证据加以检验的解释或假设。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "hypotheses"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_hypothesis",
  "wordId": "word_hypothesis",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_12"
  ],
  "primaryExampleLineId": "line_hypothesis_basic_001",
  "ieltsContextLineIds": [
    "line_ants_12"
  ],
  "morphology": {
    "segments": [
      {
        "form": "hypo-",
        "type": "prefix",
        "meaningZh": "在下；低于",
        "origin": "Greek"
      },
      {
        "form": "thesis",
        "type": "root",
        "meaningZh": "命题；放置",
        "origin": "Greek"
      }
    ],
    "explanationZh": "源自希腊语 hypo-（在下）+ thesis（命题、放置）；现代义为待检验的假说",
    "relatedWords": [
      {
        "wordId": "word_hypothesise",
        "word": "hypothesise",
        "pos": "v",
        "translationZh": "假设",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_hypothetical",
        "word": "hypothetical",
        "pos": "adj",
        "translationZh": "假设的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "test a hypothesis",
      "translationZh": "检验假说"
    },
    {
      "text": "support a hypothesis",
      "translationZh": "支持假说"
    },
    {
      "text": "reject a hypothesis",
      "translationZh": "否定假说"
    },
    {
      "text": "working hypothesis",
      "translationZh": "工作假设"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the hypothesis that + clause",
      "exampleEn": "The experiment supported the hypothesis.",
      "exampleZh": "实验支持了这一假说。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_hypothesise",
      "word": "hypothesise",
      "pos": "v",
      "translationZh": "假设",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_hypothetical",
      "word": "hypothetical",
      "pos": "adj",
      "translationZh": "假设的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [
    {
      "wrong": "many hypothesis",
      "correct": "many hypotheses",
      "explanationZh": "hypothesis 的复数是 hypotheses。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_hypothesis_basic_001",
    "text": "The experiment supported the hypothesis.",
    "translationZh": "实验支持了这一假说。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_12",
    "articleTitle": "Ants Could Teach Ants",
    "text": "This means the hypothesis that the leaders deliberately slowed down in order to pass the skills on to the followers seems potentially valid.",
    "translationZh": "这意味着，领路者为了把技能传给跟随者而有意放慢速度这一假说，似乎可能是成立的。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_hypothesis_basic_001_word_hypothesis",
    "lineId": "line_hypothesis_basic_001",
    "wordId": "word_hypothesis",
    "surfaceForms": [
      "hypothesis"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_12_word_hypothesis",
    "lineId": "line_ants_12",
    "wordId": "word_hypothesis",
    "surfaceForms": [
      "hypothesis"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_hypothesis",
    "toWordId": "word_theory",
    "toWord": "theory",
    "relationType": "contrast",
    "explanationZh": "hypothesis 是待检验的具体假说；theory 是得到较广证据支持的解释体系。",
    "exampleEn": "The experiment tested a hypothesis derived from evolutionary theory.",
    "exampleZh": "实验检验了一个源自进化理论的假说。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### ignorant

```json
{
  "_id": "word_ignorant",
  "word": "ignorant",
  "normalized": "ignorant",
  "type": "word",
  "phonetic": {
    "uk": "/ˈɪgnərənt/",
    "us": "/ˈɪgnərənt/",
    "default": "/ˈɪgnərənt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "ignorant_adj_01",
      "pos": "adj.",
      "translation": "无知的；不了解的",
      "definitionEn": "Lacking knowledge or awareness about something.",
      "definitionZh": "对某事缺乏知识或认识。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "ignorants"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_ignorant",
  "wordId": "word_ignorant",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_29"
  ],
  "primaryExampleLineId": "line_ignorant_basic_001",
  "ieltsContextLineIds": [
    "line_ants_29"
  ],
  "morphology": {
    "segments": [
      {
        "form": "ignor-",
        "type": "root",
        "meaningZh": "不知道；不认识",
        "origin": "Latin"
      },
      {
        "form": "-ant",
        "type": "suffix",
        "meaningZh": "具有某种状态的",
        "origin": "Latin"
      }
    ],
    "explanationZh": "ignore/拉丁语 ignorare（不知道）+ -ant（形容词后缀）→ 无知的",
    "relatedWords": [
      {
        "wordId": "word_ignorance",
        "word": "ignorance",
        "pos": "n",
        "translationZh": "无知",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "be ignorant of",
      "translationZh": "不知道"
    },
    {
      "text": "remain ignorant",
      "translationZh": "仍不知情"
    },
    {
      "text": "wilfully ignorant",
      "translationZh": "故意无视"
    },
    {
      "text": "ignorant about",
      "translationZh": "对……不了解"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "be ignorant of / about + noun",
      "exampleEn": "He was ignorant of the new rule.",
      "exampleZh": "他不知道这项新规定。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_ignorance",
      "word": "ignorance",
      "pos": "n",
      "translationZh": "无知",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [
    {
      "wrong": "ignorant to the facts",
      "correct": "ignorant of the facts",
      "explanationZh": "固定搭配是 ignorant of/about。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_ignorant_basic_001",
    "text": "He was ignorant of the new rule.",
    "translationZh": "他不知道这项新规定。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_29",
    "articleTitle": "Ants Could Teach Ants",
    "text": "He questioned whether Franks’ leader ants really knew that the follower ants were ignorant.",
    "translationZh": "他质疑弗兰克斯的领路蚂蚁是否真的知道跟随者对此一无所知。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_ignorant_basic_001_word_ignorant",
    "lineId": "line_ignorant_basic_001",
    "wordId": "word_ignorant",
    "surfaceForms": [
      "ignorant"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_29_word_ignorant",
    "lineId": "line_ants_29",
    "wordId": "word_ignorant",
    "surfaceForms": [
      "ignorant"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_ignorant",
    "toWordId": "word_unaware",
    "toWord": "unaware",
    "relationType": "contrast",
    "explanationZh": "unaware 只是未意识到；ignorant 还可暗示缺乏知识，有时带贬义。",
    "exampleEn": "He was ignorant of basic safety rules, while the visitors were simply unaware of the temporary closure.",
    "exampleZh": "他缺乏基本安全规则知识，而游客只是不知道临时关闭一事。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### incur

```json
{
  "_id": "word_incur",
  "word": "incur",
  "normalized": "incur",
  "type": "word",
  "phonetic": {
    "uk": "/ɪnˈkɜː(r)/",
    "us": "/ɪnˈkɜː(r)/",
    "default": "/ɪnˈkɜː(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "incur_v_01",
      "pos": "v.",
      "translation": "招致；承受",
      "definitionEn": "To become subject to an unwanted cost, penalty, or consequence.",
      "definitionZh": "因某种行为而承担不利的费用、处罚或后果。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "incurred"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "incurring"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "incurred"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "incurs"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_incur",
  "wordId": "word_incur",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_20",
    "line_ants_31"
  ],
  "primaryExampleLineId": "line_incur_basic_001",
  "ieltsContextLineIds": [
    "line_ants_20",
    "line_ants_31"
  ],
  "morphology": {
    "segments": [
      {
        "form": "incur",
        "type": "base",
        "meaningZh": "招致；承受",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "incur 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "incur costs",
      "translationZh": "产生成本"
    },
    {
      "text": "incur a penalty",
      "translationZh": "招致处罚"
    },
    {
      "text": "incur debt",
      "translationZh": "负债"
    },
    {
      "text": "incur criticism",
      "translationZh": "招致批评"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "incur + cost / penalty / criticism",
      "exampleEn": "Late payment may incur a fee.",
      "exampleZh": "逾期付款可能会产生费用。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "正式用词，宾语通常是不利后果，如 cost、debt、penalty、criticism。"
  ],
  "commonErrors": [
    {
      "wrong": "incur from extra costs",
      "correct": "incur extra costs",
      "explanationZh": "incur 是及物动词，直接接代价或损失。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_incur_basic_001",
    "text": "Late payment may incur a fee.",
    "translationZh": "逾期付款可能会产生费用。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_20",
    "articleTitle": "Ants Could Teach Ants",
    "text": "“The caller incurs a cost.",
    "translationZh": "发出叫声的动物要承担代价。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_31",
    "articleTitle": "Ants Could Teach Ants",
    "text": "And did leaders that led the way to food - only to find that it had been removed by the experimenter - incur the wrath of followers?",
    "translationZh": "如果领路者带路去寻找食物，却发现食物已被实验人员移走，它会招致跟随者的愤怒吗？",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_incur_basic_001_word_incur",
    "lineId": "line_incur_basic_001",
    "wordId": "word_incur",
    "surfaceForms": [
      "incur"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_20_word_incur",
    "lineId": "line_ants_20",
    "wordId": "word_incur",
    "surfaceForms": [
      "incurs"
    ],
    "matchType": "lemma"
  },
  {
    "_id": "line_ants_31_word_incur",
    "lineId": "line_ants_31",
    "wordId": "word_incur",
    "surfaceForms": [
      "incur"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### indicate

```json
{
  "_id": "word_indicate",
  "word": "indicate",
  "normalized": "indicate",
  "type": "word",
  "phonetic": {
    "uk": "/ˈɪndɪkeɪt/",
    "us": "/ˈɪndɪkeɪt/",
    "default": "/ˈɪndɪkeɪt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "indicate_v_01",
      "pos": "v.",
      "translation": "表明；显示；暗示",
      "definitionEn": "To show that something exists or is likely to be true.",
      "definitionZh": "显示某事存在或很可能属实。"
    }
  ],
  "inflections": [
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "indicates"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "indicated"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "indicated"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "indicating"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_indicate",
  "wordId": "word_indicate",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_34"
  ],
  "primaryExampleLineId": "line_indicate_basic_001",
  "ieltsContextLineIds": [
    "line_ants_34"
  ],
  "morphology": {
    "segments": [
      {
        "form": "indicate",
        "type": "base",
        "meaningZh": "表明；显示；暗示",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "indicate 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_indication",
        "word": "indication",
        "pos": "n",
        "translationZh": "迹象；表明",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_indicator",
        "word": "indicator",
        "pos": "n",
        "translationZh": "指标",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "indicate that",
      "translationZh": "表明……"
    },
    {
      "text": "clearly indicate",
      "translationZh": "清楚表明"
    },
    {
      "text": "indicate a change",
      "translationZh": "显示变化"
    },
    {
      "text": "evidence indicates",
      "translationZh": "证据表明"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "indicate that + clause",
      "exampleEn": "The results indicate a clear trend.",
      "exampleZh": "结果显示出明确趋势。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_indication",
      "word": "indication",
      "pos": "n",
      "translationZh": "迹象；表明",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_indicator",
      "word": "indicator",
      "pos": "n",
      "translationZh": "指标",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_indicate_basic_001",
    "text": "The results indicate a clear trend.",
    "translationZh": "结果显示出明确趋势。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_34",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The occurrence of teaching in ants, if proven to be true, indicates that teaching can evolve in animals with tiny brains.",
    "translationZh": "如果蚂蚁的教学行为得到证实，就表明教学能够在脑容量很小的动物中演化出来。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_indicate_basic_001_word_indicate",
    "lineId": "line_indicate_basic_001",
    "wordId": "word_indicate",
    "surfaceForms": [
      "indicate"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_34_word_indicate",
    "lineId": "line_ants_34",
    "wordId": "word_indicate",
    "surfaceForms": [
      "indicates"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_indicate",
    "toWordId": "word_suggest",
    "toWord": "suggest",
    "relationType": "contrast",
    "explanationZh": "indicate 通常提供较明确的迹象；suggest 往往语气更保留。",
    "exampleEn": "The measurements indicate a rise, while the early observations merely suggest one.",
    "exampleZh": "测量数据表明确有上升，而早期观察只暗示可能上升。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### involve

```json
{
  "_id": "word_involve",
  "word": "involve",
  "normalized": "involve",
  "type": "word",
  "phonetic": {
    "uk": "/ɪnˈvɔlv/",
    "us": "/ɪnˈvɔlv/",
    "default": "/ɪnˈvɔlv/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "involve_v_01",
      "pos": "v.",
      "translation": "涉及；包含；需要",
      "definitionEn": "To include something as a necessary part or result.",
      "definitionZh": "把某事作为必要组成部分或结果包括在内。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "involved"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "involving"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "involves"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "involved"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_involve",
  "wordId": "word_involve",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_06",
    "line_ants_28"
  ],
  "primaryExampleLineId": "line_involve_basic_001",
  "ieltsContextLineIds": [
    "line_ants_06",
    "line_ants_28"
  ],
  "morphology": {
    "segments": [
      {
        "form": "involve",
        "type": "base",
        "meaningZh": "涉及；包含；需要",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "involve 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_involvement",
        "word": "involvement",
        "pos": "n",
        "translationZh": "参与；涉及",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "involve doing sth.",
      "translationZh": "涉及做某事"
    },
    {
      "text": "be involved in",
      "translationZh": "参与"
    },
    {
      "text": "involve a risk",
      "translationZh": "涉及风险"
    },
    {
      "text": "directly involve",
      "translationZh": "直接涉及"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "involve + doing sth. / be involved in + noun",
      "exampleEn": "The job involves working with children.",
      "exampleZh": "这份工作需要与儿童打交道。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_involvement",
      "word": "involvement",
      "pos": "n",
      "translationZh": "参与；涉及",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "involve doing sth.，不能用 involve to do sth.；be involved in 表示参与或卷入。"
  ],
  "commonErrors": [
    {
      "wrong": "The job involves to travel.",
      "correct": "The job involves travelling.",
      "explanationZh": "involve 后接动名词。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_involve_basic_001",
    "text": "The job involves working with children.",
    "translationZh": "这份工作需要与儿童打交道。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_06",
    "articleTitle": "Ants Could Teach Ants",
    "text": "\"Tandem running is an example of teaching, to our knowledge the first in a non-human animal, that involves bidirectional feedback between teacher and pupil” remarks Nigel Franks, professor of animal behaviour and ecology, whose paper on the ant educators was published last week in the journal Nature.",
    "translationZh": "奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_28",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The challenge in understanding whether other animals truly teach one another, he added, is that human teaching involves a “theory of mind”: teachers are aware that students don’t know something.",
    "translationZh": "他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_involve_basic_001_word_involve",
    "lineId": "line_involve_basic_001",
    "wordId": "word_involve",
    "surfaceForms": [
      "involve"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_06_word_involve",
    "lineId": "line_ants_06",
    "wordId": "word_involve",
    "surfaceForms": [
      "involves"
    ],
    "matchType": "lemma"
  },
  {
    "_id": "line_ants_28_word_involve",
    "lineId": "line_ants_28",
    "wordId": "word_involve",
    "surfaceForms": [
      "involves"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_involve",
    "toWordId": "word_include",
    "toWord": "include",
    "relationType": "contrast",
    "explanationZh": "include 表示包含某部分；involve 强调某事必然需要或牵涉某活动。",
    "exampleEn": "The course includes three lectures and involves completing a field project.",
    "exampleZh": "该课程包括三场讲座，并要求完成一个实地项目。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### journal

```json
{
  "_id": "word_journal",
  "word": "journal",
  "normalized": "journal",
  "type": "word",
  "phonetic": {
    "uk": "/ˈdʒɜːnl/",
    "us": "/ˈdʒɜːnl/",
    "default": "/ˈdʒɜːnl/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "journal_sense_01",
      "pos": "n.",
      "translation": "期刊；日志",
      "definitionEn": "A periodical containing academic articles, or a personal written record.",
      "definitionZh": "刊载学术文章的定期出版物，或个人的书面日志。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "journals"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_journal",
  "wordId": "word_journal",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_06"
  ],
  "primaryExampleLineId": "line_journal_basic_001",
  "ieltsContextLineIds": [
    "line_ants_06"
  ],
  "morphology": {
    "segments": [
      {
        "form": "journal",
        "type": "base",
        "meaningZh": "期刊；日志",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "journal 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "academic journal",
      "translationZh": "学术期刊"
    },
    {
      "text": "scientific journal",
      "translationZh": "科学期刊"
    },
    {
      "text": "publish in a journal",
      "translationZh": "在期刊发表"
    },
    {
      "text": "keep a journal",
      "translationZh": "写日记"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "publish in + a journal",
      "exampleEn": "The findings appeared in a scientific journal.",
      "exampleZh": "研究结果发表在一本科学期刊上。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "academic/scientific journal 指学术期刊；日常个人记录可用 journal 或 diary。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_journal_basic_001",
    "text": "The findings appeared in a scientific journal.",
    "translationZh": "研究结果发表在一本科学期刊上。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_06",
    "articleTitle": "Ants Could Teach Ants",
    "text": "\"Tandem running is an example of teaching, to our knowledge the first in a non-human animal, that involves bidirectional feedback between teacher and pupil” remarks Nigel Franks, professor of animal behaviour and ecology, whose paper on the ant educators was published last week in the journal Nature.",
    "translationZh": "奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_journal_basic_001_word_journal",
    "lineId": "line_journal_basic_001",
    "wordId": "word_journal",
    "surfaceForms": [
      "journal"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_06_word_journal",
    "lineId": "line_ants_06",
    "wordId": "word_journal",
    "surfaceForms": [
      "journal"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### landmark

```json
{
  "_id": "word_landmark",
  "word": "landmark",
  "normalized": "landmark",
  "type": "word",
  "phonetic": {
    "uk": "/ˈlændmɑːk/",
    "us": "/ˈlændmɑːk/",
    "default": "/ˈlændmɑːk/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "landmark_n_01",
      "pos": "n.",
      "translation": "地标；里程碑",
      "definitionEn": "A recognisable feature used for orientation, or an event of major importance.",
      "definitionZh": "用于辨认方位的显著特征；也指具有重大意义的事件。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "landmarks"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "landmarking"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_landmark",
  "wordId": "word_landmark",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_03"
  ],
  "primaryExampleLineId": "line_landmark_basic_001",
  "ieltsContextLineIds": [
    "line_ants_03"
  ],
  "morphology": {
    "segments": [
      {
        "form": "landmark",
        "type": "base",
        "meaningZh": "地标；里程碑",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "landmark 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "historic landmark",
      "translationZh": "历史地标"
    },
    {
      "text": "local landmark",
      "translationZh": "当地地标"
    },
    {
      "text": "landmark study",
      "translationZh": "里程碑式研究"
    },
    {
      "text": "landmark decision",
      "translationZh": "具有里程碑意义的决定"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a landmark in + field / history",
      "exampleEn": "The tower is a famous landmark.",
      "exampleZh": "这座塔是著名地标。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_landmark_basic_001",
    "text": "The tower is a famous landmark.",
    "translationZh": "这座塔是著名地标。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_03",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Time and again, followers trailed behind leaders, darting this way and that along the route, presumably to memorise landmarks.",
    "translationZh": "一次又一次，跟随者尾随领路者，沿途来回穿行，似乎是为了记住沿途的地标。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_landmark_basic_001_word_landmark",
    "lineId": "line_landmark_basic_001",
    "wordId": "word_landmark",
    "surfaceForms": [
      "landmark"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_03_word_landmark",
    "lineId": "line_ants_03",
    "wordId": "word_landmark",
    "surfaceForms": [
      "landmarks"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### level

```json
{
  "_id": "word_level",
  "word": "level",
  "normalized": "level",
  "type": "word",
  "phonetic": {
    "uk": "/ˈlevl/",
    "us": "/ˈlevl/",
    "default": "/ˈlevl/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "level_n_01",
      "pos": "n.",
      "translation": "层面；水平；等级",
      "definitionEn": "A position on a scale, or a particular way of considering something.",
      "definitionZh": "某一尺度上的位置，或看待问题的特定层面。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "levels"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "levelled"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "levelled"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "levelling"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "levels"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_level",
  "wordId": "word_level",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_25"
  ],
  "primaryExampleLineId": "line_level_basic_001",
  "ieltsContextLineIds": [
    "line_ants_25"
  ],
  "morphology": {
    "segments": [
      {
        "form": "level",
        "type": "base",
        "meaningZh": "层面；水平；等级",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "level 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "high level",
      "translationZh": "高水平"
    },
    {
      "text": "sea level",
      "translationZh": "海平面"
    },
    {
      "text": "at one level",
      "translationZh": "在某一层面"
    },
    {
      "text": "level of risk",
      "translationZh": "风险水平"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the level of + noun / at one level",
      "exampleEn": "Water levels rose overnight.",
      "exampleZh": "水位一夜之间上涨了。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_level_basic_001",
    "text": "Water levels rose overnight.",
    "translationZh": "水位一夜之间上涨了。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_25",
    "articleTitle": "Ants Could Teach Ants",
    "text": "At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.",
    "translationZh": "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_level_basic_001_word_level",
    "lineId": "line_level_basic_001",
    "wordId": "word_level",
    "surfaceForms": [
      "level"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_25_word_level",
    "lineId": "line_ants_25",
    "wordId": "word_level",
    "surfaceForms": [
      "level"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### locate

```json
{
  "_id": "word_locate",
  "word": "locate",
  "normalized": "locate",
  "type": "word",
  "phonetic": {
    "uk": "/ləʊˈkeɪt/",
    "us": "/ləʊˈkeɪt/",
    "default": "/ləʊˈkeɪt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "locate_v_01",
      "pos": "v.",
      "translation": "找到；确定……的位置",
      "definitionEn": "To find or establish the exact position of something.",
      "definitionZh": "找到或确定某物的准确位置。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "located"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "located"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "locating"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "locates"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_locate",
  "wordId": "word_locate",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_26"
  ],
  "primaryExampleLineId": "line_locate_basic_001",
  "ieltsContextLineIds": [
    "line_ants_26"
  ],
  "morphology": {
    "segments": [
      {
        "form": "locate",
        "type": "base",
        "meaningZh": "找到；确定……的位置",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "locate 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_location",
        "word": "location",
        "pos": "n",
        "translationZh": "位置",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "locate the source",
      "translationZh": "找到来源"
    },
    {
      "text": "locate information",
      "translationZh": "查找信息"
    },
    {
      "text": "be located in",
      "translationZh": "位于"
    },
    {
      "text": "accurately locate",
      "translationZh": "准确定位"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "locate + object / be located in + place",
      "exampleEn": "Rescuers located the missing climber.",
      "exampleZh": "救援人员找到了失踪的登山者。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_location",
      "word": "location",
      "pos": "n",
      "translationZh": "位置",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "locate 可表示“找到”或“把……设在”；be located in/at 表示“位于”。"
  ],
  "commonErrors": [
    {
      "wrong": "The office locates in London.",
      "correct": "The office is located in London.",
      "explanationZh": "表示某物位于某处通常用 be located。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_locate_basic_001",
    "text": "Rescuers located the missing climber.",
    "translationZh": "救援人员找到了失踪的登山者。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_26",
    "articleTitle": "Ants Could Teach Ants",
    "text": "In another instance, birds watching other birds using a stick to locate food such as insects and so on, are observed to do the same thing themselves while finding food later.",
    "translationZh": "另一个例子是，鸟类看到其他鸟用树枝寻找昆虫等食物后，后来觅食时也会做出同样的行为。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_locate_basic_001_word_locate",
    "lineId": "line_locate_basic_001",
    "wordId": "word_locate",
    "surfaceForms": [
      "locate"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_26_word_locate",
    "lineId": "line_ants_26",
    "wordId": "word_locate",
    "surfaceForms": [
      "locate"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_locate",
    "toWordId": "word_find",
    "toWord": "find",
    "relationType": "contrast",
    "explanationZh": "find 是一般的找到；locate 更正式，常强调确定精确位置。",
    "exampleEn": "The team located the signal precisely after a volunteer found the missing device.",
    "exampleZh": "志愿者找到遗失设备后，团队精确定位了信号。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### location

```json
{
  "_id": "word_location",
  "word": "location",
  "normalized": "location",
  "type": "word",
  "phonetic": {
    "uk": "/ləʊˈkeɪʃn/",
    "us": "/ləʊˈkeɪʃn/",
    "default": "/ləʊˈkeɪʃn/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "location_n_01",
      "pos": "n.",
      "translation": "位置；地点",
      "definitionEn": "A particular place or position.",
      "definitionZh": "某个特定地点或位置。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "locations"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_location",
  "wordId": "word_location",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_21"
  ],
  "primaryExampleLineId": "line_location_basic_001",
  "ieltsContextLineIds": [
    "line_ants_21"
  ],
  "morphology": {
    "segments": [
      {
        "form": "locate",
        "type": "base",
        "meaningZh": "定位；使坐落"
      },
      {
        "form": "-ion",
        "type": "suffix",
        "meaningZh": "行为、过程或结果",
        "origin": "Latin"
      }
    ],
    "explanationZh": "locate（定位）+ -ion（名词后缀）→ 位置",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "exact location",
      "translationZh": "确切位置"
    },
    {
      "text": "geographical location",
      "translationZh": "地理位置"
    },
    {
      "text": "remote location",
      "translationZh": "偏远地点"
    },
    {
      "text": "location of the site",
      "translationZh": "场地位置"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the location of + noun",
      "exampleEn": "The hotel is in a convenient location.",
      "exampleZh": "酒店位置便利。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_location_basic_001",
    "text": "The hotel is in a convenient location.",
    "translationZh": "酒店位置便利。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_21",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The naive animals gain a benefit and new knowledge that better enables them to learn about the predator’s location than if the caller had not called.",
    "translationZh": "这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_location_basic_001_word_location",
    "lineId": "line_location_basic_001",
    "wordId": "word_location",
    "surfaceForms": [
      "location"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_21_word_location",
    "lineId": "line_ants_21",
    "wordId": "word_location",
    "surfaceForms": [
      "location"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### maintain

```json
{
  "_id": "word_maintain",
  "word": "maintain",
  "normalized": "maintain",
  "type": "word",
  "phonetic": {
    "uk": "/meɪnˈteɪn/",
    "us": "/meɪnˈteɪn/",
    "default": "/meɪnˈteɪn/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "maintain_v_01",
      "pos": "v.",
      "translation": "坚持认为；维持；维护",
      "definitionEn": "To state firmly that something is true, or keep something in a particular condition.",
      "definitionZh": "坚持声称某事属实，或使某物保持特定状态。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "maintained"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "maintaining"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "maintained"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "maintains"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_maintain",
  "wordId": "word_maintain",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_36"
  ],
  "primaryExampleLineId": "line_maintain_basic_001",
  "ieltsContextLineIds": [
    "line_ants_36"
  ],
  "morphology": {
    "segments": [
      {
        "form": "maintain",
        "type": "base",
        "meaningZh": "坚持认为；维持；维护",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "maintain 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_maintenance",
        "word": "maintenance",
        "pos": "n",
        "translationZh": "维护",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "maintain quality",
      "translationZh": "保持质量"
    },
    {
      "text": "maintain contact",
      "translationZh": "保持联系"
    },
    {
      "text": "maintain that",
      "translationZh": "坚称……"
    },
    {
      "text": "properly maintain",
      "translationZh": "妥善维护"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "maintain + object / maintain that + clause",
      "exampleEn": "Regular repairs maintain the system.",
      "exampleZh": "定期维修可维持系统运转。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_maintenance",
      "word": "maintenance",
      "pos": "n",
      "translationZh": "维护",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "可表示维持、维护，也可接 that 从句表示“坚持声称”。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_maintain_basic_001",
    "text": "Regular repairs maintain the system.",
    "translationZh": "定期维修可维持系统运转。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_36",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Bennett Galef Jr., a psychologist who studies animal behaviour and social learning at McMaster University in Canada, maintained that ants were unlikely to have a \"theory of mind” - meaning that leaders and followers may well have been following instinctive routines that were not based on an understanding of what was happening in another ant’s brain.",
    "translationZh": "研究动物行为和社会学习的心理学家小贝内特·盖利夫认为，蚂蚁不太可能具有‘心智理论’；这意味着领路者和跟随者很可能只是在遵循本能程序，并非基于对另一只蚂蚁脑中活动的理解。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_maintain_basic_001_word_maintain",
    "lineId": "line_maintain_basic_001",
    "wordId": "word_maintain",
    "surfaceForms": [
      "maintain"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_36_word_maintain",
    "lineId": "line_ants_36",
    "wordId": "word_maintain",
    "surfaceForms": [
      "maintained"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_maintain",
    "toWordId": "word_preserve",
    "toWord": "preserve",
    "relationType": "contrast",
    "explanationZh": "maintain 强调使状态持续；preserve 强调防止损坏、丧失或改变。",
    "exampleEn": "Engineers maintain the bridge, while conservationists preserve its historic features.",
    "exampleZh": "工程师维护桥梁，而文物保护人员保存其历史特征。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### memorise

```json
{
  "_id": "word_memorise",
  "word": "memorise",
  "normalized": "memorise",
  "type": "word",
  "phonetic": {
    "uk": "/ˈmeməraɪz/",
    "us": "/ˈmeməraɪz/",
    "default": "/ˈmeməraɪz/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "memorise_v_01",
      "pos": "v.",
      "translation": "记住；熟记",
      "definitionEn": "To learn something so that it can be recalled exactly.",
      "definitionZh": "学习并记牢某内容，以便准确回忆。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "memorised"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "memorising"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "memorised"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "memorises"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_memorise",
  "wordId": "word_memorise",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_03"
  ],
  "primaryExampleLineId": "line_memorise_basic_001",
  "ieltsContextLineIds": [
    "line_ants_03"
  ],
  "morphology": {
    "segments": [
      {
        "form": "memorise",
        "type": "base",
        "meaningZh": "记住；熟记",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "memorise 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_memorisation",
        "word": "memorisation",
        "pos": "n",
        "translationZh": "记忆",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_memory",
        "word": "memory",
        "pos": "n",
        "translationZh": "记忆",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "memorise a list",
      "translationZh": "记住清单"
    },
    {
      "text": "memorise vocabulary",
      "translationZh": "背单词"
    },
    {
      "text": "memorise facts",
      "translationZh": "记住事实"
    },
    {
      "text": "memorise information",
      "translationZh": "记住信息"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "memorise + object",
      "exampleEn": "Students memorised the new vocabulary.",
      "exampleZh": "学生们记住了新词汇。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_memorisation",
      "word": "memorisation",
      "pos": "n",
      "translationZh": "记忆",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_memory",
      "word": "memory",
      "pos": "n",
      "translationZh": "记忆",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_memorise_basic_001",
    "text": "Students memorised the new vocabulary.",
    "translationZh": "学生们记住了新词汇。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_03",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Time and again, followers trailed behind leaders, darting this way and that along the route, presumably to memorise landmarks.",
    "translationZh": "一次又一次，跟随者尾随领路者，沿途来回穿行，似乎是为了记住沿途的地标。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_memorise_basic_001_word_memorise",
    "lineId": "line_memorise_basic_001",
    "wordId": "word_memorise",
    "surfaceForms": [
      "memorise"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_03_word_memorise",
    "lineId": "line_ants_03",
    "wordId": "word_memorise",
    "surfaceForms": [
      "memorise"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_memorise",
    "toWordId": "word_remember",
    "toWord": "remember",
    "relationType": "contrast",
    "explanationZh": "memorise 是主动记住；remember 是记得或回想起。",
    "exampleEn": "Students memorise the formula first and remember it more easily after applying it.",
    "exampleZh": "学生先记住公式，并在应用后更容易长期记得它。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### mere

```json
{
  "_id": "word_mere",
  "word": "mere",
  "normalized": "mere",
  "type": "word",
  "phonetic": {
    "uk": "/mɪə(r)/",
    "us": "/mɪə(r)/",
    "default": "/mɪə(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "mere_adj_01",
      "pos": "adj.",
      "translation": "仅仅的；只不过的",
      "definitionEn": "Used to emphasise how small, unimportant, or limited something is.",
      "definitionZh": "强调某事物数量少、不重要或程度有限。"
    }
  ],
  "inflections": [
    {
      "type": "t",
      "labelZh": "最高级",
      "form": "merest"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "meres"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_mere",
  "wordId": "word_mere",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_15"
  ],
  "primaryExampleLineId": "line_mere_basic_001",
  "ieltsContextLineIds": [
    "line_ants_15"
  ],
  "morphology": {
    "segments": [
      {
        "form": "mere",
        "type": "base",
        "meaningZh": "仅仅的；只不过的",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "mere 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_merely",
        "word": "merely",
        "pos": "adv",
        "translationZh": "仅仅",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "mere fact",
      "translationZh": "仅仅这一事实"
    },
    {
      "text": "mere presence",
      "translationZh": "仅仅在场"
    },
    {
      "text": "mere possibility",
      "translationZh": "仅有的可能性"
    },
    {
      "text": "not a mere",
      "translationZh": "不只是……"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "mere + noun",
      "exampleEn": "A mere ten people attended.",
      "exampleZh": "只有十个人参加。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_merely",
      "word": "merely",
      "pos": "adv",
      "translationZh": "仅仅",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "mere 是形容词，修饰名词；merely 是副词，修饰动词、形容词或整句话。"
  ],
  "commonErrors": [
    {
      "wrong": "It merely fact proves nothing.",
      "correct": "The mere fact proves nothing.",
      "explanationZh": "名词前用形容词 mere，不用副词 merely。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_mere_basic_001",
    "text": "A mere ten people attended.",
    "translationZh": "只有十个人参加。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_15",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Hauser noted that mere communication of information is commonplace in the animal world.",
    "translationZh": "豪瑟指出，单纯的信息交流在动物界十分常见。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_mere_basic_001_word_mere",
    "lineId": "line_mere_basic_001",
    "wordId": "word_mere",
    "surfaceForms": [
      "mere"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_15_word_mere",
    "lineId": "line_ants_15",
    "wordId": "word_mere",
    "surfaceForms": [
      "mere"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_mere",
    "toWordId": "word_merely",
    "toWord": "merely",
    "relationType": "contrast",
    "explanationZh": "mere 是形容词，merely 是副词，意义都接近“仅仅”。",
    "exampleEn": "The mere presence of a teacher changed the room; students were not merely pretending to work.",
    "exampleZh": "老师仅仅在场就改变了教室氛围；学生并不只是假装学习。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### merely

```json
{
  "_id": "word_merely",
  "word": "merely",
  "normalized": "merely",
  "type": "word",
  "phonetic": {
    "uk": "/ˈmɪəli/",
    "us": "/ˈmɪəli/",
    "default": "/ˈmɪəli/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "merely_adv_01",
      "pos": "adv.",
      "translation": "仅仅；只不过",
      "definitionEn": "Only; simply and no more than that.",
      "definitionZh": "只是如此，没有更多含义或程度。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_merely",
  "wordId": "word_merely",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_08",
    "line_ants_24",
    "line_ants_25",
    "line_ants_32"
  ],
  "primaryExampleLineId": "line_merely_basic_001",
  "ieltsContextLineIds": [
    "line_ants_08",
    "line_ants_24",
    "line_ants_25",
    "line_ants_32"
  ],
  "morphology": {
    "segments": [
      {
        "form": "mere",
        "type": "base",
        "meaningZh": "仅仅的"
      },
      {
        "form": "-ly",
        "type": "suffix",
        "meaningZh": "构成副词"
      }
    ],
    "explanationZh": "mere（仅仅的）+ -ly（副词后缀）→ 仅仅",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "merely a matter of",
      "translationZh": "仅仅是……的问题"
    },
    {
      "text": "merely suggest",
      "translationZh": "只是表明"
    },
    {
      "text": "not merely",
      "translationZh": "不仅仅"
    },
    {
      "text": "merely because",
      "translationZh": "仅仅因为"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "merely + verb / adjective",
      "exampleEn": "The figures are merely estimates.",
      "exampleZh": "这些数字只是估算值。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_merely_basic_001",
    "text": "The figures are merely estimates.",
    "translationZh": "这些数字只是估算值。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_08",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Marc Hauser, a psychologist and biologist and one of the scientists who came up with the definition of teaching, said it was unclear whether the ants had learned a new skill or merely acquired new information.",
    "translationZh": "心理学家兼生物学家马克·豪瑟是提出教学定义的科学家之一；他说，目前尚不清楚蚂蚁是学会了一项新技能，还是仅仅获得了新信息。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_24",
    "articleTitle": "Ants Could Teach Ants",
    "text": "He found that cheetah mothers that take their cubs along on hunts gradually allow their cubs to do more of the hunting —going, for example, from killing a gazelle and allowing young cubs to eat merely tripping the gazelle and letting the cubs finish it off.",
    "translationZh": "他发现，猎豹母亲带幼崽狩猎时，会逐渐让幼崽承担更多捕猎任务，例如从杀死羚羊后让幼崽进食，过渡到只把羚羊绊倒，再让幼崽完成捕杀。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_25",
    "articleTitle": "Ants Could Teach Ants",
    "text": "At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.",
    "translationZh": "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_32",
    "articleTitle": "Ants Could Teach Ants",
    "text": "That, Hauser said, would suggest that the follower ant actually knew the leader was more knowledgeable and not merely following an instinctive routine itself.",
    "translationZh": "豪瑟说，这将表明跟随者确实知道领路者掌握更多信息，而不只是自己在遵循本能程序。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_merely_basic_001_word_merely",
    "lineId": "line_merely_basic_001",
    "wordId": "word_merely",
    "surfaceForms": [
      "merely"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_08_word_merely",
    "lineId": "line_ants_08",
    "wordId": "word_merely",
    "surfaceForms": [
      "merely"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_24_word_merely",
    "lineId": "line_ants_24",
    "wordId": "word_merely",
    "surfaceForms": [
      "merely"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_25_word_merely",
    "lineId": "line_ants_25",
    "wordId": "word_merely",
    "surfaceForms": [
      "merely"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_32_word_merely",
    "lineId": "line_ants_32",
    "wordId": "word_merely",
    "surfaceForms": [
      "merely"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### naive

```json
{
  "_id": "word_naive",
  "word": "naive",
  "normalized": "naive",
  "type": "word",
  "phonetic": {
    "uk": "/naɪˈiːv/",
    "us": "/naɪˈiːv/",
    "default": "/naɪˈiːv/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "naive_adj_01",
      "pos": "adj.",
      "translation": "天真的；缺乏经验的",
      "definitionEn": "Lacking experience or judgement and therefore trusting too easily.",
      "definitionZh": "因缺乏经验或判断力而过于轻信。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_naive",
  "wordId": "word_naive",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_21"
  ],
  "primaryExampleLineId": "line_naive_basic_001",
  "ieltsContextLineIds": [
    "line_ants_21"
  ],
  "morphology": {
    "segments": [
      {
        "form": "naive",
        "type": "base",
        "meaningZh": "天真的；缺乏经验的",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "naive 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "naive belief",
      "translationZh": "天真的看法"
    },
    {
      "text": "naive assumption",
      "translationZh": "幼稚的假设"
    },
    {
      "text": "politically naive",
      "translationZh": "政治上不成熟"
    },
    {
      "text": "seem naive",
      "translationZh": "显得天真"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "be naive about + noun / it is naive to do sth.",
      "exampleEn": "It was naive to trust every claim.",
      "exampleZh": "相信每一种说法是天真的。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_naive_basic_001",
    "text": "It was naive to trust every claim.",
    "translationZh": "相信每一种说法是天真的。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_21",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The naive animals gain a benefit and new knowledge that better enables them to learn about the predator’s location than if the caller had not called.",
    "translationZh": "这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_naive_basic_001_word_naive",
    "lineId": "line_naive_basic_001",
    "wordId": "word_naive",
    "surfaceForms": [
      "naive"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_21_word_naive",
    "lineId": "line_ants_21",
    "wordId": "word_naive",
    "surfaceForms": [
      "naive"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### necessarily

```json
{
  "_id": "word_necessarily",
  "word": "necessarily",
  "normalized": "necessarily",
  "type": "word",
  "phonetic": {
    "uk": "/ˈnesəsərəlɪ; ˏnesəˈserəl/",
    "us": "/ˈnesəsərəlɪ; ˏnesəˈserəl/",
    "default": "/ˈnesəsərəlɪ; ˏnesəˈserəl/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "necessarily_adv_01",
      "pos": "adv.",
      "translation": "必然地；不可避免地",
      "definitionEn": "As an inevitable or logically required result.",
      "definitionZh": "作为不可避免或逻辑上必需的结果。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_necessarily",
  "wordId": "word_necessarily",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_38"
  ],
  "primaryExampleLineId": "line_necessarily_basic_001",
  "ieltsContextLineIds": [
    "line_ants_38"
  ],
  "morphology": {
    "segments": [
      {
        "form": "necessary",
        "type": "base",
        "meaningZh": "必要的"
      },
      {
        "form": "-ly",
        "type": "suffix",
        "meaningZh": "构成副词"
      }
    ],
    "explanationZh": "necessary（必要的）+ -ly（副词后缀）→ 必然地；必要地",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "not necessarily",
      "translationZh": "未必"
    },
    {
      "text": "necessarily involve",
      "translationZh": "必然涉及"
    },
    {
      "text": "necessarily lead to",
      "translationZh": "必然导致"
    },
    {
      "text": "necessarily true",
      "translationZh": "必然正确"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "not necessarily + verb / adjective",
      "exampleEn": "Higher prices do not necessarily mean better quality.",
      "exampleZh": "价格更高未必意味着质量更好。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_necessarily_basic_001",
    "text": "Higher prices do not necessarily mean better quality.",
    "translationZh": "价格更高未必意味着质量更好。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_38",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Animals may behave in ways similar to humans without a similar cognitive system, he said, so the behaviour is not necessarily a good guide into how humans came to think the way they do.",
    "translationZh": "他说，动物可能在没有相似认知系统的情况下表现出与人类相似的行为，因此，行为未必能很好地说明人类如何形成如今的思维方式。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_necessarily_basic_001_word_necessarily",
    "lineId": "line_necessarily_basic_001",
    "wordId": "word_necessarily",
    "surfaceForms": [
      "necessarily"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_38_word_necessarily",
    "lineId": "line_ants_38",
    "wordId": "word_necessarily",
    "surfaceForms": [
      "necessarily"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### observe

```json
{
  "_id": "word_observe",
  "word": "observe",
  "normalized": "observe",
  "type": "word",
  "phonetic": {
    "uk": "/əbˈzɜːv/",
    "us": "/əbˈzɜːv/",
    "default": "/əbˈzɜːv/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "observe_v_01",
      "pos": "v.",
      "translation": "观察；注意到；遵守",
      "definitionEn": "To watch carefully, notice, or comply with a rule.",
      "definitionZh": "仔细观看、注意到某事，或遵守规则。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "observed"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "observed"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "observing"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "observes"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_observe",
  "wordId": "word_observe",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_26"
  ],
  "primaryExampleLineId": "line_observe_basic_001",
  "ieltsContextLineIds": [
    "line_ants_26"
  ],
  "morphology": {
    "segments": [
      {
        "form": "observe",
        "type": "base",
        "meaningZh": "观察；注意到；遵守",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "observe 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_observation",
        "word": "observation",
        "pos": "n",
        "translationZh": "观察",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_observer",
        "word": "observer",
        "pos": "n",
        "translationZh": "观察者",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "observe behaviour",
      "translationZh": "观察行为"
    },
    {
      "text": "observe a pattern",
      "translationZh": "观察到规律"
    },
    {
      "text": "closely observe",
      "translationZh": "仔细观察"
    },
    {
      "text": "observe the law",
      "translationZh": "遵守法律"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "observe + object / observe that + clause",
      "exampleEn": "Scientists observed the animals closely.",
      "exampleZh": "科学家仔细观察了这些动物。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_observation",
      "word": "observation",
      "pos": "n",
      "translationZh": "观察",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_observer",
      "word": "observer",
      "pos": "n",
      "translationZh": "观察者",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "observe 可表示仔细观察、注意到或遵守；watch 更强调持续观看动态过程。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_observe_basic_001",
    "text": "Scientists observed the animals closely.",
    "translationZh": "科学家仔细观察了这些动物。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_26",
    "articleTitle": "Ants Could Teach Ants",
    "text": "In another instance, birds watching other birds using a stick to locate food such as insects and so on, are observed to do the same thing themselves while finding food later.",
    "translationZh": "另一个例子是，鸟类看到其他鸟用树枝寻找昆虫等食物后，后来觅食时也会做出同样的行为。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_observe_basic_001_word_observe",
    "lineId": "line_observe_basic_001",
    "wordId": "word_observe",
    "surfaceForms": [
      "observe"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_26_word_observe",
    "lineId": "line_ants_26",
    "wordId": "word_observe",
    "surfaceForms": [
      "observed"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_observe",
    "toWordId": "word_watch",
    "toWord": "watch",
    "relationType": "contrast",
    "explanationZh": "observe 更正式、分析性更强；watch 强调持续观看动态事物。",
    "exampleEn": "Researchers observed the ants systematically while visitors watched from behind the glass.",
    "exampleZh": "研究人员系统观察蚂蚁，参观者则隔着玻璃观看。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### oppose

```json
{
  "_id": "word_oppose",
  "word": "oppose",
  "normalized": "oppose",
  "type": "word",
  "phonetic": {
    "uk": "/əˈpəʊz/",
    "us": "/əˈpəʊz/",
    "default": "/əˈpəʊz/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "oppose_v_01",
      "pos": "v.",
      "translation": "反对；抵制",
      "definitionEn": "To disagree with and try to prevent an idea, plan, or action.",
      "definitionZh": "不同意并试图阻止某种观点、计划或行动。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "opposed"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "opposed"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "opposing"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "opposes"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_oppose",
  "wordId": "word_oppose",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_14"
  ],
  "primaryExampleLineId": "line_oppose_basic_001",
  "ieltsContextLineIds": [
    "line_ants_14"
  ],
  "morphology": {
    "segments": [
      {
        "form": "oppose",
        "type": "base",
        "meaningZh": "反对；抵制",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "oppose 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_opposition",
        "word": "opposition",
        "pos": "n",
        "translationZh": "反对",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_opponent",
        "word": "opponent",
        "pos": "n",
        "translationZh": "对手",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "strongly oppose",
      "translationZh": "强烈反对"
    },
    {
      "text": "oppose a proposal",
      "translationZh": "反对提案"
    },
    {
      "text": "be opposed to",
      "translationZh": "反对"
    },
    {
      "text": "oppose doing sth.",
      "translationZh": "反对做某事"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "oppose + noun / be opposed to + noun",
      "exampleEn": "Local residents opposed the plan.",
      "exampleZh": "当地居民反对这项计划。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_opposition",
      "word": "opposition",
      "pos": "n",
      "translationZh": "反对",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_opponent",
      "word": "opponent",
      "pos": "n",
      "translationZh": "对手",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [
    {
      "wrong": "oppose against the plan",
      "correct": "oppose the plan / be opposed to the plan",
      "explanationZh": "oppose 作动词时直接接宾语。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_oppose_basic_001",
    "text": "Local residents opposed the plan.",
    "translationZh": "当地居民反对这项计划。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_14",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Opposing views still arose, however.",
    "translationZh": "然而，反对意见依然出现了。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_oppose_basic_001_word_oppose",
    "lineId": "line_oppose_basic_001",
    "wordId": "word_oppose",
    "surfaceForms": [
      "oppose"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_14_word_oppose",
    "lineId": "line_ants_14",
    "wordId": "word_oppose",
    "surfaceForms": [
      "Opposing"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_oppose",
    "toWordId": "word_object",
    "toWord": "object",
    "relationType": "contrast",
    "explanationZh": "oppose 可直接反对人、计划或政策；object 常用 object to 表示提出异议。",
    "exampleEn": "Residents opposed the development, and several groups formally objected to the planning application.",
    "exampleZh": "居民反对这项开发，多个团体正式对规划申请提出异议。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### predator

```json
{
  "_id": "word_predator",
  "word": "predator",
  "normalized": "predator",
  "type": "word",
  "phonetic": {
    "uk": "/ˈpredətə(r)/",
    "us": "/ˈpredətə(r)/",
    "default": "/ˈpredətə(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "predator_n_01",
      "pos": "n.",
      "translation": "捕食者；捕食性动物",
      "definitionEn": "An animal that hunts and eats other animals.",
      "definitionZh": "捕猎并以其他动物为食的动物。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "predators"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_predator",
  "wordId": "word_predator",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_17",
    "line_ants_21"
  ],
  "primaryExampleLineId": "line_predator_basic_001",
  "ieltsContextLineIds": [
    "line_ants_17",
    "line_ants_21"
  ],
  "morphology": {
    "segments": [
      {
        "form": "predat-",
        "type": "root",
        "meaningZh": "捕食；掠夺",
        "origin": "Latin"
      },
      {
        "form": "-or",
        "type": "suffix",
        "meaningZh": "做某动作的人或事物",
        "origin": "Latin"
      }
    ],
    "explanationZh": "predate（捕食）+ -or（行为者）→ 捕食者",
    "relatedWords": [
      {
        "wordId": "word_predatory",
        "word": "predatory",
        "pos": "adj",
        "translationZh": "捕食性的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "natural predator",
      "translationZh": "天敌"
    },
    {
      "text": "top predator",
      "translationZh": "顶级捕食者"
    },
    {
      "text": "escape predators",
      "translationZh": "逃避捕食者"
    },
    {
      "text": "predator population",
      "translationZh": "捕食者种群"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a predator of + species",
      "exampleEn": "The bird escaped from a predator.",
      "exampleZh": "这只鸟逃过了捕食者。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_predatory",
      "word": "predatory",
      "pos": "adj",
      "translationZh": "捕食性的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_predator_basic_001",
    "text": "The bird escaped from a predator.",
    "translationZh": "这只鸟逃过了捕食者。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_17",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Sounding the alarm can be costly, because the animal may draw the attention of the predator to itself.",
    "translationZh": "发出警报可能代价高昂，因为这只动物可能会把捕食者的注意力吸引到自己身上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_21",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The naive animals gain a benefit and new knowledge that better enables them to learn about the predator’s location than if the caller had not called.",
    "translationZh": "这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_predator_basic_001_word_predator",
    "lineId": "line_predator_basic_001",
    "wordId": "word_predator",
    "surfaceForms": [
      "predator"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_17_word_predator",
    "lineId": "line_ants_17",
    "wordId": "word_predator",
    "surfaceForms": [
      "predator"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_21_word_predator",
    "lineId": "line_ants_21",
    "wordId": "word_predator",
    "surfaceForms": [
      "predator’s"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### presence

```json
{
  "_id": "word_presence",
  "word": "presence",
  "normalized": "presence",
  "type": "word",
  "phonetic": {
    "uk": "/ˈprezns/",
    "us": "/ˈprezns/",
    "default": "/ˈprezns/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "presence_n_01",
      "pos": "n.",
      "translation": "存在；在场",
      "definitionEn": "The state of being in a place or of existing.",
      "definitionZh": "处于某个地方或实际存在的状态。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "presences"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_presence",
  "wordId": "word_presence",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_16"
  ],
  "primaryExampleLineId": "line_presence_basic_001",
  "ieltsContextLineIds": [
    "line_ants_16"
  ],
  "morphology": {
    "segments": [
      {
        "form": "presence",
        "type": "base",
        "meaningZh": "存在；在场",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "presence 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "presence of",
      "translationZh": "存在……"
    },
    {
      "text": "physical presence",
      "translationZh": "亲自到场"
    },
    {
      "text": "in the presence of",
      "translationZh": "当着……的面"
    },
    {
      "text": "detect the presence of",
      "translationZh": "检测到……存在"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the presence of + noun / in the presence of + person",
      "exampleEn": "Her presence changed the atmosphere.",
      "exampleZh": "她的到场改变了气氛。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_presence_basic_001",
    "text": "Her presence changed the atmosphere.",
    "translationZh": "她的到场改变了气氛。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_16",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Consider a species, for example, that uses alarm calls to warn fellow members about the presence.",
    "translationZh": "例如，设想有一种动物会发出警报声，提醒同类有危险存在。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft",
    "sourceNote": "PDF 原文止于 'the presence.'，句子疑似缺词；中文仅按上下文作保守补译，需回源复核。"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_presence_basic_001_word_presence",
    "lineId": "line_presence_basic_001",
    "wordId": "word_presence",
    "surfaceForms": [
      "presence"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_16_word_presence",
    "lineId": "line_ants_16",
    "wordId": "word_presence",
    "surfaceForms": [
      "presence"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### presumably

```json
{
  "_id": "word_presumably",
  "word": "presumably",
  "normalized": "presumably",
  "type": "word",
  "phonetic": {
    "uk": "/prɪˈzjuːməbli/",
    "us": "/prɪˈzjuːməbli/",
    "default": "/prɪˈzjuːməbli/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "presumably_adv_01",
      "pos": "adv.",
      "translation": "大概；推测起来",
      "definitionEn": "Used to say that something is believed to be likely.",
      "definitionZh": "用于表示根据现有信息推测某事很可能属实。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_presumably",
  "wordId": "word_presumably",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_03"
  ],
  "primaryExampleLineId": "line_presumably_basic_001",
  "ieltsContextLineIds": [
    "line_ants_03"
  ],
  "morphology": {
    "segments": [
      {
        "form": "presume",
        "type": "base",
        "meaningZh": "推定；假定"
      },
      {
        "form": "-able",
        "type": "suffix",
        "meaningZh": "可以……的"
      },
      {
        "form": "-ly",
        "type": "suffix",
        "meaningZh": "构成副词"
      }
    ],
    "explanationZh": "presumable（可推定的）+ -ly（副词后缀）→ 大概、推测起来",
    "relatedWords": [
      {
        "wordId": "word_presume",
        "word": "presume",
        "pos": "v",
        "translationZh": "推定",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_presumption",
        "word": "presumption",
        "pos": "n",
        "translationZh": "推定",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "presumably because",
      "translationZh": "大概因为"
    },
    {
      "text": "presumably due to",
      "translationZh": "推测由于"
    },
    {
      "text": "presumably true",
      "translationZh": "大概属实"
    },
    {
      "text": "presumably intended",
      "translationZh": "推测原本打算"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "presumably, + clause / presumably because + clause",
      "exampleEn": "The road is closed, presumably because of flooding.",
      "exampleZh": "道路关闭了，大概是因为洪水。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_presume",
      "word": "presume",
      "pos": "v",
      "translationZh": "推定",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_presumption",
      "word": "presumption",
      "pos": "n",
      "translationZh": "推定",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_presumably_basic_001",
    "text": "The road is closed, presumably because of flooding.",
    "translationZh": "道路关闭了，大概是因为洪水。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_03",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Time and again, followers trailed behind leaders, darting this way and that along the route, presumably to memorise landmarks.",
    "translationZh": "一次又一次，跟随者尾随领路者，沿途来回穿行，似乎是为了记住沿途的地标。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_presumably_basic_001_word_presumably",
    "lineId": "line_presumably_basic_001",
    "wordId": "word_presumably",
    "surfaceForms": [
      "presumably"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_03_word_presumably",
    "lineId": "line_ants_03",
    "wordId": "word_presumably",
    "surfaceForms": [
      "presumably"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### proceed

```json
{
  "_id": "word_proceed",
  "word": "proceed",
  "normalized": "proceed",
  "type": "word",
  "phonetic": {
    "uk": "/prəˈsiːd/",
    "us": "/prəˈsiːd/",
    "default": "/prəˈsiːd/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "proceed_v_01",
      "pos": "v.",
      "translation": "继续进行；前进",
      "definitionEn": "To continue an action or move forward.",
      "definitionZh": "继续某项行动或向前移动。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "proceeds"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "proceeded"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "proceeding"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "proceeds"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "proceeded"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_proceed",
  "wordId": "word_proceed",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_04",
    "line_ants_30"
  ],
  "primaryExampleLineId": "line_proceed_basic_001",
  "ieltsContextLineIds": [
    "line_ants_04",
    "line_ants_30"
  ],
  "morphology": {
    "segments": [
      {
        "form": "proceed",
        "type": "base",
        "meaningZh": "继续进行；前进",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "proceed 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "proceed with",
      "translationZh": "继续进行"
    },
    {
      "text": "proceed to do",
      "translationZh": "接着做"
    },
    {
      "text": "proceed as planned",
      "translationZh": "按计划进行"
    },
    {
      "text": "proceed with caution",
      "translationZh": "谨慎行事"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "proceed with + noun / proceed to do sth.",
      "exampleEn": "The meeting proceeded as planned.",
      "exampleZh": "会议按计划进行。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "proceed with + 名词；proceed to do 表示完成一事后接着做另一事。"
  ],
  "commonErrors": [
    {
      "wrong": "proceed the plan",
      "correct": "proceed with the plan",
      "explanationZh": "表示继续某事用 proceed with。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_proceed_basic_001",
    "text": "The meeting proceeded as planned.",
    "translationZh": "会议按计划进行。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_04",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Once a follower got its bearings, it tapped the leader with its antennae, prompting the lesson to literally proceed to the next step.",
    "translationZh": "一旦跟随者辨清方向，它就用触角轻触领路者，促使这一教学过程真正进入下一步。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_30",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Could they simply have been following an instinctive rule to proceed when the followers tapped them on the legs or abdomen?",
    "translationZh": "它们是否只是遵循一种本能规则：当跟随者轻触它们的腿或腹部时便继续前进？",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_proceed_basic_001_word_proceed",
    "lineId": "line_proceed_basic_001",
    "wordId": "word_proceed",
    "surfaceForms": [
      "proceed"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_04_word_proceed",
    "lineId": "line_ants_04",
    "wordId": "word_proceed",
    "surfaceForms": [
      "proceed"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_30_word_proceed",
    "lineId": "line_ants_30",
    "wordId": "word_proceed",
    "surfaceForms": [
      "proceed"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_proceed",
    "toWordId": "word_continue",
    "toWord": "continue",
    "relationType": "contrast",
    "explanationZh": "continue 最通用；proceed 更正式，常指按步骤继续或前往。",
    "exampleEn": "After the safety check, the team proceeded with the test and continued recording data.",
    "exampleZh": "安全检查后，团队继续进行测试并持续记录数据。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### project

```json
{
  "_id": "word_project",
  "word": "project",
  "normalized": "project",
  "type": "word",
  "phonetic": {
    "uk": "/ˈprɔdʒekt/",
    "us": "/ˈprɔdʒekt/",
    "default": "/ˈprɔdʒekt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "project_n_01",
      "pos": "n.",
      "translation": "项目；课题；计划",
      "definitionEn": "A planned piece of work with a particular purpose.",
      "definitionZh": "为实现特定目的而规划的一项工作。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "projects"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "projected"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "projecting"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "projects"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "projected"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_project",
  "wordId": "word_project",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_13"
  ],
  "primaryExampleLineId": "line_project_basic_001",
  "ieltsContextLineIds": [
    "line_ants_13"
  ],
  "morphology": {
    "segments": [
      {
        "form": "project",
        "type": "base",
        "meaningZh": "项目；课题；计划",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "project 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "research project",
      "translationZh": "研究项目"
    },
    {
      "text": "major project",
      "translationZh": "重大项目"
    },
    {
      "text": "carry out a project",
      "translationZh": "开展项目"
    },
    {
      "text": "project costs",
      "translationZh": "项目成本"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a project on + topic / carry out a project",
      "exampleEn": "The research project lasted two years.",
      "exampleZh": "这个研究项目持续了两年。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "名词通常读 /ˈprɒdʒekt/；动词通常读 /prəˈdʒekt/。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_project_basic_001",
    "text": "The research project lasted two years.",
    "translationZh": "这个研究项目持续了两年。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_13",
    "articleTitle": "Ants Could Teach Ants",
    "text": "His ideas were advocated by the students who carried out the video project with him.",
    "translationZh": "与他一起完成视频项目的学生支持他的观点。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_project_basic_001_word_project",
    "lineId": "line_project_basic_001",
    "wordId": "word_project",
    "surfaceForms": [
      "project"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_13_word_project",
    "lineId": "line_ants_13",
    "wordId": "word_project",
    "surfaceForms": [
      "project"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### remark

```json
{
  "_id": "word_remark",
  "word": "remark",
  "normalized": "remark",
  "type": "word",
  "phonetic": {
    "uk": "/rɪˈmɑːk/",
    "us": "/rɪˈmɑːk/",
    "default": "/rɪˈmɑːk/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "remark_v_01",
      "pos": "v.",
      "translation": "评论；谈到",
      "definitionEn": "To say something as a comment or observation.",
      "definitionZh": "以评论或观察的方式说出某事。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "remarks"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "remarked"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "remarked"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "remarks"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "remarking"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_remark",
  "wordId": "word_remark",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_06"
  ],
  "primaryExampleLineId": "line_remark_basic_001",
  "ieltsContextLineIds": [
    "line_ants_06"
  ],
  "morphology": {
    "segments": [
      {
        "form": "remark",
        "type": "base",
        "meaningZh": "评论；谈到",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "remark 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "remark that",
      "translationZh": "评论说"
    },
    {
      "text": "make a remark",
      "translationZh": "发表评论"
    },
    {
      "text": "brief remark",
      "translationZh": "简短评论"
    },
    {
      "text": "opening remarks",
      "translationZh": "开场白"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "remark on + noun / remark that + clause",
      "exampleEn": "She remarked that the room was cold.",
      "exampleZh": "她评论说房间很冷。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "remark on/upon sth. 或 remark that...；比 say 更强调评论或注意到。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_remark_basic_001",
    "text": "She remarked that the room was cold.",
    "translationZh": "她评论说房间很冷。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_06",
    "articleTitle": "Ants Could Teach Ants",
    "text": "\"Tandem running is an example of teaching, to our knowledge the first in a non-human animal, that involves bidirectional feedback between teacher and pupil” remarks Nigel Franks, professor of animal behaviour and ecology, whose paper on the ant educators was published last week in the journal Nature.",
    "translationZh": "奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_remark_basic_001_word_remark",
    "lineId": "line_remark_basic_001",
    "wordId": "word_remark",
    "surfaceForms": [
      "remark"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_06_word_remark",
    "lineId": "line_ants_06",
    "wordId": "word_remark",
    "surfaceForms": [
      "remarks"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_remark",
    "toWordId": "word_comment",
    "toWord": "comment",
    "relationType": "contrast",
    "explanationZh": "两者均可指评论；remark 常指简短说出观察，comment 可更系统。",
    "exampleEn": "The scientist remarked that the result was unusual, then added a detailed comment in the report.",
    "exampleZh": "科学家说这一结果不同寻常，随后在报告中补充了详细评论。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### remove

```json
{
  "_id": "word_remove",
  "word": "remove",
  "normalized": "remove",
  "type": "word",
  "phonetic": {
    "uk": "/rɪˈmuːv/",
    "us": "/rɪˈmuːv/",
    "default": "/rɪˈmuːv/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "remove_v_01",
      "pos": "v.",
      "translation": "移走；去除；撤除",
      "definitionEn": "To take something away from a place or position.",
      "definitionZh": "把某物从某个地点或位置拿走。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "removed"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "removing"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "removed"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "removes"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_remove",
  "wordId": "word_remove",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_31"
  ],
  "primaryExampleLineId": "line_remove_basic_001",
  "ieltsContextLineIds": [
    "line_ants_31"
  ],
  "morphology": {
    "segments": [
      {
        "form": "remove",
        "type": "base",
        "meaningZh": "移走；去除；撤除",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "remove 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "remove a barrier",
      "translationZh": "消除障碍"
    },
    {
      "text": "remove from",
      "translationZh": "从……移走"
    },
    {
      "text": "remove waste",
      "translationZh": "清除废物"
    },
    {
      "text": "completely remove",
      "translationZh": "彻底去除"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "remove + object + from + place",
      "exampleEn": "Please remove your shoes.",
      "exampleZh": "请脱鞋。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_remove_basic_001",
    "text": "Please remove your shoes.",
    "translationZh": "请脱鞋。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_31",
    "articleTitle": "Ants Could Teach Ants",
    "text": "And did leaders that led the way to food - only to find that it had been removed by the experimenter - incur the wrath of followers?",
    "translationZh": "如果领路者带路去寻找食物，却发现食物已被实验人员移走，它会招致跟随者的愤怒吗？",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_remove_basic_001_word_remove",
    "lineId": "line_remove_basic_001",
    "wordId": "word_remove",
    "surfaceForms": [
      "remove"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_31_word_remove",
    "lineId": "line_ants_31",
    "wordId": "word_remove",
    "surfaceForms": [
      "removed"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### route

```json
{
  "_id": "word_route",
  "word": "route",
  "normalized": "route",
  "type": "word",
  "phonetic": {
    "uk": "/ruːt; raut/",
    "us": "/ruːt; raut/",
    "default": "/ruːt; raut/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "route_n_01",
      "pos": "n.",
      "translation": "路线；路径",
      "definitionEn": "A way or course taken to reach a place.",
      "definitionZh": "到达某地所采用的道路或路径。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "routes"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "routing"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "routed"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "routes"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "routed"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_route",
  "wordId": "word_route",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_03"
  ],
  "primaryExampleLineId": "line_route_basic_001",
  "ieltsContextLineIds": [
    "line_ants_03"
  ],
  "morphology": {
    "segments": [
      {
        "form": "route",
        "type": "base",
        "meaningZh": "路线；路径",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "route 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "direct route",
      "translationZh": "直接路线"
    },
    {
      "text": "main route",
      "translationZh": "主要路线"
    },
    {
      "text": "escape route",
      "translationZh": "逃生路线"
    },
    {
      "text": "along the route",
      "translationZh": "沿途"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a route to / through + place",
      "exampleEn": "We chose the shortest route home.",
      "exampleZh": "我们选择了回家最短的路线。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_route_basic_001",
    "text": "We chose the shortest route home.",
    "translationZh": "我们选择了回家最短的路线。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_03",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Time and again, followers trailed behind leaders, darting this way and that along the route, presumably to memorise landmarks.",
    "translationZh": "一次又一次，跟随者尾随领路者，沿途来回穿行，似乎是为了记住沿途的地标。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_route_basic_001_word_route",
    "lineId": "line_route_basic_001",
    "wordId": "word_route",
    "surfaceForms": [
      "route"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_03_word_route",
    "lineId": "line_ants_03",
    "wordId": "word_route",
    "surfaceForms": [
      "route"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### routine

```json
{
  "_id": "word_routine",
  "word": "routine",
  "normalized": "routine",
  "type": "word",
  "phonetic": {
    "uk": "/ruːˈtiːn/",
    "us": "/ruːˈtiːn/",
    "default": "/ruːˈtiːn/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "routine_n_01",
      "pos": "n./adj.",
      "translation": "惯例；常规程序；例行的",
      "definitionEn": "A usual sequence of actions; regular and ordinary.",
      "definitionZh": "通常反复进行的一系列行动；常规且普通的。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "routines"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_routine",
  "wordId": "word_routine",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_32",
    "line_ants_36"
  ],
  "primaryExampleLineId": "line_routine_basic_001",
  "ieltsContextLineIds": [
    "line_ants_32",
    "line_ants_36"
  ],
  "morphology": {
    "segments": [
      {
        "form": "routine",
        "type": "base",
        "meaningZh": "惯例；常规程序；例行的",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "routine 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "daily routine",
      "translationZh": "日常安排"
    },
    {
      "text": "routine check",
      "translationZh": "常规检查"
    },
    {
      "text": "routine procedure",
      "translationZh": "常规程序"
    },
    {
      "text": "follow a routine",
      "translationZh": "按惯例行事"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a daily routine / routine + noun",
      "exampleEn": "Exercise is part of my daily routine.",
      "exampleZh": "锻炼是我日常安排的一部分。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_routine_basic_001",
    "text": "Exercise is part of my daily routine.",
    "translationZh": "锻炼是我日常安排的一部分。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_32",
    "articleTitle": "Ants Could Teach Ants",
    "text": "That, Hauser said, would suggest that the follower ant actually knew the leader was more knowledgeable and not merely following an instinctive routine itself.",
    "translationZh": "豪瑟说，这将表明跟随者确实知道领路者掌握更多信息，而不只是自己在遵循本能程序。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_36",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Bennett Galef Jr., a psychologist who studies animal behaviour and social learning at McMaster University in Canada, maintained that ants were unlikely to have a \"theory of mind” - meaning that leaders and followers may well have been following instinctive routines that were not based on an understanding of what was happening in another ant’s brain.",
    "translationZh": "研究动物行为和社会学习的心理学家小贝内特·盖利夫认为，蚂蚁不太可能具有‘心智理论’；这意味着领路者和跟随者很可能只是在遵循本能程序，并非基于对另一只蚂蚁脑中活动的理解。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_routine_basic_001_word_routine",
    "lineId": "line_routine_basic_001",
    "wordId": "word_routine",
    "surfaceForms": [
      "routine"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_32_word_routine",
    "lineId": "line_ants_32",
    "wordId": "word_routine",
    "surfaceForms": [
      "routine"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_36_word_routine",
    "lineId": "line_ants_36",
    "wordId": "word_routine",
    "surfaceForms": [
      "routines"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### species

```json
{
  "_id": "word_species",
  "word": "species",
  "normalized": "species",
  "type": "word",
  "phonetic": {
    "uk": "/ˈspiːʃiːz/",
    "us": "/ˈspiːʃiːz/",
    "default": "/ˈspiːʃiːz/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "species_n_01",
      "pos": "n.",
      "translation": "物种；种",
      "definitionEn": "A group of organisms capable of reproducing with one another.",
      "definitionZh": "能够相互繁殖的一类生物群体。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_species",
  "wordId": "word_species",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_16"
  ],
  "primaryExampleLineId": "line_species_basic_001",
  "ieltsContextLineIds": [
    "line_ants_16"
  ],
  "morphology": {
    "segments": [
      {
        "form": "species",
        "type": "base",
        "meaningZh": "物种；种",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "species 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "endangered species",
      "translationZh": "濒危物种"
    },
    {
      "text": "native species",
      "translationZh": "本地物种"
    },
    {
      "text": "animal species",
      "translationZh": "动物物种"
    },
    {
      "text": "species diversity",
      "translationZh": "物种多样性"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a species of + organism",
      "exampleEn": "This species lives near rivers.",
      "exampleZh": "这一物种生活在河流附近。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_species_basic_001",
    "text": "This species lives near rivers.",
    "translationZh": "这一物种生活在河流附近。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_16",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Consider a species, for example, that uses alarm calls to warn fellow members about the presence.",
    "translationZh": "例如，设想有一种动物会发出警报声，提醒同类有危险存在。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft",
    "sourceNote": "PDF 原文止于 'the presence.'，句子疑似缺词；中文仅按上下文作保守补译，需回源复核。"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_species_basic_001_word_species",
    "lineId": "line_species_basic_001",
    "wordId": "word_species",
    "surfaceForms": [
      "species"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_16_word_species",
    "lineId": "line_ants_16",
    "wordId": "word_species",
    "surfaceForms": [
      "species"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### stage

```json
{
  "_id": "word_stage",
  "word": "stage",
  "normalized": "stage",
  "type": "word",
  "phonetic": {
    "uk": "/steɪdʒ/",
    "us": "/steɪdʒ/",
    "default": "/steɪdʒ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "stage_n_01",
      "pos": "n.",
      "translation": "阶段；时期",
      "definitionEn": "A particular point or period in a process of development.",
      "definitionZh": "发展过程中的某个特定时期或步骤。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "stages"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "staged"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "staged"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "staging"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "stages"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_stage",
  "wordId": "word_stage",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_25"
  ],
  "primaryExampleLineId": "line_stage_basic_001",
  "ieltsContextLineIds": [
    "line_ants_25"
  ],
  "morphology": {
    "segments": [
      {
        "form": "stage",
        "type": "base",
        "meaningZh": "阶段；时期",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "stage 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "early stage",
      "translationZh": "早期阶段"
    },
    {
      "text": "at this stage",
      "translationZh": "在现阶段"
    },
    {
      "text": "final stage",
      "translationZh": "最后阶段"
    },
    {
      "text": "stage of development",
      "translationZh": "发展阶段"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "at a stage / a stage of + process",
      "exampleEn": "The disease was found at an early stage.",
      "exampleZh": "疾病在早期阶段被发现。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_stage_basic_001",
    "text": "The disease was found at an early stage.",
    "translationZh": "疾病在早期阶段被发现。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_25",
    "articleTitle": "Ants Could Teach Ants",
    "text": "At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.",
    "translationZh": "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_stage_basic_001_word_stage",
    "lineId": "line_stage_basic_001",
    "wordId": "word_stage",
    "surfaceForms": [
      "stage"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_25_word_stage",
    "lineId": "line_ants_25",
    "wordId": "word_stage",
    "surfaceForms": [
      "stages"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### stick

```json
{
  "_id": "word_stick",
  "word": "stick",
  "normalized": "stick",
  "type": "word",
  "phonetic": {
    "uk": "/stɪk/",
    "us": "/stɪk/",
    "default": "/stɪk/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "stick_v_01",
      "pos": "n.",
      "translation": "枝条；棍；棒",
      "definitionEn": "A thin piece of wood broken or cut from a tree.",
      "definitionZh": "从树上折下或截取的一段细木条。"
    }
  ],
  "inflections": [
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "stuck"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "sticking"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "stuck"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "sticks"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "sticks"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_stick",
  "wordId": "word_stick",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_26"
  ],
  "primaryExampleLineId": "line_stick_basic_001",
  "ieltsContextLineIds": [
    "line_ants_26"
  ],
  "morphology": {
    "segments": [
      {
        "form": "stick",
        "type": "base",
        "meaningZh": "枝条；棍；棒",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "stick 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "wooden stick",
      "translationZh": "木棍"
    },
    {
      "text": "walking stick",
      "translationZh": "手杖"
    },
    {
      "text": "stick to",
      "translationZh": "坚持；遵守"
    },
    {
      "text": "stick in",
      "translationZh": "卡在……里"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "use a stick to do sth. / stick to + noun",
      "exampleEn": "She used a stick to support the plant.",
      "exampleZh": "她用一根木棍支撑植物。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_stick_basic_001",
    "text": "She used a stick to support the plant.",
    "translationZh": "她用一根木棍支撑植物。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_26",
    "articleTitle": "Ants Could Teach Ants",
    "text": "In another instance, birds watching other birds using a stick to locate food such as insects and so on, are observed to do the same thing themselves while finding food later.",
    "translationZh": "另一个例子是，鸟类看到其他鸟用树枝寻找昆虫等食物后，后来觅食时也会做出同样的行为。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_stick_basic_001_word_stick",
    "lineId": "line_stick_basic_001",
    "wordId": "word_stick",
    "surfaceForms": [
      "stick"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_26_word_stick",
    "lineId": "line_ants_26",
    "wordId": "word_stick",
    "surfaceForms": [
      "stick"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### subject

```json
{
  "_id": "word_subject",
  "word": "subject",
  "normalized": "subject",
  "type": "word",
  "phonetic": {
    "uk": "/ˈsʌbdʒɪkt/",
    "us": "/ˈsʌbdʒɪkt/",
    "default": "/ˈsʌbdʒɪkt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "subject_n_01",
      "pos": "n.",
      "translation": "研究对象；受试者；主题",
      "definitionEn": "A person or animal studied in an experiment.",
      "definitionZh": "在实验或研究中被观察、测试的人或动物。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "subjects"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "subjected"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "subjecting"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "subjected"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "subjects"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_subject",
  "wordId": "word_subject",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_02"
  ],
  "primaryExampleLineId": "line_subject_basic_001",
  "ieltsContextLineIds": [
    "line_ants_02"
  ],
  "morphology": {
    "segments": [
      {
        "form": "subject",
        "type": "base",
        "meaningZh": "研究对象；受试者；主题",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "subject 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "research subject",
      "translationZh": "研究对象"
    },
    {
      "text": "school subject",
      "translationZh": "学科"
    },
    {
      "text": "subject to",
      "translationZh": "受……影响；须经"
    },
    {
      "text": "main subject",
      "translationZh": "主题"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "a subject of + study / be subject to + noun",
      "exampleEn": "The volunteers became research subjects.",
      "exampleZh": "这些志愿者成为研究对象。"
    }
  ],
  "derivatives": [],
  "usageNotes": [
    "名词重音在首音节；动词 subject 重音在第二音节；be subject to 表示受制于或须经。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_subject_basic_001",
    "text": "The volunteers became research subjects.",
    "translationZh": "这些志愿者成为研究对象。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_02",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Transformed into research subjects at the University of Bristol, they raced along a tabletop foraging for food - and then, remarkably, returned to guide others.",
    "translationZh": "它们被转移到布里斯托大学作为研究对象，在桌面上竞相觅食，随后又出人意料地返回去引导其他蚂蚁。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_subject_basic_001_word_subject",
    "lineId": "line_subject_basic_001",
    "wordId": "word_subject",
    "surfaceForms": [
      "subject"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_02_word_subject",
    "lineId": "line_ants_02",
    "wordId": "word_subject",
    "surfaceForms": [
      "subjects"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### suggest

```json
{
  "_id": "word_suggest",
  "word": "suggest",
  "normalized": "suggest",
  "type": "word",
  "phonetic": {
    "uk": "/səˈdʒest/",
    "us": "/səˈdʒest/",
    "default": "/səˈdʒest/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "suggest_v_01",
      "pos": "v.",
      "translation": "表明；暗示；建议",
      "definitionEn": "To indicate that something may be true, or put forward an idea.",
      "definitionZh": "显示某事可能属实，或提出一种想法或建议。"
    }
  ],
  "inflections": [
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "suggests"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "suggested"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "suggested"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "suggesting"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_suggest",
  "wordId": "word_suggest",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_32"
  ],
  "primaryExampleLineId": "line_suggest_basic_001",
  "ieltsContextLineIds": [
    "line_ants_32"
  ],
  "morphology": {
    "segments": [
      {
        "form": "suggest",
        "type": "base",
        "meaningZh": "表明；暗示；建议",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "suggest 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_suggestion",
        "word": "suggestion",
        "pos": "n",
        "translationZh": "建议；暗示",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "suggest that",
      "translationZh": "表明；建议"
    },
    {
      "text": "strongly suggest",
      "translationZh": "强烈表明"
    },
    {
      "text": "suggest doing sth.",
      "translationZh": "建议做某事"
    },
    {
      "text": "results suggest",
      "translationZh": "结果表明"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "suggest doing sth. / suggest that + clause",
      "exampleEn": "The evidence suggests a link.",
      "exampleZh": "证据表明存在联系。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_suggestion",
      "word": "suggestion",
      "pos": "n",
      "translationZh": "建议；暗示",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "suggest doing 或 suggest that...；标准用法不说 suggest sb. to do sth.。"
  ],
  "commonErrors": [
    {
      "wrong": "She suggested me to wait.",
      "correct": "She suggested that I wait / suggested waiting.",
      "explanationZh": "suggest 不接 sb. to do。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_suggest_basic_001",
    "text": "The evidence suggests a link.",
    "translationZh": "证据表明存在联系。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_32",
    "articleTitle": "Ants Could Teach Ants",
    "text": "That, Hauser said, would suggest that the follower ant actually knew the leader was more knowledgeable and not merely following an instinctive routine itself.",
    "translationZh": "豪瑟说，这将表明跟随者确实知道领路者掌握更多信息，而不只是自己在遵循本能程序。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_suggest_basic_001_word_suggest",
    "lineId": "line_suggest_basic_001",
    "wordId": "word_suggest",
    "surfaceForms": [
      "suggest"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_32_word_suggest",
    "lineId": "line_ants_32",
    "wordId": "word_suggest",
    "surfaceForms": [
      "suggest"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_suggest",
    "toWordId": "word_recommend",
    "toWord": "recommend",
    "relationType": "contrast",
    "explanationZh": "suggest 可表示建议或暗示；recommend 更明确地推荐选择或行动。",
    "exampleEn": "The data suggest a link, but the panel recommends further research before action is taken.",
    "exampleZh": "数据暗示存在联系，但专家组建议在采取行动前进一步研究。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### tap

```json
{
  "_id": "word_tap",
  "word": "tap",
  "normalized": "tap",
  "type": "word",
  "phonetic": {
    "uk": "/tæp/",
    "us": "/tæp/",
    "default": "/tæp/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "tap_v_01",
      "pos": "v.",
      "translation": "轻拍；轻触",
      "definitionEn": "To touch or hit something lightly and quickly.",
      "definitionZh": "快速而轻柔地触碰或敲击某物。"
    }
  ],
  "inflections": [
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "tapped"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "tapping"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "taps"
    },
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "tapped"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "taps"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_tap",
  "wordId": "word_tap",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_04",
    "line_ants_30"
  ],
  "primaryExampleLineId": "line_tap_basic_001",
  "ieltsContextLineIds": [
    "line_ants_04",
    "line_ants_30"
  ],
  "morphology": {
    "segments": [
      {
        "form": "tap",
        "type": "base",
        "meaningZh": "轻拍；轻触",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "tap 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "tap the screen",
      "translationZh": "轻点屏幕"
    },
    {
      "text": "tap on",
      "translationZh": "轻敲"
    },
    {
      "text": "tap into",
      "translationZh": "利用"
    },
    {
      "text": "water tap",
      "translationZh": "水龙头"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "tap + object / tap on / tap into + noun",
      "exampleEn": "He tapped the screen twice.",
      "exampleZh": "他轻点了两下屏幕。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_tap_basic_001",
    "text": "He tapped the screen twice.",
    "translationZh": "他轻点了两下屏幕。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_04",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Once a follower got its bearings, it tapped the leader with its antennae, prompting the lesson to literally proceed to the next step.",
    "translationZh": "一旦跟随者辨清方向，它就用触角轻触领路者，促使这一教学过程真正进入下一步。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_30",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Could they simply have been following an instinctive rule to proceed when the followers tapped them on the legs or abdomen?",
    "translationZh": "它们是否只是遵循一种本能规则：当跟随者轻触它们的腿或腹部时便继续前进？",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_tap_basic_001_word_tap",
    "lineId": "line_tap_basic_001",
    "wordId": "word_tap",
    "surfaceForms": [
      "tap"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_04_word_tap",
    "lineId": "line_ants_04",
    "wordId": "word_tap",
    "surfaceForms": [
      "tapped"
    ],
    "matchType": "lemma"
  },
  {
    "_id": "line_ants_30_word_tap",
    "lineId": "line_ants_30",
    "wordId": "word_tap",
    "surfaceForms": [
      "tapped"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### theory

```json
{
  "_id": "word_theory",
  "word": "theory",
  "normalized": "theory",
  "type": "word",
  "phonetic": {
    "uk": "/ˈθɪərɪ/",
    "us": "/ˈθɪərɪ/",
    "default": "/ˈθɪərɪ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "theory_n_01",
      "pos": "n.",
      "translation": "理论；学说",
      "definitionEn": "A system of ideas intended to explain facts or events.",
      "definitionZh": "用于解释事实或事件的一套系统性观点。"
    }
  ],
  "inflections": [
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "theories"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_theory",
  "wordId": "word_theory",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_28",
    "line_ants_36"
  ],
  "primaryExampleLineId": "line_theory_basic_001",
  "ieltsContextLineIds": [
    "line_ants_28",
    "line_ants_36"
  ],
  "morphology": {
    "segments": [
      {
        "form": "theory",
        "type": "base",
        "meaningZh": "理论；学说",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "theory 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_theoretical",
        "word": "theoretical",
        "pos": "adj",
        "translationZh": "理论的",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_theoretically",
        "word": "theoretically",
        "pos": "adv",
        "translationZh": "理论上",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "scientific theory",
      "translationZh": "科学理论"
    },
    {
      "text": "theory of mind",
      "translationZh": "心智理论"
    },
    {
      "text": "test a theory",
      "translationZh": "检验理论"
    },
    {
      "text": "in theory",
      "translationZh": "理论上"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "the theory of + noun / theory that + clause",
      "exampleEn": "The evidence supports the theory.",
      "exampleZh": "证据支持这一理论。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_theoretical",
      "word": "theoretical",
      "pos": "adj",
      "translationZh": "理论的",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_theoretically",
      "word": "theoretically",
      "pos": "adv",
      "translationZh": "理论上",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_theory_basic_001",
    "text": "The evidence supports the theory.",
    "translationZh": "证据支持这一理论。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_28",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The challenge in understanding whether other animals truly teach one another, he added, is that human teaching involves a “theory of mind”: teachers are aware that students don’t know something.",
    "translationZh": "他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_36",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Bennett Galef Jr., a psychologist who studies animal behaviour and social learning at McMaster University in Canada, maintained that ants were unlikely to have a \"theory of mind” - meaning that leaders and followers may well have been following instinctive routines that were not based on an understanding of what was happening in another ant’s brain.",
    "translationZh": "研究动物行为和社会学习的心理学家小贝内特·盖利夫认为，蚂蚁不太可能具有‘心智理论’；这意味着领路者和跟随者很可能只是在遵循本能程序，并非基于对另一只蚂蚁脑中活动的理解。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_theory_basic_001_word_theory",
    "lineId": "line_theory_basic_001",
    "wordId": "word_theory",
    "surfaceForms": [
      "theory"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_28_word_theory",
    "lineId": "line_ants_28",
    "wordId": "word_theory",
    "surfaceForms": [
      "theory"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_36_word_theory",
    "lineId": "line_ants_36",
    "wordId": "word_theory",
    "surfaceForms": [
      "theory"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### thereby

```json
{
  "_id": "word_thereby",
  "word": "thereby",
  "normalized": "thereby",
  "type": "word",
  "phonetic": {
    "uk": "/ˏðeəˈbaɪ/",
    "us": "/ˏðeəˈbaɪ/",
    "default": "/ˏðeəˈbaɪ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "thereby_adv_01",
      "pos": "adv.",
      "translation": "因此；从而",
      "definitionEn": "As a result of the action just mentioned.",
      "definitionZh": "作为刚才所述行动的结果。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_thereby",
  "wordId": "word_thereby",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_05"
  ],
  "primaryExampleLineId": "line_thereby_basic_001",
  "ieltsContextLineIds": [
    "line_ants_05"
  ],
  "morphology": {
    "segments": [
      {
        "form": "there",
        "type": "base",
        "meaningZh": "由此"
      },
      {
        "form": "by",
        "type": "base",
        "meaningZh": "借此；通过"
      }
    ],
    "explanationZh": "there（由此）+ by（借此）→ 因此、从而",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "thereby reducing",
      "translationZh": "从而减少"
    },
    {
      "text": "thereby increasing",
      "translationZh": "从而增加"
    },
    {
      "text": "thereby allowing",
      "translationZh": "从而使……成为可能"
    },
    {
      "text": "and thereby",
      "translationZh": "并因此"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "clause, thereby + -ing",
      "exampleEn": "The policy reduced waste, thereby saving money.",
      "exampleZh": "这项政策减少了浪费，从而节省了资金。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_thereby_basic_001",
    "text": "The policy reduced waste, thereby saving money.",
    "translationZh": "这项政策减少了浪费，从而节省了资金。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_05",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The ants were only looking for food, but the researchers said the careful way the leaders led followers, thereby turning them into leaders in their own right, marked the Temnothorax albipennis ant as the very first example of a non-human animal exhibiting teaching behaviour.",
    "translationZh": "这些蚂蚁只是在寻找食物，但研究人员表示，领路者谨慎地带领跟随者、进而把它们也变成领路者的方式，使白扁胸蚁成为首个表现出教学行为的非人类动物实例。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_thereby_basic_001_word_thereby",
    "lineId": "line_thereby_basic_001",
    "wordId": "word_thereby",
    "surfaceForms": [
      "thereby"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_05_word_thereby",
    "lineId": "line_ants_05",
    "wordId": "word_thereby",
    "surfaceForms": [
      "thereby"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### throughout

```json
{
  "_id": "word_throughout",
  "word": "throughout",
  "normalized": "throughout",
  "type": "word",
  "phonetic": {
    "uk": "/θruːˈaʊt/",
    "us": "/θruːˈaʊt/",
    "default": "/θruːˈaʊt/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "throughout_prep_01",
      "pos": "prep./adv.",
      "translation": "遍及；贯穿；自始至终",
      "definitionEn": "In every part of a place or during the whole of a period.",
      "definitionZh": "遍及某地各处，或贯穿整个时间段。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_throughout",
  "wordId": "word_throughout",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_22"
  ],
  "primaryExampleLineId": "line_throughout_basic_001",
  "ieltsContextLineIds": [
    "line_ants_22"
  ],
  "morphology": {
    "segments": [
      {
        "form": "through",
        "type": "base",
        "meaningZh": "贯穿"
      },
      {
        "form": "out",
        "type": "particle",
        "meaningZh": "完全；遍及"
      }
    ],
    "explanationZh": "through（贯穿）+ out（完全、遍及）→ 自始至终；遍及",
    "relatedWords": []
  },
  "collocations": [
    {
      "text": "throughout the year",
      "translationZh": "全年"
    },
    {
      "text": "throughout history",
      "translationZh": "纵观历史"
    },
    {
      "text": "throughout the world",
      "translationZh": "遍及世界"
    },
    {
      "text": "throughout the process",
      "translationZh": "在整个过程中"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "throughout + place / period",
      "exampleEn": "It rained throughout the night.",
      "exampleZh": "雨下了一整夜。"
    }
  ],
  "derivatives": [],
  "usageNotes": [],
  "commonErrors": [
    {
      "wrong": "throughout of the year",
      "correct": "throughout the year",
      "explanationZh": "throughout 作介词时不加 of。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_throughout_basic_001",
    "text": "It rained throughout the night.",
    "translationZh": "雨下了一整夜。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_22",
    "articleTitle": "Ants Could Teach Ants",
    "text": "This happens throughout the animal kingdom, but we don’t call it teaching, even though it is clearly transfer of information.",
    "translationZh": "这种情况遍及整个动物界，但我们并不称之为教学，尽管它显然属于信息传递。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_throughout_basic_001_word_throughout",
    "lineId": "line_throughout_basic_001",
    "wordId": "word_throughout",
    "surfaceForms": [
      "throughout"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_22_word_throughout",
    "lineId": "line_ants_22",
    "wordId": "word_throughout",
    "surfaceForms": [
      "throughout"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### transfer

```json
{
  "_id": "word_transfer",
  "word": "transfer",
  "normalized": "transfer",
  "type": "word",
  "phonetic": {
    "uk": "/trænsˈfɜː(r)/",
    "us": "/trænsˈfɜː(r)/",
    "default": "/trænsˈfɜː(r)/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "transfer_v_01",
      "pos": "n./v.",
      "translation": "传递；转移；调动",
      "definitionEn": "To move something or someone from one place, person, or system to another.",
      "definitionZh": "把某物或某人从一个地点、主体或系统转到另一个。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "transferred"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "transfers"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "transferring"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "transferred"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "transfers"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_transfer",
  "wordId": "word_transfer",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_22"
  ],
  "primaryExampleLineId": "line_transfer_basic_001",
  "ieltsContextLineIds": [
    "line_ants_22"
  ],
  "morphology": {
    "segments": [
      {
        "form": "transfer",
        "type": "base",
        "meaningZh": "传递；转移；调动",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "transfer 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_transferable",
        "word": "transferable",
        "pos": "adj",
        "translationZh": "可转移的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "transfer information",
      "translationZh": "传递信息"
    },
    {
      "text": "transfer to",
      "translationZh": "转到"
    },
    {
      "text": "knowledge transfer",
      "translationZh": "知识转移"
    },
    {
      "text": "bank transfer",
      "translationZh": "银行转账"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "transfer A to / from B",
      "exampleEn": "The files were transferred to a new computer.",
      "exampleZh": "文件被转移到一台新电脑上。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_transferable",
      "word": "transferable",
      "pos": "adj",
      "translationZh": "可转移的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "名词重音通常在首音节，动词重音通常在第二音节。"
  ],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_transfer_basic_001",
    "text": "The files were transferred to a new computer.",
    "translationZh": "文件被转移到一台新电脑上。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_22",
    "articleTitle": "Ants Could Teach Ants",
    "text": "This happens throughout the animal kingdom, but we don’t call it teaching, even though it is clearly transfer of information.",
    "translationZh": "这种情况遍及整个动物界，但我们并不称之为教学，尽管它显然属于信息传递。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_transfer_basic_001_word_transfer",
    "lineId": "line_transfer_basic_001",
    "wordId": "word_transfer",
    "surfaceForms": [
      "transfer"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_22_word_transfer",
    "lineId": "line_ants_22",
    "wordId": "word_transfer",
    "surfaceForms": [
      "transfer"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_transfer",
    "toWordId": "word_transform",
    "toWord": "transform",
    "relationType": "contrast",
    "explanationZh": "transfer 是转移位置或所有权；transform 是改变性质或形态。",
    "exampleEn": "The laboratory transferred the samples to another site but did not transform their chemical structure.",
    "exampleZh": "实验室把样本转移到另一地点，但没有改变其化学结构。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### transform

```json
{
  "_id": "word_transform",
  "word": "transform",
  "normalized": "transform",
  "type": "word",
  "phonetic": {
    "uk": "/trænsˈfɔːm/",
    "us": "/trænsˈfɔːm/",
    "default": "/trænsˈfɔːm/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "transform_v_01",
      "pos": "v.",
      "translation": "使转变；彻底改变",
      "definitionEn": "To change something greatly in form, character, or appearance.",
      "definitionZh": "使某物的形态、性质或外观发生重大改变。"
    }
  ],
  "inflections": [
    {
      "type": "d",
      "labelZh": "过去分词",
      "form": "transformed"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "transforming"
    },
    {
      "type": "p",
      "labelZh": "过去式",
      "form": "transformed"
    },
    {
      "type": "3",
      "labelZh": "第三人称单数",
      "form": "transforms"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_transform",
  "wordId": "word_transform",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_02"
  ],
  "primaryExampleLineId": "line_transform_basic_001",
  "ieltsContextLineIds": [
    "line_ants_02"
  ],
  "morphology": {
    "segments": [
      {
        "form": "trans-",
        "type": "prefix",
        "meaningZh": "跨越；改变",
        "origin": "Latin"
      },
      {
        "form": "form",
        "type": "root",
        "meaningZh": "形态",
        "origin": "Latin"
      }
    ],
    "explanationZh": "trans-（跨越、改变）+ form（形态）→ 改变形态",
    "relatedWords": [
      {
        "wordId": "word_transformation",
        "word": "transformation",
        "pos": "n",
        "translationZh": "转变",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "transform into",
      "translationZh": "转变为"
    },
    {
      "text": "completely transform",
      "translationZh": "彻底改变"
    },
    {
      "text": "transform society",
      "translationZh": "改变社会"
    },
    {
      "text": "digital transformation",
      "translationZh": "数字化转型"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "transform A into B",
      "exampleEn": "Education can transform lives.",
      "exampleZh": "教育可以改变人生。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_transformation",
      "word": "transformation",
      "pos": "n",
      "translationZh": "转变",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_transform_basic_001",
    "text": "Education can transform lives.",
    "translationZh": "教育可以改变人生。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_02",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Transformed into research subjects at the University of Bristol, they raced along a tabletop foraging for food - and then, remarkably, returned to guide others.",
    "translationZh": "它们被转移到布里斯托大学作为研究对象，在桌面上竞相觅食，随后又出人意料地返回去引导其他蚂蚁。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_transform_basic_001_word_transform",
    "lineId": "line_transform_basic_001",
    "wordId": "word_transform",
    "surfaceForms": [
      "transform"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_02_word_transform",
    "lineId": "line_ants_02",
    "wordId": "word_transform",
    "surfaceForms": [
      "Transformed"
    ],
    "matchType": "lemma"
  }
]
```

**word_relations**

```json
[]
```

### understanding

```json
{
  "_id": "word_understanding",
  "word": "understanding",
  "normalized": "understanding",
  "type": "word",
  "phonetic": {
    "uk": "/ˏʌndəˈstændɪŋ/",
    "us": "/ˏʌndəˈstændɪŋ/",
    "default": "/ˏʌndəˈstændɪŋ/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "understanding_n_01",
      "pos": "n.",
      "translation": "理解；认识",
      "definitionEn": "Knowledge of how something works or what it means.",
      "definitionZh": "对某事如何运作或具有何种含义的认识。"
    }
  ],
  "inflections": [
    {
      "type": "0",
      "labelZh": "原形",
      "form": "understand"
    },
    {
      "type": "i",
      "labelZh": "现在分词",
      "form": "understanding"
    },
    {
      "type": "s",
      "labelZh": "名词复数",
      "form": "understandings"
    }
  ]
}
```

**word_learning_content**

```json
{
  "_id": "word_understanding",
  "wordId": "word_understanding",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_28",
    "line_ants_36"
  ],
  "primaryExampleLineId": "line_understanding_basic_001",
  "ieltsContextLineIds": [
    "line_ants_28",
    "line_ants_36"
  ],
  "morphology": {
    "segments": [
      {
        "form": "understanding",
        "type": "base",
        "meaningZh": "理解；认识",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "understanding 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_understand",
        "word": "understand",
        "pos": "v",
        "translationZh": "理解",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_understandable",
        "word": "understandable",
        "pos": "adj",
        "translationZh": "可理解的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "deep understanding",
      "translationZh": "深入理解"
    },
    {
      "text": "gain an understanding",
      "translationZh": "获得理解"
    },
    {
      "text": "mutual understanding",
      "translationZh": "相互理解"
    },
    {
      "text": "understanding of",
      "translationZh": "对……的理解"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "an understanding of + noun",
      "exampleEn": "The course improved my understanding of science.",
      "exampleZh": "这门课程加深了我对科学的理解。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_understand",
      "word": "understand",
      "pos": "v",
      "translationZh": "理解",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_understandable",
      "word": "understandable",
      "pos": "adj",
      "translationZh": "可理解的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_understanding_basic_001",
    "text": "The course improved my understanding of science.",
    "translationZh": "这门课程加深了我对科学的理解。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_28",
    "articleTitle": "Ants Could Teach Ants",
    "text": "The challenge in understanding whether other animals truly teach one another, he added, is that human teaching involves a “theory of mind”: teachers are aware that students don’t know something.",
    "translationZh": "他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  },
  {
    "_id": "line_ants_36",
    "articleTitle": "Ants Could Teach Ants",
    "text": "Bennett Galef Jr., a psychologist who studies animal behaviour and social learning at McMaster University in Canada, maintained that ants were unlikely to have a \"theory of mind” - meaning that leaders and followers may well have been following instinctive routines that were not based on an understanding of what was happening in another ant’s brain.",
    "translationZh": "研究动物行为和社会学习的心理学家小贝内特·盖利夫认为，蚂蚁不太可能具有‘心智理论’；这意味着领路者和跟随者很可能只是在遵循本能程序，并非基于对另一只蚂蚁脑中活动的理解。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_understanding_basic_001_word_understanding",
    "lineId": "line_understanding_basic_001",
    "wordId": "word_understanding",
    "surfaceForms": [
      "understanding"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_28_word_understanding",
    "lineId": "line_ants_28",
    "wordId": "word_understanding",
    "surfaceForms": [
      "understanding"
    ],
    "matchType": "exact"
  },
  {
    "_id": "line_ants_36_word_understanding",
    "lineId": "line_ants_36",
    "wordId": "word_understanding",
    "surfaceForms": [
      "understanding"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[]
```

### valid

```json
{
  "_id": "word_valid",
  "word": "valid",
  "normalized": "valid",
  "type": "word",
  "phonetic": {
    "uk": "/ˈvælɪd/",
    "us": "/ˈvælɪd/",
    "default": "/ˈvælɪd/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "valid_adj_01",
      "pos": "adj.",
      "translation": "有根据的；有效的；正当的",
      "definitionEn": "Based on sound reasoning or evidence; legally or officially acceptable.",
      "definitionZh": "以合理推理或证据为基础；或在法律、正式规则上有效。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_valid",
  "wordId": "word_valid",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_12"
  ],
  "primaryExampleLineId": "line_valid_basic_001",
  "ieltsContextLineIds": [
    "line_ants_12"
  ],
  "morphology": {
    "segments": [
      {
        "form": "valid",
        "type": "base",
        "meaningZh": "有根据的；有效的；正当的",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "valid 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_validity",
        "word": "validity",
        "pos": "n",
        "translationZh": "有效性",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_validate",
        "word": "validate",
        "pos": "v",
        "translationZh": "验证；使生效",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_invalid",
        "word": "invalid",
        "pos": "adj",
        "translationZh": "无效的",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "valid argument",
      "translationZh": "有根据的论点"
    },
    {
      "text": "valid reason",
      "translationZh": "正当理由"
    },
    {
      "text": "valid evidence",
      "translationZh": "有效证据"
    },
    {
      "text": "remain valid",
      "translationZh": "仍然有效"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "valid for + period / valid + reason",
      "exampleEn": "That is a valid reason.",
      "exampleZh": "那是一个合理的理由。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_validity",
      "word": "validity",
      "pos": "n",
      "translationZh": "有效性",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_validate",
      "word": "validate",
      "pos": "v",
      "translationZh": "验证；使生效",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_invalid",
      "word": "invalid",
      "pos": "adj",
      "translationZh": "无效的",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [
    "valid 强调逻辑上有根据或法律/期限上有效；effective 强调实际产生效果。"
  ],
  "commonErrors": [
    {
      "wrong": "a valid method that works well",
      "correct": "an effective method that works well",
      "explanationZh": "强调实际效果时通常用 effective。"
    }
  ],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_valid_basic_001",
    "text": "That is a valid reason.",
    "translationZh": "那是一个合理的理由。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_12",
    "articleTitle": "Ants Could Teach Ants",
    "text": "This means the hypothesis that the leaders deliberately slowed down in order to pass the skills on to the followers seems potentially valid.",
    "translationZh": "这意味着，领路者为了把技能传给跟随者而有意放慢速度这一假说，似乎可能是成立的。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_valid_basic_001_word_valid",
    "lineId": "line_valid_basic_001",
    "wordId": "word_valid",
    "surfaceForms": [
      "valid"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_12_word_valid",
    "lineId": "line_ants_12",
    "wordId": "word_valid",
    "surfaceForms": [
      "valid"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_valid",
    "toWordId": "word_effective",
    "toWord": "effective",
    "relationType": "contrast",
    "explanationZh": "valid 强调有根据或有效期合法；effective 强调实际有效。",
    "exampleEn": "The criticism is valid, but the proposed solution may not be effective.",
    "exampleZh": "这项批评有根据，但提出的解决方案未必有效。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

### various

```json
{
  "_id": "word_various",
  "word": "various",
  "normalized": "various",
  "type": "word",
  "phonetic": {
    "uk": "/ˈveəriəs/",
    "us": "/ˈveəriəs/",
    "default": "/ˈveəriəs/"
  },
  "audio": {
    "uk": "",
    "us": ""
  },
  "senses": [
    {
      "senseId": "various_adj_01",
      "pos": "adj.",
      "translation": "各种各样的；不同的",
      "definitionEn": "Of several different types.",
      "definitionZh": "属于若干不同种类的。"
    }
  ],
  "inflections": []
}
```

**word_learning_content**

```json
{
  "_id": "word_various",
  "wordId": "word_various",
  "articleTitle": "Ants Could Teach Ants",
  "articleSentenceIds": [
    "line_ants_25"
  ],
  "primaryExampleLineId": "line_various_basic_001",
  "ieltsContextLineIds": [
    "line_ants_25"
  ],
  "morphology": {
    "segments": [
      {
        "form": "various",
        "type": "base",
        "meaningZh": "各种各样的；不同的",
        "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。"
      }
    ],
    "explanationZh": "various 在本稿中按整体词处理，不强行拆分词根词缀。",
    "relatedWords": [
      {
        "wordId": "word_vary",
        "word": "vary",
        "pos": "v",
        "translationZh": "变化",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_variation",
        "word": "variation",
        "pos": "n",
        "translationZh": "变化",
        "connectionZh": "与当前词属于同一词族。"
      },
      {
        "wordId": "word_variety",
        "word": "variety",
        "pos": "n",
        "translationZh": "多样性",
        "connectionZh": "与当前词属于同一词族。"
      }
    ]
  },
  "collocations": [
    {
      "text": "various reasons",
      "translationZh": "各种原因"
    },
    {
      "text": "various methods",
      "translationZh": "各种方法"
    },
    {
      "text": "various stages",
      "translationZh": "不同阶段"
    },
    {
      "text": "in various ways",
      "translationZh": "以各种方式"
    }
  ],
  "grammarPatterns": [
    {
      "pattern": "various + plural noun",
      "exampleEn": "The museum displays objects from various cultures.",
      "exampleZh": "博物馆展示来自不同文化的物品。"
    }
  ],
  "derivatives": [
    {
      "wordId": "word_vary",
      "word": "vary",
      "pos": "v",
      "translationZh": "变化",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_variation",
      "word": "variation",
      "pos": "n",
      "translationZh": "变化",
      "connectionZh": "与当前词属于同一词族。"
    },
    {
      "wordId": "word_variety",
      "word": "variety",
      "pos": "n",
      "translationZh": "多样性",
      "connectionZh": "与当前词属于同一词族。"
    }
  ],
  "usageNotes": [],
  "commonErrors": [],
  "examProfile": {
    "skills": [
      "reading",
      "writing"
    ],
    "topics": [
      "animal_behaviour",
      "education"
    ],
    "priority": 3,
    "writingValue": 3
  },
  "provenance": {
    "dictionarySources": [
      "miniprogram/assets/data/wordbooks/ielts.json",
      "ECDICT"
    ],
    "corpusSource": "IELTS-Reading-Actual-Tests-2016-2017.pdf",
    "articleTitle": "Ants Could Teach Ants",
    "editorialSource": "Codex editorial draft",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
}
```

**content_lines**

```json
[
  {
    "_id": "line_various_basic_001",
    "text": "The museum displays objects from various cultures.",
    "translationZh": "博物馆展示来自不同文化的物品。",
    "sourceType": "editorial",
    "level": "B2",
    "tags": [
      "ielts",
      "basic_example",
      "writing"
    ],
    "status": "draft"
  },
  {
    "_id": "line_ants_25",
    "articleTitle": "Ants Could Teach Ants",
    "text": "At one level, such behaviour might be called teaching — except the mother was not really teaching the cubs to hunt but merely facilitating various stages of learning.",
    "translationZh": "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    "sourceType": "ielts_reading_pdf",
    "level": "B2-C1",
    "tags": [
      "ielts",
      "reading",
      "animal_behaviour"
    ],
    "status": "source_verified_translation_draft"
  }
]
```

**content_line_words**

```json
[
  {
    "_id": "line_various_basic_001_word_various",
    "lineId": "line_various_basic_001",
    "wordId": "word_various",
    "surfaceForms": [
      "various"
    ],
    "matchType": "editorial"
  },
  {
    "_id": "line_ants_25_word_various",
    "lineId": "line_ants_25",
    "wordId": "word_various",
    "surfaceForms": [
      "various"
    ],
    "matchType": "exact"
  }
]
```

**word_relations**

```json
[
  {
    "fromWordId": "word_various",
    "toWordId": "word_varied",
    "toWord": "varied",
    "relationType": "contrast",
    "explanationZh": "various 强调有多个不同种类；varied 强调变化丰富、不单一。",
    "exampleEn": "The study used various methods and produced a varied set of responses.",
    "exampleZh": "研究采用了多种方法，并得到丰富多样的回答。",
    "status": "draft",
    "reviewStatus": "pending_human_review"
  }
]
```

## 审核清单

- [x] 文章标题及英文原句与 PDF 文本核对。
- [x] 排除 `Franks -> frank` 的专名误匹配。
- [x] 词形变化仅采用 ECDICT 结构化字段，不推测不存在的变化。
- [x] 构词、派生、辨析和常见错误允许为空。
- [ ] 中文释义、编辑例句、搭配及辨析待英语编辑逐词审核。
- [ ] 原文中文翻译待第二人复核。
- [ ] 审核完成前不得把记录状态改为 `reviewed` 或 `published`。
