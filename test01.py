"""
test01.py — 验证三个 API 是否正常调用
1. DashScope (qwen-plus)
2. 和风天气 (QWeather)
3. 高德地图 (Amap)
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
load_dotenv()

DASHSCOPE_KEY = os.getenv("DASHSCOPE_API_KEY")
QWEATHER_KEY = os.getenv("QWEATHER_API_KEY")
QWEATHER_HOST = os.getenv("QWEATHER_API_HOST")
AMAP_KEY = os.getenv("AMAP_API_KEY")

SEPARATOR = "-" * 50


def test_dashscope():
    """测试 DashScope — qwen-plus 文本生成"""
    print(SEPARATOR)
    print("[1/3] 测试 DashScope (qwen-plus)...")
    if not DASHSCOPE_KEY:
        print("  SKIP: DASHSCOPE_API_KEY 未配置")
        return False

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "user", "content": "用一句话介绍杭州"}
        ],
        "temperature": 0.5,
        "max_tokens": 200,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"  状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            print(f"  模型回复: {text}")
            print("  ✅ DashScope 测试通过")
            return True
        else:
            print(f"  错误: {resp.text[:300]}")
            print("  ❌ DashScope 测试失败")
            return False
    except Exception as e:
        print(f"  异常: {e}")
        print("  ❌ DashScope 测试失败")
        return False


def test_qweather():
    """测试和风天气 — 实时天气（需专属 API Host）"""
    print(SEPARATOR)
    print("[2/3] 测试和风天气 (QWeather)...")
    if not QWEATHER_KEY:
        print("  SKIP: QWEATHER_API_KEY 未配置")
        return False
    if not QWEATHER_HOST or "你的专属" in QWEATHER_HOST:
        print("  SKIP: QWEATHER_API_HOST 未配置，请在 .env 中填入你的专属 API Host")
        print("  获取方式：https://console.qweather.com → 设置 → API Host")
        return False

    # 使用专属 Host
    url = f"https://{QWEATHER_HOST}/v7/weather/now"
    params = {
        "key": QWEATHER_KEY,
        "location": "101010100",  # 北京
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"  状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            now = data.get("now", {})
            print(f"  北京当前: {now.get('temp', '?')}°C, "
                  f"{now.get('text', '?')}, "
                  f"体感{now.get('feelsLike', '?')}°C, "
                  f"{now.get('windDir', '?')}风{now.get('windScale', '?')}级")
            print("  ✅ 和风天气测试通过")
            return True
        else:
            print(f"  错误: {resp.text[:300]}")
            print("  ❌ 和风天气测试失败")
            return False
    except Exception as e:
        print(f"  异常: {e}")
        print("  ❌ 和风天气测试失败")
        return False


def test_amap():
    """测试高德地图 — POI 搜索"""
    print(SEPARATOR)
    print("[3/3] 测试高德地图 (Amap)...")
    if not AMAP_KEY:
        print("  SKIP: AMAP_API_KEY 未配置")
        return False

    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": AMAP_KEY,
        "keywords": "景点",
        "city": "杭州",
        "offset": 3,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        print(f"  状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "1":
                pois = data.get("pois", [])
                print(f"  杭州景点搜索结果 ({len(pois)} 条):")
                for poi in pois:
                    print(f"    - {poi.get('name', '?')} "
                          f"({poi.get('type', '?')}), "
                          f"地址: {poi.get('address', '?')[:30]}")
                print("  ✅ 高德地图测试通过")
                return True
            else:
                print(f"  API 返回错误: {data.get('info', '?')}")
                print("  ❌ 高德地图测试失败")
                return False
        else:
            print(f"  错误: {resp.text[:300]}")
            print("  ❌ 高德地图测试失败")
            return False
    except Exception as e:
        print(f"  异常: {e}")
        print("  ❌ 高德地图测试失败")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("API 连通性测试")
    print("=" * 50)

    r1 = test_dashscope()
    r2 = test_qweather()
    r3 = test_amap()

    print(SEPARATOR)
    print("\n测试汇总:")
    print(f"  DashScope:  {'✅ 通过' if r1 else '❌ 失败'}")
    print(f"  和风天气:  {'✅ 通过' if r2 else '❌ 失败'}")
    print(f"  高德地图:  {'✅ 通过' if r3 else '❌ 失败'}")

    if r1 and r2 and r3:
        print("\n🎉 全部通过，可以开始开发 agent_demo04 了！")
    else:
        print("\n⚠️ 部分 API 未通过，请检查配置。")
