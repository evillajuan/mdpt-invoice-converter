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
    by0,by1=144.57,207.0; remit_y0=207.0
    company_zone=fitz.Rect(42.52,42.52,269.29,141.33); bill_zone=fitz.Rect(x0,by0+12.76,x1,by1); remit_zone=fitz.Rect(x0,remit_y0,x1,420.0)
    # Find ceiling: first full-width block below remit zone
    ceiling_y=p1.rect.height
    for block in p1.get_text('blocks'):
        bx0,by0_,bx1,by1_=block[0],block[1],block[2],block[3]
        if by0_>remit_y0 and bx1>x1+20 and by0_<ceiling_y:ceiling_y=by0_
    # Extract MAKE PAYABLE TO content lines before redaction
    remit_content=[]
    for block in p1.get_text('blocks'):
        bx0,by0_,bx1,by1_=block[0],block[1],block[2],block[3]
        if bx0>=x0-5 and bx1<=x1+5 and by0_>=remit_y0 and by0_<ceiling_y:
            for line in block[4].strip().split('\n'):
                line=line.strip()
                if line and line!='MAKE PAYABLE TO':remit_content.append(line)
    # Delete all widgets in all three zones
    remit_redact=fitz.Rect(x0,remit_y0,x1,ceiling_y)
    for w in list(p1.widgets()):
        if w.rect.intersects(company_zone) or w.rect.intersects(bill_zone) or w.rect.intersects(remit_zone):p1.delete_widget(w)
    for a in list(p1.annots()):
        if a.type[0]!=12 and (a.rect.intersects(company_zone) or a.rect.intersects(bill_zone)):p1.delete_annot(a)
    p1.clean_contents()
    for r in [company_zone,bill_zone,remit_redact]:p1.add_redact_annot(r,fill=(1,1,1))
    p1.apply_redactions(images=2,graphics=1)
    for r in [company_zone,bill_zone,remit_redact]:p1.draw_rect(r,color=None,fill=white,overlay=True)
    # Company box
    y0,y1=42.52,141.33; p1.draw_rect(fitz.Rect(x0,y0,x1,y0+12.76),color=None,fill=grey); p1.draw_rect(fitz.Rect(x0,y0,x1,y1),color=black,width=W)
    y=y0+26
    for text,font,size in [(companyName,'Helvetica-Bold',11),(website,'Helvetica',11),(addr1,'Helvetica',11),(addr2,'Helvetica',11)]:
        if text:p1.insert_text(fitz.Point(x0+6,y),text,fontname=font,fontsize=size,color=black)
        y+=13
    # Bill-to box
    p1.draw_line(fitz.Point(x0,by0),fitz.Point(x0,by1),color=black,width=W);p1.draw_line(fitz.Point(x1,by0),fitz.Point(x1,by1),color=black,width=W);p1.draw_line(fitz.Point(x0,by1),fitz.Point(x1,by1),color=black,width=W)
    y=by0+22
    for text in [clientName,locLine1,locLine2]:
        if text:p1.insert_text(fitz.Point(x0+6,y),text,fontname='Helvetica',fontsize=11,color=black);y+=13
    # MAKE PAYABLE TO box — redrawn with compact spacing to always fit email remittance
    hh=12; p1.draw_rect(fitz.Rect(x0,remit_y0,x1,remit_y0+hh),color=None,fill=grey)
    p1.insert_text(fitz.Point(x0+6,remit_y0+hh-2),'MAKE PAYABLE TO',fontname='Helvetica-Bold',fontsize=11,color=black)
    y=remit_y0+hh+13
    for line in remit_content+['Email remittance advice to:',remitEmail]:
        if line:p1.insert_text(fitz.Point(x0+6,y),line,fontname='Helvetica',fontsize=11,color=black)
        y+=13
    p1.draw_rect(fitz.Rect(x0,remit_y0,x1,y-4),color=black,width=W,fill=None)
    if len(doc)>1:
        p2=doc[1]; p2.clean_contents(); p2.add_redact_annot(fitz.Rect(690,42,800,132),fill=(1,1,1)); p2.apply_redactions(images=2,graphics=1)
    out=io.BytesIO();doc.save(out,deflate=True,garbage=3);doc.close();return Response(content=out.getvalue(),media_type='application/pdf')
