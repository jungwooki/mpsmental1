# -*- coding: utf-8 -*-
"""Add missing assessments, restore source names, and rebuild the report statistics.
Usage: python3 scripts/merge_authoring.py input.xlsx
Existing assessments are retained; exact assessment matches are not re-added.
"""
from pathlib import Path
from collections import Counter
from statistics import mean
from decimal import Decimal
import sys,json,re,math,csv,html
from xlsx_reader import rows
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'MPS_멘탈포지션_A4_3페이지_리포트_v3.html'
s=REPORT.read_text()
ath=json.loads(re.search(r'const ATH=(.*?);\n',s)[1])
types=json.loads(re.search(r'const TYPES=(.*?);\n',s)[1])
previous=json.loads(re.search(r'const ANALYSIS=(.*?);\n',s)[1])
core=['경기긴장도','사회적 도움 활용','경기 준비 능력','실수 후 회복력','자기 통제력']
axes={'P':['경기긴장도','경기 안정성','경기 중 감정 조절','실패 후 회복력'],'R':['경기 준비 능력','자기주도 학습능력','이미지트레이닝 활용능력'],'I':['실수 후 회복력','외부평가 독립성']}
priority=['실수 후 회복력','경기 준비 능력','경기긴장도','자기 통제력','사회적 도움 활용']
path=Path(sys.argv[1]);source_cache={}
# Restore names only through the recorded file and row, never infer masked names.
for a in ath:
 f=a['source']['file']
 if f not in source_cache:
  original=ROOT/f if f.startswith('MPS_') else path.parent/f
  source_cache[f]=dict(rows(original,5 if f.startswith('MPS_') else 1))
 r=source_cache[f][a['source']['row']]
 a['n']=r['A'].strip()
 if not f.startswith('MPS_'):a['birth']=r['C'];a['chart']=r.get('E','')
counts=Counter(previous['exclusions']);counts['input']=previous['input']
audit=previous['audit'];file_counts=previous['files'];legacy_count=previous['legacyCount']
# Idempotence: do not count an already-imported source file twice.
already=any(f['file']==path.name for f in file_counts)
rr=rows(path);headers=rr[2][1];fc=Counter();added=[]
for row,r in rr[3:]:
 if not any(r.values()):continue
 source={'file':path.name,'row':row}
 if not already:counts['input']+=1;fc['input']+=1
 try:
  assert all(r.get(c) for c in 'ABCD')
  values={headers[c]:float(r[c]) for c in 'KLMNOPQRSTUVWX'}
  assert all(math.isfinite(v) and 1<=v<=6 for v in values.values())
  assert not re.search('sample|샘플|예시',r['A']+' '+r.get('F',''),re.I)
 except (KeyError,ValueError,AssertionError):
  if not already:counts['신규 결측/범위/샘플']+=1;audit.append({**source,'name':r.get('A',''),'reason':'신규 결측/범위/샘플'})
  continue
 raw={k:v for k,v in values.items() if k!='MGI'}
 matches=[a for a in ath if a['n']==r['A'].strip() and a['sex']==r['B'] and a['date']==r['D'] and (not a.get('birth') or a['birth']==r['C'])]
 exact=[a for a in matches if abs(a['mgi']-values['MGI'])<1e-8 and all(abs(a['raw'][k]-raw[k])<1e-8 for k in a['raw'] if k in raw)]
 if matches and not exact:raise ValueError(f'Conflicting assessment at input row {row}')
 if exact:
  assert len(exact)==1, f'Ambiguous identity at input row {row}'
  exact[0]['birth']=r['C'];exact[0]['chart']=r.get('E','')
  if not already:counts['추가파일 동일 측정']+=1;fc['overlap']+=1;audit.append({**source,'name':r['A'],'reason':'추가파일 동일 측정','kept':exact[0]['source']})
  continue
 ax={k:float(sum(Decimal(str(raw[n])) for n in names)/len(names)) for k,names in axes.items()}
 code=''.join('H' if ax[k]>=4.5 else 'L' for k in axes);letter=next(k for k,t in types.items() if t['code']==code)
 strengths=[n for n in core if raw[n]>=4.8];strongest=max(core,key=lambda n:raw[n]);eligible=[n for n in priority if raw[n]<4.8 and (strengths or n!=strongest)]
 nxt=('심화: '+min(priority,key=lambda n:raw[n])) if not eligible else max(eligible,key=lambda n:raw[n]) if max(raw[n] for n in eligible)>=4.5 else eligible[0]
 near=[math.floor(100*(1-math.sqrt(mean((ax[k]-t['bench'][k])**2 for k in axes))/5)+.5) for t in types.values()]
 a={'id':len(ath),'n':r['A'].strip(),'birth':r['C'],'chart':r.get('E',''),'sex':r['B'],'team':r.get('F',''),'date':r['D'],'phv':r.get('Y',''),'mgi':values['MGI'],'raw':raw,'axes':ax,'code':code,'type':letter,'typeName':types[letter]['name'],'strength':', '.join(strengths) or '가장 높은 지표: '+strongest,'next':nxt,'near':near,'core':{k:raw[k] for k in core},'source':source}
 ath.append(a);added.append(a);fc['added']+=1
if not already:file_counts.append({'file':path.name,**fc})
ath.sort(key=lambda a:(a['date'],a['n']),reverse=True)
for i,a in enumerate(ath):a['id']=i
print('New assessments:',len(added),'Total:',len(ath))
def profile(group):
 return {'n':len(group),'mgi':mean(a['mgi'] for a in group) if group else None,'core':{k:mean(a['core'][k] for a in group) if group else None for k in core},'axes':{k:mean(a['axes'][k] for a in group) if group else None for k in axes},'raw':{k:mean(a['raw'][k] for a in group if k in a['raw']) if any(k in a['raw'] for a in group) else None for k in sorted({n for a in ath for n in a['raw']})}}
stats={'legacyCount':legacy_count,'newCount':len(ath)-legacy_count,'unit':'records','identityNote':'기존 자료는 생년월일 부재로 동일인 재측정 여부를 확정할 수 없어 기록 단위로 유지합니다. 이름만 같은 기록은 병합하지 않습니다.','input':counts['input'],'included':len(ath),'exclusions':{k:v for k,v in counts.items() if k!='input'},'files':file_counts,'period':[min(a['date'] for a in ath),max(a['date'] for a in ath)],'overall':profile(ath),'types':{k:profile([a for a in ath if a['type']==k]) for k in types},'audit':audit}
j=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
s=re.sub(r'const ATH=.*?;\n',lambda _: 'const ATH='+j(ath)+';\n',s,count=1)
if 'const ANALYSIS=' in s:s=re.sub(r'const ANALYSIS=.*?;\n',lambda _:'const ANALYSIS='+j(stats)+';\n',s,count=1)
else:s=s.replace('const CORE_NAMES=','const ANALYSIS='+j(stats)+';\nconst CORE_NAMES=',1)
s=re.sub(r'(?<=class="analysis-link" href="MPS_멘탈_통합_유형별_분석.html">).*?(?=</a>)',f'{len(ath)}건 · 유형별 분석',s)
REPORT.write_text(s)
(ROOT/'멘탈_통합분석.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2))
with (ROOT/'멘탈_유형별_평균.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['유형','유형명','기록 수','비율 (%)','MGI',*core,*axes])
 for key,p in [('전체',stats['overall']),*stats['types'].items()]:
  w.writerow([key,types[key]['name'] if key in types else '분석 대상 전체',p['n'],round(p['n']/len(ath)*100,2),*[round(x,3) if x is not None else '' for x in [p['mgi'],*p['core'].values(),*p['axes'].values()]]])
with (ROOT/'멘탈_분석대상_검수.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['구분','선수(실명)','원본 파일','엑셀 행','측정일','유형','비고'])
 for a in ath:w.writerow(['포함',a['n'],a['source']['file'],a['source']['row'],a['date'],a['type'],''])
 for a in audit:w.writerow(['제외',a['name'],a['file'],a['row'],'','',a['reason']])
E=html.escape
tr=[];cards=[]
for key,p in stats['types'].items():
 tr.append('<tr><th>'+key+' · '+E(types[key]['name'])+'</th>'+''.join('<td>'+x+'</td>' for x in [str(p['n']),f"{p['n']/len(ath)*100:.1f}%",*[f'{x:.2f}' if x is not None else '—' for x in [p['mgi'],*p['core'].values()]]])+'</tr>')
 if not p['n']:cards.append(f'<article><h2>{key} · {E(types[key]["name"])}</h2><p>해당 유형의 데이터가 없습니다.</p></article>');continue
 high=max(core,key=lambda n:p['core'][n]);low=min(core,key=lambda n:p['core'][n]);delta={n:p['core'][n]-stats['overall']['core'][n] for n in core};diff=max(core,key=lambda n:abs(delta[n]))
 cards.append(f'''<article><h2>{key} · {E(types[key]['name'])} <small>{p['n']}건 · {p['n']/len(ath)*100:.1f}%</small></h2><p>유형 내 가장 높은 지표: <b>{high} {p['core'][high]:.2f}</b><br>유형 내 가장 낮은 지표: <b>{low} {p['core'][low]:.2f}</b></p><p>전체 평균과 가장 큰 차이: {diff} <b>{delta[diff]:+.2f}점</b><br>3축 평균: P {p['axes']['P']:.2f} · R {p['axes']['R']:.2f} · I {p['axes']['I']:.2f}</p><p class="note">{'표본 10건 미만으로 개인별 차이의 영향이 큽니다. ' if p['n']<10 else ''}같은 지표로 유형을 나눈 뒤 비교한 기술통계입니다. 유형의 우열·원인·일반적인 선수 특성을 뜻하지 않습니다.</p></article>''')
o=stats['overall']; overall='<tr class="overall"><th>전체 평균</th>'+''.join('<td>'+x+'</td>' for x in [str(o['n']),'100.0%',*[f'{x:.2f}' for x in [o['mgi'],*o['core'].values()]]])+'</tr>'
summary=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MPS 멘탈 · 통합 유형 분석</title><style>body{{margin:0;background:#F2EEE8;color:#17395C;font-family:"Apple SD Gothic Neo",sans-serif;line-height:1.7}}main{{max-width:1120px;margin:32px auto;padding:32px;background:#FFFCF7;border-radius:20px}}h1{{font-size:30px;margin:4px 0}}h2{{font-size:18px}}small,.note{{font-size:13px;color:#6C7883}}.eyebrow,a{{color:#D64B20}}.scroll{{overflow:auto}}table{{width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap}}th,td{{padding:12px 9px;border-bottom:1px solid #E6DDD2;text-align:right}}th:first-child{{text-align:left}}.overall{{background:#FFF0DC;font-weight:bold}}.cards{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px}}article{{padding:18px;background:white;border:1px solid #E6DDD2;border-radius:16px}}button{{padding:8px 16px;cursor:pointer}}@media(max-width:700px){{main{{margin:8px;padding:18px}}.cards{{grid-template-columns:1fr}}}}@media print{{main{{margin:0;padding:0}}nav{{display:none}}article{{break-inside:avoid}}}}</style><main><div class="eyebrow">SportsMPS · Mental Position Analysis</div><h1>데이터가 있는 선수들의 멘탈 지도</h1><p>기존 {legacy_count}건 + 추가 {len(ath)-legacy_count}건 → <b>{len(ath)}건</b> · MGI 평균 <b>{o['mgi']:.2f}</b> · {stats['period'][0]}~{stats['period'][1]}</p><nav><a href="{REPORT.name}">개인별 3페이지 리포트</a> · <a href="멘탈_유형별_평균.csv">유형별 평균 CSV</a> · <a href="멘탈_분석대상_검수.csv">분석대상 검수 CSV</a> · <button onclick="window.print()">인쇄 / PDF</button></nav><p class="note">샘플·멘탈 결측/범위 오류·식별정보 누락은 제외합니다. 이번 제외: {E(' · '.join(k+' '+str(v)+'건' for k,v in stats['exclusions'].items()))}. 기존 원본 {legacy_count}건을 보존하여 추가 파일의 유효 {len(ath)-legacy_count}건과 함께 계산합니다. 기존 기록은 보존하고 추가 파일은 동일 측정 여부를 대조하여 누락 기록만 반영했습니다. 기존 자료는 생년월일이 없어 동일인 여부를 확정할 수 없어 기록 단위로 유지하며, 이름만 같은 기록은 합치지 않습니다. 합계는 고유 선수 수가 아닙니다. 전체 및 유형별 평균은 기록별 동일 가중치입니다. 결측을 0으로 채우지 않으며, 기존 자료에 없는 주위 적응 및 활용 능력은 해당 값이 있는 추가 기록에서만 평균을 냅니다. 연령·성별·소속 보정 없는 이번 표본의 평균입니다.</p><div class="scroll"><table><thead><tr><th>유형</th><th>기록 수</th><th>비율</th><th>MGI</th>{''.join('<th>'+x+'</th>' for x in core)}</tr></thead><tbody>{overall}{''.join(tr)}</tbody></table></div><div class="cards">{''.join(cards)}</div><p class="note">기존 리포트 기준 유지: P = 경기긴장도·경기 안정성·경기 중 감정 조절·실패 후 회복력 평균 / R = 경기 준비 능력·자기주도 학습능력·이미지트레이닝 활용능력 평균 / I = 실수 후 회복력·외부평가 독립성 평균. 반올림 전 4.5 이상 H, 미만 L. MGI는 원본 값을 평균했습니다. 분포와 평균은 같은 {len(ath)}건을 기준으로 합니다.</p></main></html>'''
(ROOT/'MPS_멘탈_통합_유형별_분석.html').write_text(summary)
print(json.dumps({'input':counts['input'],'included':len(ath),'excluded':stats['exclusions'],'mean':o,'types':{k:p['n'] for k,p in stats['types'].items()}},ensure_ascii=False,indent=2))
