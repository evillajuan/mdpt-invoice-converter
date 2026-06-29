'use client';
import {useMemo,useState} from 'react';import JSZip from 'jszip';import InvoiceSidebar from './InvoiceSidebar';import InvoiceForm,{FormState,emptyForm} from './InvoiceForm';import PdfPreview from './PdfPreview';import type {Client,EmailConfig,Profile} from '@/lib/types';
export type Invoice={id:string;file:File;name:string;edited?:Uint8Array;form:FormState;clientId?:string};
const download=(bytes:Uint8Array,name:string)=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
async function applyOne(invoice:Invoice):Promise<Uint8Array>{const d=new FormData();d.set('pdf',invoice.file);Object.entries(invoice.form).forEach(([k,v])=>{if(k!=='profileId'&&k!=='locationId')d.set(k,String(v||''))});const r=await fetch('/api/pdf_edit',{method:'POST',body:d});if(!r.ok){const txt=await r.text().catch(()=>'PDF editing failed');let msg='PDF editing failed';try{msg=JSON.parse(txt)?.detail||JSON.parse(txt)?.error||txt}catch{}throw new Error(msg)}return new Uint8Array(await r.arrayBuffer())}
export default function EditorView({clients,profiles,email,notify,goSettings}:{clients:Client[];profiles:Profile[];email:EmailConfig;notify:(m:string)=>void;goSettings:()=>void}){
  const [items,setItems]=useState<Invoice[]>([]);
  const [activeId,setActiveId]=useState<string>();
  const [selectedIds,setSelectedIds]=useState<Set<string>>(new Set());
  const [busy,setBusy]=useState(false);
  const active=items.find(i=>i.id===activeId);
  const add=(files:File[])=>{const valid=files.filter(f=>f.type==='application/pdf'||f.name.toLowerCase().endsWith('.pdf'));const def=profiles.find(p=>p.isDefault)||profiles[0];const fresh=valid.map(file=>({id:crypto.randomUUID(),file,name:file.name,form:{...emptyForm,...(def?{profileId:def.id,companyName:def.name,website:def.website||'',addr1:def.addr1||'',addr2:[def.city,def.state&&def.zip?`${def.state} ${def.zip}`:def.state||def.zip].filter(Boolean).join(', '),remitEmail:def.remitEmail||''}:{})}}));setItems(x=>[...x,...fresh]);if(!activeId&&fresh[0])setActiveId(fresh[0].id)};
  // When multiple invoices are selected, form changes propagate to all of them
  const update=(patch:Partial<Invoice>)=>{
    if(!active)return;
    const targets=selectedIds.size>1?selectedIds:new Set([active.id]);
    setItems(x=>x.map(i=>{
      if(!targets.has(i.id))return i;
      // For non-form patches (like edited bytes), only apply to active
      if(!patch.form&&i.id!==active.id)return i;
      return {...i,...patch,form:patch.form?{...i.form,...patch.form}:i.form};
    }));
  };
  const apply=async()=>{if(!active)return;setBusy(true);try{const edited=await applyOne(active);setItems(x=>x.map(i=>i.id===active.id?{...i,edited}:i));notify('Invoice is ready')}catch(e){notify(e instanceof Error?e.message:'PDF editing failed')}finally{setBusy(false)}};
  const applySelected=async()=>{
    if(selectedIds.size===0||!active)return;
    setBusy(true);
    // Sync active invoice's form + clientId to all selected before processing
    const sharedForm=active.form;
    const sharedClientId=active.clientId;
    const synced=items.map(i=>selectedIds.has(i.id)?{...i,form:{...sharedForm},clientId:sharedClientId}:i);
    setItems(synced);
    const targets=synced.filter(i=>selectedIds.has(i.id));
    let done=0,failed=0;
    await Promise.all(targets.map(async inv=>{
      try{const edited=await applyOne(inv);setItems(x=>x.map(i=>i.id===inv.id?{...i,edited}:i));done++}catch{failed++}
    }));
    setBusy(false);
    notify(failed?`${done} ready, ${failed} failed`:`${done} invoice${done!==1?'s':''} ready`);
  };
  const ready=items.filter(i=>i.edited);
  const zipAll=async()=>{const z=new JSZip();ready.forEach(i=>z.file(`tessen-payroll-${i.name}`,i.edited!));const b=await z.generateAsync({type:'blob'});const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='tessen_invoices.zip';a.click()};
  const multiSelected=selectedIds.size>1;
  return <div className="h-full flex flex-col"><div className="flex-1 min-h-0 grid grid-cols-[252px_288px_minmax(360px,1fr)] grid-rows-1 overflow-hidden"><InvoiceSidebar items={items} activeId={activeId} setActiveId={setActiveId} selectedIds={selectedIds} setSelectedIds={setSelectedIds} add={add} remove={id=>{setItems(x=>x.filter(i=>i.id!==id));setSelectedIds(s=>{const n=new Set(s);n.delete(id);return n});if(id===activeId)setActiveId(items.find(i=>i.id!==id)?.id)}}/><InvoiceForm invoice={active} profiles={profiles} clients={clients} update={update} multiSelected={multiSelected}/><PdfPreview invoice={active}/></div><footer className="h-[52px] border-t border-[var(--rule)] flex items-center px-4 gap-2 bg-[var(--paper)]"><span className="mono text-[10px] text-[var(--smoke)] truncate mr-auto">{multiSelected?`${selectedIds.size} invoices selected`:active?`${active.name} · ${active.edited?'READY':'PENDING'}`:'NO INVOICE SELECTED'}</span><button className="btn" disabled={!active||busy||multiSelected} onClick={apply}>{busy&&!multiSelected?'Applying…':'Apply Changes'}</button><button className="btn btn-primary" disabled={selectedIds.size===0||busy} onClick={applySelected}>{busy&&multiSelected?`Applying…`:`Apply to ${selectedIds.size>0?`${selectedIds.size} Selected`:'Selected'}`}</button><button className="btn" disabled={!active?.edited||multiSelected} onClick={()=>active?.edited&&download(active.edited,`tessen-payroll-${active.name}`)}>Download</button><button className="btn" disabled={!ready.length} onClick={zipAll}>Download All</button></footer></div>}
