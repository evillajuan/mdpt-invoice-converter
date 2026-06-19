import {NextResponse} from 'next/server'; import {prisma} from '@/lib/prisma';
export async function GET(){return NextResponse.json(await prisma.emailSettings.upsert({where:{id:'singleton'},create:{id:'singleton'},update:{}}));}
export async function POST(r:Request){const b=await r.json();return NextResponse.json(await prisma.emailSettings.upsert({where:{id:'singleton'},create:{id:'singleton',...b},update:b}));}
