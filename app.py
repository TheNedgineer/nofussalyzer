# app.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from zs_bias_model import analyse_bias
from scraper import extract_article_text
import re

# from urllib.parse import urlparse
# import asyncio

app = FastAPI(title="AI Political Bias Analyser")
templates = Jinja2Templates(directory="templates")


# Warm-up the model on startup
@app.on_event("startup")
async def warmup():
    print("Warming up model...")
    try:
        _ = analyse_bias("Climate change is the biggest threat facing humanity today.")
        print("Model ready & cached!")
    except Exception as e:
        print("Warmup failed:", e)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyse", response_class=HTMLResponse)
async def analyse(request: Request, input: str = Form(...)):
    try:
        raw = input.strip()
        if not raw:
            raise ValueError("Please enter some text or a URL")

        # Smart URL detection
        url_regex = re.compile(
            r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
            r"(?:/[\w.~:/?#[\]@!$&'()*+,;=%-]*)?$"
        )
        is_url = raw.lower().startswith(("http://", "https://")) or bool(
            url_regex.match(raw)
        )

        if is_url:
            # Clean up common copy-paste junk
            clean_url = raw.split()[0].strip("<>")
            print(f"Fetching article from URL: {clean_url}")
            article_text = extract_article_text(clean_url)

            if not article_text or len(article_text) < 120:
                raise ValueError(
                    "Couldn't extract readable text from that page. "
                    "Try pasting the article text directly instead."
                )
            text_to_analyse = article_text
            source_note = f"(extracted from {clean_url})"
        else:
            if len(raw) < 30:
                raise ValueError(
                    "Please enter a longer piece of text (at least a sentence or two)"
                )
            text_to_analyse = raw
            source_note = ""

        # Run the bias analysis
        result = analyse_bias(text_to_analyse)

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "scores": result,
                "text": text_to_analyse[:1200]
                + ("..." if len(text_to_analyse) > 1200 else ""),
                "source_note": source_note,
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "error": str(e),
            },
        )


# git to hf test
