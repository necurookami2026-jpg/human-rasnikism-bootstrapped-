'use strict';

// Smoke checks for the reviewed, pinned Ministry snapshot. This small fake DOM
// exercises local interactions; it is neither an HTML parser nor a browser test.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const vm = require('node:vm');

const root = `${__dirname}/../vendor/internetwomanagementministry`;
const html = fs.readFileSync(`${root}/site/index.html`, 'utf8');
assert.equal(html, fs.readFileSync(`${root}/docs/index.html`, 'utf8'),
  'The retained site and publication HTML must remain identical.');
assert.equal(fs.statSync(`${root}/docs/.nojekyll`).size, 0);

const ids = Array.from(html.matchAll(/\bid\s*=\s*["']([^"']+)["']/gi), match => match[1]);
assert.equal(ids.length, new Set(ids).size, 'HTML element IDs must be unique.');
for (const id of ['lore', 'mechanics', 'characters', 'glossary', 'weave', 'seed', 'search', 'terms', 'empty']) {
  assert(ids.includes(id), `Expected element #${id}.`);
}
const links = Array.from(html.matchAll(/<a\b[^>]*\bhref\s*=\s*["']([^"']*)["']/gi), match => match[1]);
for (const href of links) {
  assert(href.startsWith('#'), `Expected local navigation, received ${href}.`);
  if (href.length > 1) assert(ids.includes(href.slice(1)), `Unresolved anchor ${href}.`);
}
assert.deepEqual(links.filter(href => href.length > 1).sort(),
  ['#characters', '#glossary', '#lore', '#mechanics']);
assert(!/<[^>]+\b(?:src|action)\s*=/i.test(html), 'The snapshot must have no external assets or form actions.');
assert(!/https?:\/\//i.test(html), 'The original page must contain no remote URL destinations.');

const scripts = Array.from(html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi));
assert.equal(scripts.length, 1, 'Expected the single reviewed inline script.');
assert.equal(scripts[0][1].trim(), '', 'The retained script must be inline without attributes.');
const script = scripts[0][2];
assert(!/\b(?:eval|Function)\b/.test(script), 'The reviewed script must not evaluate generated code.');
assert(!/\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|sendBeacon|importScripts)\b/.test(script),
  'The reviewed script must not issue external requests.');
assert(!/\bimport\s*(?:\(|["'{*])/.test(script), 'The reviewed script must not import external modules.');
new vm.Script(script, {filename: 'ministry-inline.js'});

function textOf(markup) {
  // The pinned records use plain text and markup, with no encoded entities.
  return markup.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
}

function element(textContent = '', initialClasses = []) {
  const classes = new Set(initialClasses);
  const handlers = new Map();
  return {
    textContent,
    classes,
    addEventListener(type, handler) {
      assert(!handlers.has(type), `Unexpected duplicate ${type} listener.`);
      handlers.set(type, handler);
    },
    dispatch(type, event = {}) {
      assert(handlers.has(type), `Missing ${type} listener.`);
      handlers.get(type)(event);
    },
    classList: {
      toggle(name, force) {
        const added = force === undefined ? !classes.has(name) : Boolean(force);
        if (added) classes.add(name);
        else classes.delete(name);
        return added;
      }
    }
  };
}

const records = Array.from(html.matchAll(/<details\b[^>]*>([\s\S]*?)<\/details\s*>/gi), match => match[1]);
assert.equal(records.length, 7, 'Expected seven glossary records.');
const labels = records.map(record => {
  const summary = record.match(/<summary\b[^>]*>([\s\S]*?)<\/summary\s*>/i);
  assert(summary, 'Every glossary record needs a summary.');
  return textOf(summary[1]);
});
assert.deepEqual(labels, ['Primitive', 'Composite', 'Kerot', 'Hensensual', 'Penfinal', 'Exact Final', 'Final Quilt']);
const terms = records.map(record => element(textOf(record)));
const initialSeed = html.match(/<p\b[^>]*\bid=["']seed["'][^>]*>([\s\S]*?)<\/p>/i);
assert(initialSeed, 'Expected the initial story-seed message.');
const elements = {
  '#weave': element(),
  '#seed': element(textOf(initialSeed[1])),
  '#search': element(),
  '#empty': element('', ['hidden'])
};
const document = {
  querySelector(selector) {
    assert(Object.hasOwn(elements, selector), `Unexpected selector ${selector}.`);
    return elements[selector];
  },
  querySelectorAll(selector) {
    assert.equal(selector, '#terms details');
    return terms;
  }
};

// No network APIs, Node loader or process are exposed. VM code generation is
// disabled; this harness runs only the already reviewed source snapshot.
const context = vm.createContext({document}, {codeGeneration: {strings: false, wasm: false}});
new vm.Script(script, {filename: 'ministry-inline.js'}).runInContext(context, {timeout: 1000});

const initialMessage = elements['#seed'].textContent;
const seeds = [];
for (let i = 0; i < 8; i++) {
  elements['#weave'].dispatch('click');
  const seed = elements['#seed'].textContent;
  assert.equal(typeof seed, 'string');
  assert(seed.length > 0 && seed !== initialMessage, 'A click must display a prepared story seed.');
  seeds.push(seed);
}
assert.equal(new Set(seeds.slice(0, 4)).size, 4, 'The first cycle must contain four distinct story seeds.');
assert.deepEqual(seeds.slice(4), seeds.slice(0, 4), 'The four story seeds must repeat in order.');

function search(value) {
  elements['#search'].dispatch('input', {target: {value}});
  return labels.filter((label, index) => !terms[index].classes.has('hidden'));
}
assert.deepEqual(search('  KeRoT  '), ['Kerot'], 'Search must trim whitespace and ignore case.');
assert(elements['#empty'].classes.has('hidden'), 'Matching results must hide the empty-state message.');
assert.deepEqual(search('recorded boundary'), ['Exact Final'], 'Search must include the definition text.');
assert.deepEqual(search('unlikely-no-matching-term'), []);
assert(!elements['#empty'].classes.has('hidden'), 'No results must show the empty-state message.');
assert.deepEqual(search(''), labels, 'Clearing the query must restore all seven records.');
assert(elements['#empty'].classes.has('hidden'));
assert.deepEqual(search('   '), labels, 'A whitespace-only query must restore all seven records.');

console.log('Ministry smoke: PASS (mirrors, local anchors, seven terms, search/reset, four-seed cycle, reviewed inline script).');
