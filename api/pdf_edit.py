import io
import fitz
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import Response
from mangum import Mangum

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def render_invoice(pdf_bytes, company_name, website, addr1, addr2, client_name, loc_line1, loc_line2, remit_email):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if not len(doc):
        raise ValueError("The uploaded PDF has no pages.")
    page = doc[0]
    width = 0.57
    grey, black, white = (0.784, 0.784, 0.784), (0, 0, 0), (1, 1, 1)
    x0, x1 = 42.52, 269.29
    HEADER_H = 12.76   # grey header bar height used in all boxes
    BOX_GAP  = 3.24    # vertical gap between stacked boxes
    REMIT_TOP_ORIG = 207.0  # original y where MAKE PAYABLE TO begins — do not move this

    # --- Company box height (content-driven) ---
    co_lines = [(company_name, "Helvetica-Bold", 10), (website, "Helvetica", 10),
                (addr1, "Helvetica", 10), (addr2, "Helvetica", 10)]
    co_lines = [(t, f, s) for t, f, s in co_lines if t]
    n_co = len(co_lines) or 1
    LINE_H_CO = 13
    co_y0 = 42.52
    co_y1 = co_y0 + HEADER_H + 8 + n_co * LINE_H_CO + 6   # header + top pad + lines + bottom pad

    # --- Bill-to box height (content-driven) ---
    bill_lines = [t for t in [client_name, loc_line1, loc_line2] if t]
    n_bill = len(bill_lines) or 1
    LINE_H_BILL = 13
    bill_y0 = co_y1 + BOX_GAP
    bill_y1 = bill_y0 + HEADER_H + 8 + n_bill * LINE_H_BILL + 6

    # Sanity: never overlap the MAKE PAYABLE TO box
    bill_y1 = min(bill_y1, REMIT_TOP_ORIG - BOX_GAP)

    remit_top = REMIT_TOP_ORIG  # MAKE PAYABLE TO stays exactly where it was

    # Clear zone covers the full original company + bill-to area (logo, old text, borders, all)
    clear_zone = fitz.Rect(x0, 42.52, x1, REMIT_TOP_ORIG)
    remit_zone = fitz.Rect(x0, remit_top, x1, 420.0)

    # Delete widgets in clear zone; update email widget in remit zone
    for widget in list(page.widgets()):
        if widget.rect.intersects(clear_zone):
            page.delete_widget(widget)
        elif widget.rect.intersects(remit_zone):
            val = widget.field_value or ""
            name = widget.field_name or ""
            if "@" in val or "email" in name.lower() or "remit" in name.lower():
                widget.field_value = remit_email
                widget.update()

    # Find the lowest content in the remit zone before we redact anything
    last_y = remit_top + 30
    for block in page.get_text("blocks"):
        bx0, by0, bx1, by1 = block[0], block[1], block[2], block[3]
        if bx0 >= x0 - 5 and bx1 <= x1 + 5 and by0 >= remit_top and by1 > last_y:
            last_y = by1
    for widget in list(page.widgets()):
        r = widget.rect
        if r.x0 >= x0 - 5 and r.x1 <= x1 + 5 and r.y0 >= remit_top and r.y1 > last_y:
            last_y = r.y1
    label_y = last_y + 14
    new_box_bottom = label_y + 26

    # Remove free-text annotations in the clear zone
    for annot in list(page.annots()):
        if annot.type[0] != 12 and annot.rect.intersects(clear_zone):
            page.delete_annot(annot)

    # Redact the full clear zone (nukes logo, original text, borders)
    page.clean_contents()
    page.add_redact_annot(clear_zone, fill=(1, 1, 1))
    page.apply_redactions(images=2, graphics=1)
    page.draw_rect(clear_zone, color=None, fill=white, overlay=True)

    # --- Draw company box ---
    page.draw_rect(fitz.Rect(x0, co_y0, x1, co_y0 + HEADER_H), color=None, fill=grey)
    page.draw_rect(fitz.Rect(x0, co_y0, x1, co_y1), color=black, width=width)
    y = co_y0 + HEADER_H + 8 + LINE_H_CO - 3   # baseline of first text line
    for text, font, size in co_lines:
        page.insert_text(fitz.Point(x0 + 6, y), text, fontname=font, fontsize=size, color=black)
        y += LINE_H_CO

    # --- Draw bill-to box (fully redrawn including header) ---
    page.draw_rect(fitz.Rect(x0, bill_y0, x1, bill_y0 + HEADER_H), color=None, fill=grey)
    page.draw_rect(fitz.Rect(x0, bill_y0, x1, bill_y1), color=black, width=width)
    page.insert_text(fitz.Point(x0 + 4, bill_y0 + HEADER_H - 2), "BILL TO",
                     fontname="Helvetica-Bold", fontsize=7, color=black)
    y = bill_y0 + HEADER_H + 8 + LINE_H_BILL - 3
    for text in bill_lines:
        page.insert_text(fitz.Point(x0 + 6, y), text, fontname="Helvetica", fontsize=10, color=black)
        y += LINE_H_BILL

    # --- Extend the MAKE PAYABLE TO box downward and insert remittance label ---
    page.draw_rect(fitz.Rect(x0 - 2, last_y, x1 + 2, last_y + 20), color=None, fill=white, overlay=True)
    page.draw_line(fitz.Point(x0, last_y), fitz.Point(x0, new_box_bottom), color=black, width=width)
    page.draw_line(fitz.Point(x1, last_y), fitz.Point(x1, new_box_bottom), color=black, width=width)
    page.draw_line(fitz.Point(x0, new_box_bottom), fitz.Point(x1, new_box_bottom), color=black, width=width)
    page.insert_text(fitz.Point(x0 + 6, label_y), "Email remittance information to:", fontname="Helvetica", fontsize=10, color=black)
    page.insert_text(fitz.Point(x0 + 6, label_y + 13), remit_email, fontname="Helvetica", fontsize=10, color=black)

    if len(doc) > 1:
        doc[1].clean_contents()
        doc[1].add_redact_annot(fitz.Rect(690, 42, 800, 132), fill=(1, 1, 1))
        doc[1].apply_redactions(images=2, graphics=1)

    output = io.BytesIO()
    doc.save(output, deflate=True, garbage=3)
    doc.close()
    return output.getvalue()


@app.post("/api/pdf_inspect")
@app.post("/api/pdf_inspect/")
async def inspect_pdf(pdf: UploadFile = File(...)):
    """Temporary diagnostic: returns text block coordinates from page 1."""
    doc = fitz.open(stream=await pdf.read(), filetype="pdf")
    page = doc[0]
    blocks = [
        {"y0": round(b[1], 2), "y1": round(b[3], 2), "x0": round(b[0], 2), "x1": round(b[2], 2), "text": b[4].strip()}
        for b in page.get_text("blocks")
        if b[4].strip()
    ]
    widgets = [
        {"rect": [round(v, 2) for v in w.rect], "value": w.field_value, "type": w.field_type_string}
        for w in (page.widgets() or [])
    ]
    doc.close()
    return {"blocks": blocks, "widgets": widgets}


@app.get("/api/pdf_edit")
@app.get("/")
def health():
    return {"ok": True}


@app.post("/api/pdf_edit")
@app.post("/api/pdf_edit/")
@app.post("/")
async def edit_invoice(
    pdf: UploadFile = File(...),
    companyName: str = Form("Tessen Payroll USA LLC"),
    website: str = Form("tessenpayroll.com"),
    addr1: str = Form("1309 Coffeen Ave"),
    addr2: str = Form("Sheridan, WY 82801"),
    clientName: str = Form(""),
    locLine1: str = Form(""),
    locLine2: str = Form(""),
    remitEmail: str = Form("finance@tessenpayroll.com"),
):
    edited = render_invoice(await pdf.read(), companyName, website, addr1, addr2, clientName, locLine1, locLine2, remitEmail)
    return Response(content=edited, media_type="application/pdf", headers={"Cache-Control": "no-store"})

# Vercel ASGI handler
handler = Mangum(app, lifespan="off")
