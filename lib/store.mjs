import {get,put,BlobPreconditionFailedError} from '@vercel/blob';
import {randomUUID} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const pathname='mental/state.json';
export async function readState(){
 if(process.env.LOCAL_DATA_FILE&&!process.env.VERCEL){const state=JSON.parse(await readFile(process.env.LOCAL_DATA_FILE,'utf8'));return {state,etag:String(state.revision)};}
 if(!process.env.BLOB_READ_WRITE_TOKEN)throw Error('서버 저장소 연결이 필요합니다.');
 const result=await get(pathname,{access:'private',useCache:false});
 if(!result)throw Error('서버 초기 데이터가 없습니다.');
 return {state:await new Response(result.stream).json(),etag:result.blob.etag};
}
export async function writeState(previous,next,etag){
 if(process.env.LOCAL_DATA_FILE&&!process.env.VERCEL){const current=await readState();if(current.etag!==etag)throw Object.assign(Error('다른 업로드가 먼저 반영되었습니다. 다시 검사해 주세요.'),{status:409});await writeFile(process.env.LOCAL_DATA_FILE,JSON.stringify(next));return;}
 await put(`mental/backups/${previous.revision}-${randomUUID()}.json`,JSON.stringify(previous),{access:'private',addRandomSuffix:false,contentType:'application/json'});
 try{await put(pathname,JSON.stringify(next),{access:'private',addRandomSuffix:false,allowOverwrite:true,ifMatch:etag,contentType:'application/json'});}catch(e){if(e instanceof BlobPreconditionFailedError)throw Object.assign(Error('다른 업로드가 먼저 반영되었습니다. 다시 검사해 주세요.'),{status:409});throw e;}
}
