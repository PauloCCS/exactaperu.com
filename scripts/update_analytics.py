"""Install shared analytics in all HTML pages; run after adding catalog pages."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TAG = '<script defer src="/assets/analytics.js"></script>'
SCRIPT = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)
LEGACY_QUOTE = re.compile(r"document\.querySelectorAll\('\.btn-whatsapp'\)\.forEach\(a=>a\.addEventListener\('click',\(\)=>\{if\(typeof gtag==='function'\)gtag\('event','whatsapp_quote',\{product:'[^']+',brand:'OHAUS'\}\);\}\)\);")


def synchronize():
    count = 0
    for path in sorted(ROOT.rglob('*.html')):
        original = path.read_text()
        def replace(match):
            attributes, body = match.groups()
            if 'src="/assets/analytics.js"' in attributes:
                return ''
            if 'googletagmanager.com/gtag/js?id=G-7MJ5DEYK1K' in attributes:
                return ''
            if "gtag('config'" in body and 'G-7MJ5DEYK1K' in body:
                return ''
            if "gtag('event'" in body and 'whatsapp_click' in body and 'cotizacion_click' in body:
                return ''
            body = LEGACY_QUOTE.sub('', body)
            if not body.strip() and not attributes.strip():
                return ''
            if body != match[2]:
                return '<script' + attributes + '>' + body + '</script>'
            return match[0]
        text = SCRIPT.sub(replace, original)
        text = text.replace('</head>', TAG + '</head>', 1)
        if text != original:
            path.write_text(text)
            count += 1
    print(f'Updated pages: {count}')


if __name__ == '__main__':
    synchronize()
