"""第1回: LLMと会話履歴を保ちながら対話するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする

終了するには `exit` または `quit` を入力します。
講座に固有のことを聞くと、会話履歴がないため「分からない」と答えるか、
一般論でもっともらしく答える（講座の実際とは違う）ことを確かめられます。
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(question: str) -> str:
    client = genai.Client(api_key=get_api_key())
    response = client.models.generate_content(model=MODEL, contents=question)

    print_usage(response)
    return response.text


def print_usage(response) -> None:
    if response.usage_metadata is not None:
        print(f"[入力トークン数] {response.usage_metadata.prompt_token_count}")
        print(f"[出力トークン数] {response.usage_metadata.candidates_token_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="LLMと対話する")
    parser.add_argument("question", nargs="?")
    args = parser.parse_args()

    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    question = args.question or DEFAULT_QUESTION

    print(f"[model] {MODEL}")

    while question:
        print(f"[質問] {question}\n")
        try:
            response = chat.send_message(question)
            print_usage(response)
            print(response.text)
        except errors.APIError as e:
            print(api_error_message(e.code, e.message))
            raise SystemExit(1)

        try:
            question = input("\n次の質問（終了するには exit または quit）: ").strip()
        except EOFError:
            break

        if question.lower() in {"exit", "quit"}:
            break


if __name__ == "__main__":
    main()
