# Aura Skincare — AI Voice Support Agent

A browser-based AI customer support agent built for Aura Skincare as part of the DataStraw AI Voice Agent assessment. The application allows customers to interact with Aria, an AI support assistant, through voice or typed messages, ask questions about brand policies, look up predefined mock orders, and review a conversation transcript with a structured JSON summary.

The project focuses on a lightweight architecture, practical voice interaction, controlled order lookup, and policy-aware responses.

## Features

- **Voice interaction:** Browser-based speech recognition and speech synthesis on supported devices and browsers.
- **Typed chat fallback:** Customers can interact with the agent through text when voice functionality is unavailable.
- **AI-powered responses:** Uses the Groq API with the `openai/gpt-oss-20b` model.
- **Order lookup:** Retrieves predefined order details through the `get_order_details(order_id)` function.
- **Language handling:** Supports English, Hindi, and Hinglish response handling.
- **Policy guardrails:** Provides guidance on shipping, delivery timelines, returns, damaged or defective products, cancellation eligibility, and cash on delivery.
- **Conversation management:** Maintains conversation history and language preference during the session.
- **Call interface:** Includes call controls, interaction status indicators, and voice-related feedback.
- **Transcript and structured summary:** Displays the conversation transcript and a JSON-formatted call summary.
- **Responsive interface:** Uses Bootstrap to support a practical interface across different screen sizes.

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Backend | Python, Flask | Handles requests, conversation flow, and application logic |
| AI model access | Groq API | Generates conversational responses |
| Order lookup | Python function | Retrieves details from predefined mock orders |
| Frontend | HTML, CSS, JavaScript | Implements the user interface and interaction logic |
| UI framework | Bootstrap 5 | Provides responsive layout and interface components |
| Voice input | Browser Web Speech APIs | Converts supported browser speech input into text |
| Voice output | Browser speech synthesis | Reads assistant responses aloud |
| Cross-origin support | Flask-CORS | Configures cross-origin request handling |
| Environment configuration | python-dotenv | Loads local environment variables |
| Deployment server | Gunicorn | Serves the Flask application in deployment |

## Architecture and Request Flow

The application uses a lightweight browser-to-backend architecture rather than a heavy frontend framework or a dedicated real-time voice infrastructure.

1. **User input:** The customer speaks through the browser's speech recognition feature or enters a typed message.
2. **Frontend processing:** JavaScript captures the message and sends it to the Flask backend.
3. **Backend processing:** Flask manages the request and conversation context, then communicates with the Groq API when an AI-generated response is needed.
4. **Order lookup:** When order information is required, the model can request the `get_order_details(order_id)` function. The backend executes the function against the predefined mock records and supplies the result for response generation.
5. **Response delivery:** The backend returns the response to the frontend. The interface displays it and uses browser speech synthesis for spoken output when supported.
6. **Conversation summary:** The interface presents the transcript and structured JSON summary for review.

Policy checks and deterministic handling are used for specific scenarios where the application should not rely solely on free-form model responses. For example, an order in `Processing` can be identified as eligible for cancellation, but the application does not execute a real cancellation.

## Project Structure

```text
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

The frontend template belongs in `templates/index.html` because Flask serves it through `render_template("index.html")`.

## Local Setup and Installation

### Prerequisites

- Python 3.10 or later recommended
- A Groq API key
- A modern browser with microphone access and speech API support for voice testing
- Git, if cloning the repository

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_PROJECT_FOLDER
```

Replace the placeholders with the actual public repository URL and project folder name.

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

**macOS/Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to a new file named `.env` and provide your own credentials.

```dotenv
GROQ_API_KEY=your_groq_api_key_here
FLASK_SECRET_KEY=replace_with_a_long_random_secret
```

Use your actual Groq API key locally and a strong, randomly generated Flask secret key. Never commit `.env`, expose API credentials in frontend code, or include real secrets in screenshots or recordings.

### 5. Run the application

```bash
python app.py
```

Open the local URL shown in the terminal, typically:

```text
http://127.0.0.1:5000
```

For voice testing, grant microphone permission when prompted. If the browser does not support the required speech functionality, use the typed chat interface.

## Demo Orders

The application uses predefined mock records for testing. These are not live customer orders.

| Order ID | Customer | Product | Value | Status | Tracking and Notes |
|---|---|---|---:|---|---|
| `ORD-101` | Priya Sharma | Vitamin C Serum (30ml) | ₹699 | Out for Delivery | BlueDart, BD-982103; expected by 6 PM today |
| `ORD-102` | Rahul Verma | Hydrating Sunscreen SPF 50 | ₹499 | Delivered | Delhivery, DL-441029; delivered 14 days ago |
| `ORD-103` | Ananya Patel | Green Tea Face Wash + Toner | ₹850 | Processing | Eligible for cancellation based on the mock order status |

These orders allow the evaluator to test order lookup, delivery information, return eligibility discussions, and cancellation-related responses.

## Configured Aura Skincare Policies

The assistant is configured to answer questions using the following policy guidance:

- **Shipping:** Free delivery on orders above ₹499. Orders below ₹499 have a ₹50 shipping charge.
- **Delivery timeline:** Typically 3–5 business days.
- **Returns:** Products can be returned within 7 days of delivery if they are unopened, unused, and in their original packaging.
- **Damaged or defective products:** Customers should report the issue within 48 hours and provide photos for replacement review.
- **Cancellation:** Cancellation eligibility is limited to orders in the `Processing` status. Orders that are shipped or out for delivery cannot be cancelled through this flow.
- **Cash on Delivery:** Available for orders up to ₹2,500, payable by cash or UPI at the doorstep.

The provided policy wording does not explicitly define the shipping charge for an order exactly equal to ₹499. The application should not invent a boundary rule that is not specified in the policy.

**Important limitation:** These policies guide the demonstration agent. The application does not process actual returns, refunds, replacements, payments, shipments, or cancellations.

## API Overview

### `GET /`

Serves the web interface.

### `POST /api/chat`

Accepts a customer message and returns the assistant response along with the relevant conversation or call-outcome data.

Example request:

```json
{
  "message": "Where is ORD-101?"
}
```

Refer to `app.py` for the exact request and response schema.

### `POST /api/reset`

Resets the current conversation/session.

### `get_order_details(order_id)`

A backend function that normalizes supported order ID formats, retrieves matching records from the mock order data, and returns an error when an order cannot be found.

The function is designed to provide order information from the application's records instead of allowing the model to invent order status or tracking details.

## Deployment on Render

The application can be deployed as a Render Web Service.

1. Push the project to GitHub, excluding `.env` and all real credentials.
2. Create a Web Service on Render and connect the repository.
3. Set the build command:

   ```bash
   pip install -r requirements.txt
   ```

4. Set the start command:

   ```bash
   gunicorn app:app
   ```

5. Add the following environment variables in the deployment dashboard:
   - `GROQ_API_KEY`
   - `FLASK_SECRET_KEY`
6. Deploy the application and open the public URL.
7. Test typed interaction, microphone permissions, voice responses, order lookups, policy questions, and the transcript/summary on desktop and mobile.

The command `gunicorn app:app` assumes that the backend file is `app.py` and the Flask application object is named `app`.

## Design Decisions and Reflection

### 1. Why did you choose this architecture and technology stack?

My main objective was to build a functional AI voice support application within the time available while keeping the architecture lightweight. I wanted to focus on implementing the core requirements rather than introducing heavy frameworks or additional infrastructure that was not necessary for this assignment.

I chose Python and Flask for the backend because they allowed me to implement the API routes, conversation handling, policy logic, and order lookup in a straightforward way. I used the Groq API with the `openai/gpt-oss-20b` model for conversational responses, avoiding the additional complexity of hosting a language model myself.

For the frontend, I chose HTML, CSS, JavaScript, and Bootstrap. Browser-based speech recognition and speech synthesis allowed me to add voice interaction without building a separate speech-processing service. I also implemented a dedicated `get_order_details(order_id)` function so the agent could retrieve order information from controlled mock records.

This stack provided a practical balance between implementation speed, simplicity, and the ability to demonstrate the required features. For the scope of this assignment, I considered it more appropriate than introducing a larger framework or a more complex real-time voice architecture.

### 2. What was the most difficult part of the assignment, and how did you solve it?

One of the most challenging parts was handling English, Hindi, and Hinglish consistently, especially when the customer switched languages during a conversation. I needed the assistant's response language and the browser's spoken output to work together without making the interaction confusing.

Another issue appeared after deployment when I tested the application on a mobile device. The voice interaction entered a loop, which delayed testing and took additional time to troubleshoot. The challenge was coordinating speech recognition, backend processing, and speech synthesis so that the assistant's spoken response would not be picked up again as new customer input.

I addressed these issues by refining the language-handling logic and the voice interaction flow. I also worked on controlling when speech recognition should be active while the backend was processing a request or the assistant was speaking. Testing the hosted application on a phone helped me identify behavior that was not obvious during local development.

This experience showed me that implementing voice functionality involves more than connecting speech recognition to an AI API. The timing and coordination of the different components, browser behavior, and language handling are equally important to a reliable user experience.

### 3. If you had one more week to work on this, what would you improve first and why?

My first priority would be to replace the hard-coded mock order data with a proper database or a secure order-management API. The current records are useful for demonstrating order lookup, but they do not represent a real customer support system.

Using a database would make it possible to manage a larger number of orders, update order statuses, and retrieve information dynamically rather than relying on predefined records. I would also introduce appropriate customer verification and access controls before exposing real order information.

Alongside that improvement, I would continue refining the voice experience, especially language switching, interruptions, error handling, and behavior across desktop and mobile browsers. I would add more test cases for invalid order IDs, unclear requests, API failures, and unsupported browser voice features.

I would prioritize the database integration first because it would move the project beyond a demonstration with mock data and provide a stronger foundation for future functionality.

### 4. Imagine the agent is handling 1,000 customer conversations per day. What needs to change or improve?

I would begin by measuring actual traffic patterns, average conversation length, peak concurrency, response latency, and model API usage. A daily total of 1,000 conversations is useful context, but it does not by itself determine the required infrastructure.

Based on those measurements, I would focus on the following areas:

- **Application scalability:** Run multiple application instances behind a load balancer if the measured traffic requires it, and configure resource limits based on load testing.
- **Session management:** Move session and conversation state to a shared session store if needed for reliable operation across multiple application instances.
- **Database integration:** Replace mock orders with a database or secure order-management API, including appropriate customer authentication and authorization.
- **AI API reliability:** Add request timeouts, controlled retries, rate-limit handling, and graceful error responses when the model API is unavailable.
- **Voice experience:** Test on supported browsers and mobile devices, improve interruption and language-switching behavior, and measure end-to-end response latency.
- **Monitoring:** Track response times, request failures, model API errors, service availability, and usage costs.
- **Security and privacy:** Store credentials securely, use a strong Flask secret key, validate incoming data, restrict access to customer information, and avoid retaining sensitive conversation data unnecessarily.
- **Load testing and cost management:** Simulate expected concurrent usage, identify bottlenecks, and optimize model requests and application resource consumption.

I would make these changes incrementally based on evidence from testing and monitoring rather than assuming that a particular server configuration would automatically handle the workload. The current application is a demonstration with mock data, so supporting production customer conversations would require further work on infrastructure, security, reliability, and integration.

## Limitations and Security Considerations

- The application uses hard-coded mock order records; it is not connected to a live order-management system.
- It does not authenticate customers against real accounts.
- It does not execute real cancellations or process returns, refunds, replacements, payments, or shipments.
- Voice interaction depends on browser/device support and microphone permissions. Typed chat provides an alternative input method.
- The AI API requires valid credentials and network connectivity.
- API keys must remain on the backend and must never be committed to source control.
- A strong `FLASK_SECRET_KEY` must be configured in deployment instead of relying on a development fallback secret.
- A production deployment would require additional security reviews, testing, monitoring, and privacy controls.

## Future Improvements

Potential next steps include:

- Integrating a real database or order-management API.
- Adding customer identity verification and authorization for order-related requests.
- Improving interruption handling and reducing voice-response latency.
- Expanding automated testing for policy rules, language switching, invalid inputs, and API failures.
- Adding structured logging, operational monitoring, and production-grade error handling.
- Evaluating scalability and model usage costs under realistic traffic conditions.

## Acknowledgements

This project was developed as a practical implementation of the DataStraw AI Voice Agent assessment, with a focus on lightweight architecture, conversational AI, browser-based voice interaction, and controlled customer-support workflows.
