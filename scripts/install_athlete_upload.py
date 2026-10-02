"""Keep the generated entry points and source template aligned for Excel uploads."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = '''<style id="athlete-upload-style">
.toolbar .athlete-upload{margin-left:auto;display:inline-flex;align-items:center;gap:7px;background:var(--ink);border-color:var(--ink);color:white;white-space:nowrap;font-weight:700;padding:10px 14px}
.athlete-upload svg{width:18px;height:18px}.athlete-upload:disabled{opacity:.6;cursor:wait}
.upload-feedback{margin:0;padding:9px 20px;background:#f6f8f2;border-bottom:1px solid var(--line);font-size:12px;line-height:1.6;color:var(--green)}
.upload-feedback p{font-size:12px}.upload-feedback .error{color:#954b30}.upload-feedback details{margin-top:5px}.upload-feedback summary{cursor:pointer}.upload-feedback ul{max-height:180px;overflow:auto;padding-left:22px}
.upload-help{font-size:10px;color:var(--sub)}
@media(max-width:820px){.toolbar .athlete-upload{margin-left:0}.upload-feedback{padding:8px 12px}}
@media print{.upload-feedback{display:none!important}}
</style>'''
BUTTON = '''<button id="athleteUploadBtn" class="athlete-upload" type="button" aria-describedby="uploadHelp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 16V3m-5 5 5-5 5 5M4 15v5a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-5"/></svg>선수 Excel 업로드</button><input id="athleteUploadInput" type="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" hidden>'''
FEEDBACK = '''<section class="upload-feedback" aria-label="선수 업로드 안내"><p id="uploadHelp" class="upload-help">MPS 입력값 Excel (.xlsx) · 이름·생년월일·성별이 같은 선수는 제외하고 새 선수만 추가합니다. 같은 차트번호·생년월일·성별도 중복으로 확인합니다. 파일 안의 중복 선수는 최신 유효 기록 1건만 추가합니다. 저장은 현재 브라우저에만 적용되며 다른 기기와 공유되지 않습니다.</p><p id="uploadStatus" role="status" aria-live="polite" hidden></p><details id="uploadErrors" hidden><summary>추가되지 않은 행 확인</summary><ul id="uploadErrorList"></ul></details></section>'''

for path in [ROOT/'index.html', ROOT/'MPS_멘탈포지션_성장통합_A4_3페이지_v4.html', ROOT/'scripts/growth_report_template.html']:
    content = path.read_text()
    if 'id="athleteUploadBtn"' in content:
        continue
    content = content.replace('</head>', STYLE+'\n</head>', 1)
    content = content.replace('<small id="filterCount"></small></nav>', '<small id="filterCount"></small>'+BUTTON+'</nav>\n'+FEEDBACK, 1)
    content = content.replace('</body>', '<script src="scripts/athlete_import.js"></script>\n<script src="scripts/athlete_upload_ui.js"></script>\n</body>', 1)
    path.write_text(content)
