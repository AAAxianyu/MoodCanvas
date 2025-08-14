#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from typing import Any, Dict, List
import requests

BASE_URL = "http://127.0.0.1:8000"  # 如有需要可改成你的服务地址

def print_json(tag: str, data: Dict[str, Any]) -> None:
    print(f"\n=== {tag} ===")
    print(json.dumps(data, ensure_ascii=False, indent=2))

def extract_urls(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    out = []
    for item in payload.get("outputs", []):
        out.append({
            "remote_url": item.get("remote_url"),
            "local_url": item.get("local_url")
        })
    return out

def test_health() -> None:
    url = f"{BASE_URL}/api/v1/health"
    try:
        resp = requests.get(url, timeout=10)
        if resp.ok:
            print_json("HEALTH OK", resp.json())
        else:
            print(f"❌ HEALTH FAIL {resp.status_code}: {resp.text}", file=sys.stderr)
    except Exception as e:
        print(f"❌ HEALTH EXCEPTION: {e}", file=sys.stderr)

def test_i2i_single_case() -> None:
    """测试 /api/v1/images/edit，用 URL 方式（推荐）"""
    url = f"{BASE_URL}/api/v1/images/edit"
    data = {
        "image_url": "https://ark-project.tos-cn-beijing.volces.com/doc_image/seededit_i2i.jpeg",
        "prompt": "改成正方形状的泡泡",
        "guidance_scale": "5.5",
        "size": "adaptive",
        "save_local": "true"
    }
    resp = requests.post(url, data=data, timeout=180)
    if resp.ok:
        payload = resp.json()
        print_json("I2I /images/edit OK (single case)", payload)
        urls = extract_urls(payload)
        for i, u in enumerate(urls):
            print(f"[i2i #{i}] remote_url: {u.get('remote_url')}")
            if u.get("local_url"):
                print(f"[i2i #{i}]  local_url: {u.get('local_url')}")
    else:
        print(f"❌ I2I FAIL {resp.status_code}: {resp.text}", file=sys.stderr)

def test_t2i_single_case() -> None:
    """测试 /api/v1/images/generate，JSON 方式"""
    url = f"{BASE_URL}/api/v1/images/generate"
    payload = {
        "prompt": "胶片质感的清晨咖啡，暖光、浅景深",
        "size": "1024x1024",
        "guidance_scale": 7.0,
        "num_images": 1,
        "save_local": True
    }
    resp = requests.post(url, json=payload, timeout=300)
    if resp.ok:
        body = resp.json()
        print_json("T2I /images/generate OK (single case)", body)
        # t2i 返回 outputs 里每张图的 remote_url / local_url
        for i, item in enumerate(body.get("outputs", [])):
            print(f"[t2i #{i}] remote_url: {item.get('remote_url')}")
            if item.get("local_url"):
                print(f"[t2i #{i}]  local_url: {item.get('local_url')}")
    else:
        print(f"❌ T2I FAIL {resp.status_code}: {resp.text}", file=sys.stderr)

def main() -> None:
    print(">> 测试开始：", BASE_URL)
    test_health()
    test_i2i_single_case()
    test_t2i_single_case()
    print("\n>> 全部测试已完成。")

if __name__ == "__main__":
    main()
