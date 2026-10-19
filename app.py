import os
import json
import re
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "aura-skincare-secret-key-123")
CORS(app)

# Initialize Groq Client
GROQ_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_KEY)

# Mock Order Database
MOCK_ORDERS = {
    "ORD-101": {
        "order_id": "ORD-101",
        "customer": "Priya Sharma",
        "product": "Vitamin C Serum (30ml)",
        "value": "₹699",
        "status": "Out for Delivery",
        "notes": "BlueDart - BD-982103. Expected by 6 PM today"
    },
    "ORD-102": {
        "order_id": "ORD-102",
        "customer": "Rahul Verma",
        "product": "Hydrating Sunscreen SPF 50",
        "value": "₹499",
        "status": "Delivered",
        "notes": "Delhivery DL-441029. Delivered 14 days ago"
    },
    "ORD-103": {
        "order_id": "ORD-103",
        "customer": "Ananya Patel",
        "product": "Green Tea Face Wash + Toner",
        "value": "₹850",
        "status": "Processing",
        "notes": "Ordered 3 hours ago. Eligible for cancellation"
    }
}


def get_order_details(order_id: str):
    """Retrieve order details after normalizing common spoken order ID formats."""
    clean_id = str(order_id or "").strip().upper()

    # Normalize spoken formats such as "ORD 101" and "order ID 101".
    match = re.fullmatch(
        r"(?:ORD|ORDER(?:\s+ID|\s+NUMBER)?)\s*[- ]?\s*(10[1-3])",
        clean_id
    )

    if match:
        clean_id = f"ORD-{match.group(1)}"
    elif re.fullmatch(r"10[1-3]", clean_id):
        clean_id = f"ORD-{clean_id}"

    if clean_id in MOCK_ORDERS:
        return MOCK_ORDERS[clean_id]

    return {"error": f"Order ID {clean_id} was not found."}


def detect_explicit_language_switch(message):
    """Return a language only when the customer explicitly requests a switch."""
    text = str(message or "").lower().strip()

    phrases = {
        "hinglish": [
            "hinglish mein bolo", "hinglish me bolo", "speak in hinglish",
            "reply in hinglish", "hinglish mein baat karo", "hinglish me baat karo",
        ],
        "hindi": [
            "hindi mein bolo", "hindi me bolo", "hindi mein baat karo",
            "hindi me baat karo", "speak in hindi", "reply in hindi",
            "respond in hindi", "hindi mein jawab do", "hindi me jawab do",
            "hindi bolo", "हिंदी में बोलो", "हिंदी में बात करो", "हिंदी में जवाब दो",
        ],
        "english": [
            "english mein bolo", "english me bolo", "english mein baat karo",
            "english me baat karo", "speak in english", "reply in english",
            "respond in english", "switch to english", "now speak english",
            "अंग्रेज़ी में बोलो", "अंग्रेजी में बोलो",
        ],
    }
    for language in ("hinglish", "hindi", "english"):
        if any(phrase in text for phrase in phrases[language]):
            return language
    return None


def language_instruction(language):
    """Build a per-request instruction without polluting saved conversation history."""
    instructions = {
        "hindi": (
            "PERSISTENT LANGUAGE PREFERENCE: The customer explicitly chose Hindi. "
            "Reply in natural Hindi written in Devanagari for this and every following "
            "turn until they explicitly request another language. Do not switch to English "
            "or Hinglish just because their message contains English words. Preserve order "
            "IDs, product names, courier names, and tracking codes exactly."
        ),
        "english": (
            "PERSISTENT LANGUAGE PREFERENCE: The customer explicitly chose English. "
            "Reply in English for every following turn until they explicitly request another "
            "language. Do not switch because their message contains Hindi or Hinglish. "
            "Preserve order IDs, product names, courier names, and tracking codes exactly."
        ),
        "hinglish": (
            "PERSISTENT LANGUAGE PREFERENCE: The customer explicitly chose Hinglish. "
            "Reply in natural conversational Hinglish using Latin script for every following "
            "turn until they explicitly request another language. Preserve order IDs, product "
            "names, courier names, and tracking codes exactly."
        ),
    }
    return instructions.get(language)


def build_model_messages(history, language):
    """Copy history and add the current language preference as a temporary system message."""
    result = list(history)
    instruction = language_instruction(language)
    if instruction and result and result[0].get("role") == "system":
        result.insert(1, {"role": "system", "content": instruction})
    return result


def format_order_response(order_id, order, language):
    """Render trusted mock-order facts in the selected language without changing values."""
    product = order["product"]
    value = order["value"]
    if language == "hindi":
        if order_id == "ORD-101":
            return (f"आपका ऑर्डर {order_id}, {product} ({value}), BlueDart के ज़रिए डिलीवरी के लिए निकल चुका है। "
                    "ट्रैकिंग कोड BD-982103 है और इसके आज शाम 6 बजे तक पहुँचने की उम्मीद है।")
        if order_id == "ORD-102":
            return (f"आपका ऑर्डर {order_id}, {product} ({value}), Delhivery के ज़रिए डिलीवर हो चुका है। "
                    "ट्रैकिंग कोड DL-441029 है और यह 14 दिन पहले डिलीवर हुआ था।")
        return (f"आपका ऑर्डर {order_id}, {product} ({value}), अभी Processing में है। इसे 3 घंटे पहले दिया गया था "
                "और यह कैंसिलेशन के लिए योग्य है। मैं ऑर्डर कैंसिल नहीं कर सकता या अनुरोध सबमिट नहीं कर सकता; "
                "इसके लिए Aura Skincare के आधिकारिक सपोर्ट चैनल से संपर्क करें। मैंने ऑर्डर कैंसिल नहीं किया है।")
    if language == "hinglish":
        if order_id == "ORD-101":
            return (f"Aapka order {order_id}, {product} ({value}), BlueDart ke through out for delivery hai. "
                    "Tracking code BD-982103 hai aur expected delivery aaj shaam 6 baje tak hai.")
        if order_id == "ORD-102":
            return (f"Aapka order {order_id}, {product} ({value}), Delhivery ke through deliver ho chuka hai. "
                    "Tracking code DL-441029 hai aur yeh 14 din pehle deliver hua tha.")
        return (f"Aapka order {order_id}, {product} ({value}), abhi Processing mein hai. Yeh 3 ghante pehle place hua tha "
                "aur cancellation ke liye eligible hai. Main order cancel ya cancellation request submit nahi kar sakta; "
                "please Aura Skincare ke official support channel se contact karein. Maine order cancel nahi kiya hai.")
    if order_id == "ORD-101":
        return (f"Your order {order_id} for {product} ({value}) is currently Out for Delivery via BlueDart "
                "(tracking BD-982103). It is expected to arrive by 6 PM today.")
    if order_id == "ORD-102":
        return (f"Your order {order_id} for {product} ({value}) has been Delivered via Delhivery "
                "(tracking DL-441029). It was delivered 14 days ago.")
    return (f"Your order {order_id} for {product} ({value}) is currently Processing. It was placed 3 hours ago "
            "and is eligible for cancellation. I cannot cancel it or submit a cancellation request; please contact "
            "Aura Skincare's official support channel. I have not cancelled the order.")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_details",
            "description": "Fetch status, shipping details, and items for a specific order ID (e.g., ORD-101).",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID to look up, e.g., ORD-101"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]

ARIA_SYSTEM_PROMPT = """
You are Aria, a warm, professional, and empathetic AI customer support voice agent for Aura Skincare.

CRITICAL LANGUAGE MATCHING AND LANGUAGE-SWITCH RULES:
- An explicit request to change language ALWAYS overrides language detection from the latest message.
- If the customer says things like "Hindi mein bolo", "Hindi me baat karo", "please speak Hindi", or "हिंदी में बोलो", immediately switch to Hindi.
- When Hindi is requested, respond in natural, conversational Hindi written in Devanagari script. Do NOT respond in Latin-script Hinglish unless the customer explicitly asks for Hinglish.
- If the customer explicitly requests English, respond entirely in English.
- If the customer explicitly requests Hinglish, respond naturally in Hinglish using Latin script.
- Remember the customer's explicitly selected language for the remainder of the active conversation, until they request another language. A language-switch request should not itself be treated as an ordinary Hinglish message.
- If no explicit language preference has been set, match the language of the customer's latest message: English -> English, Hindi -> Hindi in Devanagari, Hinglish -> natural Hinglish.
- Order IDs, product names, courier names, and tracking codes must remain unchanged; translate the surrounding sentence into the selected language.
- These rules apply to every response, including errors, order lookup results, clarifying questions, and apologies.
- If uncertain and the customer has not explicitly selected a language, default to English.

CRITICAL GUARDRAILS & POLICIES TO ENFORCE:
1. Shipping Policy: Free delivery on orders above ₹499. Orders below ₹499 incur a ₹50 shipping fee. Standard delivery time is 3-5 business days.
2. Return Policy: Returns are accepted within 7 days of delivery only for unopened, unused products in original packaging. Damaged/defective items must be reported within 48 hours with photos. State only these provided conditions; do not claim that no other conditions apply.
3. Cancellation Policy: Orders can ONLY be cancelled while status is 'Processing'. Once 'Shipped' or 'Out for Delivery', cancellations are not permitted.
4. Cash on Delivery (COD): COD is available for orders up to ₹2,500. Customers can pay using cash or UPI at the doorstep. For orders above ₹2,500, COD is unavailable and the customer must use an available alternative payment method.
5. Out-of-Scope Requests: If asked about topics unrelated to Aura Skincare (flights, weather, movies, sports), politely inform the customer that you can only assist with Aura Skincare products and orders.
6. Cancellation Action Safety:
- You can check cancellation eligibility, but you CANNOT cancel orders or submit cancellation requests.
- If an order is in 'Processing', say it is eligible for cancellation and instruct the customer to contact Aura Skincare's official support channel to request cancellation.
- Explicitly clarify that the order has NOT been cancelled by this assistant.
- NEVER claim or imply that a cancellation request has been submitted or that an email, refund, or other follow-up action will occur unless a backend tool explicitly confirms that action.
- Do not invent support contact details, website links, app pages, or cancellation procedures that are not provided in the available information.
- If the order is 'Shipped' or 'Out for Delivery', explain that it cannot be cancelled under the stated policy.
- If asked whether an order has already been cancelled, clearly state that this assistant has not cancelled it.
7.Return and Support Action Safety: For damaged or defective products, explain that the customer must report the issue within 48 hours and provide photos. Never invent support email addresses, phone numbers, account pages, upload links, or other contact channels. If the customer asks where to send photos and no verified channel is available in the provided information, explain that the correct submission channel has not been provided and they should contact the official Aura Skincare support channel. Never promise a return, replacement, or refund unless an actual backend tool confirms the action.

VOICE STYLE & FORMATTING INSTRUCTIONS:
- Keep answers short, natural, and conversational (1-3 sentences maximum).
- Answer only the customer's specific question. Do not add unsolicited shipping fees, tracking instructions, or other order details unless relevant to the question.
- DO NOT use markdown symbols like asterisks (**), hashes (#), or bullet points in your response text because this text is read aloud by a voice synthesizer. Speak in clean plain text only!
- When retrieving order details, always call the `get_order_details` tool function and remember context within the current active session.
"""

def get_session_history():
    """Retrieve or initialize conversation history per session."""
    if "history" not in session:
        session["history"] = [{"role": "system", "content": ARIA_SYSTEM_PROMPT}]
    return session["history"]

@app.route("/")
def index():
    # Clear and reset conversation history and order summary for a fresh call.
    session["history"] = [{"role": "system", "content": ARIA_SYSTEM_PROMPT}]
    session["orders_discussed"] = []
    session["response_language"] = "auto"
    return render_template("index.html")

@app.route("/api/reset", methods=["POST"])
def reset_call():
    """Explicitly reset the conversation when a call ends."""
    session["history"] = [{"role": "system", "content": ARIA_SYSTEM_PROMPT}]
    session["orders_discussed"] = []
    session["response_language"] = "auto"
    return jsonify({"success": True, "message": "Call session reset successfully."})

@app.route("/api/chat", methods=["POST"])

def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "success": False,
            "error": "Empty message"
        }), 400

    # Keep an explicit language choice for the whole active call. Ordinary messages
    # do not reset it; only another explicit language request changes it.
    requested_language = detect_explicit_language_switch(user_message)
    if requested_language:
        session["response_language"] = requested_language
    response_language = session.get("response_language", "auto")

    history = get_session_history()
    history.append({
        "role": "user",
        "content": user_message
    })

    intent = "GENERAL_INQUIRY"
    detected_order_id = None
    resolution_status = "PENDING"

    # Distinguish policy/process questions from requests to check cancellation eligibility.
    is_cancellation_policy_question = bool(re.search(
        r"\b(?:cancellation policy|cancel(?:lation)? policy|policy on cancellations?|rules for cancellations?)\b",
        user_message,
        re.IGNORECASE
    ))
    is_cancellation_process_question = bool(re.search(
        r"\b(?:cancellation process|process to cancel|how (?:do|can|should) i cancel|how to cancel|steps to cancel|procedure for cancellation|what is the process)\b",
        user_message,
        re.IGNORECASE
    ))
    is_cancellation_request = bool(re.search(
        r"\b(?:i want to cancel|i'd like to cancel|i would like to cancel|please cancel|cancel (?:this|the|my|order|product)|can i cancel|could i cancel|would like to cancel)\b",
        user_message,
        re.IGNORECASE
    ))
    try:
            # Answer general cancellation policy/process questions without treating
            # them as a new request to cancel a specific order.
            if is_cancellation_policy_question:
                intent = "POLICY_OR_ISSUE"
                final_reply = (
                    "Aura Skincare's policy allows cancellation only while an order is "
                    "Processing. Orders that are Shipped or Out for Delivery cannot be "
                    "cancelled. This assistant cannot cancel orders or submit requests."
                )
                resolution_status = "RESOLVED"
                history.append({"role": "assistant", "content": final_reply})

            elif is_cancellation_process_question:
                intent = "POLICY_OR_ISSUE"
                final_reply = (
                    "Under Aura Skincare's stated policy, an order can be requested for "
                    "cancellation only while it is Processing. Please contact Aura "
                    "Skincare's official support channel to request cancellation. "
                    "This assistant cannot submit the request, and no cancellation "
                    "has been completed here. No more specific support steps or contact "
                    "details have been provided."
                )
                resolution_status = "RESOLVED"
                history.append({"role": "assistant", "content": final_reply})

            # Handle direct requests to check cancellation eligibility safely.
            elif is_cancellation_request:
                intent = "ORDER_CANCELLATION"

                # First try to extract the order ID from the latest message.
                order_match = re.search(
                    r"\b(?:ord|odd|order(?:\s+id|\s+number)?|id)\b"
                    r"\D{0,15}(10[1-3])\b",
                    user_message,
                    re.IGNORECASE
                )

                supplied_order_id = None

                if order_match:
                    supplied_order_id = f"ORD-{order_match.group(1)}"
                else:
                    # Reuse a valid order ID mentioned earlier in this session.
                    for previous_message in reversed(history[:-1]):
                        previous_text = previous_message.get("content", "")
                        if not isinstance(previous_text, str):
                            continue

                        previous_match = re.search(
                            r"\b(?:ord|odd|order(?:\s+id|\s+number)?|id)\b"
                            r"\D{0,15}(10[1-3])\b",
                            previous_text,
                            re.IGNORECASE
                        )

                        if previous_match:
                            supplied_order_id = (
                                f"ORD-{previous_match.group(1)}"
                            )
                            break

                if not supplied_order_id:
                    detected_order_id = None
                    final_reply = (
                        "Please share your order ID so I can check "
                        "whether it is eligible for cancellation. "
                        "I cannot cancel orders through this assistant."
                    )
                    resolution_status = "PENDING_ACTION"

                else:
                    tool_result = get_order_details(supplied_order_id)

                    if "error" in tool_result:
                        final_reply = (
                            f"I couldn't find order {supplied_order_id}. "
                            "Please double-check the order ID."
                        )
                        # Do not add an invalid ID to the structured order summary.
                        detected_order_id = None
                        resolution_status = "UNRESOLVED_INVALID_ORDER"

                    else:
                        detected_order_id = tool_result["order_id"]
                        order_status = tool_result.get("status", "")

                        if order_status == "Processing":
                            final_reply = (
                                f"Order {detected_order_id} is currently "
                                "Processing and is eligible for cancellation. "
                                "I cannot cancel it or submit a cancellation "
                                "request for you. Please contact Aura "
                                "Skincare's official support channel to "
                                "request cancellation. No cancellation has "
                                "been completed through this assistant."
                            )
                            resolution_status = "PENDING_ACTION"

                        elif order_status in ("Shipped", "Out for Delivery"):
                            final_reply = (
                                f"Order {detected_order_id} is currently "
                                f"{order_status} and cannot be cancelled "
                                "under Aura Skincare's cancellation policy."
                            )
                            resolution_status = "RESOLVED"

                        elif order_status == "Delivered":
                            final_reply = (
                                f"Order {detected_order_id} has already "
                                "been delivered and cannot be cancelled. "
                                "You can ask me about the return policy."
                            )
                            resolution_status = "RESOLVED"

                        else:
                            final_reply = (
                                f"I couldn't verify cancellation eligibility "
                                f"for order {detected_order_id}. Please "
                                "contact Aura Skincare's official support."
                            )
                            resolution_status = "PENDING_ACTION"

                history.append({
                    "role": "assistant",
                    "content": final_reply
                })


            elif re.search(r"\b(?:official\s+)?support\s+channel\b|\bwhere can i (?:contact|reach) (?:customer )?support\b|\bcontact details\b", user_message, re.IGNORECASE):
                # Never invent a support channel that is not configured in this app.
                intent = "POLICY_OR_ISSUE"
                final_reply = (
                    "I don't have verified contact details for Aura Skincare's official support channel, "
                    "so I can't provide a specific phone number, email address, website, or app route. "
                    "Please use a support contact method that you already know is official."
                )
                resolution_status = "RESOLVED"
                history.append({"role": "assistant", "content": final_reply})

            elif re.search(r"\b(?:ord|order(?:\s+id|\s+number)?|id)\b\D{0,15}(\d{1,6})\b", user_message, re.IGNORECASE):
                # Return order facts directly from the mock database instead of asking
                # the language model to restate prices/statuses, which can introduce errors.
                intent = "ORDER_TRACKING"
                order_match = re.search(
                    r"\b(?:ord|order(?:\s+id|\s+number)?|id)\b\D{0,15}(\d{1,6})\b",
                    user_message,
                    re.IGNORECASE
                )
                spoken_number = order_match.group(1) if order_match else ""
                normalized_id = f"ORD-{spoken_number}" if spoken_number in ("101", "102", "103") else None

                if not normalized_id or normalized_id not in MOCK_ORDERS:
                    detected_order_id = None
                    final_reply = f"I'm sorry, but I couldn't locate an order with ID {spoken_number}. Please double-check the order ID."
                    resolution_status = "UNRESOLVED_INVALID_ORDER"
                else:
                    order = MOCK_ORDERS[normalized_id]
                    detected_order_id = normalized_id
                    resolution_status = "RESOLVED"
                    final_reply = format_order_response(
                        normalized_id, order, response_language
                    )
                history.append({"role": "assistant", "content": final_reply})

            else:
                # Normal AI conversation for non-order, non-support-channel questions.
                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=build_model_messages(history, response_language),
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0.2
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if tool_calls:
                    intent = "ORDER_TRACKING"

                    history.append({
                        "role": "assistant",
                        "content": response_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in tool_calls
                        ]
                    })

                    for tool_call in tool_calls:
                        function_name = tool_call.function.name

                        try:
                            function_args = json.loads(
                                tool_call.function.arguments
                            )
                        except (json.JSONDecodeError, TypeError):
                            function_args = {}

                        if function_name == "get_order_details":
                            detected_order_id = function_args.get("order_id")

                            if (
                                not isinstance(detected_order_id, str)
                                or not detected_order_id.strip()
                            ):
                                tool_result = {
                                    "error": "A valid order ID is required."
                                }
                                resolution_status = "UNRESOLVED_INVALID_ORDER"
                            else:
                                tool_result = get_order_details(
                                    detected_order_id
                                )

                                if "error" in tool_result:
                                    # Invalid IDs must not enter orders_discussed or call_outcome.
                                    detected_order_id = None
                                    resolution_status = (
                                        "UNRESOLVED_INVALID_ORDER"
                                    )
                                else:
                                    detected_order_id = tool_result.get(
                                        "order_id",
                                        detected_order_id
                                    )
                                    resolution_status = "RESOLVED"

                            history.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": json.dumps(tool_result)
                            })

                    second_response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=build_model_messages(history, response_language)
                    )

                    final_reply = (
                        second_response.choices[0].message.content
                        or "I'm sorry, I couldn't generate a response. Please try again."
                    )

                    history.append({
                        "role": "assistant",
                        "content": final_reply
                    })

                else:
                    final_reply = (
                        response_message.content
                        or "I'm sorry, I couldn't generate a response. Please try again."
                    )

                    lower_msg = user_message.lower()

                    if any(
                        word in lower_msg
                        for word in [
                            "return", "refund", "issue", "problem", "help"
                        ]
                    ):
                        resolution_status = "PENDING_ACTION"
                        intent = "POLICY_OR_ISSUE"
                    else:
                        resolution_status = "RESOLVED"

                    history.append({
                        "role": "assistant",
                        "content": final_reply
                    })

            # Save conversation history and track every order discussed in this call.
            session["history"] = history
            orders_discussed = session.get("orders_discussed", [])

            if detected_order_id in ("ORD-101", "ORD-102", "ORD-103"):
                existing_order = next(
                    (item for item in orders_discussed
                     if item.get("order_id") == detected_order_id),
                    None
                )

                if existing_order is None:
                    existing_order = {
                        "order_id": detected_order_id,
                        "customer_intents": [],
                        "resolution_status": resolution_status
                    }
                    orders_discussed.append(existing_order)

                if intent not in existing_order["customer_intents"]:
                    existing_order["customer_intents"].append(intent)
                # A later tracking lookup must not erase an unresolved action from
                # an earlier cancellation request in the same call.
                if (
                    existing_order.get("resolution_status") != "PENDING_ACTION"
                    or resolution_status == "PENDING_ACTION"
                ):
                    existing_order["resolution_status"] = resolution_status

            session["orders_discussed"] = orders_discussed

            # The call-level status reflects whether any discussed order still
            # requires customer action; per-order statuses remain independent.
            overall_status = resolution_status
            if any(
                item.get("resolution_status") == "PENDING_ACTION"
                for item in orders_discussed
            ):
                overall_status = "PENDING_ACTION"

            if orders_discussed:
                order_summaries = []
                for item in orders_discussed:
                    order_id = item["order_id"]
                    topics = ", ".join(item["customer_intents"])
                    order_status = item["resolution_status"]
                    details = f"{order_id} (topics: {topics}; resolution: {order_status})"

                    # Make unresolved actions explicit rather than implying the
                    # assistant performed them.
                    if (
                        "ORDER_CANCELLATION" in item["customer_intents"]
                        and order_status == "PENDING_ACTION"
                        and MOCK_ORDERS.get(order_id, {}).get("status") == "Processing"
                    ):
                        details += "; cancellation not submitted—customer must contact official support"
                    elif (
                        "ORDER_CANCELLATION" in item["customer_intents"]
                        and MOCK_ORDERS.get(order_id, {}).get("status") == "Delivered"
                    ):
                        details += "; cancellation unavailable because the order is delivered"

                    order_summaries.append(details)

                call_summary = (
                    "Orders discussed: " + " | ".join(order_summaries)
                    + f". Call-level status: {overall_status}."
                )
            else:
                call_summary = (
                    f"Latest topic: {intent}. No valid order was identified. "
                    f"Call-level status: {overall_status}."
                )

            call_outcome = {
                "customer_intent": intent,
                "order_id": (
                    detected_order_id
                    if detected_order_id in ("ORD-101", "ORD-102", "ORD-103")
                    else None
                ),
                "orders_discussed": orders_discussed,
                "resolution_status": overall_status,
                "call_summary": call_summary
            }

            return jsonify({
                "success": True,
                "response": final_reply,
                "call_outcome": call_outcome
            })

    except Exception as e:
        print("Groq API Error:", str(e))

        return jsonify({
            "success": False,
            "response": (
                "I'm sorry, a temporary service issue occurred. "
                "Please try again."
            ),
            "call_outcome": {
                "customer_intent": "ERROR",
                "order_id": detected_order_id,
                "resolution_status": "FAILED",
                "call_summary": "Encountered a server connection error."
            }
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)