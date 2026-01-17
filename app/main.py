"""
FastMCP学習プロジェクトのエントリーポイント

このファイルはuvのデフォルトエントリーポイントとして使用される。
実際のMCPサーバー/クライアントは以下のファイルを参照:

サーバー:
    - my_server.py: 基本的なToolsのみのサーバー
    - learn_server.py: Tools/Resources/Promptsを含む高度なサーバー

クライアント:
    - my_client.py: 基本的な直接呼び出しクライアント
    - my_server_llm_client.py: LLM経由でmy_serverのツールを呼び出す
    - learn_client.py: learn_serverの全コンポーネントを直接呼び出す
    - learn_llm_client.py: LLM経由でlearn_serverの全コンポーネントを活用
"""


def main():
    """アプリケーションのエントリーポイント"""
    print("Hello from app!")


if __name__ == "__main__":
    main()
