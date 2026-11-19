# 第3回 解答
## 演習
- 第1回（素のLLM）とエージェントの回答の違い：
  - RAGとは何ですか？：app.ask は一般的な詳細説明のみ。app.agent は用語集に直接の項目がないことを断った上で一般的な定義を説明し、関連語として第3回を示した。
  - 第1回で使ったモデルは何ですか？：app.ask は「第1回」が何を指すか分からないとして GPT-4・Claude・Geminiなどを一般論で挙げるだけだった。app.agent は「第1回では、モデルとして Gemini API を使用しています。関連語： 第1回」と用語集に基づく回答をした。
  - 第2回の課題の提出方法を教えてください：app.ask は一般的なポータル・LMS・紙提出などの説明にとどまった。app.agent は用語集に課題提出方法の項目がないことを断った上で一般的なLMS・GitHub提出を説明し、関連語として第2回（ファインチューニングとLoRA）を示した。
  - まとめ：app.agent は用語集・講義要約をツールで参照するため、講義固有の質問で具体性が上がる。ただし用語集にない情報（課題の提出方法）については一般論にとどまる。
- `--trace` で見えたツール呼び出し（ツール名と引数）：
  - 演習ツール追加前（RAGとは何ですか？）：search_glossary({'query': 'RAG'})、search_glossary({'query': 'Retrieval-Augmented Generation'})。2回目は用語集に見つからない旨の返答だった。
  - make_quiz追加後（ファインチューニングのクイズを作ってください）：search_glossary({'query': 'ファインチューニング'})、make_quiz({'term': 'ファインチューニング'})。make_quiz の返答は「問題:「ファインチューニング」とは何か。最も適切な説明を選べ。」で始まる4択で、答えは C（ファインチューニング）だった。
- 1つの質問での LLM 呼び出し回数（`requests`）：
  - 演習ツール追加前（RAGとは何ですか？）：requests=3、tool_calls=2、input_tokens=1271、output_tokens=192、cost=0.0008613。
  - make_quiz追加後（ファインチューニングのクイズを作ってください）：requests=3、tool_calls=2、input_tokens=2255、output_tokens=353、cost=0.0015590。
- 追加したツールと、docstring に書いた説明：
  - make_quiz（app/tools.py、app/agent.py で tool_plain で登録）：「指定した用語について、定義から4択クイズを1問作る。クイズを作りたいときに使う。」
## 宿題
- 取り組んだレベル：実装
- やったこと：
  - app/tools.py に save_learning_log(topic: str, content: str) -> str を追加した。LEARNING_LOG_DIR（リポジトリ直下の learning_log/）を作成し、YYYY-MM-DD_テーマ.md に日付・テーマ・内容をMarkdownで保存し、既存ファイルには追記して保存したパスを返す。テーマからファイル名に使えない文字を除去する。
  - app/agent.py で agent.tool_plain(tools.save_learning_log, requires_approval=True) で登録した。tool_plain の署名に requires_approval: bool = False があることを確認した。
  - tests/test_tools.py に直接テスト4件と TestModel テスト2件を追加した。save_learning_log のテストでは LEARNING_LOG_DIR を tmp_path に差し替えた。
  - 既存の tests/test_agent.py の test_base_tools_are_registered_and_called は、TestModel が全ツールを呼ぶと承認付きツールで DeferredToolRequests エラーになるため、call_tools を ["search_glossary", "get_lecture_summary"] に限定するよう修正した。
- 結果：
  - 直接実行：make_quiz('ファインチューニング') は4択を返し、答えは C（ファインチューニング）だった。
  - 承認の確認：TestModel(call_tools=["save_learning_log"]) で agent.run_sync を実行すると、UserError「A deferred tool call was present, but `DeferredToolRequests` is not among output types for this agent.」となり、ファイルは作成されなかった。未承認では保存されないことを確認した。
  - pytest：最初は 16 passed、1 failed（test_base_tools_are_registered_and_called、承認エラー）。上記の test_agent 修正後、17 passed、0 failed（PYTEST_RC=0、3.83s）。
- 気づき・疑問：
  - ツールのdocstringと型ヒントがそのままモデルへの説明文になるため、docstringの書き方がツールの呼ばれ方を決めることが分かった。
  - 承認付きツールを追加すると、既存の「全ツールを呼ぶ」テストが壊れる。承認の扱いをテスト設計の段階で決めておく必要がある。
  - 疑問：CLIで承認付きツールを使う場合、利用者はどのように承認するか（本作業では DeferredToolRequests のエラーとして確認しただけで、CLI上での承認操作までは確認していない）。
