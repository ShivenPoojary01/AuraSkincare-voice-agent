# Approach --- Aura Skincare AI Voice Support Agent

## 1. Goal

Build a browser-based support assistant that answers Aura Skincare
policy questions, looks up mock orders, supports typed and voice
interactions, and produces a transcript plus a structured call summary.

## 2. Architecture

``` text
Browser UI (templates/index.html)
  ├─ Typed message input
  ├─ Browser speech recognition (where supported)
  ├─ Browser speech synthesis
  ├─ Transcript and call-state indicators
  └─ Structured call summary
          | POST /api/chat
          v
Flask backend (app.py)
  ├─ Session and conversation history
  ├─ Language preference/message detection
  ├─ Deterministic policy/cancellation handling
  ├─ Groq chat completion
  └─ get_order_details(order_id) tool
          v
Mock records: ORD-101, ORD-102, ORD-103
```

## 3. Request lifecycle

1.  The user types a message or speaks using browser speech recognition.
2.  The frontend sends the message to `POST /api/chat`.
3.  Flask maintains relevant conversation state and language preference
    in the session.
4.  Deterministic backend branches handle specific cases; other
    conversational requests go to the configured Groq model.
5.  When order data is needed, the assistant can use
    `get_order_details(order_id)`, which looks up the configured mock
    orders.
6.  Flask returns the assistant response and call-outcome fields as
    JSON.
7.  The frontend updates the transcript and structured summary and may
    speak the response through browser speech synthesis.
8.  Ending/resetting the interaction clears conversation state for a
    fresh session.

## 4. Order lookup and guardrails

The order lookup function is the controlled source for the three mock
orders. The assistant should not invent order records, tracking numbers,
or delivery events. Policy guidance covers shipping, delivery windows,
returns, damaged/defective items, COD, and cancellation eligibility.
Cancellation is limited to eligibility explanation: the assistant must
not claim a cancellation was submitted or completed, and must not invent
support contact details.

## 5. Language handling

The backend detects explicit language switches and can preserve the
selected language preference in the session. It also attempts to
distinguish English, Hindi, and Hinglish. Configured response guidance
uses Devanagari for Hindi and Latin script for Hinglish.

## 6. Voice interface

Voice recognition and text-to-speech run in the browser; this is not a
telephony integration. The interface includes call controls,
listening/thinking/speaking states, retry behavior, and typed chat
fallback. Microphone permission is required and browser support varies.

## 7. Output and limitations

The UI displays the conversation transcript and structured JSON call
summary. The orders are static mock records. No real commerce, CRM,
shipping, payment, cancellation, return, or refund API is connected, and
there is no real customer authentication. Deployment requires
`GROQ_API_KEY` and a strong `FLASK_SECRET_KEY` environment variable.
