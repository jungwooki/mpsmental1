import http from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import reports from '../api/reports.js';import session from '../api/session.js';import upload from '../api/upload.js';
const routes={'/api/reports':reports,'/api/session':session,'/api/upload':upload};
http.createServer(async(req,res)=>{
 res.status=n=>{res.statusCode=n;return res;};res.json=b=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(b));};
 const url=new URL(req.url,'http://localhost');if(routes[url.pathname])return routes[url.pathname](req,res);
 try{const file=path.resolve('public','.'+(url.pathname==='/'?'/index.html':decodeURIComponent(url.pathname)));if(!file.startsWith(path.resolve('public')+path.sep))throw Error();res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2'})[path.extname(file)]||'application/octet-stream');res.end(await readFile(file));}catch{res.statusCode=404;res.end('Not found');}
}).listen(3000,'127.0.0.1',()=>console.log('http://127.0.0.1:3000'));
