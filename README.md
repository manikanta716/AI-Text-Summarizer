# 🤖 AI Text Summarizer

A command-line tool that uses Claude (Anthropic API) to summarize text from files, URLs, or stdin — with multiple summary styles.

## Features

- Summarize any text file, URL, or piped input
- 5 summary styles: `concise`, `detailed`, `bullets`, `eli5`, `tldr`
- Save output to a file
- Handles large inputs (auto-truncates at 100k chars)

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # get one at console.anthropic.com
```

## Usage

```bash
# Summarize a file
python summarizer.py --file article.txt

# Summarize a webpage
python summarizer.py --url https://en.wikipedia.org/wiki/Python_(programming_language)

# Pipe text in
cat long_doc.txt | python summarizer.py

# Choose a style
python summarizer.py --file doc.txt --style bullets
python summarizer.py --file doc.txt --style eli5
python summarizer.py --file doc.txt --style tldr

# Save to file
python summarizer.py --file doc.txt --output summary.txt
```

## Summary Styles

| Style | Description |
|-------|-------------|
| `concise` | 2-3 sentence summary (default) |
| `detailed` | Full breakdown with bullet points |
| `bullets` | 5-7 concise bullet points |
| `eli5` | Explain like I'm 5 |
| `tldr` | One-sentence TL;DR |

## Requirements

- Python 3.9+
- `anthropic` package
- Anthropic API key
