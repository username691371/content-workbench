"""
爆款素材工作台 - 一键运行入口
每天执行一次：抓取 → AI总结 → 生成HTML工作台

用法:
    python3.11 run.py          # 完整流程
    python3.11 run.py --fetch  # 仅抓取
    python3.11 run.py --build  # 仅生成HTML（用已有数据）

输出: 工作台.html （浏览器打开即可）
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    print("🔥 爆款素材工作台 · 每日运行")
    print(f"   模式: {mode}")
    print(f"   目录: {HERE}")
    print()

    if mode in ("all", "--fetch"):
        print("━━━ 步骤1: 抓取B站爆款内容 ━━━")
        import fetch_daily
        data = fetch_daily.run_daily_fetch()
        print()

    if mode in ("all", "--summarize"):
        print("━━━ 步骤2: AI总结 + 创作灵感 ━━━")
        import ai_summarize
        data = json_load(HERE / "daily_data.json")
        data = ai_summarize.process_all(data)
        json_save(HERE / "daily_data.json", data)
        print()

    if mode in ("all", "--build"):
        print("━━━ 步骤3: 生成HTML工作台 ━━━")
        import build_app
        data = json_load(HERE / "daily_data.json")
        html = build_app.generate_html(data)
        out = HERE / "工作台.html"
        out.write_text(html, encoding="utf-8")
        print(f"✅ 已生成: {out}  ({len(html)//1024}KB)")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✅ 全部完成！浏览器打开「工作台.html」即可查看。")
    print(f"   📅 日期: {data.get('date','')}")
    print(f"   📊 总内容: {data.get('total_videos',0)} 条")
    print(f"   💡 创作灵感: {len(data.get('daily_inspirations',[]))} 条")
    print(f"   📁 文件: {HERE / '工作台.html'}")


def json_load(p):
    import json
    return json.load(open(p, encoding="utf-8"))

def json_save(p, d):
    import json
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
