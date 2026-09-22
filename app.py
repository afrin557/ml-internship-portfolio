import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "profile.json"

# Load local .env values for development. Production systems should set
# environment variables directly in the hosting platform.
load_dotenv(BASE_DIR / ".env")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    PROFILE = json.load(f)

app = Flask(__name__)

SYSTEM_PROMPT = """
You are the AI portfolio assistant for a student's ML internship portfolio.
Answer questions only from the supplied portfolio profile below.
Do not invent personal details, grades, employers, technologies, projects, dates,
certifications, links, or achievements.
If the profile does not contain the answer, clearly say that the information is not
available in the portfolio. Do not guess.
Keep answers concise, friendly, and professional.
When useful, mention the relevant portfolio section or project name.

PORTFOLIO PROFILE:
""" + json.dumps(PROFILE, indent=2, ensure_ascii=False)


def local_fallback(message: str) -> str:
    """Offline fallback so the portfolio still works without an API key."""
    q = message.lower()
    sections = {
        "profile": PROFILE.get("about", ""),
        "about": PROFILE.get("about", ""),
        "skill": "Skills: " + ", ".join(PROFILE.get("skills", [])),
        "education": "Education: " + "; ".join(
            f"{x['degree']} — {x['institution']} ({x['year']})"
            for x in PROFILE.get("education", [])
        ),
        "internship": "Internships: " + "; ".join(
            f"{x['role']} at {x['company']} ({x['period']})"
            for x in PROFILE.get("internships", [])
        ),
        "project": "Projects: " + "; ".join(
            x["name"] for x in PROFILE.get("projects", [])
        ),
        "certification": "Certifications: " + "; ".join(
            PROFILE.get("certifications", [])
        ),
        "achievement": "Achievements: " + "; ".join(
            PROFILE.get("achievements", [])
        ),
        "contact": (
            f"Email: {PROFILE['contact']['email']} | "
            f"GitHub: {PROFILE['links']['github']} | "
            f"LinkedIn: {PROFILE['links']['linkedin']}"
        ),
    }
    for key, answer in sections.items():
        if key in q:
            return answer
    return (
        "I can answer questions about the student's profile, skills, education, "
        "internships, ML projects, certifications, achievements, and contact information."
    )


def get_openai_client():
    """Return an OpenAI client when the SDK and API key are configured."""
    if OpenAI is None:
        return None
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key.startswith("sk-your-"):
        return None

    # The SDK also retries transient failures, which helps with short-lived
    # network/API connection problems.
    return OpenAI(
        api_key=api_key,
        timeout=float(os.getenv("OPENAI_TIMEOUT", "45")),
        max_retries=3,
    )


@app.get("/")
def index():
    return render_template("index.html", profile=PROFILE)


@app.get("/api/profile")
def profile():
    return jsonify(PROFILE)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "chatbot": "ai" if get_openai_client() else "fallback",
        "model": os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
    })


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400
    if len(message) > 1000:
        return jsonify({"error": "Please keep your question under 1000 characters."}), 400

    client = get_openai_client()
    if client is None:
        # The site remains usable even before the API key is configured.
        return jsonify({
            "reply": local_fallback(message),
            "mode": "fallback"
        })

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            input=[
                {
                    "role": "developer",
                    "content": [
                        {"type": "input_text", "text": SYSTEM_PROMPT}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": message}
                    ],
                },
            ],
        )

        reply = (response.output_text or "").strip()
        if not reply:
            raise RuntimeError("The API returned an empty response.")

        return jsonify({"reply": reply, "mode": "ai"})

    except Exception as exc:
        app.logger.exception("OpenAI chatbot error")

        # Keep the chatbot functional if the API/network has a temporary issue.
        return jsonify({
            "reply": (
                "The AI service could not be reached right now. "
                "Here is the portfolio information I can provide locally:\n\n"
                + local_fallback(message)
            ),
            "mode": "fallback",
            "error": type(exc).__name__,
        })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
