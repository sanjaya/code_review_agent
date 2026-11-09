"""
Code Review Agent using LangChain.

Reviews Python code for bugs, security issues, style violations, and
suggests improvements. Accepts a file path or inline code snippet.

Usage:
    python agent.py --file path/to/code.py
    python agent.py --code "def add(a,b): return a+b"
"""

import argparse
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

SYSTEM_PROMPT =  """You are an expert code reviewer. Return a markdown review with sections: Bugs, Security, Performance, Style (PEP 8), Improvements.
Cite line numbers, skip empty sections, and end with: 🟢 Good / 🟡 Needs Work / 🔴 Critical."""

# Load the variables from the .env file (OPENROUTER_API_KEY and LLM_MODEL)
load_dotenv()


def create_llm() -> ChatOpenAI:
    """Create the AI model we will send the code to.

    OpenRouter works like the OpenAI API, so we can use ChatOpenAI
    and just point it at OpenRouter's URL.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("LLM_MODEL")

    # Stop early with a helpful message if the .env file is not filled in
    if not api_key or not model_name:
        print("Error: please set OPENROUTER_API_KEY and LLM_MODEL in your .env file.")
        exit(1)

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=os.getenv("TEMPERATURE"),  # 0 = same answer every time, good for reviews
        max_tokens=os.getenv("MAX_TOKEN"),  # limit the length of the review (keeps cost low)
    )
    return llm


def review_code(code: str, language: str = "python") -> str:
    """Send the code to the AI model and return its review as text."""
    llm = create_llm()

    # A chat with the model is a list of messages:
    # - SystemMessage tells the model what role to play
    # - HumanMessage is our actual request (the code to review)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Please review this {language} code:\n\n```{language}\n{code}\n```"),
    ]

    response = llm.invoke(messages)
    return response.content


def read_file(file_path: str) -> str:
    """Read a code file and return its contents as text."""
    if not os.path.isfile(file_path):
        print(f"Error: file not found: {file_path}")
        exit(1)

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def main():
    # 1. Read the command-line options (--file or --code)
    parser = argparse.ArgumentParser(description="AI code review agent")
    group = parser.add_mutually_exclusive_group(required=True)  # must give exactly one
    group.add_argument("--file", help="path to a code file to review")
    group.add_argument("--code", help="a code snippet to review, in quotes")
    parser.add_argument("--language", default="python", help="Programming language (default: python)")
    args = parser.parse_args()

    # 2. Get the code to review
    if args.file:
        code = read_file(args.file)
    else:
        code = args.code

    if not code.strip():
        print("Error: there is no code to review.")
        exit(1)

    # 3. Ask the AI for a review and print it
    print("Reviewing your code, please wait...\n")
    try:
        review = review_code(code, args.language)
    except Exception as error:
        print(f"Error: the review failed: {error}")
        exit(1)

    print(review)


# This runs main() only when you run this file directly
if __name__ == "__main__":
    main()
