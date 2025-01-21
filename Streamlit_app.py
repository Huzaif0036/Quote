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
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Function to get the next invoice number
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

# Function to format date to MM/DD/YYYY
def format_date(date):
    return date.strftime("%m/%d/%Y")

# Function to format phone number to 789-456-0213
def format_phone_number(phone):
    return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"

# Function to create invoice/estimate PDF with improved layout
def create_invoice(
    file_name,
    doc_type,
    invoice_number,
    date,
    customer_name,
    customer_address,
    customer_phone,
    customer_email,
    items,
    total_amount,
    payment,
    balance_due,
    due_date=None,
):
    try:
        c = canvas.Canvas(file_name, pagesize=letter)
        title = "ESTIMATE" if doc_type == "estimate" else "INVOICE"

        # Add Header Section
        y_position = 750
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 50, y_position - 80, width=120, height=80)  # Add Logo
        c.setFont("Helvetica-Bold", 20)
        c.drawString(200, y_position - 30, f"{title}")
        c.setFont("Helvetica", 12)
        c.drawString(400, y_position - 30, f"DATE: {format_date(date)}")
        if doc_type == "invoice":
            c.drawString(400, y_position - 50, f"DUE: {due_date if due_date else 'On Receipt'}")

        # Counter Below Date
        c.drawString(400, y_position - 70, f"{invoice_number}")

        # Company Info
        c.setFont("Helvetica", 10)
        y_position -= 100
        c.drawString(50, y_position, "Tranquil Heating and Cooling")
        c.drawString(50, y_position - 15, "Phone: +1 773-672-9920")
        c.drawString(50, y_position - 30, "Email: tranquilservice93@gmail.com")

        # Customer Info
        y_position -= 60
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "BILL TO")
        c.setFont("Helvetica", 10)
        c.drawString(50, y_position - 15, customer_name)
        c.drawString(50, y_position - 30, customer_address)
        c.drawString(50, y_position - 45, format_phone_number(customer_phone))
        if customer_email:
            c.drawString(50, y_position - 60, customer_email)

        # Items Table Header
        y_position -= 100
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.lightgrey)
        c.rect(50, y_position, 500, 20, fill=True, stroke=False)
        c.setFillColor(colors.black)
        c.drawString(55, y_position + 5, "DESCRIPTION")
        c.drawString(355, y_position + 5, "RATE")
        c.drawString(420, y_position + 5, "QTY")
        c.drawString(470, y_position + 5, "AMOUNT")

        # Items Table Content
        y_position -= 20
        c.setFont("Helvetica", 10)
        for item in items:
            c.drawString(55, y_position, item["description"])
            c.drawString(355, y_position, f"${item['rate']:.2f}")
            c.drawString(420, y_position, str(item["quantity"]))
            c.drawString(470, y_position, f"${item['amount']:.2f}")
            y_position -= 20

        # Partition Line
        y_position -= 10
        c.setLineWidth(1)
        c.line(50, y_position, 550, y_position)

        # Totals Section
        y_position -= 30
        c.setFont("Helvetica-Bold", 12)
        c.drawString(400, y_position, f"TOTAL: USD ${total_amount:.2f}")
        if doc_type == "invoice":
            c.setFont("Helvetica", 12)
            c.drawString(400, y_position - 20, f"Payment: USD ${payment:.2f}")
            c.drawString(400, y_position - 40, f"Balance Due: USD ${balance_due:.2f}")

        # Footer Section
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.grey)
        c.drawString(50, 50, "Thank you for choosing Tranquil Heating and Cooling!")
        if os.path.exists(LOGO_PATH):
            c.drawImage(LOGO_PATH, 450, 30, width=50, height=50)

        c.save()
        logger.info(f"Generated {title} {invoice_number} for {customer_name}")
    except Exception as e:
        logger.error(f"Error generating {title} {invoice_number} for {customer_name}: {e}")
        st.error(f"Error generating {title}: {e}")
