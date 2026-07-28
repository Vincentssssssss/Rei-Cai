#!/usr/bin/env python3
"""Test LLM API connectivity. Run from project root: python3 check_llm.py"""

from src.config import get_llm_settings, get_llm_status
from src.http_client import configure_ssl, create_http_session, get_ssl_backend, get_ssl_verify


def main() -> None:
    configure_ssl()
    settings = get_llm_settings()
    status = get_llm_status()

    print("=== Rei-Cai LLM 诊断 ===")
    print(f"SSL 模式: {get_ssl_backend()}")
    print(f"SSL 验证: {get_ssl_verify()}")
    print(f"模型: {status['model']}")
    print(f"API Key: {'已设置' if status['api_key_set'] else '未设置'}")
    print(f"Base URL: {status['base_url']}")
    if status.get("hint"):
        print(f"提示: {status['hint']}")

    if not settings["api_key"] or not settings["base_url"]:
        print("\n配置不完整，请先设置 .env 后重试。")
        return

    print("\n正在测试 API 连接...")
    session = create_http_session()
    try:
        response = session.post(
            f"{settings['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings["model"],
                "messages": [{"role": "user", "content": "你好，请回复 OK"}],
                "max_tokens": 10,
            },
            timeout=30,
        )
        print(f"HTTP 状态: {response.status_code}")
        if response.ok:
            content = response.json()["choices"][0]["message"]["content"]
            print(f"API 响应: {content}")
            print("\n连接成功！")
        else:
            print(f"API 错误: {response.text[:500]}")
    except Exception as exc:
        print(f"\n连接失败: {exc.__class__.__name__}: {exc}")
        print("\n建议：")
        print("1. pip install -r requirements.txt")
        print("2. 确认 .env 中 OPENAI_BASE_URL 为百炼 llm- 开头地址")
        print("3. 关闭 VPN/代理后重试")
        print("4. 仍失败可临时测试：LLM_INSECURE_SSL=1 python3 check_llm.py")


if __name__ == "__main__":
    main()
