"""Build the growth-integrated report without changing the v3 assessment scores."""
from pathlib import Path
import calendar
import collections
import csv
import datetime as dt
import json
import re
import sys
from xlsx_reader import rows

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / 'Downloads'
old = (ROOT / 'MPS_멘탈포지션_A4_3페이지_리포트_v3.html').read_text()
ath = json.loads(re.search(r'const ATH=(.*?);\n', old)[1])
types = json.loads(re.search(r'const TYPES=(.*?);\n', old)[1])
photos = json.loads(re.search(r'const PLAYER_PHOTOS=(.*?);\n', old)[1])
for photo in photos.values():
    photo['src'] = 'assets/players/' + Path(photo['file']).name
    assert (ROOT / photo['src']).is_file(), f"Missing player photo: {photo['src']}"
index = collections.defaultdict(list)
file_headers = {}
for i in range(1, 5):
    file = SOURCE / f'mps-authoring-inputs ({i}).xlsx'
    sheet_rows = rows(file)
    file_headers[file.name] = sheet_rows[2][1]
    for row, r in sheet_rows[3:]:
        index[(r.get('A', '').strip(), r.get('B'), r.get('C'), r.get('D'))].append((r, file.name, row))

STAGES = {'Pre-PHV': '급성장 이전', 'Stage 1': '가속기', 'Stage 2': '급성장기', 'Stage 3': '감속기', 'Stage 4': '종료기'}
PHV = dict(zip(STAGES, ['PHV -2', 'PHV -1', 'PHV 0', 'PHV 1', 'PHV 2']))

def age_months(birth, measured):
    """Completed calendar months plus fraction until next monthly birthday."""
    b, d = dt.date.fromisoformat(birth), dt.date.fromisoformat(measured)
    months = (d.year - b.year) * 12 + d.month - b.month
    def anniversary(m):
        y, mo = divmod(b.year * 12 + b.month - 1 + m, 12)
        return dt.date(y, mo + 1, min(b.day, calendar.monthrange(y, mo + 1)[1]))
    if anniversary(months) > d:
        months -= 1
    start, end = anniversary(months), anniversary(months + 1)
    return months + (d - start).days / (end - start).days

audit = []
for a in ath:
    candidates = index[(a['n'], a['sex'], a['birth'], a['date'])]
    assert candidates, f"Missing source for record {a['id']}"
    assert len({tuple(r.get(k, '') for k in ['AN', 'AO', 'AR', 'Y', 'I', 'J']) for r, _, _ in candidates}) == 1, 'Conflicting source values'
    r, file, row = candidates[0]
    # Require matching mental measurements as well as the identity and date.
    assert abs(float(r['K']) - a['mgi']) < 1e-8
    headers = file_headers[file]
    for col in 'LMNOPQRSTUVWX':
        if headers[col] in a['raw']:
            assert abs(float(r[col]) - a['raw'][headers[col]]) < 1e-8
    ca = age_months(a['birth'], a['date'])
    by, bm = float(r['AN']), float(r['AO'])
    ba = by * 12 + bm
    issues = []
    # Technical anomaly screen, not a diagnostic definition of delayed maturation.
    valid = by.is_integer() and bm.is_integer() and 0 <= bm < 12 and 48 <= ba <= 240 and abs(ba-ca) <= 48
    if not valid:
        issues.append('골연령 원자료 재확인')
    stage_ok = r.get('AR') in STAGES and PHV[r['AR']] == r.get('Y')
    if not stage_ok:
        issues.append('성장단계·PHV 불일치')
    delta = ba - ca if valid else None
    a['growth'] = {
        'chronologicalMonths': ca, 'boneYearsRaw': r['AN'], 'boneMonthsRaw': r['AO'],
        'boneMonths': ba if valid else None, 'differenceMonths': delta,
        'delayed': valid and delta <= -6, 'stageRaw': r.get('AR', ''),
        'phvRaw': r.get('Y', ''), 'stage': STAGES.get(r.get('AR')) if stage_ok else None,
        'height': r.get('I', ''), 'weight': r.get('J', ''),
        'issues': issues, 'source': {'file': file, 'row': row},
    }
    audit.append({'기록ID': a['id'], '선수': a['n'], '측정일': a['date'], '원본파일': file, '엑셀행': row,
                  '실제나이_개월': round(ca, 4), '골연령_년_원본': r['AN'], '골연령_개월_원본': r['AO'],
                  '골연령차_개월': round(delta, 4) if delta is not None else '', '6개월이상지연': a['growth']['delayed'],
                  '성장단계_원본': r.get('AR'), 'PHV_원본': r.get('Y'), '리포트성장단계': a['growth']['stage'] or '확인 필요',
                  '검수사항': ' / '.join(issues)})

stats = {'records': len(ath), 'identityKeys': len({(a['n'], a['birth'], a['sex']) for a in ath}),
         'boneValid': sum(a['growth']['boneMonths'] is not None for a in ath),
         'delayed': sum(a['growth']['delayed'] for a in ath),
         'stageConflicts': sum(a['growth']['stage'] is None for a in ath),
         'stages': dict(collections.Counter(a['growth']['stage'] or '확인 필요' for a in ath))}
payload = json.dumps({'athletes': ath, 'types': types, 'photos': photos, 'stats': stats}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
template = (ROOT / 'scripts/growth_report_template.html').read_text()
for token, filename in [('__DETAIL_PAGE__', 'mental_detail_page.html'), ('__DETAIL_STYLE__', 'mental_detail.css'), ('__DETAIL_SCRIPT__', 'mental_detail_charts.js')]:
    template = template.replace(token, (ROOT / 'scripts' / filename).read_text())
report = template.replace('__REPORT_DATA__', payload)
(ROOT / 'MPS_멘탈포지션_성장통합_A4_4페이지_v4.html').write_text(report)
# Preserve existing links; both entry points contain the current four-page report.
(ROOT / 'MPS_멘탈포지션_성장통합_A4_3페이지_v4.html').write_text(report)
(ROOT / '멘탈_성장통합_검수요약.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2))
with (ROOT / '멘탈_성장통합_검수.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(audit[0]))
    w.writeheader()
    w.writerows(audit)
print(json.dumps(stats, ensure_ascii=False, indent=2))
