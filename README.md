# Aura Skincare --- AI Voice Support Agent

A browser-based customer-support demo for Aura Skincare. It supports
typed chat and browser voice interaction, answers policy questions,
looks up a small set of mock orders, and displays a transcript and
structured call summary.

## Features

-   Browser speech recognition and speech synthesis where supported.
-   Typed chat fallback.
-   Flask backend using the Groq API and `openai/gpt-oss-20b`.
-   Mock order lookup via `get_order_details(order_id)`.
-   Session conversation history and language preference handling.
-   Guardrails for shipping, returns, damaged items, COD, and
    cancellation eligibility.
-   Transcript, call-state indicators, and structured JSON summary.

## Technology

Python, Flask, Flask-CORS, Groq, python-dotenv, Gunicorn,
HTML/CSS/JavaScript, Bootstrap, Font Awesome, browser Web Speech APIs.

## Expected project structure

``` text
aura-skincare/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── APPROACH.md
├── SUBMISSION_CHECKLIST.md
└── templates/
    └── index.html
```

If `app.py` calls `render_template("index.html")`, the HTML file must be
at `templates/index.html`.

## Run locally

Prerequisite: Python 3.10+ recommended and a Groq API key.

1.  Open the project root (the folder containing `app.py`) in VS Code.

2.  Create a virtual environment:

    **Windows PowerShell**

    ``` powershell
    py -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

    If PowerShell blocks activation, use Command Prompt:
    `.venv\Scripts\activate.bat`.

    **macOS/Linux**

    ``` bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Install packages:

    ``` bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4.  Copy `.env.example` to `.env`, then set your own key and a long
    random secret:

    ``` dotenv
    GROQ_API_KEY=your_groq_api_key_here
    FLASK_SECRET_KEY=replace_with_a_long_random_secret
    ```

    Never commit `.env` or show the real key in screenshots.

5.  Start the app:

    ``` bash
    python app.py
    ```

6.  Open `http://127.0.0.1:5000` (or the address printed in the
    terminal).

## Demo test orders

These are mock records, not live customer data.

  ------------------------------------------------------------------------------
  Order ID    Customer    Items                Total Status       Tracking /
                                                                  notes
  ----------- ----------- ----------- -------------- ------------ --------------
  ORD-101     Priya       Vitamin C             ₹699 Out for      BlueDart
              Sharma      Serum                      Delivery     BD-982103;
                                                                  expected by 6
                                                                  PM today

  ORD-102     Rahul Verma Hydrating             ₹499 Delivered    Delivered 14
                          Sunscreen                               days ago;
                          SPF 50                                  Delhivery
                                                                  DL-441029

  ORD-103     Ananya      Green Tea             ₹850 Processing   Eligible for
              Patel       Face Wash +                             cancellation
                          Toner                                   based on mock
                                                                  status; agent
                                                                  does not
                                                                  submit
                                                                  cancellation
  ------------------------------------------------------------------------------

## Configured policy guidance

-   Free shipping on orders over ₹499; ₹50 shipping charge on orders
    below ₹499.
-   Typical delivery: 3--5 business days.
-   Returns within 7 days of delivery if unopened/unused and in original
    packaging.
-   Damaged/defective products should be reported within 48 hours with
    photos for replacement review.
-   Cancellation eligibility is limited to orders in `Processing`; the
    assistant does not execute cancellations.
-   COD for orders up to ₹2,500, payable by cash or UPI at the doorstep.

The policy wording does not explicitly define the shipping fee for an
order exactly equal to ₹499; do not invent a boundary rule.

## API overview

-   `GET /` serves the web interface.
-   `POST /api/chat` accepts JSON such as
    `{"message":"Where is ORD-101?"}` and returns the assistant response
    and call-outcome data. See `app.py` for the exact response schema.
-   `POST /api/reset` resets the current conversation/session.

## Deploy on Render

1.  Push the project to GitHub without `.env` or any API key.
2.  Create a Render **Web Service** connected to the repository.
3.  Build command: `pip install -r requirements.txt`
4.  Start command: `gunicorn app:app`
5.  Add environment variables in Render: `GROQ_API_KEY` and
    `FLASK_SECRET_KEY`.
6.  Deploy, open the URL Render provides, and repeat the local smoke
    tests.

`gunicorn app:app` assumes the backend filename is `app.py` and the
Flask object is named `app`.

## Limitations and security

-   Order records are hard-coded mock data; no real order-management,
    shipping, CRM, payment, return, refund, or cancellation system is
    connected.
-   The app does not authenticate a customer against a real account.
-   Voice support depends on browser/device support and microphone
    permissions; typed chat is the fallback.
-   Keep API keys out of frontend code and source control. Set a strong
    `FLASK_SECRET_KEY` in deployment and do not rely on a development
    fallback secret for a public service.
