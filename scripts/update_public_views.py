"""Synchronize built views with the current generated JSON (mechanical build)."""
import json
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'outputs/dashboard_data.json').read_text())
summary = data['summary']
start, end = summary['year_range']['start'], summary['year_range']['end']
years = summary['years_of_data']
serialized = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
# A plain script works with both file:// and HTTP; fetch() does not on file://.
(ROOT / 'outputs/site-data.js').write_text('window.CARP_DATA = ' + serialized + ';\n')
# Retain the existing download URL, but never its obsolete independent results.
(ROOT / 'analysis_results.json').write_text((ROOT / 'outputs/dashboard_data.json').read_text())
data_hash = hashlib.sha256((ROOT / 'outputs/dashboard_data.json').read_bytes()).hexdigest()
notice = ('<aside style="padding:1rem;margin:5rem 1rem 1rem;border:2px solid #789;">'
          f'Updated 26 October 2026 (authenticated EDI revision check): SONGS revisions edi.647.9 / edi.648.9, {start}–{end}. '
          'Taxon counts include unresolved identifications. Annual location summaries are repeated measurements, not independent visits. '
          'Gaussian model panels are exploratory and should not be used for inference; some fitted densities are negative. '
          'Sampling-month summaries do not establish seasonality. Nursery-function estimates have been withdrawn. '
          '<a href="carpinteria_salt_marsh_fishes.html">Read the updated guide and methods</a>.</aside>')

for filename in ('index.html', 'analysis.html', 'dashboard.html', 'observatory.html', 'portal.html'):
    path = ROOT / filename
    text = path.read_text()
    if '<script src="outputs/site-data.js"></script>' not in text:
        text = text.replace('</head>', '<script src="outputs/site-data.js"></script>\n</head>', 1)
    text = re.sub(r'<meta name="carp-data-sha256" content="[^"]*">\n?', '', text)
    text = text.replace('</head>', f'<meta name="carp-data-sha256" content="{data_hash}">\n</head>', 1)
    text = text.replace('src="/assets/', 'src="assets/').replace('photo: "/assets/', 'photo: "assets/')
    text = text.replace('2012-2024', f'{start}-{end}').replace('2012–2024', f'{start}–{end}').replace('2012 – 2024', f'{start} – {end}').replace('2012 - 2024', f'{start} - {end}')
    text = text.replace('13 years', f'{years} years').replace('13-Year', f'{years}-Year')
    text = text.replace('Thirteen years', 'Fourteen years')
    text = text.replace('13-year', '14-year')
    text = re.sub(r'(<div class="hero-stat-value" id="stat-years">)\d+', rf'\g<1>{years}', text)
    text = text.replace('>Fish Species</div>', '>Recorded Taxa</div>').replace('>Sampling Events</div>', '>Annual Location Summaries</div>')
    text = text.replace('edi.647.8', 'edi.647.9').replace('edi.648.8', 'edi.648.9')
    text = text.replace('Last updated January 2026', 'Last updated October 2026')
    text = re.sub(r'(<div class="hero-stat-value" id="stat-species">)\d+', rf'\g<1>{summary["total_species"]}', text)
    text = re.sub(r'(<div class="hero-stat-value" id="stat-samples">)\d+', rf'\g<1>{summary["total_samples"]}', text)
    # Build from the same feed rather than retaining the old embedded snapshot.
    if filename == 'analysis.html':
        text = re.sub(r'const DATA = \{[^\n]+;', 'const DATA = window.CARP_DATA;', text, count=1)
        text = text.replace('            renderNurseryChart();', '            // Nursery function withheld: size/age data are absent.')
        text = text.replace('            renderEventsTimeline();', '            // Event-overlap illustration withheld: not a causal analysis.')
        text = text.replace('            renderSpeciesImpacts();', '            // Post-hoc event-impact calculations withheld.')
        for section in ('nursery', 'events', 'impacts', 'environmental-events', 'seasonality-detail'):
            text = re.sub(rf'<section class="analysis-section" id="{section}"[^>]*>.*?</section>', '', text, flags=re.S)
        text = text.replace('Beta Diversity Matrix', 'Between-Year Dissimilarity')
        text = text.replace('Core species (>80% of years) form the stable community backbone. Satellite species (<40%) are occasional visitors.', 'Core taxa were detected in more than 80% of surveyed years; satellite taxa in fewer than 40%. These categories describe detection frequency, not residency.')
        text = text.replace('Species-Specific Seasonality', 'Catch by Sampling Month (Unequal Survey Timing)')
        text = text.replace('            renderSpeciesSeasonality();', '            // Monthly raw-count heatmap withheld: unequal annual sampling dates.')
        # Do not leave sidebar links to sections withheld from the display.
        for anchor in ('nursery', 'environmental-events', 'seasonality-detail'):
            text = re.sub(rf'<li><a href="#{anchor}">.*?</a></li>', '', text)
        for function in ('renderEventsTimeline', 'renderSpeciesImpacts', 'renderSpeciesSeasonality', 'renderNurseryChart'):
            text = re.sub(rf'        function {function}\(\).*?(?=        function |\n    </script>)', '', text, flags=re.S)
    if filename == 'dashboard.html':
        for color, value in [('ocean', years), ('coral', summary['total_species']), ('kelp', f"{summary['mean_density']:.1f}"), ('amber', summary['total_samples'])]:
            text = re.sub(rf'(<div class="summary-card {color}">.*?<div class="summary-value">).*?(</div>)', lambda m: m[1] + str(value) + m[2], text, count=1, flags=re.S)
        text = text.replace('Total Species', 'Recorded Taxa').replace('12 fish families', 'Includes unresolved identifications').replace('+12% from baseline', 'Mean across annual location estimates')
        text = text.replace('Statistical Model Insights', 'Descriptive Monitoring Summaries').replace('High diversity', 'Pooled seine diversity')
        text = text.replace('Ecological Guilds', 'Feeding Guilds (Assigned Taxa Only)')
        text = text.replace('Run <code>python -m src.export.dashboard_api</code> to generate the data file.', 'Run <code>make all</code> to rebuild the shared site data.')
        comparison = data['model_results']['habitat_comparison']
        diversity = data['model_results']['diversity']
        values = [f"{summary['mean_density']:.1f} fish/m<sup>2</sup>", f'{start}–{end}', f"H′ = {diversity['shannon']:.2f}", f"D = {diversity['simpson']:.2f}"]
        stats = ['Repeated annual location summaries', f'{years} surveyed years; not evidence of stability', f"Evenness J′ = {diversity['evenness']:.2f}", f"{diversity['richness']} positive-catch seine taxa"]
        card_index = [0]
        def refresh_card(match):
            i = card_index[0]
            card_index[0] += 1
            card = re.sub(r'(<div class="insight-value">).*?(</div>)', lambda m: m[1] + values[i] + m[2], match[0], flags=re.S)
            return re.sub(r'(<div class="insight-stat">).*?(</div>)', lambda m: m[1] + stats[i] + m[2], card, flags=re.S)
        text = re.sub(r'<div class="insight-content">.*?</div>\s*</div>', refresh_card, text, count=4, flags=re.S)
        text = text.replace('Habitat Effect', 'Mean Density').replace('Temporal Trend', 'Monitoring Period').replace("Sen's slope estimate", 'Annual monitoring record').replace('Model Fit', 'Simpson Diversity').replace('Variance explained', 'Pooled seine catches')
    if filename == 'observatory.html':
        text = re.sub(r'<a href="/api/figures/[^\"]+"[^>]*>.*?</a>', '<a href="carpinteria_salt_marsh_fishes.html">Full guide</a>', text)
        text = text.replace('href="/api/data"', 'href="outputs/dashboard_data.json"')
        text = text.replace('Ecological Guilds', 'Feeding Guilds (Assigned Taxa Only)')
        text = text.replace('.text(\'of catch\')', '.text(\'assigned taxa only\')')
        text = text.replace('scientific: s.species_name,', 'scientific: [s.genus_name, s.species_name].filter(Boolean).join(" "),')
    if filename == 'portal.html':
        text = re.sub(r'(<div class="stat-value ocean">)\d+', rf'\g<1>{years}', text)
        text = re.sub(r'(<div class="stat-value coral">)\d+', rf'\g<1>{summary["total_species"]}', text)
        text = re.sub(r'(<div class="stat-value kelp">)\d+', rf'\g<1>{summary["total_samples"]}', text)
        text = text.replace('>Species Recorded</div>', '>Recorded Taxa</div>')
    if filename == 'index.html':
        text = text.replace('scientific: s.species_name,', 'scientific: [s.genus_name, s.species_name].filter(Boolean).join(" "),')
        text = re.sub(r'(<strong id="total-records-display">)[^<]+', rf'\g<1>{summary["enclosure_records"] + summary["seine_records"]:,}', text)
        text = re.sub(r'(<strong id="species-detected-display">)[^<]+', rf'\g<1>{summary["total_species"]}', text)
        text = text.replace('Species Detected', 'Taxon Codes Detected')
        text = text.replace('Enclosure Data (EDI)', 'Annual Summary Data (EDI)').replace('EDI Repository (Enclosure)', 'EDI Repository (Annual Summaries)')
        text = text.replace('missed entirely', 'less likely to be captured')
        text = text.replace('target small, benthic gobies in tidal creeks', 'target small benthic gobies in both habitats').replace('capture larger, mobile fish in main channels', 'capture larger mobile fish in both habitats')
        text = text.replace('github.com/adrianstier/carpinteria-salt-marsh-fishes', 'github.com/adrianstier/sbc-2012-carpinteria-salt-marsh-fish')
        descriptions = {
            'panel-abundance': 'Cumulative seine catches only; these are not whole-marsh population sizes. Diversity indices pool the full monitoring period.',
            'panel-heatmap': 'Annual seine counts scaled to each taxon’s maximum. Counts depend on effort and capture probability; zeros and unresolved identifications need care.',
            'panel-seasonality': 'Catch per sampled haul, grouped by survey month. These annual surveys were not designed to measure seasonality; differences can reflect survey year and timing.',
            'panel-guilds': 'Provisional feeding and habitat classifications for assigned taxa only. Unassigned taxa are excluded from these percentages; they do not measure nursery function.',
            'panel-stability': 'Bray–Curtis differences between consecutive annual seine catches. This describes catch composition, not a test of causes or ecosystem health.',
            'panel-trends': 'Annual mean density by habitat from the published performance summaries. Differences among years are descriptive; a non-significant trend test does not establish stability.',
            'panel-habitat': 'Mean and SD across repeated annual location summaries. Habitat differences are descriptive; independent-sample tests do not account for repeated locations or shared annual conditions.',
            'panel-accumulation': 'Randomized accumulation of positive-catch seine taxon codes across sampled location-dates (100 permutations). The shaded band is ±1 SD, not a confidence interval. A plateau does not prove all marsh species were detected.',
            'panel-nmds': 'Bray–Curtis ordination of annual seine catch totals. Differences may reflect catch composition, effort, and detection. This is a descriptive display, not an environmental-effects test.',
            'panel-gam': 'Exploratory legacy Gaussian smooth, not a validated prediction model. Residual dependence and unequal variance remain; some fitted densities are negative. Do not interpret its p-values or intervals as reliable ecological inference.',
        }
        for panel, desc in descriptions.items():
            text = re.sub(rf'(<div class="chart-panel[^"\n]*" id="{panel}">.*?<p class="chart-description">).*?(</p>)', lambda m: m[1] + desc + m[2], text, count=1, flags=re.S)
        text = text.replace('Seasonal Fish Abundance', 'Catch by Sampling Month').replace('>Seasonality</button>', '>Sampling Calendar</button>')
        text = text.replace('(n=78)', '(84 annual location summaries)')
        text = text.replace('            renderStatsPanel();', '            // Inferential scorecards withheld pending a suitable repeated-measures model.')
        text = text.replace('1.7x Higher', 'Habitat comparison').replace('Fish density in tidal creeks vs main channel (p = 0.0016)', 'Compare annual location means; repeated locations limit independent-sample inference.')
        text = text.replace('40% Turnover', 'Annual turnover').replace('Mean annual Bray-Curtis dissimilarity indicates moderate change', 'Descriptive Bray–Curtis dissimilarity of annual catches')
        text = text.replace('59% Marine', 'Not estimated').replace('Proportion of fish using marsh as nursery habitat', 'Catch identity alone cannot establish juvenile nursery use.')
        text = text.replace('46% Topsmelt', 'Seine catch dominance').replace('Single species dominates; top 5 species = 96% of catch', 'Calculated from positive seine catches; enclosure catches are separate.')
    text = re.sub(r'<aside style="padding:1rem;margin:5rem 1rem 1rem;border:2px solid #789;">Updated .*?</aside>', lambda m: notice, text, flags=re.S)
    if notice not in text:
        text = text.replace('<body>', '<body>\n' + notice, 1)
    text = text.replace('guild: "Nursery User"', 'guild: "Coastal Visitor"')
    text = re.sub(r'(<li><a href="carpinteria_salt_marsh_fishes.html">Full guide</a></li>\s*){2}', '<li><a href="carpinteria_salt_marsh_fishes.html">Full guide</a></li>\n', text)
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines()) + '\n')

path = ROOT / 'carpinteria_salt_marsh_fishes.Rmd'
text = path.read_text().replace('2012-2024', f'{start}-{end}').replace('2012–2024', f'{start}–{end}').replace('2012-2024', f'{start}-{end}')
text = text.replace('seq(2012, 2024, 2)', f'seq({start}, {end}, 2)')
text = text.replace('# References & Further Reading', '# Interpretation and Data Revision\n\nThis update uses EDI packages **edi.647.9** and **edi.648.9**, the revisions listed by the SONGS program on 25 October 2026. The original files are read from the shared catalogue cache; hashes and schema checks are recorded in `data/metadata/current_sources.json`. Historical revision-8 files remain unchanged.\n\nThe performance table contains annual location summaries, combining method-specific estimates under the published protocol. Repeated samples of the same location are not independent replicates. Raw seine and enclosure catches must remain separate when comparing abundance. Summed catch is not a whole-marsh population estimate.\n\nTaxon inventories contain unresolved family or genus identifications as well as named species. A sampling-month comparison is not evidence of seasonality because the annual survey calendar is uneven. Catch identity alone does not establish juvenile nursery use. The separate dashboard’s legacy Gaussian models are exploratory and have residual and dependence problems; they are not validated inferential results.\n\n# References & Further Reading', 1) if '# Interpretation and Data Revision' not in text else text
text = text.replace('The most abundant fish in the marsh.', 'Numerically dominant in the enclosure catches.')
text = text.replace('Juveniles spend 1-2 years in salt marsh nursery habitat. A "left-eyed" flatfish whose eye migrates during development.', 'Juveniles use shallow coastal and embayment habitats. Individuals may have eyes on either side after metamorphosis.')
text = text.replace('Half shark, half ray! A unique California endemic.', 'A ray with an elongated body and broad pectoral disc.')
text = text.replace('Has venomous spines on its gill covers. Handle with care!', 'Has sharp spines on its gill covers. Let trained staff handle unfamiliar fish.')
text = text.replace('Females visit warm, shallow estuaries specifically to give birth—the warm water accelerates embryo development and excludes larger predators.', 'Uses shallow coastal and estuarine habitats. A catch does not establish that reproduction occurred at this site.')
text = text.replace('Endemic to California. Tolerates extreme salinity changes.', 'Occurs in California and Baja California estuaries; tolerates variable salinity.')
text = text.replace('by far the most abundant fish in the salt marsh', 'numerically dominant in the enclosure catches')
text = text.replace('### Total Species Richness:', '### Recorded Taxa (Including Unresolved Identifications):')
text = text.replace('species recorded**', 'taxon entries recorded**')
text = text.replace('Proportion of resident vs marine migrant species', 'Catch proportions among assigned resident and migrant taxa')
text = text.replace('At least **`r n_species` fish species** use Carpinteria Salt Marsh', '**`r n_species` taxon entries with positive catches** were recorded at Carpinteria Salt Marsh; these include unresolved identifications')
text = text.replace('The community is dominated by resident species highly adapted to fluctuating estuarine conditions', 'Resident and visiting fishes are both represented; catch proportions depend on the sampling method')
text = text.replace('normal-looking fish with eyes on both sides of their head', 'bilaterally symmetric larvae with an eye on each side of the head')
text = text.replace('They come to hunt and give birth in the protected waters.', 'Their occurrence does not establish that reproduction took place at this site.')
text = text.replace('year_colors <- colorRampPalette(c("#c6dbef", "#08519c"))(13)', 'year_colors <- colorRampPalette(c("#c6dbef", "#08519c"))(n_distinct(csm_ps$year))')
path.write_text(text)
print(f'Updated views: {start}–{end}, {years} years, {summary["total_species"]} positive-catch taxon codes.')
