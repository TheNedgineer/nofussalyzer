# app.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from zs_bias_model import analyse_bias
from scraper import extract_article_text
import traceback

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
        raw_input = input.strip()
        if not raw_input:
            raise ValueError("No input provided.")

        # Smart URL detection
        if raw_input.lower().startswith(("http://", "https://")):
            print(f"Fetching URL: {raw_input}")
            text = extract_article_text(raw_input)
            if not text or "Error" in text or len(text) < 50:
                raise ValueError("Could not extract meaningful text from the URL.")
        else:
            text = raw_input
            if len(text) < 15:
                raise ValueError("Please enter at least a short sentence.")

        print(f"Analysing text (first 200 chars): {text[:200]}...")
        scores = analyse_bias(text)  # ← this line creates the 'scores' variable

        # ——— SHARE ON X: now safe because scores is guaranteed to exist here ———
        result_url = str(request.url)

        share_text = (
            f"AI just rated this as {scores['predicted_bias']} "
            f"({scores['confidence']:.0%} confidence) on the Political Bias Analyzer\n\n"
            f"\"{text.strip()[:140].rstrip('.')}\"...\""
        )
        share_text = share_text[:260]  # stay under X's limits

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "scores": scores,
                "text": text[:1000],
                "share_text": share_text,
                "share_url": result_url,
            },
        )

    except Exception as e:
        error_msg = f"Oops! Something went wrong: {str(e)}"
        print(f"ERROR DETAILS: {error_msg}\n{traceback.format_exc()}")

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "error": error_msg + " (Check console for details)",
                # Provide defaults so result.html never crashes
                "share_text": "",
                "share_url": "",
            },
        )
