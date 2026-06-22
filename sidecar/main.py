import io
import fitz
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
app=FastAPI()
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
@app.get('/health')
def health(): return {'ok':True}
@app.post('/edit')
async def edit_invoice(pdf:UploadFile=File(...),companyName:str=Form('Tessen Payroll USA LLC'),website:str=Form('tessenpayroll.com'),addr1:str=Form('1309 Coffeen Ave'),addr2:str=Form('Sheridan, WY 82801'),clientName:str=Form(''),locLine1:str=Form(''),locLine2:str=Form(''),remitEmail:str=Form('finance@tessenpayroll.com')):
    doc=fitz.open(stream=await pdf.read(),filetype='pdf'); p1=doc[0]; W=.57; grey=(.784,.784,.784); black=(0,0,0); white=(1,1,1); x0,x1=42.52,269.29
    by0,by1=144.57,207.0; my0,my1=209.76,350.08
    edit_zones=[fitz.Rect(42.52,42.52,269.29,141.33),fitz.Rect(x0,by0,x1,by1),fitz.Rect(x0,by1,x1,my0),fitz.Rect(x0,my0,x1,my1)]
    # Remove form widgets — never removed by apply_redactions
    for w in list(p1.widgets()):
        if any(w.rect.intersects(r) for r in edit_zones): p1.delete_widget(w)
    # Remove free-text annotations in edit zones
    for a in list(p1.annots()):
        if a.type[0]!=12 and any(a.rect.intersects(r) for r in edit_zones): p1.delete_annot(a)
    # Redact text, images, line art
    p1.clean_contents()
    for r in edit_zones: p1.add_redact_annot(r,fill=(1,1,1))
    p1.apply_redactions(images=2,graphics=1)
    # Belt-and-suspenders: solid white paint over each zone
    for r in edit_zones: p1.draw_rect(r,color=None,fill=(1,1,1),overlay=True)
    # Draw company box
    y0,y1=42.52,141.33; p1.draw_rect(fitz.Rect(x0,y0,x1,y0+12.76),color=None,fill=grey); p1.draw_rect(fitz.Rect(x0,y0,x1,y1),color=black,width=W)
    y=y0+29.76
    for text,font,size in [(companyName,'Helvetica-Bold',11),(website,'Helvetica',11),(addr1,'Helvetica',11),(addr2,'Helvetica',11)]:
        if text:p1.insert_text(fitz.Point(x0+6,y),text,fontname=font,fontsize=size,color=black)
        y+=15
    # Draw bill-to box
    p1.draw_line(fitz.Point(x0,by0),fitz.Point(x0,by1),color=black,width=W);p1.draw_line(fitz.Point(x1,by0),fitz.Point(x1,by1),color=black,width=W);p1.draw_line(fitz.Point(x0,by1),fitz.Point(x1,by1),color=black,width=W)
    y=by0+22
    for text in [clientName,locLine1,locLine2]:
        if text:p1.insert_text(fitz.Point(x0+6,y),text,fontname='Helvetica',fontsize=11,color=black);y+=13
    # Draw remit box
    p1.draw_line(fitz.Point(x0,my0),fitz.Point(x0,my1),color=black,width=W);p1.draw_line(fitz.Point(x1,my0),fitz.Point(x1,my1),color=black,width=W);p1.draw_line(fitz.Point(x0,my1),fitz.Point(x1,my1),color=black,width=W)
    p1.insert_text(fitz.Point(x0+6,310),'Email Remittance Advice to:',fontname='Helvetica',fontsize=11,color=black)
    if remitEmail:p1.insert_text(fitz.Point(x0+6,325),remitEmail,fontname='Helvetica',fontsize=11,color=black)
    if len(doc)>1:
        p2=doc[1]; p2.clean_contents(); p2.add_redact_annot(fitz.Rect(690,42,800,132),fill=(1,1,1)); p2.apply_redactions(images=2,graphics=1)
    out=io.BytesIO();doc.save(out,deflate=True,garbage=3);doc.close();return Response(content=out.getvalue(),media_type='application/pdf')
