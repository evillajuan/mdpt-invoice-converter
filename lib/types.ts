export type Location={id:string;label:string;line1:string;line2?:string|null;clientId?:string};
export type Client={id:string;name:string;type?:string|null;poNumber?:string|null;c1Name?:string|null;c1Title?:string|null;c1Email?:string|null;c1Phone?:string|null;c2Name?:string|null;c2Title?:string|null;c2Email?:string|null;c2Phone?:string|null;bcName?:string|null;bcTitle?:string|null;bcEmail?:string|null;bcPhone?:string|null;notes?:string|null;locations:Location[]};
export type Profile={id:string;name:string;website?:string|null;phone?:string|null;email?:string|null;remitEmail?:string|null;addr1?:string|null;city?:string|null;state?:string|null;zip?:string|null;isDefault:boolean};
export type EmailConfig={id:string;gmailUser?:string|null;gmailAppPwd?:string|null;senderName?:string|null};
