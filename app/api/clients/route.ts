import {NextResponse} from 'next/server'; import {prisma} from '@/lib/prisma';
export async function GET(){return NextResponse.json(await prisma.client.findMany({include:{locations:true},orderBy:{name:'asc'}}));}
export async function POST(r:Request){const b=await r.json();return NextResponse.json(await prisma.client.create({data:{name:b.name||'Untitled Client'},include:{locations:true}}));}
