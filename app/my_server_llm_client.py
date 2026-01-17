"""
LLM（Gemini）経由でMCPツールを呼び出すサンプル

このモジュールは、LLMのFunction Calling機能を使ってMCPツールを呼び出す方法を示す。
ユーザーの自然言語リクエストをLLMが解釈し、適切なツールを自動選択して実行する。

通常のクライアント（my_client.py）との違い:
    - my_client.py: 開発者が明示的にtool名を指定して呼び出す
    - llm_client.py: LLMが自然言語を解釈し、適切なtoolを自動選択して呼び出す

処理フロー:
    1. MCPサーバーからツール一覧を取得
    2. ツール定義をGemini Function Calling形式に変換
    3. ユーザーの自然言語リクエストをLLMに送信
    4. LLMがツール呼び出しを返した場合、MCPツールを実行

実行前に:
    1. GEMINI_API_KEY環境変数を設定（.env.example参照）
    2. サーバーを起動: uv run python my_server.py
    3. クライアントを実行: uv run python my_server_llm_client.py
"""

import asyncio
import json

from fastmcp import Client
from google import genai
from google.genai import types


async def main():
    """
    LLMを介してMCPツールを呼び出すデモを実行する

    LLMのFunction Calling機能を使い、自然言語から適切なツールを選択・実行する。
    """
    # MCPクライアントの接続設定
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
        # MCPのツールスキーマはJSON Schema形式で、Geminiも同じ形式を使用するため
        # そのまま変換可能
        # ============================================================
        gemini_functions = []
        for tool in mcp_tools:
            # MCPツール定義からGemini Function Calling形式に変換
            func_def = {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,  # JSON Schema形式
            }
            gemini_functions.append(func_def)

        # Geminiに渡すツール定義を作成
        gemini_tools = types.Tool(function_declarations=gemini_functions)

        # ============================================================
        # Step 3: Geminiにユーザーの自然言語リクエストを送信
        # LLMはツール定義を見て、適切なツールを選択し、必要な引数を抽出する
        # ============================================================
        # Geminiクライアントを作成（GEMINI_API_KEY環境変数から自動取得）
        gemini_client = genai.Client()

        # 自然言語でリクエスト（LLMがこれを解釈してツールを選択）
        user_message = "5と7を足してください"
        print(f"=== ユーザーのリクエスト ===\n{user_message}\n")

        # ツール定義を含めてLLMにリクエスト
        config = types.GenerateContentConfig(tools=[gemini_tools])
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=user_message,
            config=config,
        )

        # ============================================================
        # Step 4: LLMがfunction callを返した場合、MCPツールを実行
        # LLMはツールを使うべきと判断した場合、function_callを返す
        # そうでない場合は通常のテキスト応答を返す
        # ============================================================
        candidates = response.candidates
        if not candidates or not candidates[0].content or not candidates[0].content.parts:
            # レスポンスが空の場合
            print(f"=== LLMの応答 ===\n{response.text}")
            return

        part = candidates[0].content.parts[0]

        if part.function_call:
            # LLMがツール呼び出しを選択した場合
            func_call = part.function_call
            func_name = func_call.name or ""
            func_args = dict(func_call.args.items()) if func_call.args else {}
            print("=== LLMが選択したツール ===")
            print(f"  ツール名: {func_name}")
            print(f"  引数: {json.dumps(func_args, ensure_ascii=False)}")
            print()

            # MCPサーバーのツールを実行
            result = await mcp_client.call_tool(func_name, func_args)
            print("=== MCPツールの実行結果 ===")
            print(f"  {result}")
        else:
            # ツール呼び出しなしの通常レスポンス
            # （ツールで対応できない質問の場合など）
            print(f"=== LLMの応答 ===\n{response.text}")


if __name__ == "__main__":
    asyncio.run(main())
