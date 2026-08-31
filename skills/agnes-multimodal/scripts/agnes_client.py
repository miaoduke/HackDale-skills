#!/usr/bin/env python3
"""
Agnes AI Multimodal Client
支持图像生成和图片生成、视频生成的简单 CLI 客户端。
自动轮换 API Key。
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
import random
from pathlib import Path


def get_keys():
    """Read API keys from the environment (secure; no on-disk key file is shipped)."""
    key = os.environ.get("AGNES_API_KEY", "").strip()
    return [key] if key else []


BASE_URL = "https://apihub.agnes-ai.com/v1"


def _call_api(endpoint, payload, method="POST"):
    """通用 API 调用函数"""
    keys = get_keys()
    if not keys:
        print("错误：未配置 API Key。请设置 AGNES_API_KEY 环境变量。")
        sys.exit(1)

    # 随机选择 Key 实现轮换
    api_key = random.choice(keys)
    url = f"{BASE_URL}{endpoint}"

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"API 请求失败 (HTTP {e.code}): {e.read().decode('utf-8')}")
        sys.exit(1)
    except Exception as e:
        print(f"请求出错: {e}")
        sys.exit(1)


def generate_image(prompt, size="1024x1024", n=1, output_dir="."):
    """生成图像"""
    print(f"正在生成图像: {prompt[:50]}...")
    payload = {
        "model": "agnes-image-2.1-flash",
        "prompt": prompt,
        "size": size,
        "n": n,
    }
    result = _call_api("/images/generations", payload)

    images = result.get("data", [])
    saved_paths = []
    for i, img in enumerate(images):
        img_url = img.get("url")
        if img_url:
            # 下载图片
            img_name = f"agnes_img_{int(time.time())}_{i}.png"
            img_path = os.path.join(output_dir, img_name)
            urllib.request.urlretrieve(img_url, img_path)
            saved_paths.append(img_path)
            print(f"已保存: {img_path}")
        elif img.get("b64_json"):
            img_name = f"agnes_img_{int(time.time())}_{i}.png"
            img_path = os.path.join(output_dir, img_name)
            import base64
            with open(img_path, "wb") as f:
                f.write(base64.b64decode(img["b64_json"]))
            saved_paths.append(img_path)
            print(f"已保存: {img_path}")

    return saved_paths


def generate_video(prompt, size="1280x768", duration=5, fps=24, interval=5, max_wait=600):
    """生成视频（异步轮询）"""
    print(f"正在创建视频任务: {prompt[:50]}...")
    payload = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "size": size,
        "duration_seconds": duration,
        "fps": fps,
    }

    result = _call_api("/videos", payload)
    task_id = result.get("task_id") or result.get("id")
    video_id = result.get("video_id")
    if not task_id:
        print("错误：未获取到 task_id")
        sys.exit(1)

    print(f"任务已创建: task_id={task_id}, video_id={video_id}")
    print(f"开始轮询结果（每{interval}秒一次）...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            keys = get_keys()
            api_key = random.choice(keys)
            # 使用推荐端点: GET /agnesapi?video_id=<VIDEO_ID>
            poll_url = f"https://apihub.agnes-ai.com/agnesapi?video_id={video_id}"
            req = urllib.request.Request(
                poll_url,
                headers={"Authorization": f"Bearer {api_key}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = json.loads(resp.read().decode("utf-8"))
                st = status.get("status", "")
                elapsed_min = int((time.time() - start_time) / 60)
                elapsed_sec = int((time.time() - start_time) % 60)
                print(f"  状态: {st} ({elapsed_min}分{elapsed_sec}秒)")
                if st == "completed":
                    video_url = status.get("remixed_from_video_id") or status.get("url") or status.get("video_url")
                    if video_url:
                        video_name = f"agnes_vid_{int(time.time())}.mp4"
                        urllib.request.urlretrieve(video_url, video_name)
                        print(f"视频已保存: {video_name}")
                        return [video_name]
                    else:
                        print("错误：视频生成完成但未找到视频 URL")
                        print(json.dumps(status, indent=2))
                        return []
                elif st == "failed":
                    print(f"视频生成失败: {status.get('error', '未知错误')}")
                    return []
        except Exception as e:
            print(f"轮询出错: {e}")
            pass
        time.sleep(interval)

    print(f"超时（{max_wait}s），任务可能还在进行中")
    return []


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  python agnes_client.py image '<prompt>' [size] [output_dir]")
        print("  python agnes_client.py video '<prompt>' [size] [duration] [fps] [interval]")
        sys.exit(1)

    cmd = sys.argv[1]
    prompt = sys.argv[2]

    if cmd == "image":
        size = sys.argv[3] if len(sys.argv) > 3 else "1024x1024"
        output_dir = sys.argv[4] if len(sys.argv) > 4 else "."
        generate_image(prompt, size, output_dir=output_dir)
    elif cmd == "video":
        size = sys.argv[3] if len(sys.argv) > 3 else "1280x768"
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 5
        fps = int(sys.argv[5]) if len(sys.argv) > 5 else 24
        interval = int(sys.argv[6]) if len(sys.argv) > 6 else 5
        generate_video(prompt, size, duration, fps, interval=interval)
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
