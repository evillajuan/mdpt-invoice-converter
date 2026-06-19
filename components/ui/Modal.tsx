'use client';
export default function Modal({children,onClose}:{children:React.ReactNode;onClose:()=>void}){return <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-[2px] grid place-items-center p-5" onMouseDown={e=>{if(e.target===e.currentTarget)onClose()}}><div className="bg-[var(--paper)] border border-[var(--rule2)] w-full max-w-[560px] shadow-2xl">{children}</div></div>}
