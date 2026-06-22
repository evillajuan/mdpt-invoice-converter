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
    doc=fitz.open(stream=await pdf.read(),filetype='pdf'); p1=doc[0]; W=.57; grey=(.784,.784,.784); black=(0,0,0); x0,x1=42.52,269.29
    by0,by1=144.57,207.0; my0,my1=209.76,410.0
    remit_zone=fitz.Rect(x0,my0,x1,my1)
    # Only edit company and bill-to zones; leave remit zone intact
    edit_zones=[fitz.Rect(42.52,42.52,269.29,141.33),fitz.Rect(x0,by0,x1,by1),fitz.Rect(x0,by1,x1,my0)]
    # Remove form widgets in company/bill zones; update email widget in remit zone
    for w in list(p1.widgets()):
        if any(w.rect.intersects(r) for r in edit_zones):
            p1.delete_widget(w)
        elif w.rect.intersects(remit_zone):
            val=w.field_value or ''; name=w.field_name or ''
            if '@' in val or 'email' in name.lower() or 'remit' in name.lower():
                w.field_value=remitEmail; w.update()
    # Remove free-text annotations in edit zones only
    for a in list(p1.annots()):
        if a.type[0]!=12 and any(a.rect.intersects(r) for r in edit_zones): p1.delete_annot(a)
    # Redact text, images, line art in edit zones only
    p1.clean_contents()
    for r in edit_zones: p1.add_redact_annot(r,fill=(1,1,1))
    p1.apply_redactions(images=2,graphics=1)
    for r in edit_zones: p1.draw_rect(r,color=None,fill=(1,1,1),overlay=True)
    # Draw company box
    y0,y1=42.52,141.33; p1.draw_rect(fitz.Rect(x0,y0,x1,y0+12.76),color=None,fill=grey); p1.draw_rect(fitz.Rect(x0,y0,x1,y1),color=black,width=W)
    y=y0+26
    for text,font,size in [(companyName,'Helvetica-Bold',11),(website,'Helvetica',11),(addr1,'Helvetica',11),(addr2,'Helvetica',11)]:
        if text:p1.insert_text(fitz.Point(x0+6,y),text,fontname=font,fontsize=size,color=black)
        y+=13
    # Draw bill-to box border and insert client text
    p1.draw_line(fitz.Point(x0,by0),fitz.Point(x0,by1),color=black,width=W);p1.draw_line(fitz.Point(x1,by0),fitz.Point(x1,by1),color=black,width=W);p1.draw_line(fitz.Point(x0,by1),fitz.Point(x1,by1),color=black,width=W)
    y=by0+22
    for text in [clientName,locLine1,locLine2]:
        if text:p1.insert_text(fitz.Point(x0+6,y),text,fontname='Helvetica',fontsize=11,color=black);y+=13
    # Find lowest content in remit zone then append remittance label below it
    last_y=my0+30
    for block in p1.get_text('blocks'):
        bx0,by0_,bx1,by1_=block[0],block[1],block[2],block[3]
        if fitz.Rect(bx0,by0_,bx1,by1_).intersects(remit_zone) and by1_>last_y:
            last_y=by1_
    for w in list(p1.widgets()):
        if w.rect.intersects(remit_zone) and w.rect.y1>last_y:
            last_y=w.rect.y1
    ceiling_y=p1.rect.height
    for block in p1.get_text('blocks'):
        bx0,by0_,bx1,by1_=block[0],block[1],block[2],block[3]
        if by0_>my0 and bx1>x1+20 and by0_<ceiling_y:ceiling_y=by0_
    label_y=last_y+10
    if (ceiling_y-last_y)>=30:
        p1.insert_text(fitz.Point(x0+6,label_y),'Email remittance advice to:',fontname='Helvetica',fontsize=9,color=black)
        if remitEmail:p1.insert_text(fitz.Point(x0+6,label_y+12),remitEmail,fontname='Helvetica',fontsize=9,color=black)
    if len(doc)>1:
        p2=doc[1]; p2.clean_contents(); p2.add_redact_annot(fitz.Rect(690,42,800,132),fill=(1,1,1)); p2.apply_redactions(images=2,graphics=1)
    out=io.BytesIO();doc.save(out,deflate=True,garbage=3);doc.close();return Response(content=out.getvalue(),media_type='application/pdf')
