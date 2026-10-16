from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Mock Order Database (As specified in the assessment)
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

@app.route("/")
def index():
    """Serves the main frontend testing interface"""
    return render_template("index.html")

@app.route("/api/get-order", methods=["POST"])
def get_order_details():
    """Tool function endpoint for looking up order details"""
    data = request.get_json() or {}
    order_id = data.get("order_id", "").strip().upper()
    
    if not order_id:
        return jsonify({
            "success": False,
            "error": "Missing order ID. Please provide a valid order ID like ORD-101."
        }), 400
        
    order = MOCK_ORDERS.get(order_id)
    
    if order:
        return jsonify({
            "success": True,
            "order": order
        })
    else:
        return jsonify({
            "success": False,
            "error": f"I couldn't locate an order with number {order_id}. Please verify the ID."
        }), 404
    
@app.route("/api/chat", methods=["POST"])
def chat_with_aria():
    """Handles customer queries, checks for order lookups, and applies guardrails"""
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    
    # Simple keyword/intent extraction for demonstration or integrate OpenAI API here
    response_text = ""
    order_data = None
    
    # Check if the user is asking about an order ID
    if "ord-" in user_message.lower():
        # Extract order ID (e.g., ord-101)
        words = user_message.split()
        target_id = next((w.upper() for w in words if "ORD-" in w.upper()), None)
        
        if target_id and target_id in MOCK_ORDERS:
            order = MOCK_ORDERS[target_id]
            order_data = order
            response_text = f"I found your order {target_id} for {order['product']}. Status is: {order['status']}. {order['notes']}"
        else:
            response_text = "I couldn't locate an order with that number. Could you please verify or repeat the order ID?"
            
    elif "return" in user_message.lower():
        response_text = "Returns are accepted within 7 days of delivery for unopened, unused products in their original packaging. Was your product delivered within the last 7 days?"
        
    elif "cancel" in user_message.lower():
        response_text = "Orders can only be cancelled while their status is Processing. If it has already shipped, you can refuse delivery at your doorstep."
        
    elif "shipping" in user_message.lower() or "delivery" in user_message.lower():
        response_text = "We offer free delivery on orders above ₹499! Orders below ₹499 have a ₹50 shipping fee, and standard delivery takes 3 to 5 business days."
        
    else:
        response_text = "Thanks for reaching out to Aura Skincare! How can I help you with your skincare products, shipping, or existing orders today?"

    return jsonify({
        "success": True,
        "response": response_text,
        "order_data": order_data
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)