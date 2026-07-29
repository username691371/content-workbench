"""
爆款素材工作台 - 每日抓取脚本
抓取B站目标博主的高赞视频 + 平台热门，为创作提供灵感。
用法: python3.11 fetch_daily.py
输出: daily_data.json (供生成HTML)
"""
import requests
import json
import time
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Referer": "https://search.bilibili.com/all",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 目标博主清单 (name, bili_search_keyword, tags, weight)
# weight: 1=核心重点, 2=辅助补充
BLOGGERS = [
    ("钱婧", "钱婧", ["职场", "教授", "认知"], 1),
    ("大冰", "大冰 连麦", ["人生", "情感", "直播"], 1),
    ("张雪峰", "张雪峰", ["升学", "择业", "考研"], 2),
    ("半佛仙人", "半佛仙人", ["商业", "拆解", "职场"], 2),
    ("房琪", "房琪kiki", ["治愈", "文案", "成长"], 2),
    ("咸鱼梦想家", "咸鱼梦想家", ["职场", "共鸣", "打工人"], 2),
    ("董宇辉", "董宇辉 金句", ["文化", "感悟", "成长"], 2),
]

# 补充：职场困惑相关通用关键词搜索
TOPIC_KEYWORDS = [
    "年轻人 职场 迷茫",
    "打工人 治愈 爆款",
    "人生建议 年轻人",
    "工作 焦虑 缓解",
]


def _clean_title(title: str) -> str:
    """去掉B站搜索结果里的<em>高亮标签"""
    return re.sub(r"</?em[^>]*>", "", title)


def search_bilibili_videos(keyword: str, order: str = "click", page: int = 1, page_size: int = 20):
    """B站搜索视频接口。order: click(播放)/scores(综合)/pubdate(最新)
    带重试逻辑，应对412风控。"""
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "search_type": "video",
        "keyword": keyword,
        "order": order,
        "page": page,
        "page_size": page_size,
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=20)
            d = r.json()
            if d.get("code") == -412:
                # 风控，等待后重试
                wait = (attempt + 1) * 3
                print(f"  [风控412] {keyword} 第{attempt+1}次，等待{wait}s重试")
                time.sleep(wait)
                continue
            if d.get("code") != 0:
                print(f"  [搜索失败] {keyword}: code={d.get('code')} {d.get('message')}")
                return []
            results = d.get("data", {}).get("result", [])
            videos = []
            for v in results:
                videos.append({
                    "bvid": v.get("bvid"),
                    "aid": v.get("aid"),
                    "title": _clean_title(v.get("title", "")),
                    "play": v.get("play", 0),
                    "like": v.get("like", 0),
                    "coin": v.get("video_review", 0),
                    "favorite": v.get("favorites", 0),
                    "danmaku": v.get("video_review", 0),
                    "reply": v.get("review", 0),
                    "duration": v.get("duration"),
                    "pubdate": v.get("pubdate"),
                    "author": v.get("author", ""),
                    "mid": v.get("mid"),
                    "pic": "https:" + v.get("pic", "") if v.get("pic") and not v.get("pic", "").startswith("http") else v.get("pic", ""),
                    "desc": _clean_title(v.get("description", "")),
                    "tag": v.get("tag", ""),
                    "url": f"https://www.bilibili.com/video/{v.get('bvid')}",
                })
            return videos
        except Exception as e:
            print(f"  [搜索异常] {keyword} 第{attempt+1}次: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return []
    print(f"  [重试耗尽] {keyword} 风控3次仍失败")
    return []


def get_popular(ps: int = 20, pn: int = 1):
    """B站热门视频接口"""
    url = "https://api.bilibili.com/x/web-interface/popular"
    try:
        r = requests.get(url, params={"ps": ps, "pn": pn}, headers=HEADERS, timeout=20)
        d = r.json()
        if d.get("code") != 0:
            return []
        videos = []
        for v in d.get("data", {}).get("list", []):
            stat = v.get("stat", {})
            videos.append({
                "bvid": v.get("bvid"),
                "aid": v.get("aid"),
                "title": v.get("title", ""),
                "play": stat.get("view", 0),
                "like": stat.get("like", 0),
                "coin": stat.get("coin", 0),
                "favorite": stat.get("favorite", 0),
                "danmaku": stat.get("danmaku", 0),
                "reply": stat.get("reply", 0),
                "duration": v.get("duration"),
                "pubdate": v.get("pubdate"),
                "author": v.get("owner", {}).get("name", ""),
                "mid": v.get("owner", {}).get("mid"),
                "pic": v.get("pic", ""),
                "desc": v.get("desc", ""),
                "tag": "",
                "url": f"https://www.bilibili.com/video/{v.get('bvid')}",
            })
        return videos
    except Exception as e:
        print(f"  [热门异常]: {e}")
        return []


def _is_target_blogger(video, blogger_name, blogger_mid=None):
    """判断视频是否属于目标博主（按作者名匹配，宽松匹配）"""
    author = video.get("author", "")
    if blogger_name in author or author in blogger_name:
        return True
    # 钱婧特殊：作者名可能是"钱婧老师"
    if blogger_name == "钱婧" and "钱婧" in author:
        return True
    if blogger_name == "大冰" and ("大冰" in author or "大冰哥" in author):
        return True
    if blogger_name == "房琪" and ("房琪" in author):
        return True
    return False


def fetch_blogger_content(blogger_name, keyword, tags, weight, top_n=10):
    """抓取单个博主的高赞内容"""
    print(f"\n[抓取] {blogger_name} (权重={weight}) 关键词='{keyword}'")
    all_videos = []

    # 1. 按播放量搜索博主名
    videos = search_bilibili_videos(keyword, order="click", page_size=30)
    print(f"  搜索'{keyword}' 按播放量: {len(videos)}条")
    all_videos.extend(videos)
    time.sleep(1)

    # 2. 按综合排序再搜一次（拿近期热门）
    videos2 = search_bilibili_videos(keyword, order="scores", page_size=20)
    print(f"  搜索'{keyword}' 按综合: {len(videos2)}条")
    all_videos.extend(videos2)
    time.sleep(1)

    # 3. 标记是否为目标博主的内容
    for v in all_videos:
        v["target_blogger"] = blogger_name
        v["blogger_tags"] = tags
        v["blogger_weight"] = weight
        v["is_owner"] = _is_target_blogger(v, blogger_name)

    # 4. 去重(按bvid)
    seen = set()
    unique = []
    for v in all_videos:
        bid = v.get("bvid")
        if bid and bid not in seen:
            seen.add(bid)
            unique.append(v)

    # 5. 排序：博主本人内容优先，其次按播放量
    unique.sort(key=lambda x: (-int(x.get("is_owner")), -x.get("play", 0)))

    # 6. 取top N
    return unique[:top_n]


def fetch_topic_content(keyword, top_n=8):
    """抓取话题关键词的高赞内容"""
    print(f"\n[话题抓取] '{keyword}'")
    videos = search_bilibili_videos(keyword, order="click", page_size=20)
    print(f"  获得 {len(videos)} 条")
    for v in videos:
        v["target_blogger"] = "话题精选"
        v["blogger_tags"] = ["职场", "生活"]
        v["blogger_weight"] = 3
        v["is_owner"] = False
    time.sleep(1)
    return videos[:top_n]


def run_daily_fetch():
    """执行每日抓取"""
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz).strftime("%Y-%m-%d")
    print(f"========== 每日爆款抓取 {today} ==========")

    all_content = []

    # 1. 抓取各博主内容
    for name, kw, tags, weight in BLOGGERS:
        videos = fetch_blogger_content(name, kw, tags, weight, top_n=10 if weight == 1 else 6)
        all_content.extend(videos)

    # 2. 抓取话题关键词
    for topic_kw in TOPIC_KEYWORDS:
        videos = fetch_topic_content(topic_kw, top_n=5)
        all_content.extend(videos)

    # 3. 抓取B站全站热门(补充)
    print("\n[抓取B站全站热门]")
    popular = get_popular(ps=20, pn=1)
    print(f"  获得 {len(popular)} 条")
    for v in popular:
        v["target_blogger"] = "B站热门"
        v["blogger_tags"] = ["热门", "全站"]
        v["blogger_weight"] = 4
        v["is_owner"] = False
    all_content.extend(popular)

    # 4. 全局去重
    seen = set()
    unique = []
    for v in all_content:
        bid = v.get("bvid")
        if bid and bid not in seen:
            seen.add(bid)
            unique.append(v)

    # 5. 计算互动分(用于排序)
    for v in unique:
        play = v.get("play", 0) or 0
        like = v.get("like", 0) or 0
        coin = v.get("coin", 0) or 0
        fav = v.get("favorite", 0) or 0
        reply = v.get("reply", 0) or 0
        v["interact_score"] = like + coin * 2 + fav * 1.5 + reply * 3
        v["hot_score"] = play + v["interact_score"] * 10

    # 6. 按博主分组统计
    by_blogger = {}
    for v in unique:
        b = v.get("target_blogger", "其他")
        by_blogger.setdefault(b, []).append(v)

    # 7. 每组内按播放量排序
    for b in by_blogger:
        by_blogger[b].sort(key=lambda x: -x.get("play", 0))

    result = {
        "date": today,
        "fetched_at": datetime.now(tz).isoformat(),
        "total_videos": len(unique),
        "bloggers": [b[0] for b in BLOGGERS],
        "content": unique,
        "by_blogger": {b: len(v) for b, v in by_blogger.items()},
    }

    out_path = Path(__file__).parent / "daily_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n[完成] 共抓取 {len(unique)} 条，已保存到 {out_path}")
    print(f"  博主分布: {by_blogger.keys()}")
    for b, vids in by_blogger.items():
        if vids:
            top = vids[0]
            print(f"  [{b}] top: play={top.get('play')} {top.get('title','')[:35]}")
    return result


if __name__ == "__main__":
    run_daily_fetch()
