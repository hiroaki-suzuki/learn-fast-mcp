# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastMCP（Model Context Protocol）のクライアント・サーバーアーキテクチャを学ぶためのPythonプロジェクト。サーバーがTools、Resources、Promptsを公開し、クライアントがRPC経由で呼び出す。

## Commands

All commands should be run from the `app/` directory.

```bash
# Install dependencies
uv sync

# Run the server (starts on http://localhost:8000)
uv run python my_server.py      # 基本サーバー
uv run python learn_server.py   # Resources/Prompts含む高度なサーバー

# Run the client (requires server to be running)
uv run python my_client.py         # 基本クライアント
uv run python learn_client.py      # Resources/Prompts呼び出しデモ
uv run python my_server_llm_client.py    # LLM経由（my_server用）
uv run python learn_llm_client.py        # LLM経由（learn_server用）

# Lint & Type check
uv run ruff check .
uv run ty check
```

## Architecture

FastMCPの3つのデコレーター:

| Decorator | Purpose | Control |
|-----------|---------|---------|
| `@mcp.tool` | 実行可能な関数 | LLMが呼び出しを決定 |
| `@mcp.resource("uri://path")` | 読み取り専用データ | アプリケーション制御 |
| `@mcp.prompt` | 再利用可能なテンプレート | ユーザーが明示的に呼び出し |

### Server-Client Pairs

| Server | Client | Description |
|--------|--------|-------------|
| `my_server.py` | `my_client.py` | 基本的なTool（greet, add） |
| `my_server.py` | `my_server_llm_client.py` | LLM（Gemini）経由でTool呼び出し |
| `learn_server.py` | `learn_client.py` | Tools + Resources + Prompts |
| `learn_server.py` | `learn_llm_client.py` | LLM経由で3コンポーネント活用 |

### LLM Client Pattern

LLMクライアントは以下のフローで動作:
1. `client.list_tools()` でMCPからツール一覧取得
2. ツール定義をGemini Function Calling形式に変換
3. 自然言語をLLMに送信、LLMがツール選択
4. `client.call_tool()` でMCPツール実行

## Environment

LLMクライアント実行時は`GEMINI_API_KEY`環境変数が必要（`.env.example`参照）。

## Session Context

ユーザーはMCPの学習中。FastMCPを使って理解を深めている。Claudeはその学習を手伝う役割。

学習の進め方:
- コードを書いて動かしながら理解を深める
- 疑問点があれば都度説明する
- 必要に応じてサンプルコードを追加・修正する
