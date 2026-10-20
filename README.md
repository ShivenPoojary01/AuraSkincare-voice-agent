# Aura Skincare — AI Voice Support Agent

A browser-based AI voice customer support agent built for Aura Skincare as part of the DataStraw AI Voice Agent assessment.

The application allows customers to interact with Aria, an AI support assistant, through voice or typed messages. Customers can ask questions about Aura Skincare's policies, look up predefined mock orders, and review their conversation transcript and structured JSON summary.

The primary goal of this project was to build a functional, lightweight AI voice support application within the available time, without introducing unnecessarily complex frameworks or infrastructure.

## Features

- **Voice interaction:** Browser-based speech recognition and speech synthesis on supported browsers and devices.
- **Typed chat:** Alternative text input when voice functionality is unavailable.
- **AI-powered responses:** Uses the Groq API with the `openai/gpt-oss-20b` model.
- **Order lookup:** Retrieves order information through the `get_order_details(order_id)` function.
- **Multilingual interaction:** Supports English, Hindi, and Hinglish response handling.
- **Policy guardrails:** Answers questions about shipping, delivery, returns, damaged or defective products, cancellation eligibility, and Cash on Delivery.
- **Conversation history:** Maintains conversation context during the session.
- **Call controls:** Provides call controls and interaction status indicators.
- **Transcript and JSON summary:** Displays the conversation transcript and a structured JSON summary after the interaction.
- **Responsive UI:** Uses Bootstrap to provide a user interface suitable for different screen sizes.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming and application logic |
| Flask | Backend web framework and API routes |
| Groq API | Access to the AI language model |
| `openai/gpt-oss-20b` | Generates conversational responses |
| HTML5 and CSS3 | Frontend structure and styling |
| JavaScript | Frontend interactions and voice flow |
| Bootstrap 5 | Responsive user interface |
| Browser Web Speech APIs | Speech recognition and speech synthesis |
| Flask-CORS | Cross-origin request handling |
| python-dotenv | Loading environment variables |
| Gunicorn | Application server for deployment |

## Architecture and Workflow

The application follows a lightweight browser-to-backend architecture.

1. **User input:** The customer speaks through the browser or enters a message using the text interface.
2. **Frontend processing:** JavaScript captures the input and sends it to the Flask backend.
3. **AI processing:** The backend manages the conversation context and communicates with the Groq API when an AI-generated response is needed.
4. **Function calling:** When order information is required, the model can request the `get_order_details(order_id)` function.
5. **Order retrieval:** The backend executes the function against the predefined mock order records and returns the relevant information.
6. **Response delivery:** The frontend displays the assistant's response and uses browser speech synthesis to speak it aloud when supported.
7. **Conversation summary:** The application displays the transcript and structured JSON summary for review.

Specific policy and cancellation scenarios use deterministic backend handling where appropriate. The application can identify whether a mock order is eligible for cancellation, but it does not execute an actual cancellation.

This architecture allowed me to focus on the core assessment requirements while keeping the implementation manageable and easy to understand.

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

The frontend file should be located at `templates/index.html`, as the Flask backend uses `render_template("index.html")`.

## Installation and Local Setup

### Prerequisites

- Python 3.10 or later recommended
- A Groq API key
- A modern browser
- Microphone access for voice interaction

### 1. Get the project

Clone the repository from GitHub or download the repository files to your computer.

### 2. Install dependencies

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Create a `.env` file in the project root and add your Groq API key:

```dotenv
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your own API key.

Keep your `.env` file private. Do not commit your actual API key to GitHub or expose it in frontend code.

### 4. Run the application

Run the following command:

```bash
python app.py
```

Open the local URL displayed in the terminal, typically:

```text
http://127.0.0.1:5000
```

Allow microphone access when prompted to test voice interaction. If speech recognition is unavailable in your browser, use the typed chat interface.

## Demo Orders

The application uses predefined mock order records to demonstrate order lookup and customer support scenarios.

| Order ID | Customer | Product | Value | Status | Tracking and Notes |
|---|---|---|---|---|---|
| `ORD-101` | Priya Sharma | Vitamin C Serum (30ml) | ₹699 | Out for Delivery | BlueDart — BD-982103; expected by 6 PM today |
| `ORD-102` | Rahul Verma | Hydrating Sunscreen SPF 50 | ₹499 | Delivered | Delhivery — DL-441029; delivered 14 days ago |
| `ORD-103` | Ananya Patel | Green Tea Face Wash + Toner | ₹850 | Processing | Ordered 3 hours ago; eligible for cancellation |

These records allow the evaluator to test order lookups, delivery information, return-policy questions, and cancellation eligibility.

**Note:** These are demonstration records, not live customer orders.

## Aura Skincare Policies

The assistant is configured to answer customer questions using the following policy information.

### Shipping and Delivery

- Free delivery applies to orders above ₹499.
- Orders below ₹499 have a ₹50 shipping charge.
- The typical delivery timeline is 3–5 business days.

### Returns

- Returns are accepted within 7 days if the product is unopened, unused, and in its original packaging.

### Damaged or Defective Products

- Customers should report damage or defects within 48 hours.
- Photos must be provided for replacement review.

### Order Cancellation

- Cancellation is available only while an order is in the `Processing` status.
- Orders that have been shipped or are out for delivery cannot be cancelled through this flow.

### Cash on Delivery

- COD is available for orders up to ₹2,500.
- Customers can pay by cash or UPI at the doorstep.

The supplied policy does not explicitly define the shipping charge for an order exactly equal to ₹499. The application should not invent a policy for that boundary case.

**Important limitation:** The application provides policy guidance but does not process real returns, refunds, replacements, payments, shipments, or cancellations.

## API Overview

### `GET /`

Serves the web interface.

### `POST /api/chat`

Accepts a customer message and processes the conversation through the backend.

Example request:

```json
{
  "message": "Where is ORD-101?"
}
```

Refer to `app.py` for the exact request and response structure.

### `POST /api/reset`

Resets the current conversation session.

### `get_order_details(order_id)`

A backend function that normalizes supported order ID formats, retrieves matching information from the predefined mock records, and returns an error when an order cannot be found.

This helps the agent retrieve order details from controlled data instead of relying on the language model to invent order statuses or tracking information.

## Deployment

The application is deployed on Render and can be accessed through its public application URL.

For deployment or redeployment:

1. Push the project files to GitHub.
2. Create or open the Render Web Service connected to the repository.
3. Use the following build command:

   ```bash
   pip install -r requirements.txt
   ```

4. Use the following start command:

   ```bash
   gunicorn app:app
   ```

5. Add `GROQ_API_KEY` to the environment variables in the Render dashboard.
6. Deploy the application and open its public URL.
7. Test voice input, typed chat, order lookup, policy responses, and the transcript/JSON summary.

The start command assumes the backend file is named `app.py` and the Flask application object is named `app`.

Voice functionality depends on browser support, microphone permissions, and network connectivity. Testing on both desktop and mobile devices is recommended.

## Design Decisions and Reflection

### 1. Why did you choose your particular architecture and technology stack?

My main objective was to build a functional AI voice support application within the given time while keeping the architecture lightweight. I wanted to focus on implementing the core requirements rather than introducing heavy frameworks or unnecessary infrastructure.

I chose Python and Flask for the backend because they allowed me to implement the API routes, conversation handling, policy logic, and order lookup in a straightforward way. I used the Groq API with the `openai/gpt-oss-20b` model for conversational responses, avoiding the additional complexity of hosting a language model myself.

For the frontend, I chose HTML, CSS, JavaScript, and Bootstrap. Browser-based speech recognition and speech synthesis allowed me to implement voice interaction without building a separate speech-processing service.

I also created a dedicated `get_order_details(order_id)` function so that order information could be retrieved from controlled mock records.

Overall, I considered this stack a practical choice for completing the assignment on time. It allowed me to demonstrate the required functionality without adding complexity that was not necessary for the project's scope.

### 2. What was the most difficult part of the assignment, and how did you solve it?

One of the most challenging parts was handling English, Hindi, and Hinglish consistently, particularly when the customer switched languages during a conversation. Making the assistant respond in the appropriate language while keeping the spoken output consistent required additional refinement.

I also encountered an issue after deployment when I tested the application on a mobile device. The voice interaction entered a loop, which delayed testing and took additional time to troubleshoot. The problem highlighted the difficulty of coordinating speech recognition, backend processing, and speech synthesis without accidentally treating the assistant's spoken response as new customer input.

I worked on refining the language-handling logic and the voice interaction flow, including controlling when speech recognition should be active while the backend was processing a request or the assistant was speaking.

Testing the deployed application on a phone helped me identify issues that were not as apparent during local development. This experience taught me that building a voice application involves more than connecting speech recognition to an AI API. The coordination between components, language handling, and browser behavior also play an important role in delivering a reliable experience.

### 3. If you had one more week to work on this, what would you improve first and why?

My first priority would be to replace the hard-coded mock order data with a proper database or a secure order-management API.

The current mock records are useful for demonstrating order lookup, but they do not represent a real customer support system. A database would make it possible to store and manage more orders, retrieve information dynamically, and update order statuses without modifying the application's code.

I would also introduce appropriate customer verification and access controls before exposing real order information.

Alongside this improvement, I would continue refining the voice experience, especially language switching, interruption handling, error handling, and compatibility across desktop and mobile browsers. I would add more test cases for invalid order IDs, unclear customer requests, and API failures.

I would prioritize database integration because it would move the application beyond a demonstration using predefined data and provide a stronger foundation for future improvements.

### 4. Imagine the agent is handling 1,000 customer conversations per day. What needs to change or improve?

I would begin by measuring actual traffic patterns, average conversation length, peak concurrency, response latency, and model API usage. A daily total of 1,000 conversations does not by itself determine the infrastructure required.

Based on those measurements, I would focus on the following areas:

- **Application scalability:** Run multiple application instances behind a load balancer if testing shows that the existing deployment cannot handle the required traffic.
- **Session management:** Use a shared session store if needed to maintain conversation state reliably across multiple application instances.
- **Database integration:** Replace mock orders with a database or secure order-management API, with appropriate customer authentication and authorization.
- **AI API reliability:** Add request timeouts, controlled retries, rate-limit handling, and graceful responses when the model API is unavailable.
- **Voice experience:** Improve interruption handling, language switching, and end-to-end response latency across supported browsers and devices.
- **Monitoring:** Track response times, errors, API usage, and service availability to identify bottlenecks.
- **Security and privacy:** Protect API credentials, validate input, restrict access to customer information, and avoid unnecessary retention of sensitive conversation data.
- **Load testing and cost management:** Simulate expected concurrent usage, measure system performance, and optimize model requests and resource consumption.

I would implement these improvements incrementally based on the results of testing and monitoring rather than assuming a particular server configuration would automatically handle the workload.

The current project is a demonstration using mock data. Supporting production-level customer conversations would require further work on infrastructure, security, reliability, and integration.

## Limitations and Security Considerations

- The application uses predefined mock order records and is not connected to a live order-management system.
- It does not authenticate customers against real accounts.
- It does not execute actual cancellations or process returns, refunds, replacements, payments, or shipments.
- Voice functionality depends on browser support and microphone permissions.
- The application requires a valid Groq API key and network connectivity.
- API credentials must remain on the backend and must never be committed to source control.
- The current code uses a fallback Flask session secret if `FLASK_SECRET_KEY` is not configured. This should be replaced with a strong, randomly generated secret before production use.
- A production deployment would require further security reviews, monitoring, privacy controls, and reliability testing.

## Future Improvements

Potential next steps include:

- Integrating a database or order-management API.
- Adding customer verification and authorization for order-related requests.
- Improving voice interruption handling and reducing response latency.
- Expanding testing for language switching, invalid inputs, policy rules, and API failures.
- Adding structured logging and operational monitoring.
- Evaluating performance and model usage costs under realistic traffic.

## Acknowledgements

Developed as a practical implementation of the DataStraw AI Voice Agent assessment, with a focus on lightweight architecture, conversational AI, browser-based voice interaction, and controlled customer support workflows.
