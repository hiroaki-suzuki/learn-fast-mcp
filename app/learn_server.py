"""
ResourcesとPromptsを学ぶためのサンプルサーバー
"""

from fastmcp import Context, FastMCP
from fastmcp.prompts import Message

mcp = FastMCP("Learning Server")


# 共有データ（ResourceとToolの両方から利用）
def _get_users_data() -> list:
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
    """アプリケーション設定を提供する静的リソース"""
    return {
        "app_name": "Learning MCP",
        "version": "1.0.0",
        "debug": True,
    }


@mcp.resource("data://users")
def get_all_users() -> list:
    """全ユーザーリストを提供"""
    return _get_users_data()


# --- パラメータ付きResource（テンプレート） ---
# URIに {parameter} を含めると動的に値を受け取れる
@mcp.resource("user://{user_id}")
def get_user_by_id(user_id: str) -> dict:
    """
    特定ユーザーの情報を取得
    例: user://u001 → 田中太郎の情報
    """
    users = {u["id"]: u for u in _get_users_data()}
    return users.get(user_id, {"error": f"User {user_id} not found"})


# --- 複数パラメータのテンプレート ---
@mcp.resource("weather://{city}/{date}")
def get_weather(city: str, date: str) -> dict:
    """
    指定都市・日付の天気を取得
    例: weather://tokyo/2024-01-15
    """
    # 実際のアプリではAPIを呼び出す
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
    サーバーステータスを取得（Contextでリクエスト情報にアクセス）
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
    """トピックの説明を依頼するプロンプト"""
    return f"「{topic}」について、初心者にも分かりやすく説明してください。"


# --- オプションパラメータ付きPrompt ---
@mcp.prompt
def code_review(
    language: str,
    code: str,
    focus: str = "全般",  # デフォルト値があるとオプションになる
) -> str:
    """コードレビューを依頼するプロンプト"""
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
    複数のMessageを返すことで会話のコンテキストを設定できる
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
    """レポート生成を依頼するプロンプト"""
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
    """デバッグ依頼プロンプト（リクエスト情報付き）"""
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
    """部署でユーザーを検索"""
    all_users = _get_users_data()
    return [u for u in all_users if u["department"] == department]


if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
