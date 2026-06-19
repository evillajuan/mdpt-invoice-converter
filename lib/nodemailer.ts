import nodemailer from 'nodemailer';
export const gmailTransport=(user:string,pass:string)=>nodemailer.createTransport({host:'smtp.gmail.com',port:465,secure:true,auth:{user,pass}});
