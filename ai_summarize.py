"""
爆款素材工作台 - AI总结模块
基于标题/描述关键词分析，生成摘要+核心观点+创作灵感。
不依赖外部API，纯本地规则引擎，保证脚本可独立运行。
"""
import json
import re
from pathlib import Path

# 痛点关键词 -> 主题分类
PAIN_POINTS = {
    "职场": ["工作", "上班", "老板", "同事", "职场", "辞职", "跳槽", "面试", "HR", "加班", "内卷", "996", "打工人", "就业", "找工作"],
    "学业": ["考研", "读博", "读研", "本科", "研究生", "导师", "申博", "高考", "选专业", "大学", "学历", "论文"],
    "情感": ["分手", "恋爱", "结婚", "离婚", "男友", "女友", "对象", "相亲", "爱情", "情感"],
    "认知": ["焦虑", "迷茫", "拧巴", "内耗", "摆烂", "上进", "改变", "成长", "自己", "人生", "意义", "压力", "疲惫"],
    "金钱": ["钱", "搞钱", "理财", "存款", "消费", "收入", "工资", "贫穷"],
    "人生": ["人生", "选择", "旷野", "结婚", "生孩子", "三十", "年龄", "方向"],
}

# 创作灵感模板（按主题）
INSPIRATION_TEMPLATES = {
    "职场": [
        "从'{title}'切入，做一期『打工人真实困境拆解』，采访3个不同行业的朋友",
        "提炼视频里的金句，改成『职场人清醒指南』系列图文",
        "反向操作：写『那些职场博主没告诉你的事』，补充被忽略的视角",
    ],
    "学业": [
        "以'{title}'为引，做『学历通胀时代的真实选择』深度分析",
        "拆解钱婧/张雪峰的择业逻辑，做一期『985vs双非 谁更惨』对比内容",
        "整理『读研/读博前必须知道的10件事』清单体内容",
    ],
    "情感": [
        "把'{title}'里的情感冲突改写成短故事/短剧脚本",
        "做一期『年轻人为什么不敢爱了』话题盘点，引用多个博主观点",
        "提炼金句做成情感治愈系图文卡片",
    ],
    "认知": [
        "从'{title}'提炼3个认知重塑点，做『反内耗手册』",
        "对比大冰的旷野vs钱婧的现实，做一期『年轻人该听谁的』思辨内容",
        "把视频核心观点改成『每天一个清醒小提醒』日更系列",
    ],
    "金钱": [
        "以'{title}'为切入点，做『普通人搞钱的真相』系列",
        "拆解博主谈钱逻辑，做成『金钱观重塑清单』",
        "对比不同博主的金钱观，做一期『谁的建议更适合你』",
    ],
    "人生": [
        "从'{title}'出发，做『20/25/30岁的人生分岔路』话题内容",
        "提炼大冰的『人生旷野』哲学，做治愈系长图文",
        "做一期『年轻人的人生选择题』互动式内容",
    ],
}

# 金句提取模式（匹配中文引号或冒号后的内容）
_QUOTE_CHARS = "\u201c\u201d\u300c\u300d\u300e\u300f"
QUOTE_PATTERNS = [
    r"[" + _QUOTE_CHARS + r"]([^" + _QUOTE_CHARS + r"]{6,40})[" + _QUOTE_CHARS + r"]",
    r"[::](.{8,30})$",
]


def classify_topic(video):
    """根据标题和描述判断主题分类"""
    text = (video.get("title", "") + " " + video.get("desc", "") + " " + video.get("tag", "")).lower()
    scores = {}
    for topic, keywords in PAIN_POINTS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[topic] = score
    if not scores:
        return "认知"
    return max(scores, key=scores.get)


def extract_keywords(video, topic):
    """从标题提取关键词"""
    title = video.get("title", "")
    # 去掉【】内容里的博主名
    clean = re.sub(r"【[^】]*】", "", title)
    # 提取核心短语
    keywords = PAIN_POINTS.get(topic, [])
    matched = [kw for kw in keywords if kw in title]
    return matched[:3] if matched else []


def generate_summary(video, topic):
    """生成50字摘要"""
    title = video.get("title", "")
    author = video.get("author", "")
    play = video.get("play", 0)
    like = video.get("like", 0)

    # 基于互动数据判断热度
    if play > 1000000:
        heat = "千万级爆款"
    elif play > 500000:
        heat = "百万级热门"
    elif play > 100000:
        heat = "十万级高赞"
    else:
        heat = "潜力内容"

    kws = extract_keywords(video, topic)
    kw_str = "、".join(kws) if kws else topic

    summary = f"{author}关于「{kw_str}」的{heat}。"
    if topic == "认知":
        summary += "直击年轻人内耗焦虑，提供认知重塑视角。"
    elif topic == "职场":
        summary += "拆解打工人真实困境，给出可执行建议。"
    elif topic == "学业":
        summary += "针对学历与择业焦虑，给出清醒建议。"
    elif topic == "情感":
        summary += "呈现情感冲突，引发共鸣与反思。"
    elif topic == "金钱":
        summary += "重塑金钱观，提供普通人视角。"
    else:
        summary += "引发人生方向思考，提供旷野视角。"

    return summary


def generate_inspiration(video, topic):
    """生成3个创作角度建议"""
    title = video.get("title", "")
    templates = INSPIRATION_TEMPLATES.get(topic, INSPIRATION_TEMPLATES["认知"])
    inspirations = [t.format(title=title) for t in templates]
    return inspirations


def extract_quote(video):
    """尝试从标题提取金句"""
    title = video.get("title", "")
    desc = video.get("desc", "")
    for pattern in QUOTE_PATTERNS:
        m = re.search(pattern, title + " " + desc)
        if m:
            return m.group(1)
    # 没匹配到，用标题截取
    clean = re.sub(r"【[^】]*】", "", title)
    if len(clean) > 10:
        return clean[:20]
    return clean


def process_all(data):
    """处理所有视频，生成总结"""
    content = data.get("content", [])
    print(f"[AI总结] 处理 {len(content)} 条视频...")

    for v in content:
        topic = classify_topic(v)
        v["ai_topic"] = topic
        v["ai_summary"] = generate_summary(v, topic)
        v["ai_quote"] = extract_quote(v)
        if v.get("blogger_weight", 3) <= 2:  # 核心博主+辅助博主才生成灵感
            v["ai_inspiration"] = generate_inspiration(v, topic)
        else:
            v["ai_inspiration"] = []

    # 生成今日创作灵感汇总（取核心博主top内容的灵感去重）
    inspirations = []
    for v in content:
        if v.get("blogger_weight", 3) <= 2 and v.get("ai_inspiration"):
            for insp in v["ai_inspiration"]:
                inspirations.append({
                    "source": v.get("target_blogger", ""),
                    "title": v.get("title", ""),
                    "inspiration": insp,
                    "topic": v.get("ai_topic", ""),
                })
    # 去重（按inspiration文本）
    seen = set()
    unique_insp = []
    for i in inspirations:
        if i["inspiration"] not in seen:
            seen.add(i["inspiration"])
            unique_insp.append(i)

    # 按主题分组
    by_topic = {}
    for i in unique_insp:
        t = i["topic"]
        by_topic.setdefault(t, []).append(i)

    data["daily_inspirations"] = unique_insp[:30]  # 最多30条
    data["inspirations_by_topic"] = {t: len(v) for t, v in by_topic.items()}

    # 统计
    topic_stats = {}
    for v in content:
        t = v.get("ai_topic", "其他")
        topic_stats[t] = topic_stats.get(t, 0) + 1
    data["topic_stats"] = topic_stats

    print(f"[完成] 生成 {len(unique_insp)} 条创作灵感，主题分布: {topic_stats}")
    return data


if __name__ == "__main__":
    data_path = Path(__file__).parent / "daily_data.json"
    data = json.load(open(data_path, encoding="utf-8"))
    data = process_all(data)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已更新 {data_path}")
