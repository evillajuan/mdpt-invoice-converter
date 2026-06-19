import {NextResponse} from 'next/server'; import {prisma} from '@/lib/prisma';
export async function GET(_:Request,{params}:{params:{id:string}}){return NextResponse.json(await prisma.client.findUnique({where:{id:params.id},include:{locations:true}}));}
export async function PATCH(r:Request,{params}:{params:{id:string}}){const b=await r.json();delete b.locations;delete b.id;return NextResponse.json(await prisma.client.update({where:{id:params.id},data:b,include:{locations:true}}));}
export async function DELETE(_:Request,{params}:{params:{id:string}}){await prisma.client.delete({where:{id:params.id}});return NextResponse.json({success:true});}
