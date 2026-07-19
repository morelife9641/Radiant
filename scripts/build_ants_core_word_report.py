#!/usr/bin/env python3
"""Build the first-article IELTS core-word enrichment sample as Markdown."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PDF = Path("/Users/chengtingwei/Downloads/IELTS-Reading-Actual-Tests-2016-2017.pdf")
WORDS_PATH = ROOT / "tmp/import_ready/words.import.json"
RELATIONS_PATH = ROOT / "tmp/import_ready/word_relations.import.json"
OUTPUT = ROOT / "docs/Ants-Could-Teach-Ants-核心词学习数据样稿.md"
TITLE = "Ants Could Teach Ants"

MATCHER_SPEC = importlib.util.spec_from_file_location(
    "matcher", ROOT / "scripts/match_pdf_to_ielts_wordbook.py"
)
MATCHER = importlib.util.module_from_spec(MATCHER_SPEC)
assert MATCHER_SPEC.loader
MATCHER_SPEC.loader.exec_module(MATCHER)

FORM_LABELS = {
    "s": "名词复数", "p": "过去式", "d": "过去分词", "i": "现在分词",
    "3": "第三人称单数", "r": "比较级", "t": "最高级", "0": "原形",
}

SENTENCE_ZH = {
    2: "它们被转移到布里斯托大学作为研究对象，在桌面上竞相觅食，随后又出人意料地返回去引导其他蚂蚁。",
    3: "一次又一次，跟随者尾随领路者，沿途来回穿行，似乎是为了记住沿途的地标。",
    4: "一旦跟随者辨清方向，它就用触角轻触领路者，促使这一教学过程真正进入下一步。",
    5: "这些蚂蚁只是在寻找食物，但研究人员表示，领路者谨慎地带领跟随者、进而把它们也变成领路者的方式，使白扁胸蚁成为首个表现出教学行为的非人类动物实例。",
    6: "奈杰尔·弗兰克斯评论道：‘串联奔跑是一种教学行为，据我们所知，这是非人类动物中的首例，它涉及教师与学生之间的双向反馈。’弗兰克斯是动物行为学与生态学教授，他关于蚂蚁‘教育者’的论文于上周发表在《自然》期刊上。",
    7: "当然，这篇论文刚一发表，就遭到另一位教育研究者的质疑。",
    8: "心理学家兼生物学家马克·豪瑟是提出教学定义的科学家之一；他说，目前尚不清楚蚂蚁是学会了一项新技能，还是仅仅获得了新信息。",
    10: "在领路者的引导下，蚂蚁能够更快地找到食物。",
    11: "但这种帮助会让领路者付出代价：如果不受跟随者拖累，它通常能快约四倍到达食物所在地。",
    12: "这意味着，领路者为了把技能传给跟随者而有意放慢速度这一假说，似乎可能是成立的。",
    13: "与他一起完成视频项目的学生支持他的观点。",
    14: "然而，反对意见依然出现了。",
    15: "豪瑟指出，单纯的信息交流在动物界十分常见。",
    16: "例如，设想有一种动物会发出警报声，提醒同类有危险存在。",
    17: "发出警报可能代价高昂，因为这只动物可能会把捕食者的注意力吸引到自己身上。",
    18: "但这能让其他动物逃到安全地带。",
    20: "发出叫声的动物要承担代价。",
    21: "这些缺乏经验的动物获得了益处和新知识，从而比没有警报时更能了解捕食者的位置。",
    22: "这种情况遍及整个动物界，但我们并不称之为教学，尽管它显然属于信息传递。",
    24: "他发现，猎豹母亲带幼崽狩猎时，会逐渐让幼崽承担更多捕猎任务，例如从杀死羚羊后让幼崽进食，过渡到只把羚羊绊倒，再让幼崽完成捕杀。",
    25: "从某种层面看，这种行为或许可以称为教学；但母兽并非真正教授幼崽捕猎，而只是在促进学习的不同阶段。",
    26: "另一个例子是，鸟类看到其他鸟用树枝寻找昆虫等食物后，后来觅食时也会做出同样的行为。",
    28: "他补充说，判断其他动物是否真正彼此教学的难点在于，人类教学涉及‘心智理论’，也就是教师知道学生尚不了解某些事情。",
    29: "他质疑弗兰克斯的领路蚂蚁是否真的知道跟随者对此一无所知。",
    30: "它们是否只是遵循一种本能规则：当跟随者轻触它们的腿或腹部时便继续前进？",
    31: "如果领路者带路去寻找食物，却发现食物已被实验人员移走，它会招致跟随者的愤怒吗？",
    32: "豪瑟说，这将表明跟随者确实知道领路者掌握更多信息，而不只是自己在遵循本能程序。",
    33: "这场争论仍在继续，而且理由充分。",
    34: "如果蚂蚁的教学行为得到证实，就表明教学能够在脑容量很小的动物中演化出来。",
    35: "决定教学行为何时演化的，可能是信息对群居动物的价值，而不是脑容量的限制。",
    36: "研究动物行为和社会学习的心理学家小贝内特·盖利夫认为，蚂蚁不太可能具有‘心智理论’；这意味着领路者和跟随者很可能只是在遵循本能程序，并非基于对另一只蚂蚁脑中活动的理解。",
    37: "他警告说，当科学家不仅在其他动物中寻找类似人类的行为，还寻找支撑这种行为的类人思维时，可能找错了方向。",
    38: "他说，动物可能在没有相似认知系统的情况下表现出与人类相似的行为，因此，行为未必能很好地说明人类如何形成如今的思维方式。",
}

# Basic example plus three to five high-value collocations. These are editorial drafts.
EDITORIAL = {
    "acquire": ("Children acquire language through interaction.", "儿童通过互动习得语言。", ["acquire knowledge 获得知识", "acquire a skill 掌握技能", "acquire information 获取信息", "acquire property 获得财产"]),
    "advocate": ("Many doctors advocate regular exercise.", "许多医生提倡规律运动。", ["advocate reform 提倡改革", "strongly advocate 大力提倡", "advocate doing sth. 主张做某事", "an advocate of equality 平等的倡导者"]),
    "alarm": ("The smoke alarm woke everyone.", "烟雾报警器惊醒了所有人。", ["sound the alarm 发出警报", "raise the alarm 拉响警报", "alarm call 警报声", "cause alarm 引起恐慌"]),
    "attention": ("Please pay attention to the instructions.", "请注意这些说明。", ["pay attention to 注意", "draw attention to 引起对……的注意", "attract attention 吸引注意", "public attention 公众关注"]),
    "aware": ("She was aware of the risk.", "她意识到了风险。", ["be aware of 意识到", "become aware that 意识到……", "fully aware 充分意识到", "raise awareness 提高认识"]),
    "bark": ("The dog barked at the stranger.", "狗冲着陌生人叫。", ["bark loudly 大声吠叫", "bark at sb. 朝某人吠叫", "tree bark 树皮", "bark up the wrong tree 找错对象"]),
    "behave": ("The children behaved well.", "孩子们表现得很好。", ["behave well 表现良好", "behave badly 表现不佳", "behave differently 表现不同", "behave like 表现得像"]),
    "benefit": ("Exercise benefits both body and mind.", "锻炼有益于身心。", ["benefit from 从……中受益", "bring benefits 带来益处", "mutual benefit 互惠", "health benefits 健康益处"]),
    "carry": ("This pipe carries water to the village.", "这条管道把水输送到村庄。", ["carry out 执行", "carry information 传递信息", "carry a risk 带有风险", "carry weight 有影响力"]),
    "challenge": ("Finding clean water is a major challenge.", "获得清洁用水是一项重大挑战。", ["face a challenge 面临挑战", "pose a challenge 构成挑战", "meet a challenge 应对挑战", "challenge an assumption 质疑假设"]),
    "controversy": ("The decision caused public controversy.", "这一决定引发了公众争议。", ["cause controversy 引发争议", "a major controversy 重大争议", "surrounding controversy 围绕……的争议", "controversy over 关于……的争议"]),
    "course": ("The river changed its course.", "河流改变了流向。", ["a training course 培训课程", "course of action 行动方针", "in the course of 在……过程中", "of course 当然"]),
    "definition": ("The term has a clear definition.", "这个术语有明确的定义。", ["a precise definition 精确定义", "dictionary definition 词典释义", "definition of success 成功的定义", "by definition 按照定义"]),
    "determine": ("Tests determine the quality of the water.", "检测可以确定水质。", ["determine whether 确定是否", "determine the cause 查明原因", "determine the outcome 决定结果", "largely determine 很大程度上决定"]),
    "ecology": ("The project may damage the local ecology.", "这个项目可能破坏当地生态。", ["local ecology 当地生态", "marine ecology 海洋生态", "ecological balance 生态平衡", "ecology research 生态学研究"]),
    "enable": ("The app enables users to work remotely.", "这款应用使用户能够远程工作。", ["enable sb. to do sth. 使某人能够做某事", "enable access 使访问成为可能", "technology enables 技术使……成为可能", "help enable 帮助实现"]),
    "evolve": ("Languages evolve over time.", "语言会随时间演变。", ["gradually evolve 逐渐演变", "evolve into 演变成", "evolve from 从……演变而来", "continue to evolve 继续发展"]),
    "except": ("Everyone came except Tom.", "除了汤姆，所有人都来了。", ["except for 除……之外", "all except 除……外全部", "with the exception of 除……以外", "nothing except 除了……什么也没有"]),
    "exhibit": ("The patient exhibited clear symptoms.", "患者表现出明显症状。", ["exhibit behaviour 表现出行为", "exhibit symptoms 表现出症状", "exhibit evidence 展示证据", "museum exhibit 博物馆展品"]),
    "facilitate": ("The new system facilitates communication.", "新系统促进了沟通。", ["facilitate learning 促进学习", "facilitate communication 促进交流", "facilitate access 便利获取", "facilitate the process 推动进程"]),
    "feedback": ("Students need clear feedback.", "学生需要明确的反馈。", ["provide feedback 提供反馈", "receive feedback 收到反馈", "positive feedback 积极反馈", "feedback on 关于……的反馈"]),
    "flee": ("Residents fled the burning building.", "居民逃离了着火的大楼。", ["flee the scene 逃离现场", "flee from 逃离", "be forced to flee 被迫逃亡", "flee to safety 逃到安全地带"]),
    "guidance": ("Ask your teacher for guidance.", "向老师寻求指导。", ["seek guidance 寻求指导", "provide guidance 提供指导", "under the guidance of 在……指导下", "official guidance 官方指引"]),
    "hamper": ("Heavy rain hampered the rescue effort.", "大雨妨碍了救援工作。", ["hamper progress 阻碍进展", "hamper development 妨碍发展", "severely hamper 严重阻碍", "be hampered by 受到……妨碍"]),
    "however": ("The task was difficult; however, we finished it.", "任务很困难；不过，我们完成了。", ["however difficult 无论多困难", "however small 无论多小", "however, the results 然而，结果……", "however much 无论多少"]),
    "hypothesis": ("The experiment supported the hypothesis.", "实验支持了这一假说。", ["test a hypothesis 检验假说", "support a hypothesis 支持假说", "reject a hypothesis 否定假说", "working hypothesis 工作假设"]),
    "ignorant": ("He was ignorant of the new rule.", "他不知道这项新规定。", ["be ignorant of 不知道", "remain ignorant 仍不知情", "wilfully ignorant 故意无视", "ignorant about 对……不了解"]),
    "incur": ("Late payment may incur a fee.", "逾期付款可能会产生费用。", ["incur costs 产生成本", "incur a penalty 招致处罚", "incur debt 负债", "incur criticism 招致批评"]),
    "indicate": ("The results indicate a clear trend.", "结果显示出明确趋势。", ["indicate that 表明……", "clearly indicate 清楚表明", "indicate a change 显示变化", "evidence indicates 证据表明"]),
    "involve": ("The job involves working with children.", "这份工作需要与儿童打交道。", ["involve doing sth. 涉及做某事", "be involved in 参与", "involve a risk 涉及风险", "directly involve 直接涉及"]),
    "journal": ("The findings appeared in a scientific journal.", "研究结果发表在一本科学期刊上。", ["academic journal 学术期刊", "scientific journal 科学期刊", "publish in a journal 在期刊发表", "keep a journal 写日记"]),
    "landmark": ("The tower is a famous landmark.", "这座塔是著名地标。", ["historic landmark 历史地标", "local landmark 当地地标", "landmark study 里程碑式研究", "landmark decision 具有里程碑意义的决定"]),
    "level": ("Water levels rose overnight.", "水位一夜之间上涨了。", ["high level 高水平", "sea level 海平面", "at one level 在某一层面", "level of risk 风险水平"]),
    "locate": ("Rescuers located the missing climber.", "救援人员找到了失踪的登山者。", ["locate the source 找到来源", "locate information 查找信息", "be located in 位于", "accurately locate 准确定位"]),
    "location": ("The hotel is in a convenient location.", "酒店位置便利。", ["exact location 确切位置", "geographical location 地理位置", "remote location 偏远地点", "location of the site 场地位置"]),
    "maintain": ("Regular repairs maintain the system.", "定期维修可维持系统运转。", ["maintain quality 保持质量", "maintain contact 保持联系", "maintain that 坚称……", "properly maintain 妥善维护"]),
    "memorise": ("Students memorised the new vocabulary.", "学生们记住了新词汇。", ["memorise a list 记住清单", "memorise vocabulary 背单词", "memorise facts 记住事实", "memorise information 记住信息"]),
    "mere": ("A mere ten people attended.", "只有十个人参加。", ["mere fact 仅仅这一事实", "mere presence 仅仅在场", "mere possibility 仅有的可能性", "not a mere 不只是……"]),
    "merely": ("The figures are merely estimates.", "这些数字只是估算值。", ["merely a matter of 仅仅是……的问题", "merely suggest 只是表明", "not merely 不仅仅", "merely because 仅仅因为"]),
    "naive": ("It was naive to trust every claim.", "相信每一种说法是天真的。", ["naive belief 天真的看法", "naive assumption 幼稚的假设", "politically naive 政治上不成熟", "seem naive 显得天真"]),
    "necessarily": ("Higher prices do not necessarily mean better quality.", "价格更高未必意味着质量更好。", ["not necessarily 未必", "necessarily involve 必然涉及", "necessarily lead to 必然导致", "necessarily true 必然正确"]),
    "observe": ("Scientists observed the animals closely.", "科学家仔细观察了这些动物。", ["observe behaviour 观察行为", "observe a pattern 观察到规律", "closely observe 仔细观察", "observe the law 遵守法律"]),
    "oppose": ("Local residents opposed the plan.", "当地居民反对这项计划。", ["strongly oppose 强烈反对", "oppose a proposal 反对提案", "be opposed to 反对", "oppose doing sth. 反对做某事"]),
    "predator": ("The bird escaped from a predator.", "这只鸟逃过了捕食者。", ["natural predator 天敌", "top predator 顶级捕食者", "escape predators 逃避捕食者", "predator population 捕食者种群"]),
    "presence": ("Her presence changed the atmosphere.", "她的到场改变了气氛。", ["presence of 存在……", "physical presence 亲自到场", "in the presence of 当着……的面", "detect the presence of 检测到……存在"]),
    "presumably": ("The road is closed, presumably because of flooding.", "道路关闭了，大概是因为洪水。", ["presumably because 大概因为", "presumably due to 推测由于", "presumably true 大概属实", "presumably intended 推测原本打算"]),
    "proceed": ("The meeting proceeded as planned.", "会议按计划进行。", ["proceed with 继续进行", "proceed to do 接着做", "proceed as planned 按计划进行", "proceed with caution 谨慎行事"]),
    "project": ("The research project lasted two years.", "这个研究项目持续了两年。", ["research project 研究项目", "major project 重大项目", "carry out a project 开展项目", "project costs 项目成本"]),
    "remark": ("She remarked that the room was cold.", "她评论说房间很冷。", ["remark that 评论说", "make a remark 发表评论", "brief remark 简短评论", "opening remarks 开场白"]),
    "remove": ("Please remove your shoes.", "请脱鞋。", ["remove a barrier 消除障碍", "remove from 从……移走", "remove waste 清除废物", "completely remove 彻底去除"]),
    "route": ("We chose the shortest route home.", "我们选择了回家最短的路线。", ["direct route 直接路线", "main route 主要路线", "escape route 逃生路线", "along the route 沿途"]),
    "routine": ("Exercise is part of my daily routine.", "锻炼是我日常安排的一部分。", ["daily routine 日常安排", "routine check 常规检查", "routine procedure 常规程序", "follow a routine 按惯例行事"]),
    "species": ("This species lives near rivers.", "这一物种生活在河流附近。", ["endangered species 濒危物种", "native species 本地物种", "animal species 动物物种", "species diversity 物种多样性"]),
    "stage": ("The disease was found at an early stage.", "疾病在早期阶段被发现。", ["early stage 早期阶段", "at this stage 在现阶段", "final stage 最后阶段", "stage of development 发展阶段"]),
    "stick": ("She used a stick to support the plant.", "她用一根木棍支撑植物。", ["wooden stick 木棍", "walking stick 手杖", "stick to 坚持；遵守", "stick in 卡在……里"]),
    "subject": ("The volunteers became research subjects.", "这些志愿者成为研究对象。", ["research subject 研究对象", "school subject 学科", "subject to 受……影响；须经", "main subject 主题"]),
    "suggest": ("The evidence suggests a link.", "证据表明存在联系。", ["suggest that 表明；建议", "strongly suggest 强烈表明", "suggest doing sth. 建议做某事", "results suggest 结果表明"]),
    "tap": ("He tapped the screen twice.", "他轻点了两下屏幕。", ["tap the screen 轻点屏幕", "tap on 轻敲", "tap into 利用", "water tap 水龙头"]),
    "theory": ("The evidence supports the theory.", "证据支持这一理论。", ["scientific theory 科学理论", "theory of mind 心智理论", "test a theory 检验理论", "in theory 理论上"]),
    "thereby": ("The policy reduced waste, thereby saving money.", "这项政策减少了浪费，从而节省了资金。", ["thereby reducing 从而减少", "thereby increasing 从而增加", "thereby allowing 从而使……成为可能", "and thereby 并因此"]),
    "throughout": ("It rained throughout the night.", "雨下了一整夜。", ["throughout the year 全年", "throughout history 纵观历史", "throughout the world 遍及世界", "throughout the process 在整个过程中"]),
    "transfer": ("The files were transferred to a new computer.", "文件被转移到一台新电脑上。", ["transfer information 传递信息", "transfer to 转到", "knowledge transfer 知识转移", "bank transfer 银行转账"]),
    "transform": ("Education can transform lives.", "教育可以改变人生。", ["transform into 转变为", "completely transform 彻底改变", "transform society 改变社会", "digital transformation 数字化转型"]),
    "understanding": ("The course improved my understanding of science.", "这门课程加深了我对科学的理解。", ["deep understanding 深入理解", "gain an understanding 获得理解", "mutual understanding 相互理解", "understanding of 对……的理解"]),
    "valid": ("That is a valid reason.", "那是一个合理的理由。", ["valid argument 有根据的论点", "valid reason 正当理由", "valid evidence 有效证据", "remain valid 仍然有效"]),
    "various": ("The museum displays objects from various cultures.", "博物馆展示来自不同文化的物品。", ["various reasons 各种原因", "various methods 各种方法", "various stages 不同阶段", "in various ways 以各种方式"]),
}

MORPHOLOGY = {
    "ecology": "eco-（生态、环境）+ -logy（……学）→ 生态学",
    "enable": "en-（使成为）+ able（能够的）→ 使能够",
    "feedback": "feed（输入、供给）+ back（返回）→ 返回的信息，即反馈",
    "guidance": "guide（引导）+ -ance（名词后缀）→ 指导、指引",
    "hypothesis": "源自希腊语 hypo-（在下）+ thesis（命题、放置）；现代义为待检验的假说",
    "ignorant": "ignore/拉丁语 ignorare（不知道）+ -ant（形容词后缀）→ 无知的",
    "location": "locate（定位）+ -ion（名词后缀）→ 位置",
    "merely": "mere（仅仅的）+ -ly（副词后缀）→ 仅仅",
    "necessarily": "necessary（必要的）+ -ly（副词后缀）→ 必然地；必要地",
    "predator": "predate（捕食）+ -or（行为者）→ 捕食者",
    "presumably": "presumable（可推定的）+ -ly（副词后缀）→ 大概、推测起来",
    "thereby": "there（由此）+ by（借此）→ 因此、从而",
    "throughout": "through（贯穿）+ out（完全、遍及）→ 自始至终；遍及",
    "transform": "trans-（跨越、改变）+ form（形态）→ 改变形态",
}

DERIVATIVES = {
    "acquire": ["acquisition n. 获得；收购"], "advocate": ["advocacy n. 拥护；倡导"],
    "aware": ["awareness n. 意识", "unaware adj. 未意识到的"],
    "behave": ["behaviour n. 行为", "behavioural adj. 行为的"],
    "benefit": ["beneficial adj. 有益的", "beneficiary n. 受益者"],
    "controversy": ["controversial adj. 有争议的"], "definition": ["define v. 定义", "definite adj. 明确的"],
    "determine": ["determination n. 决定；决心", "determined adj. 坚定的"],
    "ecology": ["ecological adj. 生态的", "ecologist n. 生态学家"],
    "enable": ["disable v. 使失去能力", "ability n. 能力"],
    "evolve": ["evolution n. 演化", "evolutionary adj. 演化的"],
    "exhibit": ["exhibition n. 展览", "exhibitor n. 参展者"],
    "facilitate": ["facilitation n. 促进；便利"], "guidance": ["guide v./n. 引导；指南"],
    "hypothesis": ["hypothesise v. 假设", "hypothetical adj. 假设的"],
    "ignorant": ["ignorance n. 无知"], "indicate": ["indication n. 迹象；表明", "indicator n. 指标"],
    "involve": ["involvement n. 参与；涉及"], "locate": ["location n. 位置"],
    "maintain": ["maintenance n. 维护"], "memorise": ["memorisation n. 记忆", "memory n. 记忆"],
    "mere": ["merely adv. 仅仅"], "observe": ["observation n. 观察", "observer n. 观察者"],
    "oppose": ["opposition n. 反对", "opponent n. 对手"], "predator": ["predatory adj. 捕食性的"],
    "presumably": ["presume v. 推定", "presumption n. 推定"], "suggest": ["suggestion n. 建议；暗示"],
    "theory": ["theoretical adj. 理论的", "theoretically adv. 理论上"],
    "transfer": ["transferable adj. 可转移的"], "transform": ["transformation n. 转变"],
    "understanding": ["understand v. 理解", "understandable adj. 可理解的"],
    "valid": ["validity n. 有效性", "validate v. 验证；使生效", "invalid adj. 无效的"],
    "various": ["vary v. 变化", "variation n. 变化", "variety n. 多样性"],
}

USAGE = {
    "advocate": "动词重音通常在末音节；名词重音通常在首音节。动词常接名词或动名词，不接 advocate sb. to do。",
    "aware": "通常作表语：be aware of/that；一般不放在名词前表示“有意识的某人”。",
    "benefit": "benefit sb./sth. 表示“使……受益”；benefit from 表示“从……受益”。",
    "course": "of course 是固定话语标记；course 单独还可表示课程、路线或过程，需依语境判断。",
    "except": "except 排除同类中的个体；except for 常用于对整体陈述作局部修正。",
    "however": "表示转折时通常用标点与句子隔开；however + adj./adv. 表示“无论多么……”。",
    "incur": "正式用词，宾语通常是不利后果，如 cost、debt、penalty、criticism。",
    "involve": "involve doing sth.，不能用 involve to do sth.；be involved in 表示参与或卷入。",
    "journal": "academic/scientific journal 指学术期刊；日常个人记录可用 journal 或 diary。",
    "locate": "locate 可表示“找到”或“把……设在”；be located in/at 表示“位于”。",
    "maintain": "可表示维持、维护，也可接 that 从句表示“坚持声称”。",
    "mere": "mere 是形容词，修饰名词；merely 是副词，修饰动词、形容词或整句话。",
    "observe": "observe 可表示仔细观察、注意到或遵守；watch 更强调持续观看动态过程。",
    "proceed": "proceed with + 名词；proceed to do 表示完成一事后接着做另一事。",
    "project": "名词通常读 /ˈprɒdʒekt/；动词通常读 /prəˈdʒekt/。",
    "remark": "remark on/upon sth. 或 remark that...；比 say 更强调评论或注意到。",
    "subject": "名词重音在首音节；动词 subject 重音在第二音节；be subject to 表示受制于或须经。",
    "suggest": "suggest doing 或 suggest that...；标准用法不说 suggest sb. to do sth.。",
    "transfer": "名词重音通常在首音节，动词重音通常在第二音节。",
    "valid": "valid 强调逻辑上有根据或法律/期限上有效；effective 强调实际产生效果。",
}

ERRORS = {
    "advocate": ("advocate people to recycle", "advocate recycling / encourage people to recycle", "advocate 不使用 sb. to do 结构。"),
    "attention": ("pay attention on the details", "pay attention to the details", "固定搭配是 pay attention to。"),
    "aware": ("I aware the risk.", "I am aware of the risk.", "aware 通常作表语，需要 be，并用 of 接名词。"),
    "benefit": ("Regular exercise benefits from people.", "People benefit from regular exercise.", "benefit from 的主语应是受益者。"),
    "enable": ("enable people do this", "enable people to do this", "enable 后用 object + to-infinitive。"),
    "except": ("Everyone except of Tom came.", "Everyone except Tom came.", "except 直接接被排除对象，不加 of。"),
    "however": ("However the plan failed.", "However, the plan failed.", "句首表示转折时通常需要逗号。"),
    "hypothesis": ("many hypothesis", "many hypotheses", "hypothesis 的复数是 hypotheses。"),
    "ignorant": ("ignorant to the facts", "ignorant of the facts", "固定搭配是 ignorant of/about。"),
    "incur": ("incur from extra costs", "incur extra costs", "incur 是及物动词，直接接代价或损失。"),
    "involve": ("The job involves to travel.", "The job involves travelling.", "involve 后接动名词。"),
    "locate": ("The office locates in London.", "The office is located in London.", "表示某物位于某处通常用 be located。"),
    "mere": ("It merely fact proves nothing.", "The mere fact proves nothing.", "名词前用形容词 mere，不用副词 merely。"),
    "oppose": ("oppose against the plan", "oppose the plan / be opposed to the plan", "oppose 作动词时直接接宾语。"),
    "proceed": ("proceed the plan", "proceed with the plan", "表示继续某事用 proceed with。"),
    "suggest": ("She suggested me to wait.", "She suggested that I wait / suggested waiting.", "suggest 不接 sb. to do。"),
    "throughout": ("throughout of the year", "throughout the year", "throughout 作介词时不加 of。"),
    "valid": ("a valid method that works well", "an effective method that works well", "强调实际效果时通常用 effective。"),
}

SOURCE_NOTES = {
    16: "PDF 原文止于 'the presence.'，句子疑似缺词；中文仅按上下文作保守补译，需回源复核。",
    18: "PDF 原文为 'allows others flee'；标准英语通常写作 'allows others to flee'。",
}

RELATION_NOTES = {
    "acquire": ["obtain: obtain 泛指取得；acquire 常强调逐步获得知识、技能或财产。"],
    "advocate": ["recommend: advocate 强调公开支持某种政策或做法；recommend 强调给出具体建议。"],
    "aware": ["conscious: aware 表示知道某事实；conscious 还可表示有意识、未昏迷。"],
    "benefit": ["advantage: benefit 是获得的益处；advantage 是使人占优的条件。"],
    "controversy": ["debate: controversy 强调广泛而持续的争议；debate 可指有组织的讨论。"],
    "determine": ["decide: determine 可表示查明事实或决定结果；decide 更常表示作出选择。"],
    "enable": ["allow: enable 强调提供能力或条件；allow 强调许可或不加阻止。"],
    "evolve": ["develop: evolve 强调逐渐演变；develop 泛指发展、成长或开发。"],
    "exhibit": ["display: 两者都可表示展示；exhibit 更正式，也常指表现出症状或行为。"],
    "facilitate": ["enable: facilitate 是让过程更容易；enable 是让某事成为可能。"],
    "flee": ["escape: flee 强调迅速逃离危险地点；escape 强调成功摆脱控制或危险。"],
    "hamper": ["hinder: 两者均指阻碍；hamper 常指外部条件使进展变慢。"],
    "hypothesis": ["theory: hypothesis 是待检验的具体假说；theory 是得到较广证据支持的解释体系。"],
    "ignorant": ["unaware: unaware 只是未意识到；ignorant 还可暗示缺乏知识，有时带贬义。"],
    "indicate": ["suggest: indicate 通常提供较明确的迹象；suggest 往往语气更保留。"],
    "involve": ["include: include 表示包含某部分；involve 强调某事必然需要或牵涉某活动。"],
    "locate": ["find: find 是一般的找到；locate 更正式，常强调确定精确位置。"],
    "maintain": ["preserve: maintain 强调使状态持续；preserve 强调防止损坏、丧失或改变。"],
    "memorise": ["remember: memorise 是主动记住；remember 是记得或回想起。"],
    "mere": ["merely: mere 是形容词，merely 是副词，意义都接近“仅仅”。"],
    "observe": ["watch: observe 更正式、分析性更强；watch 强调持续观看动态事物。"],
    "oppose": ["object: oppose 可直接反对人、计划或政策；object 常用 object to 表示提出异议。"],
    "proceed": ["continue: continue 最通用；proceed 更正式，常指按步骤继续或前往。"],
    "remark": ["comment: 两者均可指评论；remark 常指简短说出观察，comment 可更系统。"],
    "suggest": ["recommend: suggest 可表示建议或暗示；recommend 更明确地推荐选择或行动。"],
    "transfer": ["transform: transfer 是转移位置或所有权；transform 是改变性质或形态。"],
    "valid": ["effective: valid 强调有根据或有效期合法；effective 强调实际有效。"],
    "various": ["varied: various 强调有多个不同种类；varied 强调变化丰富、不单一。"],
}

RELATION_EXAMPLES = {
    "acquire": ("Students acquire language gradually, while researchers obtain data from experiments.", "学生逐渐习得语言，而研究人员从实验中获得数据。"),
    "advocate": ("The report advocates stricter rules but recommends a gradual timetable.", "报告主张制定更严格的规则，但建议采用渐进式时间表。"),
    "aware": ("She was aware of the danger and remained conscious throughout the rescue.", "她意识到了危险，并在救援过程中始终保持清醒。"),
    "benefit": ("Clean air is a public benefit, while a central location gives the shop a commercial advantage.", "清洁空气是一项公共福祉，而中心位置给商店带来商业优势。"),
    "controversy": ("The policy caused controversy, and Parliament held a formal debate about it.", "这项政策引发争议，议会就此举行了正式辩论。"),
    "determine": ("The evidence will determine the cause, and the committee will decide what to do next.", "证据将查明原因，委员会将决定下一步行动。"),
    "enable": ("The ramp enables wheelchair users to enter; the guard allows access after checking identification.", "坡道使轮椅使用者能够进入；警卫核验身份后准许通行。"),
    "evolve": ("Species evolve over generations, while individual skills develop through practice.", "物种经过世代演化，而个人技能通过练习得到发展。"),
    "exhibit": ("The patient exhibited unusual symptoms, and the chart displayed the test results.", "患者表现出异常症状，图表则展示了检测结果。"),
    "facilitate": ("Clear instructions facilitate learning, while internet access enables students to study remotely.", "清晰的说明促进学习，而网络接入使学生能够远程学习。"),
    "flee": ("Residents fled the town before the fire reached it, and all of them escaped safely.", "居民在大火蔓延到城镇前便逃离了，所有人都安全脱险。"),
    "hamper": ("Fog hampered the rescue operation, while fallen trees hindered traffic.", "大雾妨碍了救援行动，倒下的树木则阻碍了交通。"),
    "hypothesis": ("The experiment tested a hypothesis derived from evolutionary theory.", "实验检验了一个源自进化理论的假说。"),
    "ignorant": ("He was ignorant of basic safety rules, while the visitors were simply unaware of the temporary closure.", "他缺乏基本安全规则知识，而游客只是不知道临时关闭一事。"),
    "indicate": ("The measurements indicate a rise, while the early observations merely suggest one.", "测量数据表明确有上升，而早期观察只暗示可能上升。"),
    "involve": ("The course includes three lectures and involves completing a field project.", "该课程包括三场讲座，并要求完成一个实地项目。"),
    "locate": ("The team located the signal precisely after a volunteer found the missing device.", "志愿者找到遗失设备后，团队精确定位了信号。"),
    "maintain": ("Engineers maintain the bridge, while conservationists preserve its historic features.", "工程师维护桥梁，而文物保护人员保存其历史特征。"),
    "memorise": ("Students memorise the formula first and remember it more easily after applying it.", "学生先记住公式，并在应用后更容易长期记得它。"),
    "mere": ("The mere presence of a teacher changed the room; students were not merely pretending to work.", "老师仅仅在场就改变了教室氛围；学生并不只是假装学习。"),
    "observe": ("Researchers observed the ants systematically while visitors watched from behind the glass.", "研究人员系统观察蚂蚁，参观者则隔着玻璃观看。"),
    "oppose": ("Residents opposed the development, and several groups formally objected to the planning application.", "居民反对这项开发，多个团体正式对规划申请提出异议。"),
    "proceed": ("After the safety check, the team proceeded with the test and continued recording data.", "安全检查后，团队继续进行测试并持续记录数据。"),
    "remark": ("The scientist remarked that the result was unusual, then added a detailed comment in the report.", "科学家说这一结果不同寻常，随后在报告中补充了详细评论。"),
    "suggest": ("The data suggest a link, but the panel recommends further research before action is taken.", "数据暗示存在联系，但专家组建议在采取行动前进一步研究。"),
    "transfer": ("The laboratory transferred the samples to another site but did not transform their chemical structure.", "实验室把样本转移到另一地点，但没有改变其化学结构。"),
    "valid": ("The criticism is valid, but the proposed solution may not be effective.", "这项批评有根据，但提出的解决方案未必有效。"),
    "various": ("The study used various methods and produced a varied set of responses.", "研究采用了多种方法，并得到丰富多样的回答。"),
}

GRAMMAR_PATTERNS = {
    "acquire": "acquire + object", "advocate": "advocate + noun / doing sth.",
    "alarm": "sound / raise + the alarm", "attention": "pay attention to + noun",
    "aware": "be aware of + noun / be aware that + clause", "bark": "bark at + person / bark up the wrong tree",
    "behave": "behave + adverb / behave like + noun", "benefit": "benefit + object / benefit from + noun",
    "carry": "carry out + task / research", "challenge": "pose / face + a challenge",
    "controversy": "controversy over / surrounding + noun", "course": "in the course of + noun / of course",
    "definition": "the definition of + noun", "determine": "determine + object / determine whether + clause",
    "ecology": "the ecology of + place / species", "enable": "enable + object + to do sth.",
    "evolve": "evolve from A into B", "except": "except + noun / except for + noun",
    "exhibit": "exhibit + behaviour / symptom / quality", "facilitate": "facilitate + noun / process",
    "feedback": "feedback on + noun", "flee": "flee + place / flee from + danger",
    "guidance": "guidance on + noun / under the guidance of + person", "hamper": "hamper + progress / effort",
    "however": "however, + clause / however + adjective", "hypothesis": "the hypothesis that + clause",
    "ignorant": "be ignorant of / about + noun", "incur": "incur + cost / penalty / criticism",
    "indicate": "indicate that + clause", "involve": "involve + doing sth. / be involved in + noun",
    "journal": "publish in + a journal", "landmark": "a landmark in + field / history",
    "level": "the level of + noun / at one level", "locate": "locate + object / be located in + place",
    "location": "the location of + noun", "maintain": "maintain + object / maintain that + clause",
    "memorise": "memorise + object", "mere": "mere + noun", "merely": "merely + verb / adjective",
    "naive": "be naive about + noun / it is naive to do sth.", "necessarily": "not necessarily + verb / adjective",
    "observe": "observe + object / observe that + clause", "oppose": "oppose + noun / be opposed to + noun",
    "predator": "a predator of + species", "presence": "the presence of + noun / in the presence of + person",
    "presumably": "presumably, + clause / presumably because + clause", "proceed": "proceed with + noun / proceed to do sth.",
    "project": "a project on + topic / carry out a project", "remark": "remark on + noun / remark that + clause",
    "remove": "remove + object + from + place", "route": "a route to / through + place",
    "routine": "a daily routine / routine + noun", "species": "a species of + organism",
    "stage": "at a stage / a stage of + process", "stick": "use a stick to do sth. / stick to + noun",
    "subject": "a subject of + study / be subject to + noun", "suggest": "suggest doing sth. / suggest that + clause",
    "tap": "tap + object / tap on / tap into + noun", "theory": "the theory of + noun / theory that + clause",
    "thereby": "clause, thereby + -ing", "throughout": "throughout + place / period",
    "transfer": "transfer A to / from B", "transform": "transform A into B",
    "understanding": "an understanding of + noun", "valid": "valid for + period / valid + reason",
    "various": "various + plural noun",
}

MORPH_SEGMENTS = {
    "ecology": [{"form":"eco-","type":"combining_form","meaningZh":"生态；环境","origin":"Greek"},{"form":"-logy","type":"suffix","meaningZh":"……学；研究","origin":"Greek"}],
    "enable": [{"form":"en-","type":"prefix","meaningZh":"使成为；使处于","origin":"French/Latin"},{"form":"able","type":"base","meaningZh":"能够的","origin":"Latin"}],
    "feedback": [{"form":"feed","type":"base","meaningZh":"输入；供给"},{"form":"back","type":"base","meaningZh":"返回"}],
    "guidance": [{"form":"guide","type":"base","meaningZh":"引导；指导"},{"form":"-ance","type":"suffix","meaningZh":"行为、状态或结果","origin":"French/Latin"}],
    "hypothesis": [{"form":"hypo-","type":"prefix","meaningZh":"在下；低于","origin":"Greek"},{"form":"thesis","type":"root","meaningZh":"命题；放置","origin":"Greek"}],
    "ignorant": [{"form":"ignor-","type":"root","meaningZh":"不知道；不认识","origin":"Latin"},{"form":"-ant","type":"suffix","meaningZh":"具有某种状态的","origin":"Latin"}],
    "location": [{"form":"locate","type":"base","meaningZh":"定位；使坐落"},{"form":"-ion","type":"suffix","meaningZh":"行为、过程或结果","origin":"Latin"}],
    "merely": [{"form":"mere","type":"base","meaningZh":"仅仅的"},{"form":"-ly","type":"suffix","meaningZh":"构成副词"}],
    "necessarily": [{"form":"necessary","type":"base","meaningZh":"必要的"},{"form":"-ly","type":"suffix","meaningZh":"构成副词"}],
    "predator": [{"form":"predat-","type":"root","meaningZh":"捕食；掠夺","origin":"Latin"},{"form":"-or","type":"suffix","meaningZh":"做某动作的人或事物","origin":"Latin"}],
    "presumably": [{"form":"presume","type":"base","meaningZh":"推定；假定"},{"form":"-able","type":"suffix","meaningZh":"可以……的"},{"form":"-ly","type":"suffix","meaningZh":"构成副词"}],
    "thereby": [{"form":"there","type":"base","meaningZh":"由此"},{"form":"by","type":"base","meaningZh":"借此；通过"}],
    "throughout": [{"form":"through","type":"base","meaningZh":"贯穿"},{"form":"out","type":"particle","meaningZh":"完全；遍及"}],
    "transform": [{"form":"trans-","type":"prefix","meaningZh":"跨越；改变","origin":"Latin"},{"form":"form","type":"root","meaningZh":"形态","origin":"Latin"}],
}

PHONETIC_FIXES = {
    "landmark": "/ˈlændmɑːk/", "merely": "/ˈmɪəli/", "presumably": "/prɪˈzjuːməbli/",
    "throughout": "/θruːˈaʊt/", "various": "/ˈveəriəs/", "locate": "/ləʊˈkeɪt/",
    "location": "/ləʊˈkeɪʃn/", "oppose": "/əˈpəʊz/",
}

# Article-relevant primary senses. These remove legacy records that mixed several
# parts of speech or specialist meanings into one sense.
SENSE_OVERRIDES = {
    "acquire": ("v.", "获得；习得", "To gain or obtain something, especially through effort or experience.", "通过努力、学习或经历获得某物，尤指知识、技能或信息。"),
    "advocate": ("v.", "提倡；拥护；主张", "To publicly support or recommend a policy, idea, or course of action.", "公开支持或提倡某种政策、观点或行动方式。"),
    "alarm": ("n.", "警报；警报声；惊恐", "A warning of danger, often given by a sound or signal.", "对危险发出的警告，常以声音或信号呈现。"),
    "attention": ("n.", "注意；注意力", "The act of directing thought or awareness towards something.", "把思想或意识集中到某事物上的状态或行为。"),
    "aware": ("adj.", "意识到的；知道的", "Knowing or realising that something exists or is true.", "知道或意识到某事存在或属实。"),
    "bark": ("v.", "吠叫；厉声说", "To make the short, loud cry typical of a dog.", "发出狗所特有的短促响亮叫声；文中用于习语 bark up the wrong tree。"),
    "behave": ("v.", "表现；行为", "To act in a particular way.", "以某种特定方式行动或表现。"),
    "benefit": ("n.", "益处；好处", "An advantage or helpful effect.", "某事带来的优势、帮助或积极效果。"),
    "carry": ("v.", "携带；运送；执行", "To take something from one place to another; in carry out, to perform a task.", "把某物带到另一处；在 carry out 中表示执行或完成。"),
    "challenge": ("n.", "挑战；难题", "A difficult task or problem that tests ability or understanding.", "检验能力或理解力的困难任务或问题。"),
    "controversy": ("n.", "争议；公开辩论", "Prolonged public disagreement about an issue.", "围绕某一问题持续发生的公开分歧或争论。"),
    "course": ("n.", "过程；路线；课程", "A direction, sequence of events, or series of lessons; of course is a fixed expression meaning naturally or certainly.", "路线、事情发展的过程或系列课程；of course 是表示“当然”的固定表达。"),
    "definition": ("n.", "定义；释义", "A statement that explains the exact meaning of a word or concept.", "说明某个词语或概念确切含义的陈述。"),
    "determine": ("v.", "决定；确定；查明", "To cause a result or establish something through evidence or calculation.", "决定某种结果，或通过证据、计算查明某事。"),
    "ecology": ("n.", "生态学；生态关系", "The study of relationships between organisms and their environment.", "研究生物与其环境之间关系的学科。"),
    "enable": ("v.", "使能够；使成为可能", "To give someone the ability or opportunity to do something.", "给予某人做某事的能力或条件。"),
    "evolve": ("v.", "演化；逐渐发展", "To develop gradually, especially from a simpler form.", "逐渐发展变化，尤指从较简单的形态演变而来。"),
    "except": ("prep./conj.", "除……之外", "Not including a particular person or thing.", "不把某个特定的人或事物包括在内。"),
    "exhibit": ("v.", "表现出；展示", "To show a quality, behaviour, or characteristic clearly.", "清楚地表现出某种性质、行为或特征。"),
    "facilitate": ("v.", "促进；使便利", "To make an action or process easier.", "使某项行动或过程更容易进行。"),
    "feedback": ("n.", "反馈；反馈信息", "Information about a response or performance used to guide later action.", "关于反应或表现的信息，可用于指导后续行动。"),
    "flee": ("v.", "逃离；逃跑", "To leave a dangerous place quickly.", "迅速离开危险的地方。"),
    "guidance": ("n.", "指导；引导", "Advice or direction that helps someone act or decide.", "帮助某人行动或作决定的建议和指引。"),
    "hamper": ("v.", "妨碍；阻碍", "To make movement, progress, or action difficult.", "使移动、进展或行动变得困难。"),
    "however": ("adv./conj.", "然而；不过；无论怎样", "Used to introduce a contrast, or before an adjective or adverb to mean regardless of degree.", "用于引出转折；也可置于形容词或副词前表示“无论多么”。"),
    "hypothesis": ("n.", "假说；假设", "A proposed explanation that can be tested against evidence.", "一种可以利用证据加以检验的解释或假设。"),
    "ignorant": ("adj.", "无知的；不了解的", "Lacking knowledge or awareness about something.", "对某事缺乏知识或认识。"),
    "incur": ("v.", "招致；承受", "To become subject to an unwanted cost, penalty, or consequence.", "因某种行为而承担不利的费用、处罚或后果。"),
    "indicate": ("v.", "表明；显示；暗示", "To show that something exists or is likely to be true.", "显示某事存在或很可能属实。"),
    "involve": ("v.", "涉及；包含；需要", "To include something as a necessary part or result.", "把某事作为必要组成部分或结果包括在内。"),
    "journal": ("n.", "期刊；日志", "A periodical containing academic articles, or a personal written record.", "刊载学术文章的定期出版物，或个人的书面日志。"),
    "landmark": ("n.", "地标；里程碑", "A recognisable feature used for orientation, or an event of major importance.", "用于辨认方位的显著特征；也指具有重大意义的事件。"),
    "level": ("n.", "层面；水平；等级", "A position on a scale, or a particular way of considering something.", "某一尺度上的位置，或看待问题的特定层面。"),
    "locate": ("v.", "找到；确定……的位置", "To find or establish the exact position of something.", "找到或确定某物的准确位置。"),
    "location": ("n.", "位置；地点", "A particular place or position.", "某个特定地点或位置。"),
    "maintain": ("v.", "坚持认为；维持；维护", "To state firmly that something is true, or keep something in a particular condition.", "坚持声称某事属实，或使某物保持特定状态。"),
    "memorise": ("v.", "记住；熟记", "To learn something so that it can be recalled exactly.", "学习并记牢某内容，以便准确回忆。"),
    "mere": ("adj.", "仅仅的；只不过的", "Used to emphasise how small, unimportant, or limited something is.", "强调某事物数量少、不重要或程度有限。"),
    "merely": ("adv.", "仅仅；只不过", "Only; simply and no more than that.", "只是如此，没有更多含义或程度。"),
    "naive": ("adj.", "天真的；缺乏经验的", "Lacking experience or judgement and therefore trusting too easily.", "因缺乏经验或判断力而过于轻信。"),
    "necessarily": ("adv.", "必然地；不可避免地", "As an inevitable or logically required result.", "作为不可避免或逻辑上必需的结果。"),
    "observe": ("v.", "观察；注意到；遵守", "To watch carefully, notice, or comply with a rule.", "仔细观看、注意到某事，或遵守规则。"),
    "oppose": ("v.", "反对；抵制", "To disagree with and try to prevent an idea, plan, or action.", "不同意并试图阻止某种观点、计划或行动。"),
    "predator": ("n.", "捕食者；捕食性动物", "An animal that hunts and eats other animals.", "捕猎并以其他动物为食的动物。"),
    "presence": ("n.", "存在；在场", "The state of being in a place or of existing.", "处于某个地方或实际存在的状态。"),
    "presumably": ("adv.", "大概；推测起来", "Used to say that something is believed to be likely.", "用于表示根据现有信息推测某事很可能属实。"),
    "proceed": ("v.", "继续进行；前进", "To continue an action or move forward.", "继续某项行动或向前移动。"),
    "project": ("n.", "项目；课题；计划", "A planned piece of work with a particular purpose.", "为实现特定目的而规划的一项工作。"),
    "remark": ("v.", "评论；谈到", "To say something as a comment or observation.", "以评论或观察的方式说出某事。"),
    "remove": ("v.", "移走；去除；撤除", "To take something away from a place or position.", "把某物从某个地点或位置拿走。"),
    "route": ("n.", "路线；路径", "A way or course taken to reach a place.", "到达某地所采用的道路或路径。"),
    "routine": ("n./adj.", "惯例；常规程序；例行的", "A usual sequence of actions; regular and ordinary.", "通常反复进行的一系列行动；常规且普通的。"),
    "species": ("n.", "物种；种", "A group of organisms capable of reproducing with one another.", "能够相互繁殖的一类生物群体。"),
    "stage": ("n.", "阶段；时期", "A particular point or period in a process of development.", "发展过程中的某个特定时期或步骤。"),
    "stick": ("n.", "枝条；棍；棒", "A thin piece of wood broken or cut from a tree.", "从树上折下或截取的一段细木条。"),
    "subject": ("n.", "研究对象；受试者；主题", "A person or animal studied in an experiment.", "在实验或研究中被观察、测试的人或动物。"),
    "suggest": ("v.", "表明；暗示；建议", "To indicate that something may be true, or put forward an idea.", "显示某事可能属实，或提出一种想法或建议。"),
    "tap": ("v.", "轻拍；轻触", "To touch or hit something lightly and quickly.", "快速而轻柔地触碰或敲击某物。"),
    "theory": ("n.", "理论；学说", "A system of ideas intended to explain facts or events.", "用于解释事实或事件的一套系统性观点。"),
    "thereby": ("adv.", "因此；从而", "As a result of the action just mentioned.", "作为刚才所述行动的结果。"),
    "throughout": ("prep./adv.", "遍及；贯穿；自始至终", "In every part of a place or during the whole of a period.", "遍及某地各处，或贯穿整个时间段。"),
    "transfer": ("n./v.", "传递；转移；调动", "To move something or someone from one place, person, or system to another.", "把某物或某人从一个地点、主体或系统转到另一个。"),
    "transform": ("v.", "使转变；彻底改变", "To change something greatly in form, character, or appearance.", "使某物的形态、性质或外观发生重大改变。"),
    "understanding": ("n.", "理解；认识", "Knowledge of how something works or what it means.", "对某事如何运作或具有何种含义的认识。"),
    "valid": ("adj.", "有根据的；有效的；正当的", "Based on sound reasoning or evidence; legally or officially acceptable.", "以合理推理或证据为基础；或在法律、正式规则上有效。"),
    "various": ("adj.", "各种各样的；不同的", "Of several different types.", "属于若干不同种类的。"),
}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def parse_inflections(exchange: str) -> list[dict]:
    rows = []
    seen = set()
    for part in str(exchange or "").split("/"):
        if ":" not in part:
            continue
        kind, form = part.split(":", 1)
        key = (kind, form.lower())
        if kind in FORM_LABELS and form and key not in seen:
            seen.add(key)
            rows.append({"type": kind, "labelZh": FORM_LABELS[kind], "form": form})
    return rows


def extract_article() -> str:
    result = subprocess.run(
        ["pdftotext", "-f", "4", "-l", "6", "-layout", str(PDF), "-"],
        check=True, capture_output=True, text=True,
    )
    article = result.stdout.split(TITLE, 1)[1].split("Questions 1-5", 1)[0]
    article = re.sub(r"\n\s*\d+\|Page\s*\f?", " ", article)
    article = re.sub(r"\s+", " ", article).strip()
    article = re.sub(r"^A\s+", "", article)
    article = re.sub(r"\s+[B-I]\s+(?=[\"A-Z])", " ", article)
    return (article.replace("presence .Sounding", "presence. Sounding")
            .replace("Canada，maintained", "Canada, maintained")
            .replace("mind” teachers", "mind”: teachers")
            .replace("food 一 only", "food - only")
            .replace("mind” 一 meaning", "mind” - meaning"))


def article_sentences(article: str) -> list[str]:
    return re.split(r"(?<=[.!?])(?:[”\"])?\s+(?=[“\"A-Z])", article)


def word_hits(sentences: list[str], word_map: dict[str, dict]) -> tuple[dict[int, list[str]], dict[str, list[int]]]:
    line_hits: dict[int, list[str]] = {}
    word_lines = defaultdict(list)
    for index, sentence in enumerate(sentences, 1):
        hits = []
        for raw in MATCHER.WORD_RE.findall(sentence):
            surface = MATCHER.normalize(raw)
            key = surface if surface in word_map else next(
                (candidate for candidate in MATCHER.lemma_candidates(surface) if candidate in word_map), None
            )
            # Franks is a person's surname, not an occurrence of the adjective frank.
            if key and key != "frank" and key not in hits:
                hits.append(key)
                word_lines[key].append(index)
        if hits:
            line_hits[index] = hits
    return line_hits, dict(word_lines)


def line_word_links(sentence_id: int, sentence: str, hits: list[str], word_map: dict[str, dict]) -> list[dict]:
    forms = defaultdict(list)
    modes = defaultdict(set)
    for raw in MATCHER.WORD_RE.findall(sentence):
        surface = MATCHER.normalize(raw)
        key = surface if surface in word_map else next(
            (candidate for candidate in MATCHER.lemma_candidates(surface) if candidate in word_map), None
        )
        if key in hits and key != "frank":
            if raw not in forms[key]:
                forms[key].append(raw)
            modes[key].add("exact" if surface == key else "lemma")
    line_id = f"line_ants_{sentence_id:02d}"
    return [{
        "_id": f"{line_id}_word_{word}", "lineId": line_id, "wordId": f"word_{word}",
        "surfaceForms": forms[word], "matchType": "+".join(sorted(modes[word])),
    } for word in hits]


def clean_pos(value: str) -> str:
    return {"a": "adj.", "ad": "adv.", "vt": "v.", "vi": "v."}.get(value, value or "")


def source_status() -> dict:
    return {
        "dictionarySources": ["miniprogram/assets/data/wordbooks/ielts.json", "ECDICT"],
        "corpusSource": PDF.name,
        "articleTitle": TITLE,
        "editorialSource": "Codex editorial draft",
        "status": "draft",
        "reviewStatus": "pending_human_review",
    }


def compact_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def pretty_json(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def derivative_objects(values: list[str]) -> list[dict]:
    rows = []
    for value in values:
        match = re.match(r"^(\S+)\s+([^ ]+)\s+(.+)$", value)
        if not match:
            continue
        related_word, pos, translation = match.groups()
        rows.append({
            "wordId": f"word_{related_word}", "word": related_word,
            "pos": pos.rstrip("."), "translationZh": translation,
            "connectionZh": "与当前词属于同一词族。",
        })
    return rows


def build_report() -> str:
    words = load_jsonl(WORDS_PATH)
    word_map = {row["normalized"]: row for row in words}
    sentences = article_sentences(extract_article())
    line_hits, word_lines = word_hits(sentences, word_map)
    missing = sorted(set(word_lines) - set(EDITORIAL))
    if missing:
        raise RuntimeError(f"missing editorial content: {missing}")
    if set(SENTENCE_ZH) != set(line_hits):
        raise RuntimeError(f"sentence translation mismatch: translations={set(SENTENCE_ZH)}, hits={set(line_hits)}")
    if set(word_lines) != set(SENSE_OVERRIDES):
        raise RuntimeError("sense overrides do not match the article word set")

    out = [
        f"# {TITLE}：核心词学习数据样稿",
        "",
        "## 范围与状态",
        "",
        f"- 文章标题：**{TITLE}**",
        f"- 有效命中词：**{len(word_lines)}** 个；命中原句：**{len(line_hits)}** 个。",
        "- 已排除误匹配：人名 `Franks` 不作为单词 `frank`。",
        "- 不保存 PDF 页码。真实原句按 `content_lines` 去重，再通过 `content_line_words` 与单词关联。",
        "- 词形来自 ECDICT；基础例句、搭配、辨析与错误提示为编辑草稿。无可靠内容时数组或字符串保持为空。",
        "- 音标沿用并规范化现有词库主音标；`uk/us` 当前共用该值，仍列入词典编辑复核项。音频按既定 schema 保持空值。",
        "- 当前统一状态：`draft / pending_human_review`，不能直接标记为已人工审核或 published。",
        f"- 字段覆盖：构词说明 {len(word_lines)}/{len(word_lines)}，搭配 {len(EDITORIAL)}/{len(word_lines)}，语法模式 {len(GRAMMAR_PATTERNS)}/{len(word_lines)}，常见错误 {len(ERRORS)}/{len(word_lines)}，场景辨析 {len(RELATION_NOTES)}/{len(word_lines)}。后两项只在有学习价值时提供。",
        "",
        "## 数据结构",
        "",
        "```js",
        "{",
        "  words: { _id, word, normalized, type, phonetic, audio, senses, inflections },",
        "  word_learning_content: { wordId, morphology, derivatives, collocations, usageNotes, commonErrors, examProfile, provenance },",
        "  content_lines: { _id, articleTitle, text, translationZh, sourceType, tags, status },",
        "  content_line_words: { lineId, wordId, surfaceForms, matchType },",
        "  word_relations: { fromWordId, toWord, relationType, explanationZh, status }",
        "}",
        "```",
        "",
        "## 文章原句语料",
        "",
    ]
    for sentence_id, hits in line_hits.items():
        line_id = f"line_ants_{sentence_id:02d}"
        links = line_word_links(sentence_id, sentences[sentence_id - 1], hits, word_map)
        out.extend([
            f"### {line_id}", "",
            f"> {sentences[sentence_id - 1]}", "",
            SENTENCE_ZH[sentence_id], "",
            f"- `articleTitle`: `{TITLE}`",
            f"- `contentLineWords`: {compact_json(links)}",
            "- `sourceType`: `ielts_reading_pdf`",
            "- `status`: `source_verified_translation_draft`",
        ])
        if sentence_id in SOURCE_NOTES:
            out.append(f"- `sourceNote`: {SOURCE_NOTES[sentence_id]}")
        out.append("")

    out.extend(["## 核心词数据", ""])
    for word in sorted(word_lines):
        row = word_map[word]
        sense = (row.get("senses") or [{}])[0]
        phonetic = PHONETIC_FIXES.get(word, (row.get("phonetic") or {}).get("default", ""))
        if phonetic and not phonetic.startswith("/"):
            phonetic = f"/{phonetic}/"
        base_en, base_zh, collocations = EDITORIAL[word]
        line_ids = [f"line_ants_{value:02d}" for value in word_lines[word]]
        inflections = parse_inflections((row.get("ecdict") or {}).get("exchange", ""))
        morphology = MORPHOLOGY.get(word, "")
        derivatives = derivative_objects(DERIVATIVES.get(word, []))
        usage = USAGE.get(word, "")
        error = ERRORS.get(word)
        relations = RELATION_NOTES.get(word, [])
        override = SENSE_OVERRIDES[word]
        word_doc = {
            "_id": f"word_{word}", "word": word, "normalized": word, "type": "word",
            "phonetic": {"uk": phonetic, "us": phonetic, "default": phonetic},
            "audio": {"uk": "", "us": ""},
            "senses": [{
                "senseId": sense.get("senseId") or f"{word}_{override[0].replace('.', '')}_01",
                "pos": override[0],
                "translation": override[1],
                "definitionEn": override[2],
                "definitionZh": override[3],
            }],
            "inflections": inflections,
        }
        morph_segments = MORPH_SEGMENTS.get(word) or [{
            "form": word, "type": "base", "meaningZh": override[1],
            "noteZh": "缺少足够可靠且有学习价值的现代英语拆分依据，建议作为整体词学习。",
        }]
        morph_explanation = morphology or f"{word} 在本稿中按整体词处理，不强行拆分词根词缀。"
        collocation_rows = []
        for value in collocations:
            text, translation = value.rsplit(" ", 1)
            collocation_rows.append({"text": text, "translationZh": translation})
        grammar_rows = [{
            "pattern": GRAMMAR_PATTERNS[word], "exampleEn": base_en,
            "exampleZh": base_zh,
        }]
        learning = {
            "_id": f"word_{word}", "wordId": f"word_{word}",
            "articleTitle": TITLE, "articleSentenceIds": line_ids,
            "primaryExampleLineId": f"line_{word}_basic_001",
            "ieltsContextLineIds": line_ids,
            "morphology": {"segments": morph_segments, "explanationZh": morph_explanation, "relatedWords": derivatives},
            "collocations": collocation_rows,
            "grammarPatterns": grammar_rows,
            "derivatives": derivatives,
            "usageNotes": [usage] if usage else [],
            "commonErrors": ([{"wrong": error[0], "correct": error[1], "explanationZh": error[2]}] if error else []),
            "examProfile": {"skills": ["reading", "writing"], "topics": ["animal_behaviour", "education"], "priority": 3, "writingValue": 3},
            "provenance": source_status(),
        }
        content_lines = [{
            "_id": f"line_{word}_basic_001",
            "text": base_en, "translationZh": base_zh,
            "sourceType": "editorial", "level": "B2",
            "tags": ["ielts", "basic_example", "writing"], "status": "draft",
        }]
        for sentence_index in word_lines[word]:
            content_lines.append({
                "_id": f"line_ants_{sentence_index:02d}",
                "articleTitle": TITLE, "text": sentences[sentence_index - 1],
                "translationZh": SENTENCE_ZH[sentence_index], "sourceType": "ielts_reading_pdf",
                "level": "B2-C1", "tags": ["ielts", "reading", "animal_behaviour"],
                "status": "source_verified_translation_draft",
                **({"sourceNote": SOURCE_NOTES[sentence_index]} if sentence_index in SOURCE_NOTES else {}),
            })
        content_line_words = [{
            "_id": f"line_{word}_basic_001_word_{word}", "lineId": f"line_{word}_basic_001",
            "wordId": f"word_{word}", "surfaceForms": [word], "matchType": "editorial",
        }]
        for sentence_index in word_lines[word]:
            links = line_word_links(sentence_index, sentences[sentence_index - 1], line_hits[sentence_index], word_map)
            content_line_words.extend(link for link in links if link["wordId"] == f"word_{word}")
        relation_docs = []
        for note in relations:
            target, explanation = note.split(": ", 1)
            example_en, example_zh = RELATION_EXAMPLES[word]
            relation_docs.append({
                "fromWordId": f"word_{word}", "toWordId": f"word_{target}", "toWord": target,
                "relationType": "contrast", "explanationZh": explanation,
                "exampleEn": example_en, "exampleZh": example_zh,
                "status": "draft", "reviewStatus": "pending_human_review",
            })
        out.extend([
            f"### {word}", "",
            "```json", pretty_json(word_doc), "```", "",
            "**word_learning_content**", "", "```json", pretty_json(learning), "```", "",
            "**content_lines**", "", "```json", pretty_json(content_lines), "```", "",
            "**content_line_words**", "", "```json", pretty_json(content_line_words), "```", "",
            "**word_relations**", "", "```json", pretty_json(relation_docs), "```", "",
        ])

    out.extend([
        "## 审核清单", "",
        "- [x] 文章标题及英文原句与 PDF 文本核对。",
        "- [x] 排除 `Franks -> frank` 的专名误匹配。",
        "- [x] 词形变化仅采用 ECDICT 结构化字段，不推测不存在的变化。",
        "- [x] 构词、派生、辨析和常见错误允许为空。",
        "- [ ] 中文释义、编辑例句、搭配及辨析待英语编辑逐词审核。",
        "- [ ] 原文中文翻译待第二人复核。",
        "- [ ] 审核完成前不得把记录状态改为 `reviewed` 或 `published`。",
        "",
    ])
    return "\n".join(out)


def main() -> None:
    report = build_report()
    OUTPUT.write_text(report, encoding="utf-8")
    print(f"wrote {OUTPUT} ({report.count('### ')} records/sections)")


if __name__ == "__main__":
    main()
