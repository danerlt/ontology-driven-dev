"""一次性下载 Google Fonts 子集；产物内嵌到 HTML，演示时无需联网。"""
import html
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from content import SLIDES

ROOT = Path(__file__).resolve().parent


def download_font(family, filename, characters):
    url = 'https://fonts.googleapis.com/css2?' + urlencode({'family': family + ':wght@400..800', 'text': characters, 'display': 'swap'})
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'})
    with urlopen(request, timeout=45) as response:
        css = response.read().decode('utf-8')
    urls = list(dict.fromkeys(re.findall(r'url\((https://[^)]+)\)', css)))
    if len(urls) != 1:
        raise RuntimeError(f'字体服务未正确生成字符子集：{family}；请缩小单次字符范围。')
    with urlopen(urls[0], timeout=45) as response:
        data = response.read()
    if not data.startswith(b'wOF2'):
        raise RuntimeError(f'字体格式不符合预期：{family}')
    out = ROOT / 'fonts' / filename
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(data)
    print(f'已准备内嵌字体：{family}，{len(data) // 1024} KB。')
    return {'family': family, 'filename': filename, 'unicode_range': ','.join(f'U+{ord(c):04X}' for c in characters)}


def main():
    files = [ROOT/'content.py', ROOT/'harness_content.py', *sorted((ROOT/'src').glob('*'))]
    raw = ''.join(file.read_text(encoding='utf-8') for file in files)
    raw += ''.join(slide['title'] + slide['lead'] + slide['body'] + slide['notes'] for slide in SLIDES)
    characters = ''.join(c for c in sorted(set(html.unescape(raw))) if c.isprintable() or c == '\u3000')
    subsets = []
    for index in range(0, len(characters), 350):
        subsets.append(download_font('Noto Sans SC', f'noto-sans-sc-{index // 350 + 1}.woff2', characters[index:index+350]))
    subsets.append(download_font('Manrope', 'manrope.woff2', ''.join(chr(i) for i in range(32,127))))
    import json
    (ROOT/'fonts/manifest.json').write_text(json.dumps(subsets,ensure_ascii=False,indent=2),encoding='utf-8')
    license_file = ROOT/'fonts/LICENSES.txt'
    if license_file.is_file():
        print('沿用已保存的同名字体原始许可。')
    else:
        licenses = []
        for folder in ['notosanssc','manrope']:
            url = f'https://raw.githubusercontent.com/google/fonts/main/ofl/{folder}/OFL.txt'
            with urlopen(url, timeout=30) as response:
                licenses.append(folder + '\n' + response.read().decode('utf-8'))
        license_file.write_text('\n\n'.join(licenses),encoding='utf-8')
        print('已保存字体原始许可。')


if __name__ == '__main__':
    main()
