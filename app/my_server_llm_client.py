"""
LLM経由でMCPツールを呼び出すサンプル

通常のクライアント（my_client.py）との違い:
- my_client.py: 開発者が明示的にtool名を指定して呼び出す
- llm_client.py: LLMが自然言語を解釈し、適切なtoolを自動選択して呼び出す

実行前に:
1. GEMINI_API_KEY環境変数を設定
2. サーバーを起動: uv run python my_server.py
"""

import asyncio
import json

from fastmcp import Client
from google import genai
from google.genai import types


async def main():
    # MCPクライアントの接続
    mcp_client = Client("http://localhost:8000/mcp")

    async with mcp_client:
        # ============================================================
        # Step 1: MCPサーバーからtool一覧を取得
        # ============================================================
        mcp_tools = await mcp_client.list_tools()
        print("=== MCPサーバーから取得したツール ===")
        for tool in mcp_tools:
            print(f"  - {tool.name}: {tool.description}")
        print()

        # ============================================================
        # Step 2: MCPツールをGemini用のfunction定義に変換
        # ============================================================
        gemini_functions = []
        for tool in mcp_tools:
            func_def = {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            }
            gemini_functions.append(func_def)

        gemini_tools = types.Tool(function_declarations=gemini_functions)

        # ============================================================
        # Step 3: Geminiにユーザーの自然言語リクエストを送信
        # ============================================================
        gemini_client = genai.Client()  # GEMINI_API_KEY環境変数から自動取得

        user_message = "5と7を足してください"
        print(f"=== ユーザーのリクエスト ===\n{user_message}\n")

        config = types.GenerateContentConfig(tools=[gemini_tools])
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=user_message,
            config=config,
        )

        # ============================================================
        # Step 4: LLMがfunction callを返した場合、MCPツールを実行
        # ============================================================
        part = response.candidates[0].content.parts[0]

        if part.function_call:
            func_call = part.function_call
            print("=== LLMが選択したツール ===")
            print(f"  ツール名: {func_call.name}")
            print(f"  引数: {json.dumps(dict(func_call.args), ensure_ascii=False)}")
            print()

            # MCPツールを実行
            result = await mcp_client.call_tool(func_call.name, dict(func_call.args))
            print("=== MCPツールの実行結果 ===")
            print(f"  {result}")
        else:
            # function callなしの通常レスポンス
            print(f"=== LLMの応答 ===\n{response.text}")


if __name__ == "__main__":
    asyncio.run(main())
