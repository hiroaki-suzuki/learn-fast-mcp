"""
基本的なFastMCPクライアントの実装例

このモジュールは、my_server.pyに接続してツールを直接呼び出すシンプルなクライアントを示す。
開発者がツール名を明示的に指定して呼び出す「プログラム的な」使い方の例。

使い方:
    1. 先にサーバーを起動: uv run python my_server.py
    2. クライアントを実行: uv run python my_client.py

my_server_llm_client.pyとの違い:
    - このクライアント: 開発者がツール名を直接指定
    - LLMクライアント: LLMが自然言語から適切なツールを自動選択
"""

import asyncio

from fastmcp import Client

# MCPサーバーへの接続設定
# HTTPトランスポートの場合、エンドポイントは /mcp
client = Client("http://localhost:8000/mcp")


async def main():
    """
    MCPサーバーに接続し、ツールを呼び出すデモを実行する

    async with でコンテキストマネージャーを使用することで、
    接続の確立とクリーンアップを自動的に行う。
    """
    async with client:
        # greetツールを呼び出し
        # 第1引数: ツール名
        # 第2引数: ツールに渡す引数（dict形式）
        greet_result = await client.call_tool("greet", {"name": "Gemini"})
        print(f"Result from greet: {greet_result}")

        # addツールを呼び出し
        add_result = await client.call_tool("add", {"a": 5, "b": 7})
        print(f"Result from add: {add_result}")


if __name__ == "__main__":
    asyncio.run(main())
