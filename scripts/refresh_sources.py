"""Resolve verified, immutable SONGS inputs from the shared local catalogue.

No raw-data edits or credential persistence. --verify-remote checks EDI revisions
and EML using the private shared session. It never saves or logs the token.
"""
import argparse
import base64
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(os.environ.get('SONGS_CACHE', '/Users/adrianstier/Documents/ChatGPT/SBC-Data-Catalogue/songs-data-catalogue'))
PACKAGES = {'performance': ('edi.648.9', 1), 'enclosure': ('edi.647.9', 1), 'seine': ('edi.647.9', 2)}


def verify_remote():
    token_path = Path(os.environ.get('EDI_TOKEN_FILE', '/Users/adrianstier/.config/edi/session.jwt'))
    token = token_path.read_text().strip()
    payload = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    if claims.get('exp', 0) <= time.time():
        raise RuntimeError('Shared EDI session expired. Renew the session before remote verification.')

    class OfficialOnly(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            parsed = urllib.parse.urlparse(newurl)
            if parsed.scheme != 'https' or parsed.hostname not in {
                'pasta.lternet.edu', 'pasta.edirepository.org', 'auth.edirepository.org'
            }:
                raise RuntimeError('Refusing non-EDI redirect')
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(OfficialOnly())
    def get(url):
        with opener.open(urllib.request.Request(url, headers={'Cookie': 'edi-token=' + token}), timeout=30) as response:
            return response.read()

    checked = {}
    for package in sorted({p for p, _ in PACKAGES.values()}):
        scope, number, selected = package.split('.')
        url = f'https://pasta.lternet.edu/package/eml/{scope}/{number}'
        revisions = [int(v) for v in get(url).decode().split()]
        if max(revisions) != int(selected):
            raise RuntimeError(f'New revision for {scope}.{number}: {max(revisions)}. Inspect it before changing inputs.')
        metadata_url = f'https://pasta.lternet.edu/package/metadata/eml/{scope}/{number}/{selected}'
        remote = get(metadata_url)
        cached = (CACHE / 'data/raw/edi' / f'{package}.metadata.xml').read_bytes()
        if ET.tostring(ET.fromstring(remote)) != ET.tostring(ET.fromstring(cached)):
            raise RuntimeError(f'Cached EML differs from EDI for {package}; inspect before proceeding.')
        checked[package] = {'revision_url': url, 'available_revisions': revisions,
                            'latest_revision': max(revisions), 'metadata_url': metadata_url,
                            'remote_eml_sha256': hashlib.sha256(remote).hexdigest(),
                            'cached_eml_matches': True}
    return {'verified_at_utc': datetime.now(timezone.utc).isoformat(), 'packages': checked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-remote', action='store_true')
    args = parser.parse_args()
    remote = verify_remote() if args.verify_remote else None
    manifest = list(csv.DictReader((CACHE / 'data/metadata/songs_download_log.csv').open()))
    sources, profiles = {}, {}
    for role, (package, index) in PACKAGES.items():
        row, = [r for r in manifest if r['package_id'] == package and int(r['entity_index']) == index]
        path = CACHE / 'data/raw/entities' / package / Path(row['local_path']).name
        assert path.stat().st_size == int(row['size_bytes']), f'Cache size mismatch: {path}'
        metadata = CACHE / 'data/raw/edi' / f'{package}.metadata.xml'
        table = ET.parse(metadata).getroot().findall('.//dataset/dataTable')[index - 1]
        attributes = table.findall('./attributeList/attribute')
        names = [a.findtext('attributeName') for a in attributes]
        missing = {a.findtext('attributeName'): [m.findtext('code') for m in a.findall('missingValueCode')] for a in attributes}
        with path.open(newline='') as handle:
            reader = csv.DictReader(handle)
            assert reader.fieldnames == names, f'EML/header mismatch: {path}'
            records = [r for r in reader if r['wetland_code'] == 'CSM']
        assert records
        keys = ['year', 'tc_mc_code'] if role == 'performance' else (
            ['year', 'date', 'survey', 'tc_mc_code', 'enclosure_number', 'sampling_station_label', 'haul_no', 'species_id'] if role == 'enclosure'
            else ['year', 'date', 'survey', 'tc_mc_code', 'seine_section_code', 'seine_label', 'haul_no', 'species_id'])
        tuples = [tuple(r[k] for k in keys) for r in records]
        duplicates = len(tuples) - len(set(tuples))
        assert duplicates == 0, f'Duplicate physical keys ({role}): {duplicates}'
        blanks = {k: sum(r[k] in ('', *missing[k]) for r in records) for k in names}
        assert not any(blanks[k] for k in keys), f'Missing key: {role}'
        value = 'count_per_m2' if role == 'performance' else 'count'
        assert not blanks[value] and all(float(r[value]) >= 0 for r in records)
        assert set(r['habitat_code'] for r in records) == {'TC', 'BNMC'}
        if role != 'performance':
            assert all(r['date'][:4] == r['year'] for r in records)
        taxa = {}
        if role != 'performance':
            for r in records:
                taxa.setdefault(r['species_code'], set()).add((r['genus_name'], r['species_name']))
            assert all(len(v) == 1 for v in taxa.values()), 'Ambiguous taxon codes'
        sources[role] = {'package_id': package, 'path': str(path), 'url': row['data_url'],
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'metadata_path': str(metadata), 'metadata_sha256': hashlib.sha256(metadata.read_bytes()).hexdigest()}
        profiles[role] = {'csm_rows': len(records), 'years': sorted({int(r['year']) for r in records}),
                          'habitats': sorted({r['habitat_code'] for r in records}),
                          'missing_counts': blanks, 'missing_codes_from_eml': missing,
                          'physical_key': keys, 'duplicate_keys': duplicates,
                          'months': sorted({r['date'][5:7] for r in records}) if role != 'performance' else None,
                          'taxon_codes': {k: list(next(iter(v))) for k, v in taxa.items()}}
    a, b = profiles['enclosure']['taxon_codes'], profiles['seine']['taxon_codes']
    assert all(a[k] == b[k] for k in a.keys() & b.keys()), 'Shared method taxon codes disagree'
    output = ROOT / 'data/metadata'
    output.mkdir(parents=True, exist_ok=True)
    previous_path = output / 'current_sources.json'
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    if remote is None and previous.get('sources') == sources:
        remote = previous.get('authenticated_verification')
    previous_path.write_text(json.dumps({'checked_date': str(datetime.now(ZoneInfo('America/Los_Angeles')).date()),
        'revision_evidence': 'https://marinemitigation.msi.ucsb.edu/data',
        'authenticated_verification': remote,
        'verification_limit': 'See authenticated_verification for the time of the remote check; local rebuilds do not imply a fresh remote check.',
        'sources': sources, 'profiles': profiles}, indent=2) + '\n')
    print(json.dumps({k: {'package': sources[k]['package_id'], 'rows': v['csm_rows'], 'years': v['years'], 'months': v['months']} for k, v in profiles.items()}, indent=2))


if __name__ == '__main__':
    main()
