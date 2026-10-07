"""Synchronize code-based SEO and sitemap with existing static product pages.

Run from any directory: python scripts/update_product_seo.py
Uses published Product.sku; never infers manufacturer codes from filenames.
Preserves technical content, links, images and existing URLs.
"""
from pathlib import Path
import html
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://exactaperu.com/'
NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', NS)
SCHEMA = re.compile(r'(<script\b[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>)(.*?)(</script>)', re.S)


def synchronize():
    changed = 0
    urls = set()
    for path in sorted((ROOT / 'productos').glob('*.html')):
        original = text = path.read_text()
        if re.search(r'<meta\b[^>]*name=[\"\']robots[\"\'][^>]*content=[\"\'][^\"\']*noindex', text, re.I):
            continue
        canonical = re.search(r'<link\b[^>]*rel=[\"\']canonical[\"\'][^>]*href=[\"\']([^\"\']+)', text)
        url = BASE + path.relative_to(ROOT).as_posix()
        if not canonical or html.unescape(canonical[1]) != url:
            continue
        urls.add(url)
        product = None
        for match in SCHEMA.finditer(text):
            data = json.loads(match[2])
            if isinstance(data, dict) and data.get('@type') == 'Product':
                product = data
                break
        if not product:
            continue
        code = str(product.get('sku', '')).strip()
        if code:
            for tag in ('title', 'h1'):
                pattern = rf'(<{tag}\b[^>]*>)(.*?)(</{tag}>)'
                def add_code(m):
                    plain = html.unescape(re.sub('<[^>]+>', '', m[2]))
                    if code.casefold() in plain.casefold():
                        return m[0]
                    label = m[2]
                    suffix = ' | Exacta Perú'
                    if tag == 'title' and suffix in label:
                        label = label.replace(suffix, '') + ' · ' + html.escape(code) + suffix
                    else:
                        label += ' · ' + html.escape(code)
                    return m[1] + label + m[3]
                text = re.sub(pattern, add_code, text, count=1, flags=re.S)
            title = html.unescape(re.search(r'<title>(.*?)</title>', text, re.S)[1])
            text = re.sub(r'(<meta\b[^>]*property=[\"\']og:title[\"\'][^>]*content=)([\"\'])(.*?)(\2)',
                          lambda m: m[1] + m[2] + html.escape(title, quote=True) + m[4], text)
        if text != original:
            path.write_text(text)
            changed += 1

    sitemap_path = ROOT / 'sitemap.xml'
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    existing = {node.text for node in root.iter(f'{{{NS}}}loc')}
    missing = sorted(urls - existing)
    if missing:
        additions = ''.join(f'  <url><loc>{html.escape(url)}</loc></url>\n' for url in missing)
        sitemap_path.write_text(sitemap_path.read_text().replace('</urlset>', additions + '</urlset>'))
    print(f'Updated product pages: {changed}; sitemap URLs added: {len(missing)}')


if __name__ == '__main__':
    synchronize()
