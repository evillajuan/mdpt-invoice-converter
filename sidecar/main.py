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
    HH=12.76; GAP=3.24; REMIT_TOP=207.0
    co_lines=[(t,f,s) for t,f,s in [(companyName,'Helvetica-Bold',10),(website,'Helvetica',10),(addr1,'Helvetica',10),(addr2,'Helvetica',10)] if t]
    n_co=len(co_lines) or 1; LH=13; cy0=42.52; cy1=cy0+HH+8+n_co*LH+6
    bill_lines=[t for t in [clientName,locLine1,locLine2] if t]; n_b=len(bill_lines) or 1
    by0=cy1+GAP; by1=min(by0+HH+8+n_b*LH+6, REMIT_TOP-GAP)
    clear_zone=fitz.Rect(x0,42.52,x1,REMIT_TOP)
    last_y=REMIT_TOP+30
    for block in p1.get_text('blocks'):
        bx0,by0_,bx1,by1_=block[0],block[1],block[2],block[3]
        if bx0>=x0-5 and bx1<=x1+5 and by0_>=REMIT_TOP and by1_>last_y: last_y=by1_
    label_y=last_y+10; nbb=label_y+26
    tearoff=fitz.Rect(x0-2,last_y,x1+2,nbb+20)
    for w in list(p1.widgets()):
        if w.rect.intersects(clear_zone) or w.rect.intersects(tearoff): p1.delete_widget(w)
    for a in list(p1.annots()):
        if a.type[0]!=12 and (a.rect.intersects(clear_zone) or a.rect.intersects(tearoff)): p1.delete_annot(a)
    p1.clean_contents(); p1.add_redact_annot(clear_zone,fill=(1,1,1)); p1.add_redact_annot(tearoff,fill=(1,1,1)); p1.apply_redactions(images=2,graphics=1)
    p1.draw_rect(clear_zone,color=None,fill=white,overlay=True); p1.draw_rect(tearoff,color=None,fill=white,overlay=True)
    p1.draw_rect(fitz.Rect(x0,cy0,x1,cy0+HH),color=None,fill=grey); p1.draw_rect(fitz.Rect(x0,cy0,x1,cy1),color=black,width=W)
    y=cy0+HH+8+LH-3
    for text,font,size in co_lines: p1.insert_text(fitz.Point(x0+6,y),text,fontname=font,fontsize=size,color=black); y+=LH
    p1.draw_rect(fitz.Rect(x0,by0,x1,by0+HH),color=None,fill=grey); p1.draw_rect(fitz.Rect(x0,by0,x1,by1),color=black,width=W)
    p1.insert_text(fitz.Point(x0+4,by0+HH-3),'BILL TO',fontname='Helvetica-Bold',fontsize=8,color=black)
    y=by0+HH+8+LH-3
    for text in bill_lines: p1.insert_text(fitz.Point(x0+6,y),text,fontname='Helvetica',fontsize=10,color=black); y+=LH
    p1.draw_line(fitz.Point(x0,REMIT_TOP),fitz.Point(x0,nbb),color=black,width=W); p1.draw_line(fitz.Point(x1,REMIT_TOP),fitz.Point(x1,nbb),color=black,width=W); p1.draw_line(fitz.Point(x0,nbb),fitz.Point(x1,nbb),color=black,width=W)
    p1.insert_text(fitz.Point(x0+6,label_y),'Email remittance information to:',fontname='Helvetica',fontsize=10,color=black)
    if remitEmail: p1.insert_text(fitz.Point(x0+6,label_y+13),remitEmail,fontname='Helvetica',fontsize=10,color=black)
    if len(doc)>1:
        p2=doc[1]; p2.clean_contents(); p2.add_redact_annot(fitz.Rect(690,42,800,132),fill=(1,1,1)); p2.apply_redactions(images=2,graphics=1)
    out=io.BytesIO();doc.save(out,deflate=True,garbage=3);doc.close();return Response(content=out.getvalue(),media_type='application/pdf')
