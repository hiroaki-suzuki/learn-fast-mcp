"""
learn_server.py用のLLMクライアント

このモジュールは、MCPの3つのコンポーネントをLLM経由で活用する方法を示す:
1. Tools: LLMが自然言語から適切なツールを自動選択して実行
2. Resources: MCPからデータを取得し、LLMのコンテキストとして活用
3. Prompts: MCPからプロンプトテンプレートを取得し、LLMに送信

各コンポーネントの役割と制御:
    - Tools: LLMが呼び出しを決定（LLM制御）
    - Resources: アプリケーションがデータを提供（アプリケーション制御）
    - Prompts: ユーザーが明示的に選択（ユーザー制御）

実行前に:
    1. GEMINI_API_KEY環境変数を設定（.env.example参照）
    2. サーバーを起動: uv run python learn_server.py
    3. クライアントを実行: uv run python learn_llm_client.py
"""

import asyncio

from fastmcp import Client
from google import genai
from google.genai import types


async def demo_tools(mcp_client: Client, gemini_client: genai.Client):
    """
    Toolsのデモ: LLMが自然言語から適切なツールを選択して実行

    MCPからツール一覧を取得し、Gemini Function Calling形式に変換。
    ユーザーの自然言語リクエストをLLMに送信し、
    LLMが選択したツールをMCPサーバーで実行する。

    Args:
        mcp_client: MCPクライアント（接続済み）
        gemini_client: Geminiクライアント
    """
    print("\n" + "=" * 60)
    print("1. TOOLS: LLMによる自動ツール選択")
    print("=" * 60)

    # MCPからツール一覧を取得
    mcp_tools = await mcp_client.list_tools()
    print("\n利用可能なツール:")
    for tool in mcp_tools:
        print(f"  - {tool.name}: {tool.description}")

    # Gemini用に変換
    gemini_functions = []
    for tool in mcp_tools:
        gemini_functions.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
        )
    gemini_tools = types.Tool(function_declarations=gemini_functions)

    # 自然言語でリクエスト
    user_message = "開発部門のメンバーを教えてください"
    print(f"\nユーザー: {user_message}")

    config = types.GenerateContentConfig(tools=[gemini_tools])
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=user_message,
        config=config,
    )

    candidates = response.candidates
    if not candidates or not candidates[0].content or not candidates[0].content.parts:
        print(f"\nLLMの応答: {response.text}")
        return

    part = candidates[0].content.parts[0]
    if part.function_call:
        func_call = part.function_call
        func_name = func_call.name or ""
        func_args = dict(func_call.args.items()) if func_call.args else {}
        print(f"\nLLMが選択: {func_name}({func_args})")

        # MCPツールを実行
        result = await mcp_client.call_tool(func_name, func_args)
        print(f"実行結果: {result}")
    else:
        print(f"\nLLMの応答: {response.text}")


async def demo_resources(mcp_client: Client, gemini_client: genai.Client):
    """
    Resourcesのデモ: 読み取り専用データをLLMのコンテキストとして活用

    MCPからリソースを読み取り、そのデータをLLMへの質問のコンテキストとして使用。
    Resourcesはアプリケーションが制御するデータソースで、
    LLMに追加情報を提供するために使用する。

    Args:
        mcp_client: MCPクライアント（接続済み）
        gemini_client: Geminiクライアント
    """
    print("\n" + "=" * 60)
    print("2. RESOURCES: コンテキスト情報の提供")
    print("=" * 60)

    # リソース一覧を取得
    resources = await mcp_client.list_resources()
    print("\n利用可能なリソース:")
    for r in resources:
        print(f"  - {r.uri}: {r.name}")

    # 特定のリソースを読み取り
    print("\n--- data://users リソースを読み取り ---")
    users_data = await mcp_client.read_resource("data://users")
    print(f"取得データ: {users_data[:100]}...")  # 先頭100文字

    # リソースデータをLLMのコンテキストとして使用
    print("\n--- リソースをコンテキストとしてLLMに質問 ---")
    prompt = f"""以下のユーザーデータを基に質問に答えてください。

ユーザーデータ:
{users_data}

質問: Pythonスキルを持っているのは誰ですか？"""

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    print(f"LLMの回答: {response.text}")

    # パラメータ付きリソース（テンプレート）
    print("\n--- user://u001 パラメータ付きリソース ---")
    user_data = await mcp_client.read_resource("user://u001")
    print(f"取得データ: {user_data}")


async def demo_prompts(mcp_client: Client, gemini_client: genai.Client):
    """
    Promptsのデモ: 再利用可能なテンプレートを取得してLLMに渡す

    MCPからプロンプトテンプレートを取得し、引数を渡して展開。
    生成されたプロンプトをそのままLLMに送信する。
    Promptsはユーザーが明示的に選択するテンプレート。

    Args:
        mcp_client: MCPクライアント（接続済み）
        gemini_client: Geminiクライアント
    """
    print("\n" + "=" * 60)
    print("3. PROMPTS: 再利用可能なテンプレート")
    print("=" * 60)

    # プロンプト一覧を取得
    prompts = await mcp_client.list_prompts()
    print("\n利用可能なプロンプト:")
    for p in prompts:
        print(f"  - {p.name}: {p.description}")

    # プロンプトを取得（引数を渡す）
    print("\n--- explain_topic プロンプトを使用 ---")
    prompt_result = await mcp_client.get_prompt(
        "explain_topic", {"topic": "MCP プロトコル"}
    )
    content = prompt_result.messages[0].content
    prompt_text = content.text if hasattr(content, "text") else str(content)
    print(f"生成されたプロンプト: {prompt_text}")

    # 取得したプロンプトをLLMに送信
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt_text,
    )
    response_text = response.text or ""
    print(f"\nLLMの回答:\n{response_text[:300]}...")  # 先頭300文字

    # コードレビュープロンプト
    print("\n--- code_review プロンプトを使用 ---")
    code = "def add(a, b): return a + b"
    prompt_result = await mcp_client.get_prompt(
        "code_review",
        {"language": "Python", "code": code, "focus": "可読性"},
    )
    content = prompt_result.messages[0].content
    prompt_text = content.text if hasattr(content, "text") else str(content)
    print(f"生成されたプロンプト:\n{prompt_text}")
    # 取得したプロンプトをLLMに送信
    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt_text,
    )
    response_text = response.text or ""
    print(f"\nLLMの回答:\n{response_text[:300]}...")  # 先頭300文字


async def main():
    """
    MCPの3つのコンポーネントをLLM経由で活用するデモを実行

    Tools、Resources、Promptsの各デモを順番に実行し、
    それぞれのコンポーネントの使い方を示す。
    """
    # クライアントの初期化
    mcp_client = Client("http://localhost:8000/mcp")
    gemini_client = genai.Client()  # GEMINI_API_KEY環境変数から自動取得

    async with mcp_client:
        print("=" * 60)
        print("MCP 3つのコンポーネントのデモ")
        print("サーバー: learn_server.py")
        print("=" * 60)

        await demo_tools(mcp_client, gemini_client)
        await demo_resources(mcp_client, gemini_client)
        await demo_prompts(mcp_client, gemini_client)

        print("\n" + "=" * 60)
        print("デモ完了")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
