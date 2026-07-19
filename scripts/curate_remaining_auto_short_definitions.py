#!/usr/bin/env python3
"""Curate remaining auto-generated IELTS short definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path("/Users/chengtingwei/WeChatProjects/miniprogram-3")
DATA_DIR = ROOT / "tmp/cloud_import_ielts_content_words"
LEARNING_PATH = DATA_DIR / "word_learning_content.json"


RAW = """
hypothesis\tA proposed explanation that can be tested or discussed.\t可以被检验或讨论的假设性解释。
project\tA planned piece of work with a clear aim.\t有明确目标的计划性工作或项目。
species\tA group of similar living things that can reproduce together.\t能够相互繁殖的一类相似生物。
presence\tThe fact that someone or something is in a place or exists.\t某人或某物在场或存在的事实。
predator\tAn animal that hunts and eats other animals.\t捕猎并吃其他动物的动物。
flee\tTo leave quickly because of danger or fear.\t因危险或恐惧而迅速逃离。
naive\tToo simple or trusting because of limited experience.\t因经验不足而显得单纯或轻信的。
location\tA particular place or position.\t特定的地点或位置。
throughout\tIn every part of a place or during all of a period.\t遍及某地各处；贯穿整个时期。
challenge\tA difficult task or problem that tests ability.\t考验能力的困难任务或问题。
ignorant\tLacking knowledge or information about something.\t对某事缺乏知识或信息的。
suggest\tTo mention an idea or show that something may be true.\t提出想法，或表明某事可能属实。
routine\tA regular way of doing things.\t固定或常规的做事方式。
controversy\tPublic disagreement about an issue.\t围绕某个问题的公开争议。
indicate\tTo show, point to, or suggest something.\t显示、指出或暗示某事。
evolve\tTo develop gradually over time.\t随着时间逐渐发展或演变。
determine\tTo find out, decide, or strongly influence something.\t查明、决定或强烈影响某事。
maintain\tTo keep something going, or state firmly that it is true.\t维持某事，或坚称某事属实。
bark\tThe outer covering of a tree trunk or branch.\t树干或树枝外层的树皮。
necessarily\tUsed to show that something must be true or must happen.\t表示某事必然为真或必然发生。
inspiration\tA person, idea, or experience that gives you new thoughts.\t激发新想法的人、事物或经历。
anecdote\tA short story about a real event or person.\t关于真实事件或人物的简短故事。
epidemic\tA disease or problem that spreads quickly among many people.\t在许多人中迅速传播的疾病或问题。
recover\tTo get better, return, or get something back.\t恢复；返回；重新获得。
endure\tTo suffer something difficult without giving up.\t忍受困难而不放弃。
wealthy\tHaving a lot of money or valuable possessions.\t拥有大量金钱或财产的。
industrialise\tTo develop industries in a country or area.\t使国家或地区发展工业。
annual\tHappening once every year or lasting for one year.\t每年发生一次的；持续一年的。
distinguish\tTo recognize or show the difference between things.\t识别或显示事物之间的差异。
speculate\tTo guess or form an opinion without certain evidence.\t在没有确凿证据时推测或猜想。
organism\tA living thing such as a plant, animal, or microbe.\t植物、动物或微生物等生物体。
abundance\tA large amount or plentiful supply of something.\t大量；充足供应。
workforce\tAll the people who work in a company, industry, or country.\t公司、行业或国家中的全体劳动力。
academic\tRelated to education, study, or research.\t与教育、学习或研究有关的。
average\tA typical amount, level, or result calculated from several values.\t由多个数值计算出的平均或典型水平。
climate\tThe usual weather conditions of a place over a long period.\t某地长期的通常天气状况。
data\tFacts or information used for analysis or decisions.\t用于分析或决策的事实或信息。
curious\tWanting to know more, or unusual in an interesting way.\t好奇的；不寻常而有趣的。
impoverished\tVery poor or lacking necessary resources.\t非常贫穷的；缺乏必要资源的。
figure\tA number, amount, shape, or important person.\t数字、数量、形状或重要人物。
minimum\tThe smallest amount, level, or degree allowed or possible.\t允许或可能的最小数量、水平或程度。
limited\tSmall in amount, range, or ability.\t数量、范围或能力有限的。
render\tTo make someone or something become a particular state.\t使某人或某物变成某种状态。
material\tA substance used to make things, or information used for work.\t用于制造的材料，或用于工作的资料。
ensure\tTo make sure that something happens or is true.\t确保某事发生或属实。
spring\tThe season after winter, or a place where water comes from the ground.\t春季；泉水。
seasonal\tHappening or changing according to the season.\t随季节发生或变化的。
argument\tA reasoned statement or disagreement about something.\t论点；争论。
tropical\tRelated to hot regions near the equator.\t与赤道附近热带地区有关的。
potential\tPossible or able to develop in the future.\t可能的；有发展潜力的。
crush\tTo press something so hard that it breaks or changes shape.\t压碎；压坏；挤压变形。
complicated\tDifficult to understand because of many connected parts.\t因包含许多关联部分而复杂难懂的。
combine\tTo join two or more things together.\t把两个或多个事物结合起来。
institution\tAn established organization, especially for education or public service.\t机构，尤指教育或公共服务机构。
access\tThe ability or right to enter, use, or obtain something.\t进入、使用或获得某物的能力或权利。
effect\tA change, result, or influence caused by something.\t由某事引起的变化、结果或影响。
form\tThe type, shape, structure, or way something exists.\t形式、形状、结构或存在方式。
improvement\tA change that makes something better.\t使某事变得更好的改变。
govern\tTo control, rule, or strongly influence something.\t管理、统治或强烈影响某事。
environment\tThe conditions and surroundings in which something exists.\t某事物存在的条件和周围环境。
beyond\tFurther than a place, time, level, or limit.\t超过某个地点、时间、水平或限制。
gear\tEquipment, or to prepare something for a particular purpose.\t设备；使某事适合特定目的。
improve\tTo make or become better.\t使变好；变得更好。
agriculture\tThe practice or industry of farming.\t农业生产或农业产业。
cite\tTo mention something as evidence or an example.\t引用或提及某事作为证据或例子。
region\tA particular area of a country, place, or body.\t国家、地点或身体中的特定区域。
provided\tGiven or supplied; also used to mean if.\t被提供的；也可表示“如果”。
irrigation\tSupplying land or crops with water.\t给土地或作物供水灌溉。
productivity\tThe rate at which work or goods are produced.\t工作或产品产出的效率。
develop\tTo grow, improve, or create something over time.\t逐渐成长、改进或创造。
poverty\tThe state of being very poor.\t贫穷状态。
zoological\tRelated to animals or the study of animals.\t与动物或动物学有关的。
point\tAn idea, detail, place, or exact moment.\t观点、细节、地点或具体时刻。
livestock\tFarm animals kept for use or profit.\t为使用或盈利而饲养的牲畜。
motive\tA reason for doing something.\t做某事的动机或原因。
striking\tVery noticeable or impressive.\t非常醒目或令人印象深刻的。
correlation\tA connection in which two things change or relate together.\t两个事物共同变化或相互关联的关系。
geographical\tRelated to geography or a particular place.\t与地理或特定地点有关的。
conclude\tTo finish something or decide after considering evidence.\t结束某事，或根据证据得出结论。
hemisphere\tOne half of the Earth or of a sphere.\t地球或球体的一半。
maternal\tRelated to a mother.\t与母亲有关的。
context\tThe situation or information around something that helps explain it.\t有助于解释某事的背景或语境。
examine\tTo look at or study something carefully.\t仔细查看或研究某事。
appear\tTo become visible or seem to be true.\t出现；似乎。
agenda\tA list or plan of things to be discussed or done.\t待讨论或待处理事项的清单或计划。
emphasize\tTo show that something is especially important.\t强调某事特别重要。
individual\tA single person or thing, considered separately.\t单独看待的一个人或事物。
emerge\tTo appear, become known, or come out.\t出现；显露；被知晓。
acceptable\tGood enough to be allowed or approved.\t足够好而可被接受或认可的。
parental\tRelated to parents.\t与父母有关的。
incident\tA single event, especially an unusual or unpleasant one.\t单个事件，尤指异常或不愉快的事件。
verbal\tRelated to words or spoken language.\t与词语或口头语言有关的。
combination\tA mixture or joining of two or more things.\t两个或多个事物的组合或混合。
contemporary\tBelonging to the present time or the same period.\t属于当代或同一时期的。
approach\tA way of dealing with a problem or situation.\t处理问题或情况的方法。
viewpoint\tA way of thinking about a subject.\t看待某个问题的观点。
ultimately\tIn the end, after everything is considered.\t最终；归根结底。
comply\tTo obey a rule, request, or standard.\t遵守规则、要求或标准。
setting\tThe place, time, or situation in which something happens.\t事情发生的地点、时间或情境。
expectation\tA belief about what is likely to happen.\t对可能发生之事的预期。
upset\tTo make someone unhappy, or disturb a normal state.\t使不快；扰乱正常状态。
motivate\tTo give someone a reason or desire to act.\t给予某人行动的理由或动力。
assume\tTo think something is true without definite proof.\t在没有确证时认为某事为真。
essential\tVery important or necessary.\t非常重要或必要的。
encourage\tTo give support, confidence, or hope.\t给予支持、信心或希望。
floral\tRelated to flowers or decorated with flowers.\t与花有关的；有花卉装饰的。
emit\tTo send out light, heat, sound, gas, or smell.\t发出光、热、声音、气体或气味。
molecule\tThe smallest unit of a substance that keeps its chemical nature.\t保持物质化学性质的最小单位。
detect\tTo discover or notice something that is not obvious.\t发现或察觉不明显的事物。
chemical\tRelated to chemistry or substances produced by chemical processes.\t与化学或化学物质有关的。
trunk\tThe main stem of a tree, or the main part of a body or car.\t树干；身体或汽车的主体部分。
pine\tA type of evergreen tree with needle-like leaves.\t一种针叶常绿树。
burrow\tTo dig a hole or move through by digging.\t挖洞；钻行。
backbone\tThe spine, or the main support of a system.\t脊柱；系统的主要支撑。
cover\tTo place something over or across something else.\t覆盖某物。
deter\tTo discourage or prevent someone from doing something.\t阻止或威慑某人做某事。
nocturnal\tActive at night.\t夜间活动的。
blend\tTo mix things smoothly together.\t把事物平滑地混合在一起。
repel\tTo drive something away or resist it.\t驱赶；抵制。
herbivore\tAn animal that eats plants.\t以植物为食的动物。
induce\tTo cause something to happen.\t引起或导致某事发生。
predatory\tHunting other animals, or exploiting others.\t捕食性的；剥削性的。
prey\tAn animal hunted by another animal.\t被其他动物捕食的动物。
feed\tTo give food to someone or something.\t给某人或某物提供食物。
similarly\tIn a similar way.\t以相似的方式。
onslaught\tA strong and sudden attack or pressure.\t猛烈而突然的攻击或压力。
currency\tMoney used in a particular country.\t某个国家使用的货币。
compound\tA substance or thing made of two or more parts.\t由两个或多个部分组成的物质或事物。
antiseptic\tPreventing infection by killing harmful microorganisms.\t通过杀死有害微生物来防止感染的。
reward\tSomething given for good work or behavior.\t因良好表现或行为而给予的奖励。
impact\tA strong effect or the force of one thing hitting another.\t强烈影响；撞击力。
rely\tTo depend on someone or something.\t依赖某人或某物。
cherry\tA small round red fruit with a stone inside.\t一种小而圆、内有硬核的红色水果。
efficiency\tThe ability to do something with little waste.\t以较少浪费完成事情的能力或效率。
require\tTo need or officially demand something.\t需要或正式要求某事。
optimum\tThe best or most suitable level or condition.\t最佳或最合适的水平或状态。
decrease\tTo become or make something smaller.\t减少；使变小。
ability\tThe power or skill to do something.\t做某事的能力或技能。
considerable\tLarge enough to be important or noticeable.\t相当大的；值得注意的。
particularly\tEspecially or more than usual.\t特别地；尤其。
introduce\tTo bring something into use or make someone known.\t引入；介绍。
origin\tThe point or cause from which something begins.\t起源；开端。
enhance\tTo improve or increase the quality or value of something.\t提高或增强某物的质量或价值。
inherent\tExisting as a natural or essential part of something.\t作为某物自然或基本部分而存在的。
limitation\tA restriction or weakness that limits what is possible.\t限制；局限。
artificial\tMade by people rather than occurring naturally.\t人造的；非自然产生的。
convey\tTo communicate an idea or move something from one place to another.\t传达；运送。
characteristic\tA typical feature or quality of someone or something.\t典型特征或品质。
accomplish\tTo succeed in doing or completing something.\t成功完成某事。
frequency\tHow often something happens.\t某事发生的频率。
unfortunately\tUsed to say that something is unlucky or disappointing.\t表示某事不幸或令人失望。
traditional\tFollowing customs or ways that have existed for a long time.\t遵循长期存在的传统或方式的。
desirable\tWorth having or wanting.\t值得拥有或想要的。
target\tA goal, object, or person that an action is aimed at.\t行动瞄准的目标、对象或人。
technical\tRelated to practical skills, methods, or specialized knowledge.\t与实用技能、方法或专业知识有关的。
threshold\tThe point at which something begins or changes.\t某事开始或发生变化的临界点。
transportation\tThe movement of people or goods from one place to another.\t人员或货物从一地到另一地的运输。
plastic\tA man-made material, or able to be shaped.\t塑料；可塑的。
supersede\tTo replace something older or less useful.\t取代较旧或较不适用的事物。
creation\tThe act or result of making something new.\t创造行为或创造出的事物。
decline\tTo become smaller, weaker, or less important.\t下降；衰退；变弱。
derive\tTo come from a particular source.\t来源于某个特定来源。
cast\tThe actors in a play or film, or to throw something.\t戏剧或电影的演员阵容；投掷。
mould\tTo shape a soft substance or influence development.\t塑造软物质；影响发展。
moderate\tAverage in amount, or to make something less extreme.\t适中的；使不那么极端。
household\tAll the people living together in one home.\t同住一家的所有人。
electrical\tRelated to electricity.\t与电有关的。
component\tOne part of a larger whole or system.\t整体或系统中的组成部分。
discover\tTo find or learn something for the first time.\t首次发现或得知某事。
pressure\tForce, stress, or strong influence on someone or something.\t压力；压强；强烈影响。
suitable\tRight or appropriate for a particular purpose.\t适合特定目的的。
substitute\tTo use one thing or person instead of another.\t用一物或一人替代另一物或另一人。
friction\tResistance between surfaces, or disagreement between people.\t表面间的摩擦；人与人之间的摩擦或分歧。
domestic\tRelated to the home or to one country.\t与家庭或本国有关的。
appliance\tA machine or device used in the home or for a task.\t家用或工作用机器设备。
expand\tTo become or make something larger.\t扩大；扩展。
insulation\tMaterial or protection that prevents heat, sound, or electricity passing through.\t防止热、声音或电通过的隔离材料或保护层。
crude\tSimple, rough, or not yet processed.\t粗糙的；未经加工的。
force\tStrength, power, or influence that causes change.\t力量；作用力；影响力。
treatment\tThe way someone or something is dealt with or cared for.\t对待、处理或治疗的方式。
incorporate\tTo include something as part of a whole.\t把某物纳入整体。
structure\tThe way parts of something are arranged.\t事物各部分的组织结构。
decay\tTo gradually become worse, weaker, or rotten.\t逐渐衰败、变弱或腐烂。
disintegrate\tTo break into small parts or stop holding together.\t分解；瓦解。
surround\tTo be or go all around something.\t围绕某物。
"""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> None:
    curated: dict[str, tuple[str, str]] = {}
    for line in RAW.strip().splitlines():
        word, en, zh = line.split("\t")
        curated[word] = (en, zh)

    rows = read_jsonl(LEARNING_PATH)
    changed = []
    remaining = []
    for row in rows:
        word = str(row.get("normalized") or row.get("word") or "").lower()
        if row.get("shortDefinitionStatus") != "auto_from_english_definition_pending_review":
            continue
        if word not in curated:
            remaining.append(word)
            continue
        en, zh = curated[word]
        row["shortDefinitionEn"] = en
        row["shortDefinitionZh"] = zh
        row["shortDefinitionStatus"] = "curated_manual_short_definition"
        row["shortDefinitionReview"] = {
            "status": "reviewed",
            "reviewMethod": "manual_batch_core_sense_rewrite",
        }
        provenance = row.setdefault("provenance", {})
        if isinstance(provenance, dict):
            provenance["reviewStatus"] = "reviewed"
            provenance["shortDefinitionZhSource"] = "manual_batch_core_sense_rewrite"
        changed.append(word)

    write_jsonl(LEARNING_PATH, rows)
    print(json.dumps({"changed": len(changed), "remaining": remaining, "sample": changed[:20]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
