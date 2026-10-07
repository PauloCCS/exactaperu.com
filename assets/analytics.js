/* Shared GA4 measurement for every catalog page. */
(function () {
  'use strict';
  if (window.exactaAnalyticsLoaded) return;
  window.exactaAnalyticsLoaded = true;
  const measurementId = 'G-7MJ5DEYK1K';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId);
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
  document.head.appendChild(tag);

  let product;
  for (const node of document.querySelectorAll('script[type="application/ld+json"]')) {
    try {
      const data = JSON.parse(node.textContent);
      const entries = Array.isArray(data) ? data : data['@graph'] || [data];
      product = entries.find(item => item['@type'] === 'Product');
      if (product) break;
    } catch (_) { /* Ignore unrelated malformed metadata. */ }
  }
  const item = product ? {
    item_id: String(product.sku || location.pathname.split('/').pop().replace(/\.html$/, '')),
    item_name: product.name,
    item_brand: product.brand && product.brand.name,
    item_category: product.category
  } : null;
  if (item) window.gtag('event', 'view_item', {items: [item]});

  document.addEventListener('click', function (event) {
    const link = event.target.closest && event.target.closest('a');
    if (!link) return;
    let destination;
    try { destination = new URL(link.href, location.href); } catch (_) { return; }
    const host = destination.hostname.toLowerCase();
    if (host !== 'wa.me' && host !== 'whatsapp.com' && !host.endsWith('.whatsapp.com')) return;
    const label = (link.textContent || '').trim();
    const intent = label || destination.searchParams.get('text') || '';
    let name = 'whatsapp_click';
    if (/servicio|mantenimiento|calibraci[oó]n/i.test(intent)) name = 'servicio_click';
    else if (/cotiz/i.test(intent)) name = 'cotizacion_click';
    const params = {
      send_to: measurementId,
      link_text: label,
      link_url: destination.origin + destination.pathname,
      page_location: location.href,
      transport_type: 'beacon'
    };
    if (item) {
      params.item_id = item.item_id;
      params.item_name = item.item_name;
      params.item_brand = item.item_brand;
    }
    window.gtag('event', name, params);
  });
}());
