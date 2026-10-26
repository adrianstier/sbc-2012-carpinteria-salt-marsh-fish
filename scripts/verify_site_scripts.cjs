// Source-level JavaScript checks; these are not a browser/render test.
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'outputs/dashboard_data.json'), 'utf8'));
for (const name of ['index.html', 'dashboard.html', 'observatory.html', 'analysis.html', 'portal.html']) {
  const html = fs.readFileSync(path.join(root, name), 'utf8');
  for (const match of html.matchAll(/<script([^>]*)>([\s\S]*?)<\/script>/gi)) {
    if (!/\bsrc=|application\/ld\+json/i.test(match[1])) new vm.Script(match[2], {filename: name});
  }
}
const dashboard = fs.readFileSync(path.join(root, 'dashboard.html'), 'utf8');
const start = dashboard.indexOf('function transformAPIData(api)');
const end = dashboard.indexOf('// Load data from API', start);
const context = {api: data, SPECIES_NAMES: {}, d3: {schemeTableau10: Array(10).fill('#123456')}};
vm.createContext(context);
vm.runInContext(dashboard.slice(start, end) + '\nresult = transformAPIData(api);', context);
assert.equal(context.result.scatterData.length, 168);
assert(context.result.annualTrends.every(r => Number.isFinite(r.density) && Number.isFinite(r.richness)));
assert(context.result.heatmapData.every(r => r.values.every(Number.isFinite)));
assert(Math.abs(context.result.guilds.reduce((sum, g) => sum + g.count, 0) - 100) < 0.3);
console.log('PASS: JavaScript syntax in all five sites; dashboard transformation produces finite trends, heatmap, actual scatter records, and calculated guild proportions. No browser rendering claimed.');
