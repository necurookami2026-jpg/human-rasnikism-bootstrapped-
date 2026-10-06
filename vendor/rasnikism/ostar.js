(function(){
'use strict';
const editions={makkakah:['Makkakah','Sustain purpose, care, resources, and useful work. Record effects and the next review.'],aantonymmakkakah:['Aantonymmakkakah','Reconsider assumptions and framing. Preserve useful work while choosing repair, revision, or release.'],jurisdiction:['Jurisdiction review — UNREVIEWED','Identify applicable rules, evidence, permissions, and appropriate review. This selection does not certify legal validity.']};
const requested=new URLSearchParams(window.location.search).get('edition'),edition=Object.hasOwn(editions,requested)?requested:'makkakah';
for(const node of document.querySelectorAll('[data-ostar-name]'))node.textContent=editions[edition][0];for(const node of document.querySelectorAll('[data-ostar-guidance]'))node.textContent=editions[edition][1];
for(const link of document.querySelectorAll('a[href]')){const raw=link.getAttribute('href');if(!raw||raw.startsWith('#'))continue;const url=new URL(raw,window.location.href);if(url.origin!==window.location.origin||!url.pathname.endsWith('.html'))continue;const selected=link.getAttribute('data-ostar-edition');url.searchParams.set('edition',selected&&Object.hasOwn(editions,selected)?selected:edition);link.setAttribute('href',url.href);if(selected===edition)link.setAttribute('aria-current','page');}
})();
