# Code Review Agent

A beginner-friendly AI code reviewer that runs from the command line. Give it a file or a code snippet, and it returns a review covering:

1. **Bugs & Correctness**: logic errors, edge cases, exception handling
2. **Security**: injection risks, hard-coded secrets, unsafe `eval`/`exec`/`pickle`
3. **Performance**: real inefficiencies, not micro-optimizations
4. **Style & Readability**: PEP 8, naming, clarity
5. **Improvements**: simpler or more idiomatic code

Each issue comes with a severity (🔴 High / 🟡 Medium / 🟢 Low) and a concrete fix. The review opens with an overall verdict.

Built with [LangChain](https://python.langchain.com/). It calls the model through [OpenRouter](https://openrouter.ai/), so you can use any model OpenRouter offers.

## Project structure

```
code_review_agent/
├── src/code_reviewer_agent/
│   └── reviewer.py      # the agent: CLI, prompt, and LLM call
├── requirements.txt     # Python dependencies
├── .env.example         # template for your settings
├── metadata.yaml        # project metadata
└── README.md
```

## Setup

**Requirements:** Python 3.10+ and an [OpenRouter API key](https://openrouter.ai/keys).

```bash
# 1. Clone the repo
git clone https://github.com/sanjaya/code_review_agent.git
cd code_review_agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your settings file
cp .env.example .env
```

Then open `.env` and fill in your values:

```
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=openai/gpt-4o
```

`LLM_MODEL` can be any model ID from [openrouter.ai/models](https://openrouter.ai/models), for example `anthropic/claude-sonnet-4.5` or `openai/gpt-4o-mini`.

> **Never commit `.env`.** It contains your API key. It's already listed in `.gitignore`.

## Usage

Review a file:

```bash
python src/code_reviewer_agent/reviewer.py --file path/to/code.py
```

Review an inline snippet:

```bash
python src/code_reviewer_agent/reviewer.py --code "def add(a,b): return a+b"
```

Review code in another language:

```bash
python src/code_reviewer_agent/reviewer.py --file app.js --language javascript
```

| Option | Description |
| --- | --- |
| `--file PATH` | Path to a code file to review |
| `--code CODE` | A code snippet to review (in quotes) |
| `--language LANG` | Programming language of the code (default: `python`) |

You must give either `--file` or `--code`, but not both.

### Example output

```markdown
## Verdict
🔴 Critical Issues: `eval` runs arbitrary code from the input.

## Issues
### 2. Security
- 🔴 **High**: `eval(d[k])` executes whatever string is stored in `d[k]`...
```

## How it works

1. `load_dotenv()` reads your API key and model name from `.env`.
2. `create_llm()` builds a LangChain `ChatOpenAI` model pointed at OpenRouter's OpenAI-compatible API.
3. `review_code()` sends two messages to the model:
   - a **system message** (`SYSTEM_PROMPT`) that tells the model how to review and how to format its answer
   - a **human message** that contains your code
4. The model's reply, a Markdown review, is printed to the terminal.

To change what the reviewer focuses on, edit `SYSTEM_PROMPT` in [reviewer.py](src/code_reviewer_agent/reviewer.py).

## Troubleshooting

| Error | Fix |
| --- | --- |
| `please set OPENROUTER_API_KEY and LLM_MODEL` | Fill in both values in `.env`. |
| `Error code: 402 ... requires more credits` | Add credits to your OpenRouter key, or lower `max_tokens` in `create_llm()`. |
| `Error code: 401` | Your API key is wrong or expired. Create a new one on OpenRouter. |
| `file not found` | Check the path you gave to `--file`. |
| `ModuleNotFoundError` | Activate the virtual environment: `source .venv/bin/activate`. |
