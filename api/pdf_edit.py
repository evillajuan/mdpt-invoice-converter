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

    page.draw_rect(fitz.Rect(42.52, 42.52, 157.53, 141.33), color=white, fill=white)
    y0, y1 = 42.52, 141.33
    page.draw_rect(fitz.Rect(x0, y0, x1, y0 + 12.76), color=None, fill=grey)
    page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=black, width=width)
    y = y0 + 29.76
    for text, font, size in [(company_name, "Helvetica-Bold", 11), (website, "Helvetica", 11), (addr1, "Helvetica", 11), (addr2, "Helvetica", 11)]:
        if text:
            page.insert_text(fitz.Point(x0 + 6, y), text, fontname=font, fontsize=size, color=black)
        y += 15

    bill_y0, bill_y1 = 144.57, 195.59
    page.draw_rect(fitz.Rect(x0 + 1, 157.33, x1 - 1, bill_y1 - 0.5), color=white, fill=white)
    page.draw_line(fitz.Point(x0, bill_y0), fitz.Point(x0, bill_y1), color=black, width=width)
    page.draw_line(fitz.Point(x1, bill_y0), fitz.Point(x1, bill_y1), color=black, width=width)
    page.draw_line(fitz.Point(x0, bill_y1), fitz.Point(x1, bill_y1), color=black, width=width)
    y = bill_y0 + 25
    for text in [client_name, loc_line1, loc_line2]:
        if text:
            page.insert_text(fitz.Point(x0 + 6, y), text, fontname="Helvetica", fontsize=11, color=black)
            y += 14

    remit_y0, remit_y1 = 209.76, 350.08
    page.draw_rect(fitz.Rect(x0 + 1, 292, x1 - 1, remit_y1 - 0.5), color=white, fill=white)
    page.draw_line(fitz.Point(x0, remit_y0), fitz.Point(x0, remit_y1), color=black, width=width)
    page.draw_line(fitz.Point(x1, remit_y0), fitz.Point(x1, remit_y1), color=black, width=width)
    page.draw_line(fitz.Point(x0, remit_y1), fitz.Point(x1, remit_y1), color=black, width=width)
    page.insert_text(fitz.Point(x0 + 6, 310), "Email Remittance Advice to:", fontname="Helvetica", fontsize=11, color=black)
    if remit_email:
        page.insert_text(fitz.Point(x0 + 6, 325), remit_email, fontname="Helvetica", fontsize=11, color=black)
    if len(doc) > 1:
        doc[1].draw_rect(fitz.Rect(690, 42, 800, 132), color=white, fill=white)

    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output.getvalue()


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
