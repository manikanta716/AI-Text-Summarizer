#!/usr/bin/env python3
"""
AI Text Summarizer
Uses the Anthropic API to summarize text from stdin, files, or URLs.
"""

import argparse
import os
import sys
import textwrap
import urllib.request
import urllib.error
import re

import anthropic


# ── Text extraction ───────────────────────────────────────────────────────────

def fetch_url(url: str) -> str:
    """Fetch plain text from a URL, stripping basic HTML tags."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # Very basic tag stripper — fine for demos, use BeautifulSoup for production
        text = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except urllib.error.URLError as e:
        print(f"❌ Failed to fetch URL: {e}")
        sys.exit(1)


def read_input(args) -> str:
    if args.url:
        print(f"🌐 Fetching: {args.url}")
        return fetch_url(args.url)
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
    elif not sys.stdin.isatty():
        return sys.stdin.read()
    else:
        print("📝 Enter text to summarize (Ctrl+D when done):\n")
        return sys.stdin.read()


# ── Summarizer ────────────────────────────────────────────────────────────────

STYLE_PROMPTS = {
    "concise": "Summarize the following text in 2-3 sentences. Be direct and capture the key point only.",
    "detailed": "Provide a detailed summary of the following text with the main ideas, key arguments, and important details. Use bullet points for clarity.",
    "bullets": "Summarize the following text as 5-7 concise bullet points. Each bullet should be one clear sentence.",
    "eli5": "Explain the following text simply, as if explaining to a curious 10-year-old. Avoid jargon and use plain language.",
    "tldr": "Give a one-sentence TL;DR for the following text.",
}


def summarize(text: str, style: str, client: anthropic.Anthropic) -> str:
    if len(text) > 100_000:
        print(f"⚠️  Text truncated from {len(text):,} to 100,000 characters.")
        text = text[:100_000]

    system_prompt = STYLE_PROMPTS.get(style, STYLE_PROMPTS["concise"])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"{system_prompt}\n\n---\n\n{text}"
            }
        ]
    )
    return message.content[0].text


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🤖 AI Text Summarizer — powered by Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Summarize a file
  python summarizer.py --file article.txt

  # Summarize from a URL
  python summarizer.py --url https://example.com/article

  # Pipe text in
  echo "Long text here..." | python summarizer.py

  # Different summary styles
  python summarizer.py --file doc.txt --style bullets
  python summarizer.py --file doc.txt --style eli5
  python summarizer.py --file doc.txt --style tldr

  # Save output
  python summarizer.py --file doc.txt --output summary.txt
        """,
    )
    parser.add_argument("--file", help="Path to a text file")
    parser.add_argument("--url", help="URL to fetch and summarize")
    parser.add_argument(
        "--style",
        choices=list(STYLE_PROMPTS.keys()),
        default="concise",
        help="Summary style (default: concise)",
    )
    parser.add_argument("--output", help="Save summary to file")
    parser.add_argument("--no-wrap", action="store_true", help="Disable text wrapping")

    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY environment variable not set.")
        print("   Get a key at: https://console.anthropic.com")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    text = read_input(args)
    word_count = len(text.split())
    print(f"📄 Input: {word_count:,} words ({len(text):,} characters)")
    print(f"🎨 Style: {args.style}\n")
    print("⏳ Summarizing...\n")

    summary = summarize(text, args.style, client)

    print("─" * 60)
    print("📝 SUMMARY")
    print("─" * 60)
    if args.no_wrap:
        print(summary)
    else:
        print(textwrap.fill(summary, width=80) if "\n" not in summary else summary)
    print("─" * 60)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"\n💾 Saved to: {args.output}")


if __name__ == "__main__":
    main()
