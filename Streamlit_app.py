import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

# Ensure the directory for PDFs exists
PDF_DIR = "invoices"
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Function to generate the PDF
def create_invoice(file_path, invoice_number, customer_name, items, total_amount):
    try:
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, f"Invoice #{invoice_number}")
        c.drawString(100, 720, f"Customer: {customer_name}")

        # Table Header
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 690, "Description")
        c.drawString(300, 690, "Quantity")
        c.drawString(400, 690, "Amount")

        # Table Rows
        c.setFont("Helvetica", 12)
        y = 670
        for item in items:
            c.drawString(100, y, item["description"])
            c.drawString(300, y, str(item["quantity"]))
            c.drawString(400, y, f"${item['amount']:.2f}")
            y -= 20

        # Total Amount
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y, f"Total: ${total_amount:.2f}")
        c.save()
        return True
    except Exception as e:
        st.error(f"Error generating invoice: {e}")
        return False

# Streamlit App
st.set_page_config(page_title="Invoice Generator", layout="wide")
st.title("Invoice Generator")

# State for items
if "items" not in st.session_state:
    st.session_state["items"] = []
if "generated_file" not in st.session_state:
    st.session_state["generated_file"] = None

# Form to collect invoice details
with st.form(key="invoice_form"):
    st.header("Invoice Details")
    customer_name = st.text_input("Customer Name", placeholder="John Doe")
    description = st.text_input("Item Description")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    amount = st.number_input("Amount", min_value=0.0, step=0.01)

    add_item = st.form_submit_button("Add Item")
    if add_item:
        if description and quantity > 0 and amount > 0:
            st.session_state["items"].append({"description": description, "quantity": quantity, "amount": amount})
            st.success("Item added!")
        else:
            st.error("Please provide valid item details.")

    if st.session_state["items"]:
        st.subheader("Items Added")
        for idx, item in enumerate(st.session_state["items"]):
            st.write(f"{idx+1}. {item['description']} - {item['quantity']} @ ${item['amount']:.2f}")

        total_amount = sum(item["amount"] for item in st.session_state["items"])
        st.write(f"**Total Amount:** ${total_amount:.2f}")

    # Generate the invoice
    generate_invoice = st.form_submit_button("Generate Invoice")
    if generate_invoice:
        if customer_name and st.session_state["items"]:
            invoice_number = f"{len(st.session_state['items']):03d}"
            file_path = os.path.join(PDF_DIR, f"Invoice_{invoice_number}.pdf")
            if create_invoice(file_path, invoice_number, customer_name, st.session_state["items"], total_amount):
                st.session_state["generated_file"] = file_path
                st.success("Invoice generated successfully!")
        else:
            st.error("Please provide a customer name and at least one item.")

# Display download button outside the form
if st.session_state.get("generated_file"):
    with open(st.session_state["generated_file"], "rb") as pdf_file:
        st.download_button(
            label="Download Invoice",
            data=pdf_file,
            file_name=os.path.basename(st.session_state["generated_file"]),
            mime="application/pdf"
        )
