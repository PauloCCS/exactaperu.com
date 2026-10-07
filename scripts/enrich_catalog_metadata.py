"""Complete structured metadata from visible content and sitemap from canonicals."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
import html
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://exactaperu.com/'
SCHEMA = re.compile(r'(<script\b[^>]*type=[\"\']application/ld\+json[\"\'][^>]*>)(.*?)(</script>)', re.S)


class Attributes(HTMLParser):
    def handle_starttag(self, tag, attributes):
        self.attributes = dict(attributes)


def attrs(tag):
    parser = Attributes()
    parser.feed(tag)
    return parser.attributes


def plain(text):
    return ' '.join(html.unescape(re.sub('<[^>]+>', '', text)).split())


def encoded(data):
    return json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')


def synchronize():
    counts = {'product_schema': 0, 'descriptions': 0, 'breadcrumbs': 0, 'sitemap': 0}
    urls = set()
    for path in sorted(ROOT.rglob('*.html')):
        original = text = path.read_text()
        metas = [attrs(x) for x in re.findall(r'<meta\b[^>]*>', text)]
        if any(m.get('name', '').lower() == 'robots' and 'noindex' in m.get('content', '').lower() for m in metas):
            continue
        canonical = next((attrs(x).get('href') for x in re.findall(r'<link\b[^>]*>', text) if attrs(x).get('rel') == 'canonical'), None)
        if not canonical or not canonical.startswith(BASE):
            continue
        parsed = urlsplit(canonical)
        relative = parsed.path.lstrip('/')
        canonical_path = ROOT / relative
        if canonical_path.is_dir():
            canonical_path /= 'index.html'
        if parsed.query or parsed.fragment or canonical_path.resolve() != path.resolve():
            continue
        urls.add(canonical)
        if path.parent != ROOT / 'productos':
            continue
        description = next((m.get('content', '') for m in metas if m.get('name') == 'description'), '')
        schemas = [(m, json.loads(m[2])) for m in SCHEMA.finditer(text)]
        product = next(((m, d) for m, d in schemas if d.get('@type') == 'Product'), None)
        if product:
            match, data = product
            if not data.get('description') and description:
                data['description'] = description
                text = text[:match.start()] + match[1] + encoded(data) + match[3] + text[match.end():]
                counts['descriptions'] += 1
        else:
            heading = re.search(r'<h1\b[^>]*>(.*?)</h1>', text, re.S)
            image = next((attrs(x).get('src') for x in re.findall(r'<img\b[^>]*>', text) if 'logo-exacta' not in attrs(x).get('src', '')), None)
            brand = re.search(r'<div class="product-brand">(.*?)</div>', text, re.S)
            if not heading or not image or not brand:
                raise ValueError(f'Insufficient visible product content: {path}')
            data = {'@context': 'https://schema.org', '@type': 'Product', 'name': plain(heading[1]),
                    'description': description, 'image': urljoin(canonical, image), 'url': canonical,
                    'brand': {'@type': 'Brand', 'name': plain(brand[1])}}
            text = text.replace('</head>', '<script type="application/ld+json">' + encoded(data) + '</script></head>', 1)
            counts['product_schema'] += 1
        if not any(d.get('@type') == 'BreadcrumbList' for _, d in schemas):
            crumbs = re.search(r'<div class="crumbs">(.*?)</div>', text, re.S)
            if not crumbs:
                raise ValueError(f'No visible breadcrumb trail: {path}')
            entries = []
            for anchor in re.findall(r'<a\b[^>]*>.*?</a>', crumbs[1], re.S):
                link = attrs(anchor.split('>', 1)[0] + '>').get('href')
                if link:
                    entries.append({'@type': 'ListItem', 'position': len(entries) + 1,
                                    'name': plain(anchor), 'item': urljoin(canonical, link)})
            heading = plain(re.search(r'<h1\b[^>]*>(.*?)</h1>', text, re.S)[1])
            entries.append({'@type': 'ListItem', 'position': len(entries) + 1, 'name': heading, 'item': canonical})
            if len(entries) < 2:
                raise ValueError(f'Incomplete breadcrumb trail: {path}')
            trail = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': entries}
            text = text.replace('</head>', '<script type="application/ld+json">' + encoded(trail) + '</script></head>', 1)
            counts['breadcrumbs'] += 1
        if text != original:
            path.write_text(text)
    sitemap = ROOT / 'sitemap.xml'
    existing = {x.text for x in ET.parse(sitemap).iter() if x.tag.endswith('loc')}
    missing = sorted(urls - existing)
    if missing:
        additions = ''.join(f'  <url><loc>{html.escape(url)}</loc></url>\n' for url in missing)
        sitemap.write_text(sitemap.read_text().replace('</urlset>', additions + '</urlset>'))
    counts['sitemap'] = len(missing)
    print(counts)


if __name__ == '__main__':
    synchronize()
