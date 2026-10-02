'use strict';
const UPLOAD_STORAGE_KEY='mps-mental2-athletes-v1';
const BASE_ATHLETES=ATH.slice();
function readUploadedAthletes(){
  const saved=JSON.parse(localStorage.getItem(UPLOAD_STORAGE_KEY)||'[]');
  if(!Array.isArray(saved)||!saved.every(a=>a&&a.n&&a.birth&&a.sex&&a.date&&TYPES[a.type]&&a.raw&&a.axes&&Array.isArray(a.near)&&a.growth&&Array.isArray(a.growth.issues))) throw new Error('저장된 선수 데이터를 읽을 수 없습니다.');
  return saved;
}
function applyUploadedAthletes(saved){
  const identities=new Set(BASE_ATHLETES.map(MPSAthleteImport.key));
  const charts=new Set(BASE_ATHLETES.map(MPSAthleteImport.chartKey).filter(Boolean));
  ATH.splice(0,ATH.length,...BASE_ATHLETES);
  for(const a of saved){
    const identity=MPSAthleteImport.key(a),chart=MPSAthleteImport.chartKey(a);
    if(identities.has(identity)||(chart&&charts.has(chart))) continue;
    identities.add(identity);if(chart)charts.add(chart);
    ATH.push({...a,id:ATH.length});
  }
  for(const stage of ORDER){
    const group=ATH.filter(a=>a.growth.stage===stage),mgi=group.map(a=>a.mgi).filter(Number.isFinite);
    STAGE_GROUPS[stage]=group;
    STAGE_MEANS[stage]={n:group.length,mgi:mgi.length?mgi.reduce((a,b)=>a+b,0)/mgi.length:null,raw:Object.fromEntries(stageMetrics.map(n=>[n,mean(group,n)]))};
    DETAIL_STAGE_STATS[stage]=detailStats(group);
  }
  for(const k of Object.keys(AGE_GROUPS))delete AGE_GROUPS[k];
  for(const k of Object.keys(DETAIL_AGE_STATS))delete DETAIL_AGE_STATS[k];
  ATH.forEach(a=>{const years=detailAgeYears(a);if(years!==null)(AGE_GROUPS[years]??=[]).push(a);});
  for(const [years,records] of Object.entries(AGE_GROUPS))DETAIL_AGE_STATS[years]=detailStats(records);
  DATA.stats.stageConflicts=ATH.filter(a=>!a.growth.stage).length;
  DATA.stats.records=ATH.length;
  DATA.stats.identityKeys=new Set(ATH.map(MPSAthleteImport.key)).size;
  DATA.stats.boneValid=ATH.filter(a=>a.growth.boneMonths!==null).length;
  DATA.stats.delayed=ATH.filter(a=>a.growth.delayed).length;
  DATA.stats.stages=Object.fromEntries(ORDER.map(s=>[s,STAGE_GROUPS[s].length]));
  populate();
}
function uploadStatus(message,error=false){
  const el=$('uploadStatus');el.hidden=false;el.textContent=message;el.classList.toggle('error',error);
}
let excelLibrary;
function loadExcelLibrary(){
  if(globalThis.ExcelJS)return Promise.resolve();
  if(!excelLibrary)excelLibrary=new Promise((resolve,reject)=>{
    const script=document.createElement('script');script.src='assets/vendor/exceljs.min.js';
    script.onload=()=>resolve();script.onerror=()=>{script.remove();excelLibrary=null;reject(new Error('Excel 읽기 도구를 불러오지 못했습니다. 다시 시도해 주세요.'));};document.head.append(script);
  });
  return excelLibrary;
}
$('athleteUploadBtn').addEventListener('click',()=>$('athleteUploadInput').click());
$('athleteUploadInput').addEventListener('change',async event=>{
  const file=event.target.files[0];if(!file)return;
  const button=$('athleteUploadBtn');button.disabled=true;button.setAttribute('aria-busy','true');
  $('uploadErrors').hidden=true;$('uploadErrorList').replaceChildren();
  uploadStatus('Excel 파일을 확인하고 있습니다…');
  try{
    if(!/\.xlsx$/i.test(file.name))throw new Error('.xlsx 형식의 MPS 입력값 Excel 파일을 선택해 주세요.');
    if(file.size>20*1024*1024)throw new Error('파일은 20MB 이하로 업로드해 주세요.');
    await loadExcelLibrary();
    const workbook=new ExcelJS.Workbook();
    try{await workbook.xlsx.load(await file.arrayBuffer());}catch{throw new Error('Excel 파일을 읽을 수 없습니다. 손상되거나 암호화되지 않은 .xlsx 파일인지 확인해 주세요.');}
    const saved=readUploadedAthletes();
    const result=MPSAthleteImport.parseWorkbook(workbook,[...BASE_ATHLETES,...saved],TYPES,file.name);
    if(!result.total)throw new Error('파일에 선수 데이터가 없습니다.');
    const updated=[...saved,...result.added];
    // Save before changing the report; a quota/permission failure never claims success.
    if(result.added.length){
      try{localStorage.setItem(UPLOAD_STORAGE_KEY,JSON.stringify(updated));}
      catch{throw new Error('브라우저에 저장하지 못했습니다. 저장 공간 또는 사이트 저장 권한을 확인해 주세요. 선수는 추가되지 않았습니다.');}
    }
    applyUploadedAthletes(updated);
    if(result.added.length){
      $('search').value='';delayedOnly=false;$('lateFilter').setAttribute('aria-pressed','false');$('lateFilter').classList.remove('active');populate();
      const index=ATH.findIndex(a=>MPSAthleteImport.key(a)===MPSAthleteImport.key(result.added[0]));
      $('athleteSelect').value=index;render(index);
    }
    uploadStatus(`${file.name} · 신규 선수 ${result.added.length}명 추가 · 중복 ${result.duplicate}건 건너뜀 · 입력 오류 ${result.errors.length}건${result.added.length?' · 이 브라우저에 저장되었습니다.':''}`,result.errors.length>0);
    if(result.errors.length){
      $('uploadErrors').hidden=false;
      for(const error of result.errors){const li=document.createElement('li');li.textContent=`${error.row}행: ${error.reason}`;$('uploadErrorList').append(li);}
    }
  }catch(error){uploadStatus(error.message||'업로드하지 못했습니다. 파일을 확인해 주세요.',true);}
  finally{button.disabled=false;button.removeAttribute('aria-busy');event.target.value='';}
});
try{const saved=readUploadedAthletes();if(saved.length){applyUploadedAthletes(saved);uploadStatus(`이 브라우저에 저장된 추가 선수 ${ATH.length-BASE_ATHLETES.length}명을 불러왔습니다.`);}}
catch{uploadStatus('이 브라우저의 저장 데이터에 접근할 수 없습니다. 기존 선수만 표시합니다.',true);}
window.addEventListener('storage',event=>{
  if(event.key===UPLOAD_STORAGE_KEY||event.key===null){try{applyUploadedAthletes(readUploadedAthletes());uploadStatus('다른 탭의 선수 변경 내용을 반영했습니다.');}catch{uploadStatus('저장된 선수 데이터를 읽지 못했습니다.',true);}}
});
