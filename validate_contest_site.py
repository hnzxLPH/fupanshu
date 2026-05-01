from pathlib import Path
import re, subprocess, sys, json

html_path = Path('/home/ubuntu/study-review-contest/study-review-standalone.contest.html')
html = html_path.read_text(encoding='utf-8')
required_markers = [
    '学习复盘小站 · 省赛版',
    'handleFileUpload',
    'parseExcelFile',
    'renderDashboard',
    'exportRecord',
    'generateRecommendations',
    'weakRank',
    'study_review_data_v2',
    'study_review_hero_scroll',
    'rice_paper_data_texture',
    'knowledge_gap_analysis_card',
]
missing = [m for m in required_markers if m not in html]
script_match = re.search(r'<script>\n([\s\S]*?)\n</script>\n</body>', html)
if not script_match:
    raise SystemExit('未找到内联脚本')
js_path = Path('/tmp/study_review_inline.js')
js_path.write_text(script_match.group(1), encoding='utf-8')
node = subprocess.run(['node', '--check', str(js_path)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
result = {
    'html_bytes': len(html.encode('utf-8')),
    'missing_markers': missing,
    'node_check_exit_code': node.returncode,
    'node_check_output': node.stdout.strip(),
    'has_generated_assets': all('cloudfront.net' in html for _ in [0]),
    'has_pdf_export': 'html2canvas' in html and 'jsPDF' in html,
    'has_json_backup': 'exportAllData' in html and 'importAllData' in html,
    'has_chart_reuse_guard': 'destroyCharts' in html and 'charts[k].destroy' in html,
}
Path('/home/ubuntu/upload/contest_site_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
if missing or node.returncode != 0:
    raise SystemExit(1)
