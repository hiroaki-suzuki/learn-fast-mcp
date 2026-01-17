"""
MCPの3つのコンポーネント（Resources、Prompts、Tools）を呼び出すクライアント

このモジュールは、learn_server.pyに接続して各コンポーネントの使い方を示す:
- Resources: read_resource()でデータを読み取り
- Prompts: get_prompt()でテンプレートを取得
- Tools: call_tool()でツールを実行

使い方:
    1. 先にサーバーを起動: uv run python learn_server.py
    2. クライアントを実行: uv run python learn_client.py

learn_llm_client.pyとの違い:
    - このクライアント: 開発者が直接APIを呼び出す
    - LLMクライアント: LLMを介してコンポーネントを活用
"""

import asyncio

from fastmcp import Client
from mcp.types import TextContent


def get_text(content: object) -> str:
    """
    メッセージコンテンツからテキストを抽出する

    Promptの応答はTextContent型で返されるため、
    テキストを取り出すヘルパー関数。

    Args:
        content: メッセージコンテンツ（TextContentまたは他の型）

    Returns:
        テキスト文字列
    """
    if isinstance(content, TextContent):
        return content.text
    return str(content)


async def main():
    """
    learn_server.pyの全コンポーネントをデモする

    1. Resources: 静的・動的リソースの読み取り
    2. Prompts: 各種プロンプトテンプレートの取得
    3. Tools: ツールの呼び出し
    """
    # MCPサーバーに接続（HTTPエンドポイント）
    client = Client("http://localhost:8000/mcp")

    async with client:
        # =============================================================
        # 1. Resources の読み取り
        # =============================================================
        print("=" * 60)
        print("1. Resources（リソース）の読み取り")
        print("=" * 60)

        # --- 利用可能なリソース一覧を取得 ---
        print("\n--- 利用可能なリソース一覧 ---")
        resources = await client.list_resources()
        for r in resources:
            print(f"  URI: {r.uri}, Name: {r.name}")

        # --- リソーステンプレート一覧を取得 ---
        print("\n--- リソーステンプレート一覧 ---")
        templates = await client.list_resource_templates()
        for t in templates:
            print(f"  URI Template: {t.uriTemplate}, Name: {t.name}")

        # --- 静的リソースを読み取り ---
        print("\n--- config://app を読み取り ---")
        config = await client.read_resource("config://app")
        print(f"  結果: {config}")

        print("\n--- data://users を読み取り ---")
        users = await client.read_resource("data://users")
        print(f"  結果: {users}")

        # --- パラメータ付きリソースを読み取り ---
        print("\n--- user://u001 を読み取り（テンプレート使用） ---")
        user = await client.read_resource("user://u001")
        print(f"  結果: {user}")

        print("\n--- weather://tokyo/2024-01-15 を読み取り ---")
        weather = await client.read_resource("weather://tokyo/2024-01-15")
        print(f"  結果: {weather}")

        # =============================================================
        # 2. Prompts の取得
        # =============================================================
        print("\n" + "=" * 60)
        print("2. Prompts（プロンプト）の取得")
        print("=" * 60)

        # --- 利用可能なプロンプト一覧を取得 ---
        print("\n--- 利用可能なプロンプト一覧 ---")
        prompts = await client.list_prompts()
        for p in prompts:
            print(f"  Name: {p.name}, Description: {p.description}")

        # --- プロンプトを取得（引数付き） ---
        print("\n--- explain_topic プロンプトを取得 ---")
        prompt_result = await client.get_prompt("explain_topic", {"topic": "MCP"})
        print(f"  メッセージ数: {len(prompt_result.messages)}")
        for msg in prompt_result.messages:
            text = get_text(msg.content)
            print(f"  [{msg.role}]: {text[:100]}...")

        print("\n--- code_review プロンプトを取得 ---")
        prompt_result = await client.get_prompt(
            "code_review",
            {
                "language": "python",
                "code": "def add(a, b): return a + b",
                "focus": "可読性",
            },
        )
        for msg in prompt_result.messages:
            print(f"  [{msg.role}]:\n{get_text(msg.content)}")

        print("\n--- roleplay_teacher プロンプトを取得（複数メッセージ） ---")
        prompt_result = await client.get_prompt(
            "roleplay_teacher", {"subject": "数学"}
        )
        print(f"  メッセージ数: {len(prompt_result.messages)}")
        for msg in prompt_result.messages:
            print(f"  [{msg.role}]: {get_text(msg.content)}")

        # =============================================================
        # 3. Tools の呼び出し
        # =============================================================
        print("\n" + "=" * 60)
        print("3. Tools（ツール）の呼び出し")
        print("=" * 60)

        # --- 利用可能なツール一覧を取得 ---
        print("\n--- 利用可能なツール一覧 ---")
        tools = await client.list_tools()
        for t in tools:
            print(f"  Name: {t.name}, Description: {t.description}")

        # --- ツールを呼び出し ---
        print("\n--- search_users ツールを呼び出し ---")
        result = await client.call_tool("search_users", {"department": "開発"})
        print(f"  結果: {result}")


if __name__ == "__main__":
    asyncio.run(main())
