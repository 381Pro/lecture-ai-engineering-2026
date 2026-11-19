import os
import time

from google import genai

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.8-flash",
]

QUESTIONS = [
    "LoRAとは何ですか？",
    "AIE2026の講座の宿題にある「3レベル」とは何ですか？",
]


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY が設定されていません")
        return
    client = genai.Client(api_key=api_key)
    print("| モデル | 質問 | レイテンシ秒 | 入力トークン | 出力トークン |")
    print("| --- | --- | --- | --- | --- |")
    for model in MODELS:
        for question in QUESTIONS:
            start = time.perf_counter()
            try:
                response = client.models.generate_content(model=model, contents=question)
                latency = time.perf_counter() - start
                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count if usage is not None else ""
                output_tokens = usage.candidates_token_count if usage is not None else ""
                print(f"| {model} | {question} | {latency:.2f} | {input_tokens} | {output_tokens} |")
            except Exception as e:
                latency = time.perf_counter() - start
                print(f"| {model} | {question} | エラー ({latency:.2f}秒): {e} |  |  |")


if __name__ == "__main__":
    main()
