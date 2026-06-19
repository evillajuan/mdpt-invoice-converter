import {NextResponse} from 'next/server'; import {prisma} from '@/lib/prisma';
export async function POST(r:Request,{params}:{params:{id:string}}){const b=await r.json();return NextResponse.json(await prisma.location.create({data:{label:b.label,line1:b.line1,line2:b.line2||null,clientId:params.id}}));}
export async function DELETE(r:Request){const {id}=await r.json();await prisma.location.delete({where:{id}});return NextResponse.json({success:true});}
