from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai
import html

# Load .env
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

app = Flask(__name__)

MODEL_ID = "gemini-1.5-flash"
model = genai.GenerativeModel(MODEL_ID)

ARTICLE_SYSTEM_INSTRUCTIONS = """You are an assistant that writes clean HTML articles.
Output ONLY HTML (no markdown). Structure with:
- <h1> title
- <p> paragraphs
- <h2>/<h3> subheadings
- <ul>/<ol> lists when helpful
- <strong>/<em> sparingly
Do not include <html>, <head>, or <body> tags. Return valid, minimal HTML only.
"""

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", article_html=None)

@app.route("/generate", methods=["POST"])
def generate():
    try:
        user_prompt = request.form.get("prompt", "").strip()
        if not user_prompt:
            return render_template("index.html", article_html="<p>Error: No prompt provided.</p>")

        prompt = (
            f"{ARTICLE_SYSTEM_INSTRUCTIONS}\n\n"
            f"Write a full-length, well-structured article for the title: \"{html.escape(user_prompt)}\".\n"
            f"Target length: ~900-1200 words. Use clear subheadings and short paragraphs."
        )

        resp = model.generate_content(prompt)
        article_html = (resp.text or "").strip()

        # Fallback if Gemini returns plain text
        if "<h1" not in article_html and "<p" not in article_html:
            parts = [f"<p>{html.escape(p.strip())}</p>" for p in article_html.split("\n\n") if p.strip()]
            article_html = "<h1>" + html.escape(user_prompt) + "</h1>" + "".join(parts)

        return render_template("index.html", article_html=article_html)

    except Exception as e:
        return render_template("index.html", article_html=f"<p><strong>Error:</strong> {html.escape(str(e))}</p>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
