from pathlib import Path
import base64
import re
from PIL import Image

project = Path('/home/ubuntu/study-review-contest')
upload = Path('/home/ubuntu/upload')
source_logo = upload / 'pasted_file_DHbFPe_image.png'
if not source_logo.exists():
    source_logo = upload / 'fupan_mouse_logo_primary.png'

optimized_logo = upload / 'fupan_mouse_logo_optimized.png'
img = Image.open(source_logo).convert('RGBA')
# 适配网站与离线单文件：缩小到 720px，保留透明通道。
max_size = 720
scale = min(max_size / img.width, max_size / img.height, 1)
if scale < 1:
    img = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)

# 如果图片四角是纯黑且没有透明度，尝试把接近黑色的背景转为透明；如果本身已有透明通道，则保持原样。
alpha_values = img.getchannel('A')
has_transparency = alpha_values.getextrema()[0] < 255
if not has_transparency:
    pixels = img.load()
    w, h = img.size
    corners = [pixels[0,0], pixels[w-1,0], pixels[0,h-1], pixels[w-1,h-1]]
    dark_corners = sum(1 for r,g,b,a in corners if r < 8 and g < 8 and b < 8)
    if dark_corners >= 3:
        for y in range(h):
            for x in range(w):
                r,g,b,a = pixels[x,y]
                if r < 10 and g < 10 and b < 10:
                    pixels[x,y] = (r,g,b,0)

img.save(optimized_logo, optimize=True)
logo_b64 = base64.b64encode(optimized_logo.read_bytes()).decode('ascii')
logo_data_uri = f'data:image/png;base64,{logo_b64}'

html_paths = [
    project / 'study-review-standalone.contest.html',
    upload / 'study-review-standalone-contest.html',
]
for path in html_paths:
    html = path.read_text(encoding='utf-8')
    html = html.replace('<title>学习复盘小站 · 省赛版</title>', '<title>复盘鼠 · 学习复盘数据系统 · 省赛版</title>')
    html = html.replace("<div class=\"brand\"><div class=\"seal\">复</div><div><h1>学习复盘小站 · 省赛版</h1><p>从复盘本到学习数据决策系统</p></div></div>",
                        f"<div class=\"brand\"><img class=\"brand-logo\" src=\"{logo_data_uri}\" alt=\"复盘鼠 Logo\"><div><h1>复盘鼠 · 学习复盘数据系统</h1><p>从复盘本到学习数据决策系统</p></div></div>")
    html = html.replace('.brand{display:flex;align-items:center;gap:12px}.seal{width:44px;height:44px;border-radius:14px;background:var(--cinnabar);color:#fff;display:grid;place-items:center;font-family:\'Noto Serif SC\';font-weight:900;box-shadow:0 10px 22px rgba(185,58,47,.24);transform:rotate(-5deg)}',
                        '.brand{display:flex;align-items:center;gap:12px}.brand-logo{width:58px;height:58px;object-fit:contain;border-radius:18px;filter:drop-shadow(0 10px 20px rgba(38,33,27,.16));background:rgba(255,250,240,.62);padding:3px}.seal{width:44px;height:44px;border-radius:14px;background:var(--cinnabar);color:#fff;display:grid;place-items:center;font-family:\'Noto Serif SC\';font-weight:900;box-shadow:0 10px 22px rgba(185,58,47,.24);transform:rotate(-5deg)}')
    html = html.replace('.hero h2{font-family:', '.hero-brandline{display:inline-flex;align-items:center;gap:12px;margin-bottom:14px;padding:10px 14px;border-radius:22px;background:rgba(255,250,240,.78);border:1px solid rgba(234,220,200,.86);box-shadow:0 12px 28px rgba(54,38,20,.08)}.hero-brandline img{width:64px;height:64px;object-fit:contain}.hero-brandline b{display:block;font-family:\'Noto Serif SC\';font-size:22px;color:var(--ink);letter-spacing:.04em}.hero-brandline span{display:block;color:var(--muted);font-size:12px;margin-top:2px}.hero h2{font-family:')
    html = html.replace('<section id="home" class="page active"><div class="hero"><div><span class="eyebrow">海南省青少年科技创新大赛展示版</span>',
                        f'<section id="home" class="page active"><div class="hero"><div><div class="hero-brandline"><img src="{logo_data_uri}" alt="复盘鼠 Logo"><div><b>复盘鼠</b><span>你的学习复盘小助手</span></div></div><br><span class="eyebrow">海南省青少年科技创新大赛展示版</span>')
    html = html.replace('把每一次复盘，变成<span>可行动</span>的学习证据。', '让复盘长出<span>数据大脑</span>，把努力变成学习证据。')
    html = html.replace('上传高考复盘本 XLSX，系统会在本地浏览器中解析每日复盘、周汇总与知识卡片，生成学习时长、薄弱知识点、掌握度与个性化行动建议。所有数据默认保存在你的设备中，适合现场演示与长期自我管理。', '复盘鼠会读取高考复盘本 XLSX，在本地浏览器中解析每日复盘、周汇总与知识卡片，生成学习时长、薄弱知识点、掌握度与个性化行动建议。所有数据默认保存在你的设备中，适合现场演示与长期自我管理。')
    html = html.replace('<div class="icon">📘</div><strong>拖拽或点击上传复盘本</strong>', f'<div class="icon"><img src="{logo_data_uri}" alt="复盘鼠" style="width:86px;height:86px;object-fit:contain"></div><strong>把复盘本交给复盘鼠</strong>')
    html = html.replace('学习复盘数据报告', '复盘鼠学习数据报告')
    html = html.replace('学习复盘小站_全部备份.json', '复盘鼠_全部备份.json')
    path.write_text(html, encoding='utf-8')

# 静态项目入口沿用单文件 HTML。
client_index = project / 'client/index.html'
client_index.write_text((project / 'study-review-standalone.contest.html').read_text(encoding='utf-8'), encoding='utf-8')

print('source_logo=', source_logo)
print('optimized_logo=', optimized_logo)
print('optimized_size=', optimized_logo.stat().st_size)
print('updated_files=', ', '.join(str(p) for p in html_paths + [client_index]))
