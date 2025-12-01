# 🧭 AI Political Talk Bias Analyser

A lightweight, open-source web tool that attempts to detect perceived political leaning (Left • Center • Right) in any text or news article — using a **zero-shot** BART model (no political fine-tuning required).

**Live demo**: [https://your-domain.com](https://your-domain.com) *(replace with your actual URL or delete this line)*

### Features
- Paste any text or drop a news article URL
- Instant bias estimate with confidence score
- Fully client-free — runs on your server or locally
- Experimental & educational — built for transparency, not authority

### Tech Stack
- FastAPI + Jinja2 (backend + templating)
- Hugging Face `MoritzLaurer/deberta-v3-large-zeroshot-v2.0` (zero-shot classification)
- Newspaper3k (article extraction)
- Pure HTML/CSS

### Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/TheNedgineer/nofussalyzer.git
cd nofussalyzer

# 2. Create virtual env & install
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows
pip install -r requirements.txt

# 3. Run locally
uvicorn app:app --reload

```

Open http://127.0.0.1:8000 in your browser.

License
Apache 2.0 – feel free to use, modify, or deploy commercially.
See LICENSE for details.

Disclaimer
This tool is experimental. Political bias is subjective. Results are AI-generated guesses, not objective truth. Use for learning and fun, not as evidence.

Made with ☕ and curiosity — PRs welcome!
