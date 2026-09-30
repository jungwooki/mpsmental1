import {parseWorkbook,mergeRecords} from '../lib/mental.mjs';
import {readState,writeState} from '../lib/store.mjs';
import {guard,originGuard,previewSignature,signatureOK} from '../lib/auth.mjs';
import {send,error,body} from '../lib/http.mjs';
export default async function handler(req,res){try{
 if(req.method!=='POST')return send(res,405,{error:'허용되지 않은 요청입니다.'});
 originGuard(req);guard(req);const b=await body(req);
 if(!['preview','commit'].includes(b.action)||typeof b.file!=='string'||typeof b.filename!=='string'||!/^[A-Za-z0-9+/]*={0,2}$/.test(b.file))throw Error('업로드 요청 형식을 확인해 주세요.');
 const buffer=Buffer.from(b.file,'base64');const parsed=await parseWorkbook(buffer,b.filename);
 const {state,etag}=await readState();const result=mergeRecords(state.athletes,parsed,b.replace===true);
 const signature=previewSignature(buffer,b.filename,state.revision);
 if(b.action==='preview')return send(res,200,{summary:result.summary,revision:state.revision,signature});
 if(b.revision!==state.revision||!signatureOK(b.signature,signature))return send(res,409,{error:'검사 후 데이터가 변경되었거나 파일이 바뀌었습니다. 다시 검사해 주세요.'});
 if(result.summary.errors.length)return send(res,422,{error:'오류 행을 수정한 뒤 다시 업로드해 주세요.',summary:result.summary});
 if(result.summary.conflicts.length&&!b.replace)return send(res,409,{error:'기존 값 변경을 확인한 뒤 반영해 주세요.',summary:result.summary});
 if(!result.summary.added&&!result.summary.updated&&!result.summary.metadata)return send(res,200,{ok:true,unchanged:true,summary:result.summary,revision:state.revision});
 const now=new Date().toISOString();const entry={file:b.filename.slice(0,180),at:now,added:result.summary.added,updated:result.summary.updated,metadata:result.summary.metadata,duplicates:result.summary.duplicates};
 const next={revision:state.revision+1,updatedAt:now,athletes:result.athletes,history:[entry,...state.history].slice(0,100)};
 await writeState(state,next,etag);return send(res,200,{ok:true,summary:result.summary,revision:next.revision});
 }catch(e){return error(res,e);}}
