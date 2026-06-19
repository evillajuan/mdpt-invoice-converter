'use client';
import { useRouter } from 'next/navigation';
export type Tab='editor'|'clients'|'settings';
export default function TopBar({tab,setTab}:{tab:Tab;setTab:(t:Tab)=>void}){
  const router = useRouter();
  async function logout(){
    await fetch('/api/auth/logout',{method:'POST'});
    router.replace('/login');
  }
  return <header className="h-[58px] bg-[var(--deep)] text-[#F7F2EB] flex items-stretch px-6"><div className="serif text-[24px] flex items-center mr-14">Tessen</div><nav className="flex gap-8">{(['editor','clients','settings'] as Tab[]).map(t=><button key={t} onClick={()=>setTab(t)} className={`capitalize text-[12px] border-0 border-b-2 bg-transparent px-1 ${tab===t?'border-[var(--brass)] text-white':'border-transparent text-[#AAA69E]'}`}>{t}</button>)}</nav><div className="ml-auto flex items-center gap-3 text-[10px] text-[#BDB8AF] mono"><span className="w-1.5 h-1.5 bg-[var(--success)] rounded-full"/> SYSTEM READY<button onClick={logout} className="text-[#AAA69E] hover:text-white border border-[#AAA69E] hover:border-white rounded px-2 py-0.5 transition-colors">Sign out</button></div></header>;
}
