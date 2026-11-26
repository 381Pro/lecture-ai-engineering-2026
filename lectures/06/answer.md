# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：`glossary_search_glossary`（`uv run python -m app.mcp_agent --list-tools` で見えたMCPツールは1個。`uv run python -m app.agent --list-tools` では `search_materials` / `make_quiz` / `save_learning_log` の3個が見えた）
- STEP 2 の [tool call]：`[tool call] glossary_search_glossary({'query': '3レベル'})`
- STEP 3 の [tool call]：`[tool call] fetch_fetch({'url': 'https://modelcontextprotocol.io/'})`
- STEP 4 の [tool call]：`[tool call] aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']})`（2回目：`[tool call] aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'What is versioning in Amazon S3'})`）
- 気づき・疑問：モデルは質問に応じて使うツールを自分で選んでいた。STEP 4では1回の質問で同じツールを2回呼び、まず日本語、次に英語で検索していた。疑問：ツール名 `aws_aws___search_documentation` のように接頭辞が重なるのはなぜか。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：発展
- やったこと：VS CodeのMCPサーバー設定を公式ドキュメントで調べ、演習で使った `app/mcp_servers.json` と比べた。調査日：2026-11-26。公式ドキュメント：https://code.visualstudio.com/docs/agent-customization/mcp-servers（設定リファレンス：https://code.visualstudio.com/docs/agents/reference/mcp-configuration）
- 結果：

  | 比較する点 | app/mcp_servers.json（演習） | VS Code（公式ドキュメント） |
  | --- | --- | --- |
  | 設定を書く場所（ファイル名と場所） | リポジトリ内の `app/mcp_servers.json`（1ファイル） | Copilot用（ポータブル形式）：個人・全ワークスペース共通は `$COPILOT_HOME/mcp-config.json`（未設定時は `~/.copilot/mcp-config.json`）、プロジェクト専用・チーム共有はワークスペースルートの `.mcp.json`。従来のエディタ管理形式は `.vscode/mcp.json`／プロファイルの `mcp.json`（現在は非推奨） |
  | コマンドで起動するサーバーの書き方 | `"command": "uv"`、`"args": [...]` のみ。`"type"` は書かない | `"type": "stdio"` が必須。そのうえで `"command": "npx"`、`"args": ["-y", "@playwright/mcp@latest"]` のように書く |
  | URLで接続するサーバーの書き方 | `"url": "https://knowledge-mcp.global.api.aws"` のみ。`"type"` は書かない | `"type": "http"`（旧来のSSEは `"type": "sse"`）が必須。そのうえで `"url": "https://mcp.context7.com/mcp"` のように書く |
  | 適用範囲 | このプロジェクトの `app/mcp_agent.py` が読む1ファイルだけで、このプロジェクトにだけ適用される | `mcp-config.json`（Copilot Global）は全ワークスペース・同じホストのCopilot系ツールに共通で使える。ワークスペースルートの `.mcp.json` はそのプロジェクト専用で、ソース管理でチーム共有できる |

  共通点：最上位のキーは両方とも `mcpServers`。違いは、VS Codeはサーバーごとに `"type"`（`stdio` / `http` / `sse`）を必ず書くのに対し、演習の `app/mcp_servers.json` は `command` か `url` のどちらがあるかで区別する点。
- 気づき・疑問：VS Codeの新しい形式と演習の形式は最上位キー `mcpServers` が同じで `type` の有無だけが違うので、演習の設定はほぼそのままVS CodeのCopilot用設定に移せそう。疑問：`type` を書かなくても、VS Code側は `url` の有無で判別できないのか。
