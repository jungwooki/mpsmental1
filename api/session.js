import {authenticated,passwordOK,sessionCookie,originGuard} from '../lib/auth.mjs';
import {send,error,body} from '../lib/http.mjs';
export default async function handler(req,res){try{
 if(req.method==='GET')return send(res,200,{authenticated:authenticated(req),configured:Boolean(process.env.ADMIN_PASSWORD&&process.env.BLOB_READ_WRITE_TOKEN||process.env.LOCAL_DATA_FILE)});
 originGuard(req);
 if(req.method==='DELETE'){res.setHeader('Set-Cookie',sessionCookie(req,true));return send(res,200,{ok:true});}
 if(req.method!=='POST')return send(res,405,{error:'허용되지 않은 요청입니다.'});
 const value=await body(req);if(!passwordOK(value.password)){await new Promise(r=>setTimeout(r,800));return send(res,401,{error:'관리자 비밀번호를 확인해 주세요.'});}
 res.setHeader('Set-Cookie',sessionCookie(req));return send(res,200,{ok:true});
 }catch(e){return error(res,e);}}
