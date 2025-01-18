import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime

# Function to create invoice/quote PDF
def create_invoice(file_name, invoice_number, date, due_date, customer_name, customer_address, customer_phone, items, total_amount, payment, balance_due, is_quote=False):
    c = canvas.Canvas(file_name, pagesize=letter)
    title = "QUOTE" if is_quote else "INVOICE"

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(220, 750, f"Tranquil Heating and Cooling - {title} {invoice_number}")

    # Company Details
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, "Tranquil Heating and Cooling")
    c.drawString(50, 715, "+1 773-672-9920")
    c.drawString(50, 700, "tranquilservice93@gmail.com")

    # Invoice Details
    c.drawString(400, 730, f"{title}")
    c.drawString(400, 715, f"INV{invoice_number}")
    c.drawString(400, 700, f"DATE: {date}")
    c.drawString(400, 685, f"DUE: {due_date}")
    c.drawString(400, 670, f"BALANCE DUE: USD ${balance_due:.2f}")

    # Customer Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 650, "BILL TO")
    c.setFont("Helvetica", 12)
    c.drawString(50, 635, customer_name)
    c.drawString(50, 620, customer_address)
    c.drawString(50, 605, customer_phone)

    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.lightgrey)
    c.rect(50, 580, 500, 20, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.drawString(55, 585, "DESCRIPTION")
    c.drawString(355, 585, "RATE")
    c.drawString(420, 585, "QTY")
    c.drawString(470, 585, "AMOUNT")

    # Table Rows
    c.setFont("Helvetica", 12)
    y = 560
    for item in items:
        c.drawString(55, y, item["description"])
        c.drawString(355, y, f"${item['rate']:.2f}")
        c.drawString(420, y, str(item["quantity"]))
        c.drawString(470, y, f"${item['amount']:.2f}")
        y -= 20

    # Total Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 10, f"TOTAL: USD ${total_amount:.2f}")
    c.setFont("Helvetica", 12)
    c.drawString(400, y - 30, f"Payment: USD ${payment:.2f}")
    c.drawString(400, y - 50, f"Balance Due: USD ${balance_due:.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Thank you for choosing Tranquil Heating and Cooling!")
    c.save()

# Streamlit App
st.title("Invoice/Quote Generator")

# Section 1: Type Selection
st.header("Step 1: Select Document Type")
doc_type = st.radio("What would you like to generate?", options=["Invoice", "Quote"], horizontal=True)
is_quote = doc_type == "Quote"

# Section 2: Customer Details
st.header("Step 2: Enter Customer Details")
customer_name = st.text_input("Customer Name")
customer_address = st.text_area("Customer Address")
customer_phone = st.text_input("Customer Phone Number")
invoice_number = st.text_input("Invoice/Quote Number", value="001")
date = st.date_input("Date", value=datetime.date.today())
due_date = st.text_input("Due Date", value="On Receipt")

# Section 3: Add Items
st.header("Step 3: Add Items")
if "items" not in st.session_state:
    st.session_state["items"] = []

# Form to add items
with st.form("add_item_form"):
    description = st.text_input("Description", key="description")
    rate = st.number_input("Rate", min_value=0.0, step=0.01, key="rate")
    quantity = st.number_input("Quantity", min_value=1, step=1, key="quantity")
    add_item = st.form_submit_button("Add Item")
    if add_item:
        st.session_state["items"].append(
            {"description": description, "rate": rate, "quantity": quantity, "amount": rate * quantity}
        )

# Display added items
if st.session_state["items"]:
    st.write("### Added Items")
    for item in st.session_state["items"]:
        st.write(f"- {item['description']} - ${item['rate']:.2f} x {item['quantity']} = ${item['amount']:.2f}")

# Section 4: Summary and Generate PDF
st.header("Step 4: Summary & PDF Generation")
if st.session_state["items"]:
    total_amount = sum(item["amount"] for item in st.session_state["items"])
    payment = st.number_input("Payment Amount", min_value=0.0, max_value=total_amount, step=0.01, value=0.0)
    balance_due = total_amount - payment

    st.write("### Summary")
    st.write(f"**Total Amount:** ${total_amount:.2f}")
    st.write(f"**Payment:** ${payment:.2f}")
    st.write(f"**Balance Due:** ${balance_due:.2f}")

    # Generate PDF Button
    if st.button("Generate PDF"):
        file_name = f"{doc_type}_{invoice_number}.pdf"
        create_invoice(
            file_name=file_name,
            invoice_number=invoice_number,
            date=date.strftime("%Y-%m-%d"),
            due_date=due_date,
            customer_name=customer_name,
            customer_address=customer_address,
            customer_phone=customer_phone,
            items=st.session_state["items"],
            total_amount=total_amount,
            payment=payment,
            balance_due=balance_due,
            is_quote=is_quote,
        )

        # Provide Download Button
        with open(file_name, "rb") as pdf_file:
            st.download_button(
                label=f"Download {doc_type}",
                data=pdf_file,
                file_name=file_name,
                mime="application/pdf",
            )
