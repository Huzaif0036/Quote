import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

# Configuration
PDF_DIR = "documents"
COUNTER_FILE = "invoice_counter.txt"
ESTIMATE_COUNTER_FILE = "estimate_counter.txt"

# Ensure the directory exists
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Function to get the next number
def get_next_number(counter_file, prefix):
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1")
    with open(counter_file, "r") as f:
        current_number = int(f.read().strip())
    with open(counter_file, "w") as f:
        f.write(str(current_number + 1))
    return f"{prefix}{current_number:03d}"

# Function to create a PDF
def create_pdf(
    file_name, doc_type, document_number, date, customer_details, items, total_amount, payment=None, balance_due=None
):
    c = canvas.Canvas(file_name, pagesize=letter)
    c.setTitle(doc_type.upper())

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, doc_type.upper())
    c.setFont("Helvetica", 12)
    c.drawString(50, 720, f"Number: {document_number}")
    c.drawString(400, 720, f"Date: {date}")

    # Customer Details
    c.drawString(50, 700, "Customer Details:")
    c.drawString(50, 685, f"Name: {customer_details['name']}")
    c.drawString(50, 670, f"Address: {customer_details['address']}")
    c.drawString(50, 655, f"Phone: {customer_details['phone']}")
    if customer_details['email']:
        c.drawString(50, 640, f"Email: {customer_details['email']}")

    # Items
    c.drawString(50, 620, "Items:")
    y = 600
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawString(300, y, "Rate (USD)")
    c.drawString(400, y, "Quantity")
    c.drawString(500, y, "Amount (USD)")
    c.setFont("Helvetica", 10)
    y -= 20

    for item in items:
        c.drawString(50, y, item["description"])
        c.drawString(300, y, f"{item['rate']:.2f}")
        c.drawString(400, y, str(item["quantity"]))
        c.drawString(500, y, f"{item['amount']:.2f}")
        y -= 20

    # Totals
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y, f"TOTAL: USD {total_amount:.2f}")
    y -= 20
    if doc_type == "invoice" and payment is not None:
        c.drawString(400, y, f"Payment: USD {payment:.2f}")
        y -= 20
        c.drawString(400, y, f"Balance Due: USD {balance_due:.2f}")

    c.save()

# Streamlit UI
st.title("Invoice and Estimate Generator")

doc_type = st.radio("Select Document Type", ["Invoice", "Estimate"])
customer_name = st.text_input("Customer Name")
customer_address = st.text_area("Customer Address")
customer_phone = st.text_input("Customer Phone")
customer_email = st.text_input("Customer Email (optional)")
date = st.date_input("Date", datetime.date.today())

if doc_type == "Invoice":
    payment = st.number_input("Payment Amount", min_value=0.0, step=0.01)
else:
    payment = None

if "items" not in st.session_state:
    st.session_state["items"] = []

st.subheader("Add Items")
description = st.text_input("Item Description")
rate = st.number_input("Rate (USD)", min_value=0.0, step=0.01)
quantity = st.number_input("Quantity", min_value=1, step=1)

if st.button("Add Item"):
    if description and rate > 0 and quantity > 0:
        st.session_state["items"].append(
            {"description": description, "rate": rate, "quantity": quantity, "amount": rate * quantity}
        )
        st.success("Item added!")
    else:
        st.error("Please enter valid item details.")

if st.session_state["items"]:
    st.subheader("Items")
    for idx, item in enumerate(st.session_state["items"]):
        st.write(f"{idx+1}. {item['description']} - {item['quantity']} x {item['rate']} = {item['amount']}")

    total_amount = sum(item["amount"] for item in st.session_state["items"])
    balance_due = total_amount - payment if payment is not None else None

    if st.button("Generate PDF"):
        counter_file = ESTIMATE_COUNTER_FILE if doc_type == "Estimate" else COUNTER_FILE
        prefix = "EST" if doc_type == "Estimate" else "INV"
        document_number = get_next_number(counter_file, prefix)

        file_name = f"{PDF_DIR}/{doc_type}_{document_number}.pdf"
        create_pdf(
            file_name,
            doc_type,
            document_number,
            date,
            {
                "name": customer_name,
                "address": customer_address,
                "phone": customer_phone,
                "email": customer_email,
            },
            st.session_state["items"],
            total_amount,
            payment,
            balance_due,
        )

        st.success(f"{doc_type} generated!")
        st.download_button("Download PDF", open(file_name, "rb"), file_name=os.path.basename(file_name))
