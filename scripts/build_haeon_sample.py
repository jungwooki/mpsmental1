# -*- coding: utf-8 -*-
"""Create two fictional visits using the latest four-page report design."""
from pathlib import Path
import json,re,copy
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'MPS_멘탈포지션_성장통합_A4_4페이지_v4.html').read_text()
quarterly=(ROOT/'MPS_바이오밴딩_3개월성장리뷰_샘플.html').read_text()
def data(s): return json.loads(re.search(r'const DATA=(.*?);\n',s)[1])
q=data(quarterly)
records=copy.deepcopy(q['records'][:2])
for i,a in enumerate(records):
 a.update(id=i,n='김해온(샘플)',chart='FICTIONAL-HAEON-001',team='MPS FC U12(가상)',mgi=[4.2,4.5][i])
 a['growth'].update(boneMonths=[134,137][i],differenceMonths=-3,delayed=False,height=[147.2,149.1][i],weight=[38.2,39.0][i],issues=[],stageRaw=a['stage'],phvRaw=['PHV -2','PHV -1'][i])
payload={'athletes':records,'types':q['types'],'photos':q['photos'],'references':q['references'],'peerReferences':q['peerReferences'],'stats':{'stageConflicts':0}}
source=re.sub(r'const DATA=.*?;\n',lambda m:'const DATA='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',source,count=1)
# Keep all scores and means fictional; never compute cohort means from these two visits.
start=source.index('const STAGE_MEANS=')
end=source.index('const DETAIL_STAGE_STATS=',start)
source=source[:start]+"const STAGE_MEANS=Object.fromEntries(ORDER.map(stage=>[stage,{n:0,mgi:4.5,raw:DATA.references[stage]?.raw||{}}]));\n"+source[end:]
source=source.replace('function render(idx){','function renderBase(idx){',1)
insert='''
function render(idx){
 renderBase(idx);
 const a=ATH[idx],ref=DATA.references[a.growth.stage],previous=detailPrevious(a,ATH);
 document.title=`김해온(샘플)_${idx+1}회_멘탈리포트`;
 document.querySelectorAll('.record-meta').forEach(el=>el.textContent=`김해온(샘플) · ${idx+1}회 ${idx?'3개월 후':'첫 측정'} · ${a.date}`);
 text('identity',`김해온(샘플) · ${idx+1}회 ${idx?'3개월 후 리뷰':'첫 측정'} · MPS FC U12(가상) · 남`);
 text('stageSource','가상 성장단계 · 샘플 설정');
 text('cohortLabel',a.growth.stage+' · 가상 평균');
 text('meanNote','가상 샘플: 선수 정보·체격·점수·MGI·비교 평균은 모두 예시입니다. 실제 검사 결과나 실제 집단 통계가 아닙니다. 차이 = 이번 점수 − 같은 성장단계 예시 평균.');
 text('parentHeadline',idx?'3개월 후, 다시 시도하는 힘의 변화를 살펴요.':'첫 측정, 우리 아이의 출발점을 기록해요.');
 text('parentMessage',idx?'실수 후 회복력 3.4 → 4.0점. 성장단계는 급성장 이전에서 가속기로 바뀐 가상 사례입니다. 3페이지의 직전 대비는 1회 점수와 직접 비교합니다.':'이번 결과를 첫 기준점으로 남깁니다. 이전 측정이 없어 직전 변화는 표시하지 않으며, 3개월 후 같은 지표로 다시 살펴봅니다.');
 renderDetailPage({athlete:a,stageStats:Object.fromEntries(DETAIL_METRICS.map(n=>[n,{mean:ref.raw[n],example:true}])),ageStats:Object.fromEntries(DETAIL_METRICS.map(n=>[n,{mean:DATA.peerReferences[detailAgeYears(a)][n],example:true}])),history:previous,sample:true});
 // Each page carries a visible fiction label without adding a separate block.
 document.querySelectorAll('.footer span:first-child').forEach(el=>el.innerHTML='<b>SportsMPS</b> · 가상 샘플: 선수 정보·점수·평균 모두 예시');
}
'''
source=source.replace('let delayedOnly=false;',insert+'\nlet delayedOnly=false;')
source=source.replace('o.textContent=`${a.n} · ${a.team} · ${a.date}`','o.textContent=`${a.n} · ${i+1}회 ${i?"3개월 후":"첫 측정"} · ${a.date}`')
source=source.replace('<input id="search"','<input hidden id="search"').replace('<button id="lateFilter"','<button hidden id="lateFilter"')
source=source.replace('<small id="filterCount"></small>','<small id="filterCount" hidden></small><small>선수 정보·점수·평균 모두 가상 예시</small>')
# The embedded cohort audit belongs to live-data reports, so omit it from this sample UI.
source=source.replace('<details class="web-only">','<details class="web-only" style="display:none">')
source=source.replace('resize();populate();','resize();populate();const visit=Number(new URLSearchParams(location.search).get("visit")||1)-1;if(visit===0||visit===1){$("athleteSelect").value=visit;render(visit);}')
(ROOT/'MPS_김해온(샘플)_1회_2회.html').write_text(source)
print('Created Kim Haeon fictional sample: two visits, current four-page design.')
