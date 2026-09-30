// Explicit integration runner; uses an isolated LOCAL_DATA_FILE dev server.
import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import ExcelJS from 'exceljs';
const base=process.env.TEST_URL||'http://127.0.0.1:3000';let cookie='';
async function request(path,method='GET',data,auth=true){const r=await fetch(base+path,{method,headers:{Origin:base,'Content-Type':'application/json',...(auth?{Cookie:cookie}:{})},body:data?JSON.stringify(data):undefined});if(r.headers.get('set-cookie'))cookie=r.headers.get('set-cookie').split(';')[0];return {status:r.status,data:await r.json()};}
assert.equal((await request('/api/upload','POST',{},false)).status,401);
assert.equal((await request('/api/session','POST',{password:'incorrect'})).status,401);
assert.equal((await request('/api/session','POST',{password:process.env.ADMIN_PASSWORD})).status,200);
const before=(await request('/api/reports')).data;
const file=await readFile('/Users/jungwooklee/Downloads/mps-authoring-inputs (12).xlsx');
const raw={filename:'mps-authoring-inputs (12).xlsx',file:file.toString('base64')};
const check=await request('/api/upload','POST',{...raw,action:'preview'});assert.equal(check.status,200);assert.equal(check.data.summary.input,285);assert.equal(check.data.summary.added,0);assert.equal(check.data.summary.errors.length,0);
if(base!=='http://127.0.0.1:3000'){console.log('PASS live: auth, report read, real workbook preview; production records not modified');process.exit(0);}
const source=new ExcelJS.Workbook();await source.xlsx.load(file);const workbook=new ExcelJS.Workbook(),sheet=workbook.addWorksheet('입력 템플릿');for(let i=1;i<=4;i++)sheet.getRow(i).values=source.getWorksheet('입력 템플릿').getRow(i).values;sheet.getCell('A4').value='자동업로드 검증';sheet.getCell('D4').value='2026-09-30';
const upload={filename:'integration.xlsx',file:Buffer.from(await workbook.xlsx.writeBuffer()).toString('base64')};
const p=(await request('/api/upload','POST',{...upload,action:'preview'})).data;assert.equal(p.summary.added,1);
const commit={...upload,action:'commit',revision:p.revision,signature:p.signature};
assert.equal((await request('/api/upload','POST',{...commit,signature:'forged'})).status,409);
const saved=await request('/api/upload','POST',commit);assert.equal(saved.status,200,JSON.stringify(saved.data));assert.equal(saved.data.summary.added,1);
assert.equal((await request('/api/upload','POST',commit)).status,409);
const after=(await request('/api/reports')).data;assert.equal(after.athletes.length,before.athletes.length+1);assert.equal(after.history[0].added,1);
const again=(await request('/api/upload','POST',{...upload,action:'preview'})).data;assert.equal(again.summary.duplicates,1);
const same=await request('/api/upload','POST',{...upload,action:'commit',revision:again.revision,signature:again.signature});assert.equal(same.data.unchanged,true);
sheet.getCell('K4').value=0;upload.file=Buffer.from(await workbook.xlsx.writeBuffer()).toString('base64');const invalid=(await request('/api/upload','POST',{...upload,action:'preview'})).data;assert.equal(invalid.summary.errors.length,1);assert.equal((await request('/api/upload','POST',{...upload,action:'commit',revision:invalid.revision,signature:invalid.signature})).status,422);
await request('/api/session','DELETE');assert.equal((await request('/api/session')).data.authenticated,false);
console.log('PASS: auth, real-file preview, append, persistence, duplicate no-op, invalid-row blocking, forged and stale preview rejection, logout');
