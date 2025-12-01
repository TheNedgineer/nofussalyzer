# scraper.py
from newspaper import Article, Config

# Fake a real browser → fixes 403 Forbidden on some sites (Politico, WSJ, etc.)
config = Config()
config.browser_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
config.request_timeout = 15
config.fetch_images = False  # faster


def extract_article_text(url: str) -> str:
    try:
        article = Article(url, config=config)
        article.download()

        # Check if download succeeded
        if not article.html:
            return "Error: Download failed (site may block bots). Please paste the article text directly."

        article.parse()

        text = article.text.strip()
        if len(text) < 100:
            return "Error: Very little text extracted — try pasting the article text manually."

        return text

    except Exception as e:
        return (
            f"Error: Failed to fetch article — {str(e)}. Try pasting the text directly."
        )
