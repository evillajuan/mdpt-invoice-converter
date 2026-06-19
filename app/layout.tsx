import './globals.css';
import type {Metadata} from 'next';
export const metadata:Metadata={title:'Tessen Invoice Editor',description:'White-glove invoice operations'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
