export function send(res,status,body){res.setHeader('Cache-Control','no-store');return res.status(status).json(body);}
export function error(res,e){console.error('Request failed:',e.name,e.status||500);return send(res,e.status||400,{error:e.status===500?'서버 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.':e.message});}
export async function body(req){
 if(req.body!==undefined){const b=typeof req.body==='string'?JSON.parse(req.body):req.body;if(JSON.stringify(b).length>2900000)throw Error('파일이 너무 큽니다.');return b;}
 const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>2900000)throw Error('파일이 너무 큽니다.');chunks.push(chunk);}return JSON.parse(Buffer.concat(chunks).toString());
}
