import {NextResponse} from 'next/server'; import {prisma} from '@/lib/prisma';
export async function PATCH(r:Request,{params}:{params:{id:string}}){const b=await r.json();if(b.isDefault)await prisma.companyProfile.updateMany({data:{isDefault:false}});return NextResponse.json(await prisma.companyProfile.update({where:{id:params.id},data:b}));}
export async function DELETE(_:Request,{params}:{params:{id:string}}){await prisma.companyProfile.delete({where:{id:params.id}});return NextResponse.json({success:true});}
