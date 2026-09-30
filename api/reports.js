import {readState} from '../lib/store.mjs';
import {stats} from '../lib/mental.mjs';
import {authenticated} from '../lib/auth.mjs';
import {send,error} from '../lib/http.mjs';
import config from '../data/config.json' with {type:'json'};
export default async function handler(req,res){try{
 if(req.method!=='GET')return send(res,405,{error:'허용되지 않은 요청입니다.'});
 const {state}=await readState();return send(res,200,{...config,athletes:state.athletes,stats:stats(state.athletes),revision:state.revision,updatedAt:state.updatedAt,history:authenticated(req)?state.history:[]});
 }catch(e){e.status=503;return error(res,e);}}
