import ExcelJS from 'exceljs';
import AdmZip from 'adm-zip';
import config from '../data/config.json' with {type:'json'};
export const core=['경기긴장도','사회적 도움 활용','경기 준비 능력','실수 후 회복력','자기 통제력'];
const metrics=['MGI',...core,'경기 안정성','경기 중 감정 조절','외부평가 독립성','자기주도 학습능력','이미지트레이닝 활용능력','주위 적응 및 활용 능력','실패 후 회복력','훈련 태도 지수'];
const axes={P:['경기긴장도','경기 안정성','경기 중 감정 조절','실패 후 회복력'],R:['경기 준비 능력','자기주도 학습능력','이미지트레이닝 활용능력'],I:['실수 후 회복력','외부평가 독립성']};
const priority=['실수 후 회복력','경기 준비 능력','경기긴장도','자기 통제력','사회적 도움 활용'];
const stages={'Pre-PHV':'급성장 이전','Stage 1':'가속기','Stage 2':'급성장기','Stage 3':'감속기','Stage 4':'종료기'};
const phvs={'Pre-PHV':'PHV -2','Stage 1':'PHV -1','Stage 2':'PHV 0','Stage 3':'PHV 1','Stage 4':'PHV 2'};
export const identity=a=>JSON.stringify([a.n,a.birth,a.sex,a.date]);
const average=arr=>arr.length?arr.reduce((a,b)=>a+b,0)/arr.length:null;
function dateValue(v){
 if(v instanceof Date) v=v.toISOString().slice(0,10);
 if(typeof v==='number') v=new Date(Date.UTC(1899,11,30)+v*86400000).toISOString().slice(0,10);
 const s=String(v??'').trim();
 if(!/^\d{4}-\d{2}-\d{2}$/.test(s)||!Number.isFinite(Date.parse(s))||new Date(s).toISOString().slice(0,10)!==s)throw Error('날짜는 YYYY-MM-DD 형식 또는 엑셀 날짜여야 합니다.');
 return s;
}
export function ageMonths(birth,date){
 const b=new Date(birth),d=new Date(date);let m=(d.getUTCFullYear()-b.getUTCFullYear())*12+d.getUTCMonth()-b.getUTCMonth();
 const anniversary=n=>{const start=new Date(Date.UTC(b.getUTCFullYear(),b.getUTCMonth()+n,1));return new Date(Date.UTC(start.getUTCFullYear(),start.getUTCMonth(),Math.min(b.getUTCDate(),new Date(Date.UTC(start.getUTCFullYear(),start.getUTCMonth()+1,0)).getUTCDate())));};
 if(anniversary(m)>d)m--;return m+(d-anniversary(m))/(anniversary(m+1)-anniversary(m));
}
function text(v){if(v&&typeof v==='object'){if(v.richText)return v.richText.map(t=>t.text).join('');throw Error('수식이나 링크 대신 값으로 입력해 주세요.');}return String(v??'').trim();}
export function makeRecord(r,source){
 const n=text(r['선수명']),sex=text(r['성별']),birth=dateValue(r['생년월일']),date=dateValue(r['측정일']);
 if(!n||n.length>100||!['남','여'].includes(sex)||birth>date)throw Error('선수명·성별·생년월일·측정일을 확인해 주세요.');
 const team=text(r['소속팀']);if(/sample|샘플|예시/i.test(n+' '+team))throw Error('샘플 기록은 반영하지 않습니다.');
 const values={};for(const name of metrics){const v=text(r[name]);if(v===''||!Number.isFinite(Number(v))||Number(v)<1||Number(v)>6)throw Error(`${name}: 1~6 사이의 숫자가 필요합니다.`);values[name]=Number(v);}
 const raw={...values};delete raw.MGI;
 // Integer tenths avoid floating point drift at the established 4.5 boundary.
 const ax=Object.fromEntries(Object.entries(axes).map(([k,names])=>[k,names.reduce((s,n)=>s+Math.round(raw[n]*1e8),0)/names.length/1e8]));
 const code=Object.values(ax).map(v=>v>=4.5?'H':'L').join('');const type=Object.keys(config.types).find(k=>config.types[k].code===code);
 const strengths=core.filter(n=>raw[n]>=4.8),strongest=core.reduce((a,b)=>raw[a]>=raw[b]?a:b);
 const eligible=priority.filter(n=>raw[n]<4.8&&(strengths.length||n!==strongest));
 const next=!eligible.length?'심화: '+priority.reduce((a,b)=>raw[a]<=raw[b]?a:b):Math.max(...eligible.map(n=>raw[n]))>=4.5?eligible.reduce((a,b)=>raw[a]>=raw[b]?a:b):eligible[0];
 const ca=ageMonths(birth,date),byText=text(r['골연령 (년)']),bmText=text(r['골연령 (개월)']),by=Number(byText),bm=Number(bmText),ba=by*12+bm;
 const valid=byText!==''&&bmText!==''&&Number.isInteger(by)&&Number.isInteger(bm)&&bm>=0&&bm<12&&ba>=48&&ba<=240&&Math.abs(ba-ca)<=48;
 const stageRaw=text(r['성장 단계']),phv=text(r['PHV 단계']),stageOK=Boolean(stages[stageRaw])&&phvs[stageRaw]===phv,issues=[];
 if(!valid)issues.push('골연령 원자료 재확인');if(!stageOK)issues.push('성장단계·PHV 불일치');
 return {n,sex,birth,date,chart:text(r['차트번호']),team,phv,mgi:values.MGI,raw,axes:ax,code,type,typeName:config.types[type].name,strength:strengths.join(', ')||'가장 높은 지표: '+strongest,next,near:Object.values(config.types).map(t=>Math.round(100*(1-Math.sqrt(average(Object.keys(axes).map(k=>(ax[k]-t.bench[k])**2)))/5))),core:Object.fromEntries(core.map(n=>[n,raw[n]])),source,growth:{chronologicalMonths:ca,boneYearsRaw:byText,boneMonthsRaw:bmText,boneMonths:valid?ba:null,differenceMonths:valid?ba-ca:null,delayed:valid&&ba-ca<=-6,stageRaw,phvRaw:phv,stage:stageOK?stages[stageRaw]:null,height:text(r['현재 키 (cm)']),weight:text(r['현재 체중 (kg)']),issues,source}};
}
export async function parseWorkbook(buffer,filename){
 if(!/\.xlsx$/i.test(filename)||buffer.length>2*1024*1024||buffer.length<4)throw Error('2MB 이하의 .xlsx 파일을 선택해 주세요.');
 let entries;try{entries=new AdmZip(buffer).getEntries();}catch{throw Error('정상적인 엑셀 파일이 아닙니다.');}
 if(entries.length>1000||entries.reduce((s,e)=>s+e.header.size,0)>30*1024*1024)throw Error('압축을 푼 파일이 너무 큽니다.');
 const book=new ExcelJS.Workbook();await book.xlsx.load(buffer);
 const sheet=book.getWorksheet('입력 템플릿');if(!sheet)throw Error('입력 템플릿 시트가 없습니다.');
 if(sheet.rowCount>5003||sheet.columnCount>100)throw Error('한 번에 최대 5,000개 측정 기록을 업로드할 수 있습니다.');
 const headers=new Map();sheet.getRow(3).eachCell((c,col)=>{const label=text(c.value);if(label){if(headers.has(label))throw Error('중복 열 이름: '+label);headers.set(label,col);}});
 const required=['선수명','성별','생년월일','측정일','차트번호','소속팀',...metrics,'골연령 (년)','골연령 (개월)','성장 단계','PHV 단계','현재 키 (cm)','현재 체중 (kg)'];
 const missing=required.filter(k=>!headers.has(k));if(missing.length)throw Error('필수 열 누락: '+missing.join(', '));
 const records=[],errors=[];let input=0;
 for(let row=4;row<=sheet.rowCount;row++){
  const values=Object.fromEntries([...headers].map(([k,c])=>[k,sheet.getRow(row).getCell(c).value]));
  if(Object.values(values).every(v=>v==null||v===''))continue;input++;
  try{records.push(makeRecord(values,{file:filename.slice(0,180),row}));}catch(e){errors.push({row,message:e.message});}
 }
 if(!input)throw Error('입력된 측정 기록이 없습니다.');return {records,errors,input};
}
const comparable=a=>({mgi:a.mgi,raw:a.raw,team:a.team,phv:a.phv,growth:Object.fromEntries(Object.entries(a.growth).filter(([k])=>k!=='source'))});
function differences(a,b){
 const fields=[['MGI',a.mgi,b.mgi],['소속',a.team,b.team],['PHV',a.phv,b.phv],...Object.keys(b.raw).filter(k=>k in a.raw).map(k=>[k,a.raw[k],b.raw[k]]),...Object.entries({boneYearsRaw:'골연령(년)',boneMonthsRaw:'골연령(개월)',stageRaw:'성장단계',height:'키',weight:'체중'}).map(([k,label])=>[label,a.growth[k],b.growth[k]])];
 return fields.filter(([,x,y])=>String(x)!==String(y)).map(([field,from,to])=>({field,from,to}));
}
function equivalent(a,b){
 if(a.mgi!==b.mgi||a.team!==b.team||a.phv!==b.phv)return false;
 if(Object.entries(a.raw).some(([k,v])=>Math.abs(v-b.raw[k])>1e-8))return false;
 return Object.entries(a.growth).every(([k,v])=>{
  if(k==='source')return true;
  if(typeof v==='number'&&typeof b.growth[k]==='number')return Math.abs(v-b.growth[k])<1e-7;
  return JSON.stringify(v)===JSON.stringify(b.growth[k]);
 });
}
export function mergeRecords(existing,parsed,replace=false){
 const athletes=structuredClone(existing),map=new Map(athletes.map((a,i)=>[identity(a),i]));
 const summary={input:parsed.input,added:0,duplicates:0,metadata:0,conflicts:[],errors:[...parsed.errors],warnings:[],updated:0};const seen=new Map();
 for(const a of parsed.records){
  const key=identity(a);if(seen.has(key)){if(JSON.stringify(comparable(seen.get(key)))!==JSON.stringify(comparable(a))||seen.get(key).chart!==a.chart)summary.errors.push({row:a.source.row,message:'파일 안에 값이 다른 동일 측정 기록이 있습니다.'});else summary.duplicates++;continue;}seen.set(key,a);
  if(a.growth.issues.length)summary.warnings.push({row:a.source.row,message:a.growth.issues.join(' · ')});
  if(!map.has(key)){map.set(key,athletes.length);athletes.push(a);summary.added++;continue;}
  const i=map.get(key),old=athletes[i];
  if(equivalent(old,a)){if(a.chart&&a.chart!==old.chart){old.chart=a.chart;summary.metadata++;}else summary.duplicates++;continue;}
  summary.conflicts.push({row:a.source.row,name:a.n,date:a.date,changes:differences(old,a)});if(replace){athletes[i]=a;summary.updated++;}
 }
 athletes.sort((a,b)=>b.date.localeCompare(a.date)||b.n.localeCompare(a.n,'ko'));athletes.forEach((a,i)=>a.id=i);
 return {athletes,summary};
}
export function stats(athletes){return {records:athletes.length,identityKeys:new Set(athletes.map(a=>JSON.stringify([a.n,a.birth,a.sex]))).size,boneValid:athletes.filter(a=>a.growth.boneMonths!==null).length,delayed:athletes.filter(a=>a.growth.delayed).length,stageConflicts:athletes.filter(a=>!a.growth.stage).length,stages:Object.fromEntries([...Object.values(stages),'확인 필요'].map(s=>[s,athletes.filter(a=>(a.growth.stage||'확인 필요')===s).length]))};}
