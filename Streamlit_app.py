import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import datetime
import glob
import logging

# Configuration
PDF_DIR = "documents"
COUNTER_FILE = "invoice_counter.txt"
ESTIMATE_COUNTER_FILE = "estimate_counter.txt"
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")

# Ensure the directory exists
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Function to get the next number
def get_next_number(counter_file, prefix):
    try:
        if not os.path.exists(counter_file):
            with open(counter_file, "w") as f:
                f.write("1")
        with open(counter_file, "r") as f:
            current_number = int(f.read().strip())
        with open(counter_file, "w") as f:
            f.write(str(current_number + 1))
        return f"{prefix}{current_number:03d}"
    except Exception as e:
        st.error(f"Error generating number: {e}")
        return None

# Function to format date
def format_date(date):
    return date.strftime("%m/%d/%Y")

# Function to format phone number
def format_phone_number(phone):
    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

# Function to create a professional PDF
def create_pdf(
    file_name,
    doc_type,
    document_number,
    date,
    customer_details,
    items,
    total_amount,
    payment=None,
    balance_due=None,
    due_date=None,
):
    try:
        c = canvas.Canvas(file_name, pagesize=letter)
        c.setTitle(doc_type.upper())

        # Header Section
        y = 750
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 50, y - 80, width=120, height=80)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(200, y, doc_type.upper())
        c.setFont("Helvetica", 12)
        c.drawString(200, y - 20, f"Number: {document_number}")
        c.drawString(400, y, f"Date: {format_date(date)}")
        if doc_type == "invoice" and due_date:
            c.drawString(400, y - 20, f"Due: {due_date}")

        # Company Info
        y -= 100
        c.setFont("Helvetica", 10)
        c.drawString(50, y, "Tranquil Heating and Cooling")
        c.drawString(50, y - 15, "Phone: +1 773-672-9920")
        c.drawString(50, y - 30, "Email: tranquilservice93@gmail.com")
        c.setFillColor(colors.grey)
        c.drawString(50, y - 45, "Delivering comfort with care.")

        # Customer Info
        y -= 80
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "BILL TO")
        c.setFont("Helvetica", 10)
        c.drawString(50, y - 15, customer_details["name"])
        c.drawString(50, y - 30, customer_details["address"])
        c.drawString(50, y - 45, format_phone_number(customer_details["phone"]))
        if customer_details["email"]:
            c.drawString(50, y - 60, customer_details["email"])

        # Items Table
        y -= 100
        c.setFont("Helvetica-Bold", 10)
        table_data = [["Description", "Rate (USD)", "Quantity", "Amount (USD)"]]
        for item in items:
            table_data.append(
                [item["description"], f"${item['rate']:.2f}", item["quantity"], f"${item['amount']:.2f}"]
            )

        table = Table(table_data, colWidths=[200, 100, 100, 100])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, None]),
                ]
            )
        )

        table.wrapOn(c, 50, y)
        table.drawOn(c, 50, y)

        # Totals Section
        y -= (len(items) + 2) * 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y, f"TOTAL: USD ${total_amount:.2f}")
        if doc_type == "invoice" and payment is not None:
            c.setFont("Helvetica", 12)
            c.drawString(400, y - 20, f"Payment: USD ${payment:.2f}")
            c.drawString(400, y - 40, f"Balance Due: USD ${balance_due:.2f}")

        # Footer
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.grey)
        c.drawString(50, 50, "Thank you for choosing Tranquil Heating and Cooling.")
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 500, 20, width=50, height=50)

        c.save()
        logger.info(f"Generated {doc_type} {document_number} for {customer_details['name']}")
    except Exception as e:
        logger.error(f"Error generating {doc_type} {document_number}: {e}")
        st.error(f"Error generating {doc_type}: {e}")

# Streamlit UI
st.title("Tranquil Heating and Cooling Portal")
tab1, tab2 = st.tabs(["Generate Document", "Manage Documents"])

with tab1:
    st.header("Generate Invoice or Estimate")
    doc_type = st.radio("Select Document Type", ["Invoice", "Estimate"])
    customer_name = st.text_input("Customer Name")
    customer_address = st.text_area("Customer Address")
    customer_phone = st.text_input("Customer Phone (e.g., 7894560213)")
    customer_email = st.text_input("Customer Email (optional)")
    date = st.date_input("Date", datetime.date.today())
    due_date = st.text_input("Due Date (only for invoices)", "On Receipt") if doc_type == "Invoice" else None

    if not customer_name or not customer_address or not customer_phone:
        st.warning("Please fill in all customer details.")

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
        total_amount = sum(item["amount"] for item in st.session_state["items"])
        payment = 0.0 if doc_type == "Estimate" else st.number_input("Payment Amount", min_value=0.0, max_value=total_amount, step=0.01, value=0.0)
        balance_due = total_amount - payment

        if st.button("Generate PDF"):
            counter_file = ESTIMATE_COUNTER_FILE if doc_type == "Estimate" else COUNTER_FILE
            prefix = "EST" if doc_type == "Estimate" else "INV"
            document_number = get_next_number(counter_file, prefix)

            file_name = f"{PDF_DIR}/{doc_type}_{document_number}.pdf"
            create_pdf(
                file_name,
                doc_type.lower(),
                document_number,
                date,
                {"name": customer_name, "address": customer_address, "phone": customer_phone, "email": customer_email},
                st.session_state["items"],
                total_amount,
                payment,
                balance_due,
                due_date,
            )

            st.success(f"{doc_type} generated!")
            st.download_button("Download PDF", open(file_name, "rb"), file_name=os.path.basename(file_name))

with tab2:
    st.header("Manage Documents")
    pdf_files = glob.glob(f"{PDF_DIR}/*.pdf")
    for pdf_file in pdf_files:
        st.write(os.path.basename(pdf_file))
        st.download_button("Download", open(pdf_file, "rb"), os.path.basename(pdf_file))
