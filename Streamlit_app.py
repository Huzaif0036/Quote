import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime
import glob

# Directory to store PDFs
PDF_DIR = "invoices"

# Ensure the directory exists
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Function to get the next invoice number
def get_next_invoice_number():
    counter_file = "invoice_counter.txt"
    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1")
    with open(counter_file, "r") as f:
        current_number = int(f.read().strip())
    with open(counter_file, "w") as f:
        f.write(str(current_number + 1))
    return f"{current_number:03d}"

# Function to create invoice/quote PDF
def create_invoice(file_name, invoice_number, date, due_date, customer_name, customer_address, customer_phone, items, total_amount, payment, balance_due, is_quote=False):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "logo.jpg")

    c = canvas.Canvas(file_name, pagesize=letter)
    title = "QUOTE" if is_quote else "INVOICE"

    # Add Logo
    y_position = 750
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 50, y_position, width=100, height=100)
        except Exception as e:
            print(f"Error loading logo: {e}")
    y_position -= 120  # Adjust to add space below the logo

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(170, y_position + 30, f"Tranquil Heating and Cooling - {title} {invoice_number}")

    # Partition Line
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, y_position + 10, 550, y_position + 10)

    # Company Details
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position - 10, "Tranquil Heating and Cooling")
    c.drawString(50, y_position - 25, "+1 773-672-9920")
    c.drawString(50, y_position - 40, "tranquilservice93@gmail.com")

    # Invoice Details
    c.drawString(400, y_position - 10, f"{title}")
    c.drawString(400, y_position - 25, f"INV{invoice_number}")
    c.drawString(400, y_position - 40, f"DATE: {date}")
    c.drawString(400, y_position - 55, f"DUE: {due_date}")
    c.drawString(400, y_position - 70, f"BALANCE DUE: USD ${balance_due:.2f}")

    # Partition Line
    y_position -= 80
    c.line(50, y_position, 550, y_position)

    # Customer Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position - 20, "BILL TO")
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position - 35, customer_name)
    c.drawString(50, y_position - 50, customer_address)
    c.drawString(50, y_position - 65, customer_phone)

    # Partition Line
    y_position -= 80
    c.line(50, y_position, 550, y_position)

    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.lightgrey)
    c.rect(50, y_position - 20, 500, 20, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.drawString(55, y_position - 15, "DESCRIPTION")
    c.drawString(355, y_position - 15, "RATE")
    c.drawString(420, y_position - 15, "QTY")
    c.drawString(470, y_position - 15, "AMOUNT")

    # Table Rows
    c.setFont("Helvetica", 12)
    y_position -= 40
    for item in items:
        c.drawString(55, y_position, item["description"])
        c.drawString(355, y_position, f"${item['rate']:.2f}")
        c.drawString(420, y_position, str(item["quantity"]))
        c.drawString(470, y_position, f"${item['amount']:.2f}")
        y_position -= 20

    # Partition Line
    c.line(50, y_position - 10, 550, y_position - 10)

    # Total Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y_position - 30, f"TOTAL: USD ${total_amount:.2f}")
    c.setFont("Helvetica", 12)
    c.drawString(400, y_position - 50, f"Payment: USD ${payment:.2f}")
    c.drawString(400, y_position - 70, f"Balance Due: USD ${balance_due:.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Thank you for choosing Tranquil Heating and Cooling!")
    c.save()

# Streamlit App
st.title("Invoice/Quote Portal")
tab1, tab2 = st.tabs(["Generate Document", "Manage Documents"])

# Tab 1: Generate Document
with tab1:
    st.header("Generate New Invoice/Quote")
    doc_type = st.radio("Select Document Type", options=["Invoice", "Quote"])
    is_quote = doc_type == "Quote"
    customer_name = st.text_input("Customer Name")
    customer_address = st.text_area("Customer Address")
    customer_phone = st.text_input("Customer Phone")
    date = st.date_input("Date", datetime.date.today())
    due_date = st.text_input("Due Date", "On Receipt")

    # Initialize items
    if "items" not in st.session_state:
        st.session_state["items"] = []

    # Add items
    st.subheader("Add Items")
    description = st.text_input("Description")
    rate = st.number_input("Rate", min_value=0.0, step=0.01)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    if st.button("Add Item"):
        st.session_state["items"].append({"description": description, "rate": rate, "quantity": quantity, "amount": rate * quantity})
        st.success("Item added!")

    # Display added items
    if st.session_state["items"]:
        st.subheader("Added Items")
        for item in st.session_state["items"]:
            st.write(f"{item['description']} - ${item['rate']:.2f} x {item['quantity']} = ${item['amount']:.2f}")

    # Calculate total and balance
    if st.session_state["items"]:
        total_amount = sum(item['amount'] for item in st.session_state["items"])
        payment = st.number_input("Payment Amount", min_value=0.0, max_value=total_amount, step=0.01, value=0.0)
        balance_due = total_amount - payment

        st.write(f"**Total Amount:** USD ${total_amount:.2f}")
        st.write(f"**Payment:** USD ${payment:.2f}")
        st.write(f"**Balance Due:** USD ${balance_due:.2f}")

        # Generate and save PDF
        if st.button("Generate PDF"):
            invoice_number = get_next_invoice_number()
            sanitized_name = customer_name.replace(" ", "_")
            file_name = f"{PDF_DIR}/{sanitized_name}_{doc_type}.pdf"
            create_invoice(file_name, invoice_number, date.strftime("%Y-%m-%d"), due_date, customer_name, customer_address, customer_phone, st.session_state["items"], total_amount, payment, balance_due, is_quote)
            st.success(f"{doc_type} generated!")
            st.session_state["items"] = []

# Tab 2: Manage Documents
with tab2:
    st.header("Manage Documents")
    pdf_files = glob.glob(f"{PDF_DIR}/*.pdf")
    for pdf_file in pdf_files:
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.write(os.path.basename(pdf_file))
        with col2:
            if st.button("View", key=pdf_file):
                with open(pdf_file, "rb") as f:
                    st.download_button("Download PDF", f, os.path.basename(pdf_file), mime="application/pdf")
        with col3:
            if st.button("Delete", key=f"delete_{pdf_file}"):
                os.remove(pdf_file)
                st.success(f"{os.path.basename(pdf_file)} deleted!")
                st.experimental_rerun()
