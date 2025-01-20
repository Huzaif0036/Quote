import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime
import glob
import logging

# Configuration settings
PDF_DIR = "invoices"
COUNTER_FILE = "invoice_counter.txt"
ESTIMATE_COUNTER_FILE = "estimate_counter.txt"
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")

# Ensure the directory exists
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to get the next invoice or estimate number
def get_next_number(doc_type):
    try:
        counter_file = COUNTER_FILE if doc_type == "invoice" else ESTIMATE_COUNTER_FILE
        prefix = "INV" if doc_type == "invoice" else "EST"

        if not os.path.exists(counter_file):
            with open(counter_file, "w") as f:
                f.write("1")
        with open(counter_file, "r") as f:
            current_number = int(f.read().strip())
        with open(counter_file, "w") as f:
            f.write(str(current_number + 1))
        return f"{prefix}{current_number:03d}"
    except Exception as e:
        st.error(f"Error generating {doc_type} number: {e}")
        return None

# Function to format date to MM/DD/YYYY
def format_date(date):
    return date.strftime("%m/%d/%Y")

# Function to format phone number to 789-456-0213
def format_phone_number(phone):
    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

# Function to create invoice/estimate PDF
def create_invoice(file_name, doc_type, invoice_number, date, customer_name, customer_address, customer_phone, customer_email, items, total_amount, payment, balance_due, due_date=None):
    try:
        c = canvas.Canvas(file_name, pagesize=letter)
        title = "ESTIMATE" if doc_type == "estimate" else "INVOICE"

        # Add Logo and Space
        y_position = 730
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 50, y_position - 100, width=100, height=100)  # Adjust position
        y_position -= 120  # Space below logo

        # Title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(170, y_position + 50, f"Tranquil Heating and Cooling - {title} {invoice_number}")

        # Partition Line
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(50, y_position + 40, 550, y_position + 40)

        # Company Details
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position + 20, "Tranquil Heating and Cooling")
        c.drawString(50, y_position + 5, "+1 773-672-9920")
        c.drawString(50, y_position - 10, "tranquilservice93@gmail.com")

        # Invoice/Estimate Details
        c.drawString(400, y_position + 20, f"{title}")
        c.drawString(400, y_position + 5, f"{invoice_number}")
        c.drawString(400, y_position - 10, f"DATE: {format_date(date)}")
        
        if doc_type == "invoice":
            c.drawString(400, y_position - 40, f"DUE: {due_date if due_date else 'On Receipt'}")
            c.drawString(400, y_position - 60, f"BALANCE DUE: USD ${balance_due:.2f}")
        else:
            c.drawString(400, y_position - 40, f"TOTAL: USD ${total_amount:.2f}")

        # Customer Details
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position - 60, "BILL TO")
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position - 75, customer_name)
        c.drawString(50, y_position - 90, customer_address)
        c.drawString(50, y_position - 105, format_phone_number(customer_phone))
        if customer_email:
            c.drawString(50, y_position - 120, customer_email)

        # Table Header
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.lightgrey)
        c.rect(50, y_position - 140, 500, 20, fill=True, stroke=False)
        c.setFillColor(colors.black)
        c.drawString(55, y_position - 135, "DESCRIPTION")
        c.drawString(355, y_position - 135, "RATE")
        c.drawString(420, y_position - 135, "QTY")
        c.drawString(470, y_position - 135, "AMOUNT")

        # Table Rows
        c.setFont("Helvetica", 12)
        y_position -= 160
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
        if doc_type == "invoice":
            c.setFont("Helvetica", 12)
            c.drawString(400, y_position - 50, f"Payment: USD ${payment:.2f}")
            c.drawString(400, y_position - 70, f"Balance Due: USD ${balance_due:.2f}")

        # Footer
        c.setFont("Helvetica", 10)
        c.drawString(50, 50, "Thank you for choosing Tranquil Heating and Cooling!")
        c.save()
        logger.info(f"Generated {title} {invoice_number} for {customer_name}")
    except Exception as e:
        logger.error(f"Error generating {title} {invoice_number} for {customer_name}: {e}")
        st.error(f"Error generating {title}: {e}")

# Streamlit App
st.title("Invoice/Estimate Portal")
tab1, tab2 = st.tabs(["Generate Document", "Manage Documents"])

# Tab 1: Generate Document
with tab1:
    st.header("Generate New Invoice/Estimate")
    doc_type = st.radio("Select Document Type", options=["Invoice", "Estimate"])
    is_estimate = doc_type == "Estimate"
    customer_name = st.text_input("Customer Name")
    customer_address = st.text_area("Customer Address")
    customer_phone = st.text_input("Customer Phone (format: 7894560213)")
    customer_email = st.text_input("Customer Email (optional)")
    date = st.date_input("Date", datetime.date.today())
    due_date = None

    # Due Date for Invoices Only
    if not is_estimate:
        due_date = st.text_input("Due Date (e.g., MM/DD/YYYY)", "On Receipt")

    # Initialize items
    if "items" not in st.session_state:
        st.session_state["items"] = []

    # Add items
    st.subheader("Add Items")
    description = st.text_input("Description")
    rate = st.number_input("Rate", min_value=0.0, step=0.01)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    if st.button("Add Item"):
        if description and rate > 0 and quantity > 0:
            st.session_state["items"].append({"description": description, "rate": rate, "quantity": quantity, "amount": rate * quantity})
            st.success("Item added!")
        else:
            st.error("Please provide valid item details.")

    # Calculate total and balance
    if st.session_state["items"]:
        total_amount = sum(item['amount'] for item in st.session_state["items"])
        payment = st.number_input("Payment Amount", min_value=0.0, max_value=total_amount, step=0.01, value=0.0)
        balance_due = total_amount - payment if not is_estimate else 0.0

        st.write(f"**Total Amount:** USD ${total_amount:.2f}")
        st.write(f"**Payment:** USD ${payment:.2f}")
        if not is_estimate:
            st.write(f"**Balance Due:** USD ${balance_due:.2f}")

        # Generate and save PDF
        if st.button("Generate PDF"):
            invoice_number = get_next_number("estimate" if is_estimate else "invoice")
            if invoice_number:  # Ensure invoice number is valid
                sanitized_name = customer_name.replace(" ", "_")
                file_name = f"{PDF_DIR}/{sanitized_name}_{doc_type}.pdf"
                create_invoice(file_name, "estimate" if is_estimate else "invoice", invoice_number, date, customer_name, customer_address, customer_phone, customer_email, st.session_state["items"], total_amount, payment, balance_due, due_date if not is_estimate else None)
                st.success(f"{doc_type} generated!")
                st.session_state["items"] = []

                # Add download button
                with open(file_name, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=os.path.basename(file_name),
                        mime="application/pdf",
                        key=f"download_{invoice_number}"  # Unique key for each download button
                    )

# Tab 2: Manage Documents
with tab2:
    st.header("Manage Documents")

    # Initialize deleted_files list in session state
    if "deleted_files" not in st.session_state:
        st.session_state["deleted_files"] = []

    pdf_files = glob.glob(f"{PDF_DIR}/*.pdf")

    for pdf_file in pdf_files:
        if os.path.basename(pdf_file) in st.session_state["deleted_files"]:
            continue  # Skip deleted files

        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.write(os.path.basename(pdf_file))
        with col2:
            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, os.path.basename(pdf_file), mime="application/pdf", key=f"download_{pdf_file}")
        with col3:
            if st.button("Delete", key=f"delete_{pdf_file}"):
                os.remove(pdf_file)
                st.session_state["deleted_files"].append(os.path.basename(pdf_file))
                st.success(f"{os.path.basename(pdf_file)} deleted!")
