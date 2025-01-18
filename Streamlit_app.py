import streamlit as st
from fpdf import FPDF

class InvoicePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Invoice/Quote', 0, 1, 'C')

    def add_client_info(self, name):
        self.ln(10)
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f'Client Name: {name}', ln=True)

    def add_item(self, description, quantity, price):
        total = quantity * price
        self.cell(90, 10, description, 1)
        self.cell(30, 10, str(quantity), 1)
        self.cell(30, 10, f'${price:.2f}', 1)
        self.cell(30, 10, f'${total:.2f}', 1, ln=True)

def generate_pdf(client_name, description, quantity, price, is_invoice=True):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.add_client_info(client_name)
    pdf.add_item(description, quantity, price)

    # File name based on type
    file_name = "invoice.pdf" if is_invoice else "quote.pdf"
    pdf.output(file_name)
    return file_name

# Streamlit GUI
st.title("Invoice and Quote Generator")

# Input fields
client_name = st.text_input("Client Name", placeholder="Enter client name")
description = st.text_input("Item Description", placeholder="Enter item description")
quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
price = st.number_input("Price per Item", min_value=0.0, step=0.01, value=0.0)

# Generate Invoice or Quote
col1, col2 = st.columns(2)
with col1:
    if st.button("Generate Invoice"):
        if client_name and description and quantity > 0 and price > 0:
            file_name = generate_pdf(client_name, description, quantity, price, is_invoice=True)
            st.success(f"Invoice generated: {file_name}")
            with open(file_name, "rb") as file:
                st.download_button(label="Download Invoice", data=file, file_name=file_name, mime="application/pdf")
        else:
            st.error("Please fill in all the fields correctly.")

with col2:
    if st.button("Generate Quote"):
        if client_name and description and quantity > 0 and price > 0:
            file_name = generate_pdf(client_name, description, quantity, price, is_invoice=False)
            st.success(f"Quote generated: {file_name}")
            with open(file_name, "rb") as file:
                st.download_button(label="Download Quote", data=file, file_name=file_name, mime="application/pdf")
        else:
            st.error("Please fill in all the fields correctly.")
