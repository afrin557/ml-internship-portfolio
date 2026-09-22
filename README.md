# ML Internship Portfolio + AI Chatbot (Python + OpenAI API)

A responsive portfolio website for an ML internship assignment with a Python Flask backend and an OpenAI-powered portfolio assistant.

## Stack
- HTML5 + CSS3 — semantic, responsive portfolio UI
- Vanilla JavaScript — navigation and chatbot interactions
- Python + Flask — backend and `/api/chat` endpoint
- OpenAI Python SDK + Responses API — AI chatbot
- python-dotenv — local `.env` loading
- Git + GitHub — version control
- Gunicorn / Docker — deployment

## 1. Create and activate a virtual environment

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure the OpenAI API key

Create `.env` from `.env.example`:

### Windows PowerShell
```powershell
Copy-Item .env.example .env
```

### macOS / Linux
```bash
cp .env.example .env
```

Open `.env` and replace the placeholder:

```env
OPENAI_API_KEY=sk-your-real-key-here
OPENAI_MODEL=gpt-5.6-luna
PORT=5000
FLASK_DEBUG=0
```

The API key stays on the Python server. **Do not put it in HTML, JavaScript, `profile.json`, or GitHub.**

## 4. Add the student's real portfolio data

Edit:

```text
data/profile.json
```

Fill in the real:
- name and headline
- education
- technical skills
- internship experience
- ML projects
- certifications
- achievements
- email/phone/city
- GitHub and LinkedIn

The chatbot automatically receives this profile as its grounded context, so no personal information needs to be duplicated in the Python prompt.

## 5. Run the website

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

The chatbot is available from the floating `✦` button.

## 6. Test the chatbot

Try questions such as:
- What are the student's machine learning projects?
- What programming languages does the student know?
- Where did the student intern?
- What certifications are listed?
- What is the student's educational background?

The assistant is instructed to answer only from `data/profile.json` and say when information is unavailable.

## 7. Check API configuration

Open:

```text
http://127.0.0.1:5000/api/health
```

Example:
```json
{
  "status": "ok",
  "chatbot": "ai",
  "model": "gpt-5.6-luna"
}
```

This endpoint never returns the API key.

## 8. Version control

```bash
git init
git add .
git commit -m "Build ML portfolio with AI chatbot"
```

The included `.gitignore` excludes `.env`, virtual environments, caches, and generated files.

## 9. Deployment

Set `OPENAI_API_KEY` as a server-side environment variable in your hosting provider. Do not upload `.env`.

For Gunicorn-compatible hosting:
```bash
gunicorn app:app
```

For Docker:
```bash
docker build -t ml-portfolio .
docker run --rm -p 5000:5000 --env-file .env ml-portfolio
```

## Assignment mapping
- Basic web development → semantic HTML/CSS
- Frontend development → responsive layout + JavaScript
- ML/AI integration → Python Flask + OpenAI Responses API
- Version control → Git-ready repository structure
- UI/UX design → responsive cards, navigation, accessible chatbot controls
- Development → Flask backend and JSON data layer
- Deployment → Gunicorn + Docker
- Chatbot development → portfolio-grounded AI chatbot with fallback mode


## 10. Free deployment with Render

This project is ready for a Render **Web Service** deployment.

1. Create a GitHub repository and upload the contents of `ml_portfolio`.
2. In Render, choose **New → Web Service** and connect the GitHub repository.
3. Choose the **Free** instance.
4. Render can use the included `Procfile`. The start command is:
   `gunicorn --bind 0.0.0.0:$PORT app:app`
5. In Render → Environment, add:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `OPENAI_MODEL` = `gpt-5.6-luna`
   - `OPENAI_TIMEOUT` = `45`
6. Deploy and open the generated HTTPS URL.

**Important:** never commit `.env` or put the API key in `app.js`, HTML, or `profile.json`.

### About "always working" on a free website

The chatbot is designed to keep responding through the local portfolio fallback when the AI API is temporarily unavailable. However, no free hosting service can guarantee an always-on AI backend. For example, Render's free web services spin down after 15 minutes without traffic and take time to wake on the next request. The OpenAI API is also a paid API service; the API key itself does not make API usage free.

For a continuously running public chatbot, use a hosting plan that stays running and an OpenAI API account with available billing/credits.
