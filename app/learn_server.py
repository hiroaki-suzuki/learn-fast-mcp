"""
MCPの3つのコンポーネント（Resources、Prompts、Tools）を学ぶためのサンプルサーバー

このモジュールは、FastMCPの全機能を示す包括的な例を提供する:
- Resources: 読み取り専用のデータソース（アプリケーション制御）
- Prompts: 再利用可能なプロンプトテンプレート（ユーザー制御）
- Tools: 実行可能な関数（LLM制御）

使い方:
    uv run python learn_server.py

対応するクライアント:
    - learn_client.py: 直接呼び出しのデモ
    - learn_llm_client.py: LLM経由での呼び出しデモ

サーバーは http://localhost:8000 で起動し、/mcp エンドポイントでMCPリクエストを受け付ける。
"""

from fastmcp import Context, FastMCP
from fastmcp.prompts import Message

# サーバーインスタンスを作成
mcp = FastMCP("Learning Server")


# =============================================================================
# 共有データ
# ResourceとToolの両方から利用するサンプルデータ
# =============================================================================


def _get_users_data() -> list:
    """
    サンプルユーザーデータを取得する

    Returns:
        ユーザー情報のリスト（id, name, department, skills）
    """
    return [
        {
            "id": "u001",
            "name": "田中太郎",
            "department": "開発",
            "skills": ["Python", "MCP"],
        },
        {
            "id": "u002",
            "name": "山田花子",
            "department": "営業",
            "skills": ["Excel", "交渉"],
        },
        {
            "id": "u003",
            "name": "佐藤次郎",
            "department": "開発",
            "skills": ["JavaScript", "React"],
        },
    ]


# =============================================================================
# Resources（リソース）: 読み取り専用のデータを提供
# - クライアントやLLMがコンテキストとして利用できるデータ
# - 制御はアプリケーション側が行う（パッシブなデータソース）
# =============================================================================


# --- 基本的なResource ---
@mcp.resource("config://app")
def get_app_config() -> dict:
    """
    アプリケーション設定を提供する静的リソース

    Returns:
        アプリ名、バージョン、デバッグフラグを含む設定dict
    """
    return {
        "app_name": "Learning MCP",
        "version": "1.0.0",
        "debug": True,
    }


@mcp.resource("data://users")
def get_all_users() -> list:
    """
    全ユーザーリストを提供

    Returns:
        登録されている全ユーザーのリスト
    """
    return _get_users_data()


# --- パラメータ付きResource（テンプレート） ---
# URIに {parameter} を含めると動的に値を受け取れる
@mcp.resource("user://{user_id}")
def get_user_by_id(user_id: str) -> dict:
    """
    特定ユーザーの情報を取得

    URIテンプレートを使用して、動的にユーザーIDを受け取る。
    例: user://u001 → 田中太郎の情報

    Args:
        user_id: ユーザーID（例: "u001"）

    Returns:
        ユーザー情報のdict、見つからない場合はエラーメッセージ
    """
    users = {u["id"]: u for u in _get_users_data()}
    return users.get(user_id, {"error": f"User {user_id} not found"})


# --- 複数パラメータのテンプレート ---
@mcp.resource("weather://{city}/{date}")
def get_weather(city: str, date: str) -> dict:
    """
    指定都市・日付の天気を取得

    複数のURIパラメータを使用する例。
    例: weather://tokyo/2024-01-15

    Args:
        city: 都市名（例: "tokyo"）
        date: 日付（例: "2024-01-15"）

    Returns:
        天気情報（気温、天候、湿度）を含むdict
    """
    # 実際のアプリでは外部APIを呼び出す
    return {
        "city": city,
        "date": date,
        "temperature": 15,
        "condition": "晴れ",
        "humidity": 45,
    }


# --- Contextを使ったResource ---
@mcp.resource("status://server")
async def get_server_status(ctx: Context) -> dict:
    """
    サーバーステータスを取得

    Contextオブジェクトを使用してリクエスト情報にアクセスする例。
    非同期関数として定義することも可能。

    Args:
        ctx: FastMCPのContextオブジェクト（リクエスト情報を含む）

    Returns:
        サーバーステータスとリクエストIDを含むdict
    """
    return {
        "status": "running",
        "request_id": ctx.request_id,
    }


# =============================================================================
# Prompts（プロンプト）: 再利用可能なテンプレート
# - LLMに対する指示や会話のテンプレート
# - ユーザーが明示的に呼び出す（ユーザー制御）
# =============================================================================


# --- 基本的なPrompt（文字列を返す） ---
@mcp.prompt
def explain_topic(topic: str) -> str:
    """
    トピックの説明を依頼するプロンプト

    Args:
        topic: 説明してほしいトピック

    Returns:
        LLMに送信するプロンプト文字列
    """
    return f"「{topic}」について、初心者にも分かりやすく説明してください。"


# --- オプションパラメータ付きPrompt ---
@mcp.prompt
def code_review(
    language: str,
    code: str,
    focus: str = "全般",  # デフォルト値があるとオプションになる
) -> str:
    """
    コードレビューを依頼するプロンプト

    Args:
        language: プログラミング言語
        code: レビュー対象のコード
        focus: レビューの観点（デフォルト: "全般"）

    Returns:
        コードレビュー依頼のプロンプト文字列
    """
    return f"""以下の{language}コードをレビューしてください。

特に「{focus}」の観点でチェックをお願いします。

```{language}
{code}
```
"""


# --- 複数メッセージを返すPrompt（会話形式） ---
@mcp.prompt
def roleplay_teacher(subject: str) -> list:
    """
    教師役として振る舞うプロンプト

    複数のMessageを返すことで会話のコンテキストを設定できる。
    システムプロンプトの代わりに、会話履歴で役割を定義する例。

    Args:
        subject: 教える科目

    Returns:
        Messageオブジェクトのリスト（会話履歴）
    """
    return [
        Message(
            role="user",
            content=f"あなたは{subject}の優秀な教師です。生徒の質問に丁寧に答えてください。",
        ),
        Message(
            role="assistant",
            content=f"はい、{subject}の教師として質問にお答えします。何でも聞いてください。",
        ),
    ]


# --- 複雑なパラメータを持つPrompt ---
@mcp.prompt
def generate_report(
    title: str,
    sections: list[str],  # リスト型も使える
    include_summary: bool = True,
) -> str:
    """
    レポート生成を依頼するプロンプト

    リスト型やブール型など、複雑なパラメータを使用する例。

    Args:
        title: レポートのタイトル
        sections: 含めるセクションのリスト
        include_summary: 要約を含めるかどうか（デフォルト: True）

    Returns:
        レポート生成依頼のプロンプト文字列
    """
    sections_text = "\n".join(f"- {s}" for s in sections)
    summary_instruction = "最後に要約を含めてください。" if include_summary else ""

    return f"""以下の構成でレポート「{title}」を作成してください。

## 含めるセクション:
{sections_text}

{summary_instruction}
"""


# --- Contextを使ったPrompt ---
@mcp.prompt
async def debug_request(error_message: str, ctx: Context) -> str:
    """
    デバッグ依頼プロンプト

    Contextを使用してリクエスト情報を含める例。
    非同期関数としても定義可能。

    Args:
        error_message: デバッグ対象のエラーメッセージ
        ctx: FastMCPのContextオブジェクト

    Returns:
        デバッグ依頼のプロンプト文字列（リクエストID付き）
    """
    return f"""以下のエラーをデバッグしてください。

エラーメッセージ: {error_message}
リクエストID: {ctx.request_id}

原因と解決策を教えてください。
"""


# =============================================================================
# Tools: ResourcesやPromptsと連携するツール
# =============================================================================


@mcp.tool
def search_users(department: str) -> list:
    """
    部署でユーザーを検索

    Args:
        department: 検索する部署名（例: "開発", "営業"）

    Returns:
        指定した部署に所属するユーザーのリスト
    """
    all_users = _get_users_data()
    return [u for u in all_users if u["department"] == department]


# =============================================================================
# サーバーの起動
# =============================================================================
if __name__ == "__main__":
    # HTTPトランスポートでポート8000で起動
    mcp.run(transport="http", port=8000)
