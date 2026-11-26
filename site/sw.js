const CACHE='flightlookup-shell-v1';
const ROOT=new URL('./',self.location.href).href;
const FILES=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('flightlookup-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{const u=new URL(e.request.url);if(e.request.method!=='GET'||!u.href.startsWith(ROOT)||u.pathname.endsWith('/db.json'))return;
if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).catch(()=>caches.match(new URL('index.html',ROOT).href)));return;}
if(FILES.some(f=>new URL(f,ROOT).href===u.href))e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});
