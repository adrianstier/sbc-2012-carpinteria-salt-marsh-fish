"""Fail on divergent dashboard snapshots or stale source/report revisions."""
import hashlib
import json
import re
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / 'data/metadata/current_sources.json').read_text())
data = json.loads((root / 'outputs/dashboard_data.json').read_text())
assert data == json.loads((root / 'outputs/api/dashboard_data.json').read_text())
assert data == json.loads((root / 'analysis_results.json').read_text())
bundle = (root / 'outputs/site-data.js').read_text()
assert json.loads(bundle.removeprefix('window.CARP_DATA = ').rstrip(';\n')) == data
assert 'const DATA = window.CARP_DATA;' in (root / 'analysis.html').read_text()
assert data['summary']['year_range'] == {'start': 2012, 'end': 2025}
assert data['summary']['total_samples'] == 168
assert data['summary']['total_species'] == 43
assert len(data['charts']['annual_trends']) == 14
assert len(data['charts']['location_summaries']) == 168
assert all(isinstance(row['density'], (int, float)) and isinstance(row['richness'], (int, float)) for row in data['charts']['location_summaries'])
assert all('density' in row and 'richness' in row for row in data['charts']['annual_trends'])
with Path(manifest['sources']['performance']['path']).open() as source:
    observed = {(int(r['year']), r['tc_mc_code']): r for r in csv.DictReader(source) if r['wetland_code'] == 'CSM'}
for row in data['charts']['location_summaries']:
    raw = observed[(row['year'], row['site'])]
    assert abs(row['density'] - float(raw['count_per_m2'])) < 0.001
    assert row['richness'] == int(raw['species_count'])
    assert row['habitat'] == ('Tidal Creek' if raw['habitat_code'] == 'TC' else 'Main Channel')
assert data['advanced']['nursery']['status'] == 'withheld'
for source in manifest['sources'].values():
    assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest() == source['sha256']
guide = (root / 'carpinteria_salt_marsh_fishes.html').read_text()
assert 'edi.647.9' in guide and 'edi.648.9' in guide and '2012–2025' in guide
assert '2012-2024' not in guide and '2012–2024' not in guide
assert 'wetland_ts_fish_seine-2025-08-27' not in guide
for name in ('index.html', 'analysis.html', 'dashboard.html', 'observatory.html', 'portal.html'):
    text = (root / name).read_text()
    assert 'edi.647.9' in text
    assert text.count('<script src="outputs/site-data.js"></script>') == 1
    assert hashlib.sha256((root / 'outputs/dashboard_data.json').read_bytes()).hexdigest() in text
    assert '2012-2024' not in text and '2012–2024' not in text
    assert 'diversity_indices' not in text
    assert 'year_range[' not in text
for name in ('dashboard.html', 'observatory.html'):
    text = (root / name).read_text()
    assert 'Math.random' not in text, f'Simulated scientific data in {name}'
    assert 'found.value' not in text
    assert 'count: 65' not in text
print('PASS: source hashes, all JSON downloads and shared JS agree; all five sites stamped with the same data hash; 14 years, 168 actual location summaries, 43 positive-catch taxa; no simulated scatter data or placeholder guild percentages.')
