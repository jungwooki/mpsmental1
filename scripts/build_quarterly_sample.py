# -*- coding: utf-8 -*-
"""Build a clearly fictional, interactive quarterly review concept; keep live v4 intact."""
from pathlib import Path
import json,re,math
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]
base=(ROOT/'scripts/growth_report_template.html').read_text()
v4=(ROOT/'MPS_멘탈포지션_성장통합_A4_3페이지_v4.html').read_text()
source=json.loads(re.search(r'const DATA=(.*?);\n',v4)[1])
style=re.search(r'<style>(.*?)</style>',base,re.S)[1]
helpers=base[base.index('function renderRadar('):base.index('function renderStageComparison(')]
core=['경기긴장도','사회적 도움 활용','경기 준비 능력','실수 후 회복력','자기 통제력']
axes={'P':['경기긴장도','경기 안정성','경기 중 감정 조절','실패 후 회복력'],'R':['경기 준비 능력','자기주도 학습능력','이미지트레이닝 활용능력'],'I':['실수 후 회복력','외부평가 독립성']}
records=[]
for i,(values,extra) in enumerate([
 ([3.8,4.8,5.0,3.4,4.0],[3.9,4.0,3.6,5.0,4.8,3.7]),
 ([4.1,4.9,5.1,4.0,4.2],[4.0,4.1,3.9,5.1,4.9,4.2]),
 ([4.3,5.0,5.2,4.3,4.3],[4.1,4.2,4.1,5.2,5.0,4.4]),
 ([4.2,5.1,5.3,4.2,4.4],[4.1,4.1,4.2,5.2,5.1,4.3]),
]):
 raw=dict(zip(core,values));raw.update(zip(['경기 안정성','경기 중 감정 조절','실패 후 회복력','자기주도 학습능력','이미지트레이닝 활용능력','외부평가 독립성'],extra))
 raw.update({'주위 적응 및 활용 능력':[4.2,4.5,4.7,4.5][i],'훈련 태도 지수':[4.8,4.9,5.0,4.9][i]})
 ax={k:mean(raw[n] for n in ns) for k,ns in axes.items()}
 code=''.join('H' if ax[k]>=4.5 else 'L' for k in axes)
 letter=next(k for k,t in source['types'].items() if t['code']==code)
 records.append({'n':'샘플','chart':'SAMPLE-001','birth':'2014-10-16','sex':'남','growth':{'chronologicalMonths':[137,140,143,146][i],'stage':['급성장 이전','가속기','가속기','가속기'][i]},'date':['2026-03-16','2026-06-16','2026-09-16','2026-12-16'][i], 'stage':['급성장 이전','가속기','가속기','가속기'][i], 'context':['새 팀에 적응하는 기간','학교 일정과 훈련 루틴 조정','경기 출전 기회 증가','대회 일정과 학업 부담 증가'][i], 'raw':raw,'axes':ax,'type':letter,'near':[math.floor(100*(1-math.sqrt(mean((ax[k]-t['bench'][k])**2 for k in axes))/5)+.5) for t in source['types'].values()]})
references={s:{'raw':dict(zip(core+['실패 후 회복력','외부평가 독립성'],vals))} for s,vals in [('급성장 이전',[4.2,5.0,4.6,4.5,4.4,4.2,4.5]),('가속기',[4.3,5.1,4.6,4.6,4.4,4.1,4.7])]}
detail_names=['경기 안정성','경기 중 감정 조절','외부평가 독립성','자기주도 학습능력','이미지트레이닝 활용능력','주위 적응 및 활용 능력','실패 후 회복력','훈련 태도 지수']
for stage in references:
    for name,value in zip(detail_names,[4.3,4.4,4.5,4.6,4.5,4.7,4.2,4.9]):
        references[stage]['raw'].setdefault(name,value)
peer_references={11:dict(zip(detail_names,[4.1,4.3,4.4,4.5,4.4,4.6,4.0,4.8])),12:dict(zip(detail_names,[4.3,4.4,4.6,4.7,4.6,4.8,4.3,5.0]))}
payload=json.dumps({'records':records,'peerReferences':peer_references,'references':references,'types':source['types'],'photos':source['photos']},ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
flags='''<div class="flags" aria-label="잉글랜드, 벨기에, 네덜란드 국기 장식"><svg viewBox="0 0 30 20" role="img" aria-label="잉글랜드"><title>잉글랜드</title><path fill="#fff" d="M0 0h30v20H0z"/><path fill="#ce2633" d="M12 0h6v20h-6zM0 7h30v6H0z"/></svg><svg viewBox="0 0 30 20" role="img" aria-label="벨기에"><title>벨기에</title><path fill="#242424" d="M0 0h10v20H0z"/><path fill="#edcd50" d="M10 0h10v20H10z"/><path fill="#d65356" d="M20 0h10v20H20z"/></svg><svg viewBox="0 0 30 20" role="img" aria-label="네덜란드"><title>네덜란드</title><path fill="#b34953" d="M0 0h30v7H0z"/><path fill="#fff" d="M0 7h30v6H0z"/><path fill="#3e6091" d="M0 13h30v7H0z"/></svg></div>'''
def header(): return '<header><img src="assets/mps-logo-black.png" alt="SportsMPS"><div class="meta"><b class="report-name">대한민국 유일 바이오밴딩기반 멘탈리포트</b><br><span class="record-meta"></span></div></header>'
def footer(n):return f'<div class="footer"><span><b>SportsMPS</b> · 3개월마다 이어가는 성장 기록</span>{flags if n==4 else ""}<span>가상 샘플 · {n} / 4</span></div>'
html='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MPS 3개월 성장 리뷰 · 가상 샘플</title><style>'''+style+'''
.sample-mark{font-size:8px;color:#905b41;background:#f5eadc;border-radius:4px;padding:1.5mm 2.5mm;line-height:1.5}.quarterly .page{gap:3mm}.timeline{display:grid;grid-template-columns:repeat(4,1fr);gap:2mm}.visit{border-top:2px solid #d6ddd1;padding-top:2mm;font-size:9px;color:var(--sub)}.visit b{display:block;font-size:11px;margin-bottom:1mm}.visit.current{border-color:var(--orange);color:var(--orange)}.visit.future{opacity:.6}.visit small{display:block;margin-top:1mm;font-size:8px}.quarterly #page1 .hero{min-height:33mm}.quarterly #page1 .hero img{height:33mm}.quarterly #page1 .hero h2{font-size:24px}.quarterly #page1 .players-section{margin-top:2.5mm}.quarterly #page1 .player-card img{height:27mm}.quarterly .card .big{font-size:19px}.quarterly .section-title{margin-bottom:2mm}.qtable{font-variant-numeric:tabular-nums}.qtable th,.qtable td{padding:2mm 1.5mm}.qtable th{font-size:8px;line-height:1.5}.qtable td{font-size:10px}.qtable .separate{border-left:1px solid var(--line)}.trend{width:100%;height:43mm;display:block}.trend-legend{display:flex;gap:4mm;font-size:9px;margin:1mm 0 2mm}.trend-legend span:before{content:'';display:inline-block;width:5mm;margin-right:1mm;border-top:2px solid var(--color);vertical-align:middle}.qcompare{display:grid;grid-template-columns:.86fr 1.14fr;gap:4mm;align-items:center}.qcompare #radar{height:46mm}.qcompare h4{margin:2mm 0 1mm}.qcompare p{font-size:10px}.qsummary{display:grid;grid-template-columns:1fr 1fr;gap:3mm}.qsummary .big{font-size:21px}.review-table{width:100%;border-collapse:collapse;font-size:10px}.review-table th{text-align:left;color:var(--sub);font-weight:500;width:23%;padding:3mm 2mm;border-bottom:1px solid var(--line)}.review-table td{padding:3mm 2mm;border-bottom:1px solid var(--line);line-height:1.65}.goal-card{padding:3mm!important}.goal-card h4{color:var(--green);font-size:12px;margin:1.5mm 0}.goal-card p{font-size:10px}.goal-card .number{font-size:17px}.appointment{display:flex;align-items:center;justify-content:space-between;gap:4mm}.appointment strong{font-size:19px;color:var(--green)}.flags{display:flex;gap:2.5mm;align-items:center;opacity:.72}.flags svg{display:block;width:6mm;height:4mm;border:0.2px solid #d6d6ce;border-radius:1px}.quarterly .support-scene img{height:32mm}.sample-guide{line-height:1.8}.sample-guide p{margin:8px 0}.sample-guide a{color:var(--green)}
</style></head><body><nav class="toolbar"><b style="font-size:12px">3개월 성장 리뷰 · 가상 샘플</b><select id="visitSelect" aria-label="샘플 측정 회차"><option value="0">1회차 · 첫 측정</option><option value="1" selected>2회차 · 3개월 리뷰</option><option value="2">3회차 · 6개월 누적</option><option value="3">4회차 · 9개월 누적</option></select><button class="print" onclick="window.print()">4페이지 인쇄 / PDF</button></nav><main class="report quarterly">
<section class="page" id="page1">'''+header()+'''
<div class="sample-mark">디자인 샘플 · 선수 이력, 측정 점수, 비교 평균, 관찰 기록은 모두 가상 예시입니다.</div>
<div class="heading"><div class="eyebrow">01 / My quarterly growth review</div><h1 class="main-title" id="reviewHeading"></h1><p class="identity" id="identity"></p></div>
<div class="timeline" id="timeline"></div>
<div class="hero"><div><span class="tag" id="reviewTag"></span><h2 id="mixedType"></h2><p id="heroMessage"></p></div><img src="assets/growth-mental-watercolor-v4.png" alt="다시 공을 향해 뛰어가는 어린 선수 일러스트"></div>
<div class="three" id="highlights"></div>
<div class="band orange"><h3 id="parentHeadline"></h3><p id="parentMessage"></p></div>
<div><div class="section-title"><h3>이번 측정의 8가지 멘탈 포지션</h3><span>유형 유사도 · 순위나 성공 확률이 아닙니다</span></div><div class="affinity" id="affinity"></div></div>
<div class="players-section"><div class="section-title"><h3>이 포지션을 떠올리게 하는 선수들</h3><span id="playerTypeLabel"></span></div><div class="players-grid" id="playersGrid"></div><p class="micro players-note">공개된 경기 스타일을 이해하기 위한 예시입니다. 해당 선수의 실제 심리검사 결과나 추천·제휴를 뜻하지 않습니다.</p></div>
<p class="micro">같은 유형이어도 점수와 경기 속 행동은 달라질 수 있습니다. 유형 변경을 승급·하락으로 표현하지 않고, 지난 측정 이후 무엇이 달라졌는지 함께 읽습니다.</p>'''+footer(1)+'''
</section><section class="page" id="page2">'''+header()+'''
<div class="sample-mark">변화 그래프·비교 평균 모두 가상 예시 · 각 측정의 동일한 1~6점 척도를 비교합니다.</div>
<div class="heading"><div class="eyebrow">02 / Change over time</div><h2>지난번의 나와 비교하고,<br>지금의 성장단계 안에서 읽어요.</h2><p class="intro" id="comparisonIntro"></p></div>
<div class="chart-section"><div class="section-title"><h3>다시 시도하는 힘의 변화</h3><span id="trendPeriod"></span></div><div class="trend-legend"><span style="--color:#c36846">실수 후 회복력</span><span style="--color:#568879">실패 후 회복력</span><span style="--color:#7d78a1">외부평가 독립성</span></div><svg id="trend" class="trend" viewBox="0 0 690 190" role="img" aria-labelledby="trendTitle trendDesc"></svg></div>
<div><div class="section-title"><h3>내 변화와 단계 평균, 나란히 보기</h3><span>차이 단위: 점</span></div><table class="score-table qtable"><thead><tr><th scope="col">지표</th><th scope="col">직전</th><th scope="col">이번</th><th scope="col">직전 대비</th><th scope="col">최초 대비</th><th scope="col" class="separate">현재 단계<br>평균</th><th scope="col">단계 평균<br>대비</th></tr></thead><tbody id="changeRows"></tbody></table><p class="micro" style="margin-top:2mm" id="changeNote"></p></div>
<div class="chart-section"><div class="section-title"><h3>현재의 5대 지표</h3><span id="cohortLabel"></span></div><div class="qcompare"><div><div class="legend"><span>이번 측정</span><span class="reference" id="referenceLegend"></span></div><svg id="radar" viewBox="0 0 360 285" role="img" aria-labelledby="radarTitle radarDesc"></svg></div><div><h4>성장단계도 함께 기록합니다</h4><p id="stageMessage"></p><h4>숫자와 실제 장면을 함께 봅니다</h4><p id="contextMessage"></p></div></div></div>
<p class="micro">점수 차이를 통계적으로 유의한 향상이나 프로그램의 효과로 단정하지 않습니다. 측정 때의 피로·수면·경기 경험과 응답 조건을 함께 확인합니다. 추세 그래프에는 완료된 회차만 표시합니다.</p>'''+footer(2)+'''
</section>__DETAIL_PAGE__<section class="page" id="page4">'''+header()+'''
<div class="sample-mark">아래 목표·실행·관찰 내용은 모두 작성 방식의 예시입니다. 실제 리포트는 선수·보호자·지도자 기록으로 채웁니다.</div>
<div class="heading"><div class="eyebrow">04 / Our next three months</div><h2>지난 약속을 돌아보고,<br>다음 3개월을 함께 정해요.</h2><p class="intro" id="planIntro"></p></div>
<div><div class="section-title"><h3 id="reviewTitle"></h3><span>선수 · 보호자 · 지도자의 관찰</span></div><table class="review-table"><tbody id="goalReview"></tbody></table></div>
<div class="band"><h3 id="reviewMessageTitle"></h3><p id="reviewMessage"></p></div>
<div><div class="section-title"><h3>다음 3개월, 함께 이어갈 행동</h3><span>점수 목표보다 실천할 행동</span></div><div class="three"><div class="card goal-card"><span class="number">01</span><h4>선수의 작은 연습</h4><p>실수 뒤 숨을 내쉬고 다음 위치로 움직입니다. 훈련이 끝나면 다시 참여한 장면 하나를 남깁니다.</p></div><div class="card goal-card"><span class="number">02</span><h4>보호자의 피드백</h4><p>주 1회 “다시 해본 순간이 있었어?”라고 물어봅니다. 결과보다 실제로 시도한 행동을 짚어줍니다.</p></div><div class="card goal-card"><span class="number">03</span><h4>지도자와의 연결</h4><p>한 달에 한 번 같은 행동을 관찰합니다. 출전 기회·훈련 변화·몸의 불편함을 함께 메모합니다.</p></div></div></div>
<div class="support-scene"><div><div class="eyebrow">Small steps, shared over time</div><h3>점수만 남기지 않고,<br>아이의 경험을 함께 쌓습니다.</h3><p>성장단계 · 몸의 변화 · 다시 시도한 행동을 같은 기록 안에서 이어갑니다. 다음 측정에서는 지난 목표와 실제 경험을 먼저 돌아봅니다.</p></div><img src="assets/growth-support-watercolor-v4.png" alt="아이의 이야기를 함께 듣는 보호자와 지도자"></div>
<div class="band orange appointment"><div><h4>다음 3개월 리뷰</h4><p>일정은 선수·보호자·지도자와 조율합니다.</p></div><strong id="nextDate"></strong></div>
<div class="band"><h4>다음 리포트에 함께 가져올 기록</h4><div class="checkrow"><span>같은 문항·응답 조건으로 측정한 점수</span><span>최근 성장단계와 체격의 변화</span><span>지난 목표를 실행한 장면</span><span>훈련·수면·출전 환경의 변화</span></div><div class="flow"><span>측정</span><span>→ 한 가지 목표</span><span>→ 경험 기록</span><span>→ 3개월 리뷰</span></div></div>
<p class="micro">이 샘플은 3개월 반복 측정 리포트의 구성안입니다. 반복 기록 연결은 고유 선수 ID를 기준으로 하고, 비교 집단과 집계 시점을 기록해 기준 변경을 구분하는 방식으로 운영합니다.</p>'''+footer(4)+'''
</section></main>
<details class="web-only sample-guide"><summary>샘플의 구성과 실제 운영 시 적용할 기준</summary><p>회차 선택으로 첫 측정, 3개월 리뷰, 6개월·9개월 누적 화면을 확인할 수 있습니다. 모든 선수 점수와 비교 평균은 가상입니다. 이 파일은 실제 749건 리포트와 별도의 가상 예시입니다.</p><p>첫 측정: 출발점과 다음 목표만 표시. 직전 변화는 “—”로 둡니다. 두 번째 측정: 직전·최초 대비 변화 표시. 세 번째부터: 누적 추세를 이어갑니다. 점수가 내려가는 예시도 포함했습니다.</p><p>유형·유사도 계산은 기존 P/R/I와 4.5 경계, H 5.2/L 3.8 기준점을 유지했습니다. 성장단계는 별도 배경으로 기록합니다. 누락된 측정은 0점으로 채우거나 가짜 추세선으로 연결하지 않습니다.</p><p>실제 운영: 고유 선수 ID, 측정일, 문항/척도 버전, 응답자, 성장단계, 원점수, 당시 비교집단 규모와 평균 버전을 저장합니다. 재검사 자료가 없는 현재 기록에 과거 점수를 추정해 붙이지 않습니다. 지표의 오차·신뢰도 근거 없이 ‘유의한 개선’을 자동 판정하지 않습니다.</p><p>하단 국기는 작은 장식 요소입니다. 국가기관·협회·클럽의 인증이나 제휴 문구를 붙이지 않았습니다.</p><p>표현 구조 참고: <a href="https://www.pearsonclinical.ca/content/dam/school/global/clinical/ca/assets/ssis-sel/ssis-progress-report-sample.pdf">Pearson SSIS Progress Report</a>의 최초·직전 대비 비교와 <a href="https://core.catapultsports.com/hc/en-us/articles/7551850858639-Longitudinal-Report">Catapult Longitudinal Report</a>의 기간별 비교. 동일 검사나 MPS 모델의 타당성 근거로 사용한 것은 아닙니다.</p></details>
<script>const DATA='''+payload+''';
const TYPES=DATA.types,PLAYER_PHOTOS=DATA.photos,RECORDS=DATA.records;
const CORE=['경기긴장도','사회적 도움 활용','경기 준비 능력','실수 후 회복력','자기 통제력'];
const REC=['실수 후 회복력','실패 후 회복력','외부평가 독립성'];
const $=id=>document.getElementById(id),text=(id,v)=>$(id).textContent=v;
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>Number.isFinite(v)?v.toFixed(1):'—';
const delta=(a,b)=>{if(!Number.isFinite(a)||!Number.isFinite(b))return '—';const d=Number((a-b).toFixed(1));return `${d>0?'+':''}${d.toFixed(1)}`;};
'''+helpers+'''
__DETAIL_SCRIPT__
function trend(index){
 const history=RECORDS.slice(0,index+1),colors=['#c36846','#568879','#7d78a1'],x=i=>62+i*188,y=v=>142-(v-1)*23;
 let svg='<title id="trendTitle">회복 3지표의 회차별 변화 · 가상 예시</title><desc id="trendDesc">1~6점 척도. 완료한 회차만 표시하며 다음 회차의 점수는 예측하지 않습니다.</desc>';
 for(let v=1;v<=6;v++)svg+=`<line x1="48" x2="652" y1="${y(v)}" y2="${y(v)}" stroke="#e2e5dd"/><text x="28" y="${y(v)+3}" fill="#718176" font-size="10">${v}</text>`;
 for(let i=0;i<4;i++)svg+=`<text x="${x(i)}" y="166" text-anchor="middle" fill="#67766c" font-size="11">${i+1}회 · ${RECORDS[i].date.slice(5).replace('-','.')}</text><text x="${x(i)}" y="183" text-anchor="middle" fill="#89958b" font-size="9">${i<=index?RECORDS[i].stage:'예정'}</text>`;
 REC.forEach((n,j)=>{if(history.length>1)svg+=`<polyline fill="none" stroke="${colors[j]}" stroke-width="2.5" ${j===1?'stroke-dasharray="6 3"':j===2?'stroke-dasharray="2 3"':''} points="${history.map((r,i)=>`${x(i)},${y(r.raw[n])}`).join(' ')}"/>`;history.forEach((r,i)=>svg+=`<circle cx="${x(i)}" cy="${y(r.raw[n])}" r="${j===0?4:3}" fill="${colors[j]}" stroke="white" stroke-width="1"><title>${r.date} ${n} ${fmt(r.raw[n])}점</title></circle>`);});
 if(index===0)svg+='<text x="352" y="70" text-anchor="middle" fill="#697975" font-size="12">오늘의 출발점입니다. 다음 측정부터 변화를 이어갑니다.</text>';
 $('trend').innerHTML=svg;
}
function render(index){
 const a=RECORDS[index],prev=RECORDS[index-1],first=RECORDS[0],t=TYPES[a.type],ref=DATA.references[a.stage];
 window.currentVisit=index;document.title=`MPS_3개월성장리뷰_가상샘플_${index+1}회차_${a.date}`;
 document.querySelectorAll('.record-meta').forEach(n=>n.textContent=`샘플 선수 · ${index+1}회차 · ${a.date}`);
 $('reviewHeading').innerHTML=index?'지난 3개월의 변화,<br>다음 성장의 방향을 찾습니다.':'오늘의 출발점을 기록하고,<br>다음 3개월을 함께 시작합니다.';
 text('identity',`샘플 선수 · 샘플 FC U12 · ${index?'최초 측정 후 '+index*3+'개월':'첫 측정'}`);
 $('timeline').innerHTML=RECORDS.map((r,i)=>`<div class="visit ${i===index?'current':i>index?'future':''}"><b>${i+1}회 · ${i?i*3+'개월':'출발점'}</b>${r.date}<small>${i<=index?r.stage:'측정 예정'}</small></div>`).join('');
 text('reviewTag',index?'3개월 성장 리뷰 · '+(index+1)+'회차':'첫 측정 · 나의 출발점');
 $('mixedType').innerHTML=`${a.stage}의<br>${t.name}`;
 text('heroMessage',index?'포지션 이름이 같아도, 다시 시도하는 힘은 조금씩 달라질 수 있어요.':'준비하는 강점과 회복의 출발점을 함께 기록합니다.');
 const recovery=a.raw[REC[0]],difference=prev?delta(recovery,prev.raw[REC[0]]):'—';
 $('highlights').innerHTML=[['이번 실수 후 회복력',fmt(recovery)+' / 6',prev?'직전 '+fmt(prev.raw[REC[0]])+'점 → 이번 '+fmt(recovery)+'점':'첫 측정의 실제 점수를 기록해요'],['지난 측정과의 변화',prev?difference+'점':'첫 기준점',prev?'최초 대비 '+delta(recovery,first.raw[REC[0]])+'점':'다음 측정부터 차이를 표시해요'],['성장단계의 흐름',a.stage,prev?prev.stage+' → '+a.stage:'이번 측정의 성장 배경']].map(([label,big,small])=>`<div class="card"><span class="label">${label}</span><span class="big">${big}</span><small>${small}</small></div>`).join('');
 text('parentHeadline',index===0?'오늘의 결과는, 앞으로 비교할 출발점입니다.':index===3?'작은 변동도, 지난 경험과 함께 읽습니다.':'준비하는 강점을 이어가며, 다시 돌아오는 힘을 살펴요.');
 text('parentMessage',index===0?'점수로 서열을 정하지 않고, 실수 뒤 다시 참여하는 행동 하나를 함께 고릅니다.':index===3?'실수 후 회복력은 직전보다 0.1점 낮지만 최초보다 0.8점 높습니다. 대회 일정·수면·부담을 함께 확인하고 한 번의 변동을 퇴보로 단정하지 않습니다.':`실수 후 회복력 ${fmt(prev.raw[REC[0]])} → ${fmt(recovery)}점. 숫자의 변화와 함께, 훈련에서 실수 뒤 다시 움직인 장면이 있었는지 아이에게 물어봅니다.`);
 renderDetailPage({athlete:a,stageStats:Object.fromEntries(DETAIL_METRICS.map(n=>[n,{mean:ref.raw[n],example:true}])),ageStats:Object.fromEntries(DETAIL_METRICS.map(n=>[n,{mean:DATA.peerReferences[detailAgeYears(a)][n],example:true}])),history:detailPrevious(a,RECORDS.slice(0,index+1)),sample:true});
 renderProfile(a,t);renderRadar({...a,growth:{stage:a.stage}},ref);trend(index);
 text('comparisonIntro',`${prev?prev.date+' → ':''}${a.date} · 최초 측정 ${first.date}`);text('trendPeriod',`${index+1}회 측정 · ${index*3}개월 기록`);
 const metrics=[...new Set([...CORE,...REC])];
 $('changeRows').innerHTML=metrics.map(n=>`<tr><td>${n}</td><td>${fmt(prev?.raw[n])}</td><td class="mine">${fmt(a.raw[n])}</td><td>${delta(a.raw[n],prev?.raw[n])}</td><td>${index?delta(a.raw[n],first.raw[n]):'—'}</td><td class="separate">${fmt(ref.raw[n])}</td><td>${delta(a.raw[n],ref.raw[n])}</td></tr>`).join('');
 text('changeNote',index?'직전·최초 대비는 내 원점수의 변화입니다. 단계 평균 대비는 이번 점수 − 현재 성장단계 평균이며, 별도의 비교입니다.':'첫 측정은 변화량을 계산하지 않습니다. 직전·최초 대비의 “—”는 0점이 아니라 비교할 이전 기록이 없다는 뜻입니다.');
 text('cohortLabel',a.stage+' · 비교 평균도 가상 예시');text('referenceLegend',a.stage+' 평균');
 text('stageMessage',prev&&prev.stage!==a.stage?`${prev.stage} → ${a.stage}로 바뀌었습니다. 비교 집단도 달라지므로 ‘평균과의 격차 변화’를 아이의 향상량으로 해석하지 않습니다.`:index?`이번과 직전 모두 ${a.stage}입니다. 이 샘플은 같은 단계의 비교 평균을 고정해 표시합니다. 실제 운영에서는 집계 시점·표본 수·평균 버전을 함께 기록합니다.`:`현재 ${a.stage}입니다. 첫 점수와 성장 배경을 함께 저장하고 다음 측정 때 같은 척도로 비교합니다.`);
 text('contextMessage',`이번 기록의 배경: ${a.context}. 실제 리포트에서는 선수·보호자·지도자가 확인한 경험을 함께 적습니다.`);
 text('planIntro',`${index?'지난 3개월 리뷰 + ':''}다음 목표 · ${a.date} 기준`);text('reviewTitle',index?'지난 3개월의 약속, 어떻게 이어졌을까요?':'첫 측정에서 함께 정할 출발점');
 const rows=index===0?[['현재의 경험','실수 뒤 다시 움직이기까지 어떤 생각이 드는지 아이에게 들어봅니다.'],['처음 정할 행동','짧게 숨을 내쉬고 다음 위치로 움직이는 신호 하나를 고릅니다.'],['기록 방법','주 1회, 다시 참여한 장면과 그날의 컨디션을 한 줄로 남깁니다.']]:[['지난 목표','실수 뒤 짧게 숨을 내쉬고 다음 플레이 위치로 돌아가기'],['실행 기록',index===1?'최근 관찰 6회 중 4회, 스스로 신호 동작을 사용함 · 지도자 기록 예시':index===2?'최근 관찰 6회 중 5회, 스스로 신호 동작을 사용함 · 지도자 기록 예시':'최근 관찰 6회 중 4회, 스스로 신호 동작을 사용함 · 지도자 기록 예시'],['선수의 한마디',index===3?'“대회 때는 급해져서 신호를 잊을 때가 있어요.” · 가상 발언':'“실수해도 다음 공을 받으러 가보려고 했어요.” · 가상 발언'],['함께 볼 환경',a.context+' · 보호자·지도자 기록 예시']];
 $('goalReview').innerHTML=rows.map(([k,v])=>`<tr><th scope="row">${k}</th><td>${v}</td></tr>`).join('');
 text('reviewMessageTitle',index?'다음에도 이어갈 목표 · 실수 후 다시 참여하기':'이번에 함께 시작할 목표 · 실수 후 다시 참여하기');text('reviewMessage',index?'관찰한 행동과 점수의 흐름을 함께 보고, 같은 연습을 이어갈지 조절할지 결정합니다. 횟수는 관찰 장면 수와 함께 기록합니다.':'이번에는 결과를 약속하기보다 실행할 행동과 기록 방법을 정합니다. 다음 측정에서 점수·경험·실행을 함께 돌아봅니다.');
 const date=new Date(a.date+'T00:00:00Z');date.setUTCMonth(date.getUTCMonth()+3);text('nextDate',date.toISOString().slice(0,10).replaceAll('-','.'));
}
$('visitSelect').addEventListener('change',e=>render(Number(e.target.value)));
function resize(){document.documentElement.style.setProperty('--scale',Math.min(1,(innerWidth-16)/(210*96/25.4)));}window.addEventListener('resize',resize);resize();render(1);
</script></body></html>'''
for token, filename in [('__DETAIL_PAGE__', 'mental_detail_page.html'), ('__DETAIL_STYLE__', 'mental_detail.css'), ('__DETAIL_SCRIPT__', 'mental_detail_charts.js')]:
    html = html.replace(token, (ROOT / 'scripts' / filename).read_text())
(ROOT/'MPS_바이오밴딩_3개월성장리뷰_샘플.html').write_text(html)
print('Created interactive sample with four fictional assessments; existing v4 unchanged.')
