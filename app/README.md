# FastMCP 学習プロジェクト

FastMCP（Model Context Protocol）のクライアント・サーバーアーキテクチャを学ぶためのサンプル集。

## 概要

MCPは、LLMアプリケーションがツール、リソース、プロンプトを標準化された方法で公開・利用するためのプロトコルです。このプロジェクトでは、FastMCPライブラリを使って以下を学びます：

- **Tools**: LLMが呼び出しを決定する実行可能な関数
- **Resources**: アプリケーションが提供する読み取り専用データ
- **Prompts**: ユーザーが選択する再利用可能なテンプレート

## セットアップ

```bash
cd app
uv sync
```

LLMクライアントを使用する場合は、環境変数を設定してください：

```bash
cp .env.example .env
# .envファイルを編集してGEMINI_API_KEYを設定
```

## ファイル構成

### サーバー

| ファイル | 説明 |
|----------|------|
| `my_server.py` | 基本的なサーバー（greet, add ツールのみ） |
| `learn_server.py` | 高度なサーバー（Tools + Resources + Prompts） |

### クライアント

| ファイル | 対象サーバー | 説明 |
|----------|--------------|------|
| `my_client.py` | my_server.py | ツールを直接呼び出す基本例 |
| `my_server_llm_client.py` | my_server.py | LLM経由でツールを自動選択・実行 |
| `learn_client.py` | learn_server.py | 3コンポーネントを直接呼び出す |
| `learn_llm_client.py` | learn_server.py | LLM経由で3コンポーネントを活用 |

## 使い方

### 基本的な使い方（my_server + my_client）

ターミナル1（サーバー起動）:
```bash
cd app
uv run python my_server.py
```

ターミナル2（クライアント実行）:
```bash
cd app
uv run python my_client.py
```

### LLM経由での使い方（my_server + LLMクライアント）

ターミナル1（サーバー起動）:
```bash
cd app
uv run python my_server.py
```

ターミナル2（LLMクライアント実行）:
```bash
cd app
uv run python my_server_llm_client.py
```

### 高度な使い方（learn_server + learn_client）

ターミナル1（サーバー起動）:
```bash
cd app
uv run python learn_server.py
```

ターミナル2（クライアント実行）:
```bash
cd app
uv run python learn_client.py      # 直接呼び出し
# または
uv run python learn_llm_client.py  # LLM経由
```

## MCPの3つのコンポーネント

### 1. Tools（ツール）

LLMが自動的に呼び出しを決定する実行可能な関数。

```python
@mcp.tool
def greet(name: str) -> str:
    """挨拶を返す"""
    return f"Hello, {name}!"
```

**特徴**:
- LLMが自然言語から適切なツールを選択
- 引数はJSON Schema形式で定義
- 戻り値はクライアントに返される

### 2. Resources（リソース）

アプリケーションが制御する読み取り専用データソース。

```python
@mcp.resource("config://app")
def get_config() -> dict:
    """アプリ設定を提供"""
    return {"version": "1.0.0"}

# パラメータ付きリソース（テンプレート）
@mcp.resource("user://{user_id}")
def get_user(user_id: str) -> dict:
    """ユーザー情報を取得"""
    return {"id": user_id, "name": "..."}
```

**特徴**:
- URIで識別される
- `{parameter}` でパラメータを受け取れる
- LLMのコンテキスト情報として活用

### 3. Prompts（プロンプト）

ユーザーが明示的に選択する再利用可能なテンプレート。

```python
@mcp.prompt
def explain_topic(topic: str) -> str:
    """トピック説明プロンプト"""
    return f"「{topic}」について説明してください。"

# 複数メッセージを返す（会話形式）
@mcp.prompt
def roleplay(role: str) -> list:
    """ロールプレイプロンプト"""
    return [
        Message(role="user", content=f"あなたは{role}です。"),
        Message(role="assistant", content="承知しました。"),
    ]
```

**特徴**:
- 引数を受け取ってプロンプトを生成
- 文字列またはMessageのリストを返せる
- LLMに送信する前にテンプレートを展開

## コンポーネント比較表

| 項目 | Tools | Resources | Prompts |
|------|-------|-----------|---------|
| 目的 | 実行可能な操作 | 読み取り専用データ | プロンプトテンプレート |
| 制御 | LLMが決定 | アプリケーション | ユーザー |
| 呼び出し | `call_tool()` | `read_resource()` | `get_prompt()` |
| 識別子 | 関数名 | URI | 関数名 |

## 開発

### Lint & 型チェック

```bash
cd app
uv run ruff check .
uv run ty check
```
