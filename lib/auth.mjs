import {createHmac,timingSafeEqual,createHash} from 'node:crypto';
const cookie='mps_admin';
const hash=s=>createHash('sha256').update(String(s)).digest();
export function passwordOK(value){return Boolean(process.env.ADMIN_PASSWORD)&&timingSafeEqual(hash(value),hash(process.env.ADMIN_PASSWORD));}
function sign(value){return createHmac('sha256',process.env.SESSION_SECRET||process.env.ADMIN_PASSWORD||'unconfigured').update(value).digest('base64url');}
export function authenticated(req){
 if(!process.env.ADMIN_PASSWORD)return false;
 const value=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith(cookie+'='))?.slice(cookie.length+1)||'';
 const [exp,signature]=value.split('.');return /^\d+$/.test(exp||'')&&Number(exp)>Date.now()&&Boolean(signature)&&timingSafeEqual(hash(signature),hash(sign(exp)));
}
export function sessionCookie(req,logout=false){const exp=String(Date.now()+8*60*60*1000);return `${cookie}=${logout?'':exp+'.'+sign(exp)}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${logout?0:28800}${process.env.VERCEL?'; Secure':''}`;}
export function guard(req){if(!authenticated(req))throw Object.assign(Error('관리자 로그인이 필요합니다.'),{status:401});}
export function originGuard(req){const origin=req.headers.origin;if(!origin||new URL(origin).host!==(req.headers['x-forwarded-host']||req.headers.host))throw Object.assign(Error('현재 사이트에서 다시 시도해 주세요.'),{status:403});}
export function previewSignature(buffer,filename,revision){return sign(createHash('sha256').update(buffer).update(filename).update(String(revision)).digest('hex'));}
export function signatureOK(value,expected){return typeof value==='string'&&timingSafeEqual(hash(value),hash(expected));}
