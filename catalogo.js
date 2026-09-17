let PRODUCTS=[];
const CATEGORIES=[
 {name:'Balanzas',icon:'⚖',desc:'Microbalanzas, balanzas analíticas y de precisión.',enabled:true},
 {name:'Analizadores de humedad',icon:'◫',desc:'HX204, HS153, HC103, HE73 y HE53.',enabled:true},
 {name:'Titulación',icon:'⚗',desc:'Valoradores Excellence, potenciometría y Karl Fischer.',enabled:true},
 {name:'pH y electrodos',icon:'⌁',desc:'NineFocus, medición electroquímica y sensores InLab.',enabled:true},
 {name:'Densidad',icon:'◉',desc:'Densímetros Excellence y soluciones multiparámetro.',enabled:true},
 {name:'Refractometría',icon:'◇',desc:'Refractómetros Excellence para nD, Brix y más.',enabled:true},
 {name:'Análisis térmico',icon:'△',desc:'TGA, DSC y caracterización térmica.',enabled:true},
 {name:'Punto de fusión y goteo',icon:'♨',desc:'Sistemas MP y DP para punto de fusión, goteo, reblandecimiento y otros valores térmicos.',enabled:true},
 {name:'Accesorios y consumibles',icon:'＋',desc:'Buffers, estándares, soluciones, consumibles de humedad, accesorios y material de reposición.',enabled:true}
];
function qs(k){return new URLSearchParams(location.search).get(k)}
function esc(s){return String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]))}
function menu(){const b=document.getElementById('menuButton'),m=document.getElementById('menu');if(b&&m)b.onclick=()=>m.classList.toggle('open')}
function kind(p){if(p.category==='Balanzas')return 'Balanza';if(p.category==='Analizadores de humedad')return 'Analizador de humedad';if(p.category==='Análisis térmico')return 'Sistema';if(p.category==='Titulación')return 'Valorador';if(p.category==='pH y electrodos')return 'Medidor';if(p.category==='Densidad')return 'Densímetro';if(p.category==='Refractometría')return 'Refractómetro';if(p.category==='Punto de fusión y goteo')return 'Sistema de valores térmicos';if(p.category==='Accesorios y consumibles')return 'Consumible / accesorio';return 'Equipo'}
function iconClass(p){return p.category==='Analizadores de humedad'?'moisture':p.category==='Análisis térmico'?'thermal':'balance'}
function placeholder(p,detail=false){return `<div class="equipment-placeholder ${detail?'detail-placeholder':''}"><div class="generic-icon ${iconClass(p)}"><span></span></div><strong>${esc(p.model)}</strong><small>${detail?'Fotografía del producto en preparación':'Fotografía en preparación'}</small></div>`}
function productCard(p){return `<article class="product-card" data-sub="${esc(p.sub)}" data-search="${esc((p.model+' '+p.code+' '+p.sub).toLowerCase())}"><div class="product-image ${p.image?'':'placeholder'}">${p.image?`<img src="${p.image}" alt="${esc(p.model)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.closest('.product-image')?.classList.add('image-error');this.style.display='none'">`:placeholder(p)}</div><div class="product-body"><div class="product-brand">${esc(p.brand)}</div><h3>${esc(p.model)}</h3><p class="product-meta">${esc(p.sub)}${p.code?' · '+esc(p.code):''}</p><div class="product-spec">${esc(p.capacity)} · ${esc(p.readability)}</div><a class="product-link" href="producto.html?id=${encodeURIComponent(p.id)}">Ver ficha técnica →</a></div></article>`}
function renderBrands(){const el=document.getElementById('brands');if(!el)return;el.innerHTML=`<a class="brand-card" href="marca.html?marca=mettler-toledo"><div><div class="brand-wordmark">METTLER TOLEDO</div><h2>Mettler Toledo</h2><p>Equipos de laboratorio e instrumentación.</p></div><span>Ver categorías →</span></a><div class="brand-card"><div><div class="brand-wordmark">GIARDINO</div><h2>Giardino</h2><p>Catálogo en preparación.</p></div><span>Próximamente</span></div><div class="brand-card"><div><div class="brand-wordmark">HIXWER</div><h2>Hixwer</h2><p>Catálogo en preparación.</p></div><span>Próximamente</span></div>`}
function renderCategories(){const el=document.getElementById('categories');if(!el)return;el.innerHTML=CATEGORIES.map(c=>{const n=PRODUCTS.filter(p=>p.category===c.name).length;return c.enabled?`<a class="category-card" href="catalogo.html?marca=mettler-toledo&categoria=${encodeURIComponent(c.name)}"><div><div class="category-icon">${c.icon}</div><h3>${c.name}</h3><p>${c.desc}</p><small>${n} referencias</small></div><span>Explorar catálogo →</span></a>`:`<div class="category-card" style="opacity:.72"><div><div class="category-icon">${c.icon}</div><h3>${c.name}</h3><p>${c.desc}</p></div><span>En preparación</span></div>`}).join('')}

function ensureFamilyNavStyles(){
 if(document.getElementById('family-nav-v34'))return;
 const s=document.createElement('style');s.id='family-nav-v34';
 s.textContent=`
 .family-nav{margin:24px 0 18px}
 .family-nav-head{display:flex;justify-content:space-between;gap:16px;align-items:end;margin-bottom:12px}
 .family-nav-head h2{margin:0;font-size:1.18rem;color:#102a43}
 .family-nav-head p{margin:3px 0 0;color:#66788a;font-size:.9rem}
 .family-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:10px}
 .family-tile{appearance:none;text-align:left;border:1px solid #dbe5ee;background:#fff;border-radius:14px;padding:14px 15px;cursor:pointer;transition:.18s ease;box-shadow:0 2px 10px rgba(15,42,67,.04)}
 .family-tile:hover{transform:translateY(-2px);border-color:#8fb6d8;box-shadow:0 7px 18px rgba(15,42,67,.09)}
 .family-tile.active{border-color:#1677b8;background:#f2f8fc;box-shadow:0 0 0 2px rgba(22,119,184,.08)}
 .family-tile strong{display:block;color:#102a43;font-size:.94rem;line-height:1.25}
 .family-tile span{display:block;color:#63788b;font-size:.79rem;margin-top:5px}
 .family-toolbar-note{font-size:.78rem;color:#7a8c9d}
 #chips{margin-top:14px}
 @media(max-width:640px){.family-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.family-tile{padding:12px}.family-nav-head{align-items:start;flex-direction:column}}
 `;
 document.head.appendChild(s);
}
function familyIcon(cat,sub){
 const x=(cat+' '+sub).toLowerCase();
 if(x.includes('buffer')||x.includes('conductividad')||x.includes('electrodo'))return '◉';
 if(x.includes('impresión'))return '▤';
 if(x.includes('crisol')||x.includes('tga')||x.includes('dsc'))return '△';
 if(x.includes('carepac')||x.includes('pesa'))return '⚖';
 if(x.includes('ergoclip')||x.includes('pesaje'))return '◇';
 if(x.includes('karl')||x.includes('titul'))return '⌁';
 if(x.includes('micro')||x.includes('analítica')||x.includes('precision'))return '▣';
 return '＋';
}

function renderCatalog(){
 const el=document.getElementById('products');if(!el)return;
 const cat=qs('categoria')||'Balanzas';
 const data=PRODUCTS.filter(p=>p.category===cat);
 const count=document.getElementById('productCount');
 if(count)count.textContent=`${data.length} referencias`;
 const title=document.querySelector('.page-hero h1');if(title)title.textContent=cat;
 const crumb=document.querySelector('.page-hero .crumbs');
 if(crumb)crumb.innerHTML=`<a href="marcas.html">Marcas</a> › <a href="marca.html?marca=mettler-toledo">Mettler Toledo</a> › ${esc(cat)}`;
 const intro=document.querySelector('.page-hero p');
 const intros={
  'Balanzas':'Explore por familia y encuentre microbalanzas, balanzas analíticas y de precisión.',
  'Analizadores de humedad':'Equipos y soluciones para determinación rápida de humedad.',
  'Análisis térmico':'Instrumentación para caracterización térmica de materiales.',
  'Titulación':'Valoradores, Karl Fischer, automatización y accesorios para análisis volumétrico.',
  'pH y electrodos':'Medidores, kits y sensores InLab para electroquímica de laboratorio.',
  'Accesorios y consumibles':'Buffers, estándares, soluciones, impresión, consumibles de humedad y análisis térmico.'
 };
 if(intro)intro.textContent=intros[cat]||'Seleccione una familia o busque directamente por modelo o número de material.';

 el.innerHTML=data.map(productCard).join('')||'<div class="empty">Catálogo en preparación.</div>';

 const subCounts=new Map();
 data.forEach(p=>subCounts.set(p.sub,(subCounts.get(p.sub)||0)+1));
 const subs=[...subCounts.keys()].sort((a,b)=>a.localeCompare(b,'es'));
 ensureFamilyNavStyles();
 let nav=document.getElementById('familyNavigator');
 if(!nav){
   nav=document.createElement('section');nav.id='familyNavigator';nav.className='family-nav';
   const chipsAnchor=document.getElementById('chips');
   if(chipsAnchor)chipsAnchor.parentNode.insertBefore(nav,chipsAnchor);
 }
 nav.innerHTML=`<div class="family-nav-head"><div><h2>Explorar por familia</h2><p>Seleccione una familia para reducir el catálogo.</p></div><div class="family-toolbar-note">${subs.length} familias · ${data.length} referencias</div></div>
 <div class="family-grid">
 <button class="family-tile active" data-family="Todos"><strong>Todos los productos</strong><span>${data.length} referencias</span></button>
 ${subs.map(s=>`<button class="family-tile" data-family="${esc(s)}"><strong>${familyIcon(cat,s)} ${esc(s)}</strong><span>${subCounts.get(s)} referencias</span></button>`).join('')}
 </div>`;
 const chips=document.getElementById('chips');
 if(chips){
   chips.innerHTML=`<button class="chip active" data-filter="Todos">Todos <b>${data.length}</b></button>`+
    subs.map(s=>`<button class="chip" data-filter="${esc(s)}">${esc(s)} <b>${subCounts.get(s)}</b></button>`).join('');
 }
 const search=document.getElementById('search');
 if(search)search.placeholder='Buscar por modelo, código o familia…';

 function apply(){
   const active=document.querySelector('.chip.active')?.dataset.filter||'Todos';
   const term=(search?.value||'').trim().toLowerCase();
   let visible=0;
   document.querySelectorAll('.product-card').forEach(card=>{
     const show=(active==='Todos'||card.dataset.sub===active)&&card.dataset.search.includes(term);
     card.style.display=show?'':'none'; if(show)visible++;
   });
   if(count)count.textContent=active==='Todos'&&!term?`${data.length} referencias`:`${visible} de ${data.length} referencias`;
   const u=new URL(location.href);
   if(active==='Todos')u.searchParams.delete('familia');else u.searchParams.set('familia',active);
   history.replaceState(null,'',u);
 }
 function selectFamily(name){
   document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('active',x.dataset.filter===name));
   document.querySelectorAll('.family-tile').forEach(x=>x.classList.toggle('active',x.dataset.family===name));
   apply();
 }
 document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>selectFamily(c.dataset.filter));
 document.querySelectorAll('.family-tile').forEach(c=>c.onclick=()=>selectFamily(c.dataset.family));
 if(search)search.oninput=apply;

 const requested=qs('familia');
 if(requested){
   const target=[...document.querySelectorAll('.chip')].find(c=>c.dataset.filter===requested);
   if(target){
     document.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));target.classList.add('active');
     document.querySelectorAll('.family-tile').forEach(x=>x.classList.toggle('active',x.dataset.family===requested));
     apply();
   }
 }
}
function renderProduct(){const el=document.getElementById('productDetail');if(!el)return;const p=PRODUCTS.find(x=>x.id===qs('id'));if(!p){el.innerHTML='<div class="empty">Producto no encontrado.</div>';return}document.title=`${p.model} | Exacta Perú`;const rows=Object.entries(p.specs).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('');const msg=encodeURIComponent(`Buenos días. Deseo información y cotización de ${p.brand} ${p.model}${p.code?' ('+p.code+')':''}.`);el.innerHTML=`<div class="crumbs"><a href="marcas.html">Marcas</a> › <a href="marca.html?marca=mettler-toledo">Mettler Toledo</a> › <a href="catalogo.html?marca=mettler-toledo&categoria=${encodeURIComponent(p.category)}">${esc(p.category)}</a> › ${esc(p.model)}</div><section class="detail"><div class="detail-media ${p.image?'':'placeholder'}">${p.image?`<img src="${p.image}" alt="${esc(p.model)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.closest('.product-image')?.classList.add('image-error');this.style.display='none'">`:placeholder(p,true)}</div><div><div class="product-brand">${esc(p.brand)}</div><h1>${kind(p)} ${esc(p.model)} Mettler Toledo</h1><p class="code">${p.code?'Código: '+esc(p.code)+' · ':''}Categoría: ${esc(p.category)}</p><span class="badge">Marca disponible · suministro sujeto a confirmación</span><p class="description">${esc(p.description)}</p><div class="actions"><a class="btn btn-primary" href="mailto:contacto@exactaperu.com?subject=${encodeURIComponent('Cotización '+p.model)}">Solicitar cotización</a><a class="btn btn-whatsapp" target="_blank" href="https://wa.me/51932610623?text=${msg}">WhatsApp</a><a class="btn btn-outline" target="_blank" rel="noopener" href="${p.source}">Ver referencia del fabricante</a></div><div class="spec-wrap"><h2>Especificaciones técnicas</h2><table class="spec-table">${rows}</table></div>${p.highlights?.length?`<section class="info-block"><h2>Características principales</h2><ul class="feature-list">${p.highlights.map(v=>`<li>${esc(v)}</li>`).join('')}</ul></section>`:''}${p.applications?.length?`<section class="info-block"><h2>Aplicaciones</h2><div class="application-tags">${p.applications.map(v=>`<span>${esc(v)}</span>`).join('')}</div></section>`:''}<div class="technical-note"><strong>Nota técnica</strong><p>Las prestaciones corresponden a información de referencia para el modelo indicado. La configuración, versión metrológica, accesorios, software y disponibilidad deben confirmarse antes de emitir una oferta.</p></div><p class="source-note"><a target="_blank" rel="noopener" href="${p.source}">Consultar fuente técnica del fabricante →</a></p></div></section>`}
async function init(){menu();try{const r=await fetch('productos.json?v=34');if(!r.ok)throw new Error();PRODUCTS=await r.json()}catch(e){console.error('No se pudo cargar productos.json')}renderBrands();renderCategories();renderCatalog();renderProduct()}
document.addEventListener('DOMContentLoaded',init);
