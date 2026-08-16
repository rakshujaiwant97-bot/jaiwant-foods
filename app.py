from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from database import get_db_connection

app = Flask(__name__)

# Secret key is required for the shopping cart session
app.secret_key = "jaiwant_foods_secret_key"


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# PRODUCTS PAGE
# =========================

@app.route("/products")
def products():
    return render_template("products.html")


# =========================
# ADD PRODUCT TO CART
# =========================

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    product = request.form["product"]
    size = request.form["size"]
    quantity = request.form["quantity"]

    # Get existing cart
    cart = session.get("cart", [])

    # Add the selected product
    cart.append({
        "product": product,
        "size": size,
        "quantity": quantity
    })

    # Save cart in session
    session["cart"] = cart

    return redirect(url_for("cart_page"))


# =========================
# CART PAGE
# =========================

@app.route("/cart")
def cart_page():

    cart = session.get("cart", [])

    return render_template(
        "cart.html",
        cart=cart
    )


# =========================
# REMOVE PRODUCT FROM CART
# =========================

@app.route("/remove_from_cart/<int:index>")
def remove_from_cart(index):

    cart = session.get("cart", [])

    if 0 <= index < len(cart):
        cart.pop(index)

    session["cart"] = cart

    return redirect(url_for("cart_page"))


# =========================
# CHECKOUT PAGE
# =========================

@app.route("/checkout")
def checkout():

    cart = session.get("cart", [])

    if not cart:
        return redirect(url_for("products"))

    return render_template(
        "checkout.html",
        cart=cart
    )


# =========================
# PLACE ORDER
# =========================

@app.route("/place_order", methods=["POST"])
def place_order():

    shop_name = request.form["shop_name"]
    location = request.form["location"]
    phone = request.form["phone"]

    cart = session.get("cart", [])

    if not cart:
        return redirect(url_for("products"))

    # Connect to MySQL
    connection = get_db_connection()

    cursor = connection.cursor()

    # Insert shop/order information
    order_query = """
        INSERT INTO orders
        (shop_name, location, phone)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        order_query,
        (shop_name, location, phone)
    )

    # Get newly created order ID
    order_id = cursor.lastrowid

    # Insert every product in the cart
    item_query = """
        INSERT INTO order_items
        (order_id, product_name, pack_size, quantity_kg)
        VALUES (%s, %s, %s, %s)
    """

    for item in cart:

        cursor.execute(
            item_query,
            (
                order_id,
                item["product"],
                item["size"],
                int(item["quantity"])
            )
        )

    # Save everything
    connection.commit()

    cursor.close()
    connection.close()

    # Clear cart after successful order
        # Save order information before clearing the cart

    order_details = {
        "order_id": order_id,
        "shop_name": shop_name,
        "location": location,
        "phone": phone,
        "items": cart
    }
        # Create order notification message

    order_message = f"""
NEW WHOLESALE ORDER
====================

Order No: #{order_id}

Shop Name: {shop_name}
Location: {location}
Phone: {phone}

PRODUCTS
====================
"""

    for i, item in enumerate(cart, start=1):

        order_message += f"""
{i}. {item["product"]}
   Pack Size: {item["size"]}
   Quantity: {item["quantity"]} Kg
"""

    print("\n" + order_message)
    # Clear cart after successful order
    session.pop("cart", None)

    return render_template(
        "order_success.html",
        order=order_details
    )
# =========================
# WHATSAPP WEBHOOK
# =========================

@app.route("/webhook", methods=["GET"])
def verify_webhook():

    verify_token = os.environ.get(
        "WHATSAPP_VERIFY_TOKEN",
        "jaiwant_webhook_verify"
    )

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == verify_token:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive_webhook():

    data = request.get_json()

    print("WhatsApp Webhook received:")
    print(data)

    return jsonify({"status": "received"}), 200

# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)