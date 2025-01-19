import os
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
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
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 50, 740, width=100, height=50)
        except Exception as e:
            print(f"Error loading logo: {e}")

    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(170, 750, f"Tranquil Heating and Cooling - {title} {invoice_number}")

    # Partition Line
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(50, 735, 550, 735)

    # Company Details
    c.setFont("Helvetica", 12)
    c.drawString(50, 715, "Tranquil Heating and Cooling")
    c.drawString(50, 700, "+1 773-672-9920")
    c.drawString(50, 685, "tranquilservice93@gmail.com")

    # Invoice Details
    c.drawString(400, 715, f"{title}")
    c.drawString(400, 700, f"INV{invoice_number}")
    c.drawString(400, 685, f"DATE: {date}")
    c.drawString(400, 670, f"DUE: {due_date}")
    c.drawString(400, 655, f"BALANCE DUE: USD ${balance_due:.2f}")

    # Partition Line
    c.line(50, 650, 550, 650)

    # Customer Details
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 630, "BILL TO")
    c.setFont("Helvetica", 12)
    c.drawString(50, 615, customer_name)
    c.drawString(50, 600, customer_address)
    c.drawString(50, 585, customer_phone)

    # Partition Line
    c.line(50, 580, 550, 580)

    # Table Header
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.lightgrey)
    c.rect(50, 560, 500, 20, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.drawString(55, 565, "DESCRIPTION")
    c.drawString(355, 565, "RATE")
    c.drawString(420, 565, "QTY")
    c.drawString(470, 565, "AMOUNT")

    # Table Rows
    c.setFont("Helvetica", 12)
    y = 540
    for item in items:
        c.drawString(55, y, item["description"])
        c.drawString(355, y, f"${item['rate']:.2f}")
        c.drawString(420, y, str(item["quantity"]))
        c.drawString(470, y, f"${item['amount']:.2f}")
        y -= 20

    # Partition Line
    c.line(50, y - 10, 550, y - 10)

    # Total Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y - 30, f"TOTAL: USD ${total_amount:.2f}")
    c.setFont("Helvetica", 12)
    c.drawString(400, y - 50, f"Payment: USD ${payment:.2f}")
    c.drawString(400, y - 70, f"Balance Due: USD ${balance_due:.2f}")

    # Footer
    c.setFont("Helvetica", 10)
    c.drawString(50, 50, "Thank you for choosing Tranquil Heating and Cooling!")
    c.save()

# Function to send email with PDF
def send_email(recipient_email, pdf_file_path):
    sender_email = "your_email@example.com"
    sender_password = "your_password"  # Use an app-specific password for Gmail/other providers

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Your Invoice/Quote"

    # Attach the PDF
    with open(pdf_file_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(pdf_file_path)}"')
        msg.attach(part)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Streamlit App
st.title("Invoice/Quote Portal")

# Generate a new invoice
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

# Generate and save PDF
if st.button("Generate PDF"):
    invoice_number = get_next_invoice_number()
    total_amount = sum(item['amount'] for item in st.session_state["items"])
    balance_due = total_amount
    file_name = f"{PDF_DIR}/{doc_type}_{invoice_number}.pdf"
    create_invoice(file_name, invoice_number, date.strftime("%Y-%m-%d"), due_date, customer_name, customer_address, customer_phone, st.session_state["items"], total_amount, 0, balance_due, is_quote)
    st.success(f"{doc_type} generated!")
    st.session_state["items"] = []

# Portal to manage PDFs
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

# Share via email
st.header("Share Documents")
recipient_email = st.text_input("Recipient Email")
if st.button("Send Email"):
    if pdf_files:
        pdf_file_to_send = pdf_files[-1]  # Send the most recent file
        send_email(recipient_email, pdf_file_to_send)
        st.success(f"Email sent to {recipient_email}!")
    else:
        st.error("No documents available to send.")
