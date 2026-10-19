# Submission Checklist --- Aura Skincare AI Voice Support Agent

## Project files

-   [ ] Backend filename is `app.py`.
-   [ ] Frontend is `templates/index.html` if Flask uses
    `render_template("index.html")`.
-   [ ] `requirements.txt` includes the dependencies and `gunicorn` for
    Render.
-   [ ] `README.md`, `APPROACH.md`, and `.env.example` are in the
    project root.
-   [ ] `.env` is local-only and not committed.
-   [ ] `.gitignore` excludes `.env`, `.venv/`, `__pycache__/`, and
    local/generated files.

## Local testing

-   [ ] Activate the virtual environment and run
    `pip install -r requirements.txt`.
-   [ ] Add a valid `GROQ_API_KEY` to `.env`.
-   [ ] Run `python app.py` and open the local URL.
-   [ ] Test a general policy question.
-   [ ] Test `ORD-101`, `ORD-102`, and `ORD-103`.
-   [ ] Test cancellation eligibility for `ORD-103`; ensure the app does
    not claim to cancel it.
-   [ ] Review the transcript and structured summary.
-   [ ] Test voice with microphone permission, if supported, and typed
    chat as fallback.
-   [ ] End/reset the call and start a fresh one.

## GitHub

-   [ ] Open the correct project root in VS Code.
-   [ ] Check `git status` before staging files.
-   [ ] Confirm `.env` and all real API keys are excluded.
-   [ ] Commit and push source files and documentation.
-   [ ] Open the repository in a browser and verify the files are
    present.

## Render deployment

-   [ ] Connect the repository to a Render Web Service.
-   [ ] Build command: `pip install -r requirements.txt`.
-   [ ] Start command: `gunicorn app:app`.
-   [ ] Add `GROQ_API_KEY` and a long random `FLASK_SECRET_KEY` in
    Render environment variables.
-   [ ] Deploy and wait for the service to become live.
-   [ ] Open the Render URL and repeat the smoke tests.
-   [ ] Include the deployed URL in submission details only after
    verifying it works.

## Demo preparation

-   [ ] Demonstrate a policy question, an order lookup, cancellation
    eligibility, and transcript/summary.
-   [ ] Explain that orders are mock data and no real cancellation is
    performed.
-   [ ] Do not show `.env` or reveal API keys in a screen recording.
-   [ ] Confirm the README reflects the final repository structure.
