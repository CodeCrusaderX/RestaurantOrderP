from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import datetime

def generate_pdf_receipt(buffer, order):
    # Receipt dimensions (approx 80mm width typical for thermal printers, but using A4 for PDF download as requested or custom size)
    # Let's use a custom page size that looks like a long receipt
    pdf = canvas.Canvas(buffer, pagesize=(80 * mm, 200 * mm))
    
    # Constants
    width = 80 * mm
    height = 200 * mm
    left_margin = 5 * mm
    right_margin = 75 * mm
    y = height - 10 * mm
    line_height = 5 * mm
    
    # Fonts
    pdf.setFont("Courier-Bold", 12)
    
    # Header
    pdf.drawCentredString(width / 2, y, "GASTROGENIUS RESTAURANT")
    y -= line_height
    pdf.setFont("Courier", 10)
    pdf.drawCentredString(width / 2, y, "Pure Veg")
    y -= line_height
    pdf.drawCentredString(width / 2, y, "Mumbai, India")
    y -= line_height
    
    pdf.setDash(1, 2)
    pdf.line(left_margin, y, right_margin, y)
    y -= line_height
    pdf.drawCentredString(width / 2, y, "TAX INVOICE")
    y -= line_height
    pdf.line(left_margin, y, right_margin, y)
    y -= line_height * 1.5
    
    # Metadata
    pdf.setFont("Courier", 9)
    date_str = datetime.datetime.now().strftime("%d/%m/%y")
    pdf.drawString(left_margin, y, f"Date: {date_str}")
    pdf.drawRightString(right_margin, y, f"Bill No: {order.id}")
    y -= line_height
    pdf.drawString(left_margin, y, f"Table: {order.table.number}")
    y -= line_height
    
    pdf.line(left_margin, y, right_margin, y)
    y -= line_height
    
    # Columns
    pdf.drawString(left_margin, y, "Particulars")
    pdf.drawRightString(right_margin - 30*mm, y, "Qty")
    pdf.drawRightString(right_margin - 15*mm, y, "Rate")
    pdf.drawRightString(right_margin, y, "Amount")
    y -= line_height
    pdf.line(left_margin, y, right_margin, y)
    y -= line_height * 1.5
    
    # Items
    subtotal = 0
    for item in order.items.all():
        item_total = item.item.price * item.quantity
        subtotal += item_total
        
        # Item Name (Truncate if too long)
        name = item.item.name[:15]
        pdf.drawString(left_margin, y, name)
        pdf.drawRightString(right_margin - 30*mm, y, str(item.quantity))
        pdf.drawRightString(right_margin - 15*mm, y, str(int(item.item.price)))
        pdf.drawRightString(right_margin, y, str(int(item_total)))
        y -= line_height
        
    y -= line_height
    pdf.line(left_margin, y, right_margin, y)
    y -= line_height
    
    # Totals
    # Calculate Tax
    subtotal_float = float(subtotal)
    sgst = subtotal_float * 0.025
    cgst = subtotal_float * 0.025
    grand_total = subtotal_float + sgst + cgst
    
    pdf.drawRightString(right_margin - 18*mm, y, "Sub Total :")
    pdf.drawRightString(right_margin, y, f"{subtotal:.2f}")
    y -= line_height
    
    pdf.drawRightString(right_margin - 18*mm, y, "SGST @2.5% :")
    pdf.drawRightString(right_margin, y, f"{sgst:.2f}")
    y -= line_height
    
    pdf.drawRightString(right_margin - 18*mm, y, "CGST @2.5% :")
    pdf.drawRightString(right_margin, y, f"{cgst:.2f}")
    y -= line_height
    
    pdf.line(left_margin, y, right_margin, y)
    y -= line_height
    
    pdf.setFont("Courier-Bold", 12)
    pdf.drawString(left_margin, y, "Total :")
    pdf.drawRightString(right_margin, y, f"{grand_total:.0f}")
    y -= line_height * 2
    
    # Footer
    pdf.setFont("Courier", 9)
    pdf.drawCentredString(width / 2, y, "FSSAI NO - 12345678901234")
    y -= line_height
    pdf.drawCentredString(width / 2, y, "Thank You")
    y -= line_height
    pdf.drawCentredString(width / 2, y, "Visit Again")
    
    pdf.showPage()
    pdf.save()
