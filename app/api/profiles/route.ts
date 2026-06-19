import {NextResponse} from 'next/server'; import {prisma} from '@/lib/prisma';
export async function GET(){return NextResponse.json(await prisma.companyProfile.findMany({orderBy:[{isDefault:'desc'},{name:'asc'}]}));}
export async function POST(r:Request){const b=await r.json();if(b.isDefault)await prisma.companyProfile.updateMany({data:{isDefault:false}});return NextResponse.json(await prisma.companyProfile.create({data:{...b,name:b.name||'Untitled Profile'}}));}
