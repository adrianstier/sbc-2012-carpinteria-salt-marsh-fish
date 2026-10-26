# Carpinteria Salt Marsh Fish Community Data

*Last updated: 2026-10-26*

## Read online

[Monitoring guide: fishes of Carpinteria Salt Marsh](https://adrianstier.github.io/sbc-2012-carpinteria-salt-marsh-fish/carpinteria_salt_marsh_fishes.html)

[Interactive monitoring site](https://adrianstier.github.io/sbc-2012-carpinteria-salt-marsh-fish/)

GitHub Pages publishes the checked-in HTML from `main` at the repository root.
Rebuild with `make all` before publishing a data update; GitHub does not run the
local R analysis or access the private EDI session.

## Overview

This repository analyzes Carpinteria fish monitoring from **2012–2025**, using
SONGS packages **edi.647.9** and **edi.648.9**, the revisions currently listed on
the [program's data page](https://marinemitigation.msi.ucsb.edu/data). Original
CSVs and EML are reused from the shared local SONGS catalogue, not re-downloaded
or copied over revision 8. The refresh contains 168 annual location summaries
and 43 positive-catch taxon codes, including unresolved identifications.

## Reproduce the current guide and dashboards

Run `Rscript R/00_install_packages.R`, then `make all`. This validates cached
sources, rebuilds analyses and matching JSON feeds, updates embedded dashboard
data, renders `carpinteria_salt_marsh_fishes.html`, and runs consistency checks.
The five entry points (`index.html`, `dashboard.html`, `observatory.html`,
`analysis.html`, and `portal.html`) use one generated `outputs/site-data.js`
bundle rather than separate snapshots or local JSON fetches. This permits direct
local-file loading; interactive charts still require the external D3 library.
Scatter plots contain the 168 observed annual location summaries, not simulated
points. Feeding-guild percentages are calculated for assigned taxa only.
Set `SONGS_CACHE` to a complete catalogue copy if using a different machine.
The former `01_download_data.R` placeholder URLs are removed; that command now
resolves and validates the existing cache. It does not download newer revisions.

See [data conventions and limitations](docs/data_conventions.md) and
`data/metadata/current_sources.json` for provenance, hashes, source URLs, schema
checks and interpretation limits. Authenticated PASTA revision-list requests on
26 October confirmed revision 9 is the latest for both packages; remote EML
matches the cache. Run `python3 scripts/refresh_sources.py --verify-remote`
to repeat that check with a valid private session. Legacy models are exploratory,
not validated inference. Seasonal,
causal event-impact, and nursery-function claims are not supported by this update.

## Study Context

The SONGS Mitigation Monitoring Program was established to evaluate the San Dieguito Wetland restoration project. Fish communities are monitored at the restoration site and reference wetlands to assess whether restoration meets biological performance standards. **Carpinteria Salt Marsh (CSM)** serves as one of the primary reference wetlands representing relatively undisturbed, natural tidal wetlands within the Southern California Bight.

## EEMB 106 teaching connection

The sibling [EEMB 106 — Biology of Fishes](../courses/EEMB106-Biology-of-Fishes) repository uses
these long-term monitoring data as context for a Fall 2026 Carpinteria field event. The course
will document a single, approval-gated pre-seine eDNA/capture comparison; its field logistics,
permits, custody records, and any class-event metadata live in the course repository, not here.
See its `labs/carp-edna-seine-integration-2026.md` and both repositories’ `AGENTS.md` and
`CLAUDE.md` files for the shared boundary. This repository's published EDI inputs remain
unaltered.

## Historical Revision-8 Data Files (Retained Unchanged)

### Directory: `edi.648.8/` - Performance Standard Data (Summarized)

| File | Description |
|------|-------------|
| `wetland_ps_fish_abundance_and_richness-*.csv` | **Annual summary data** of fish density (individuals/m²) and species richness at each sampling location. Combines enclosure trap and beach seine data. |

**Variables:**
- `year`: Survey year (2012-2024)
- `wetland_code`: CSM (Carpinteria), MUL (Mugu Lagoon), SDW (San Dieguito), TJE (Tijuana), LPL (Los Penasquitos - 2024 only)
- `module_code`: Spatial module within wetland
- `tc_mc_code`: Tidal creek (TC) or main channel (MC) location identifier
- `habitat_code`: TC = Tidal Creek, BNMC = Basin/Main Channel
- `count_per_m2`: Fish density (individuals per square meter)
- `species_count`: Number of unique species observed

### Directory: `edi.647.8/` - Raw Survey Data

| File | Description |
|------|-------------|
| `wetland_ts_fish_enclosure-*.csv` | **Enclosure trap data** - Raw counts of gobies (small, benthic fishes) from 0.43 m² circular enclosure traps. Five enclosures per location. |
| `wetland_ts_fish_seine-*.csv` | **Beach seine data** - Raw counts of larger, mobile fishes from ~100 m² beach seine hauls. |

**Enclosure Data Variables:**
- `year`, `date`, `survey`: Temporal identifiers
- `wetland_code`, `habitat_code`, `tc_mc_code`: Spatial identifiers
- `enclosure_number`, `sampling_station_label`: Replicate identifiers
- `depth`: Water depth (cm)
- `haul_no`: Sequential haul number
- `species_id`, `species_code`, `genus_name`, `species_name`: Taxonomic identifiers
- `count`: Number of individuals
- `enclosure_area`: Area sampled (0.43 m²)

**Seine Data Variables:**
- Similar spatial/temporal variables as enclosure data
- `seine_section_code`, `seine_label`: Seine replicate identifiers
- `seine_sample_width`, `seine_sample_length`, `seine_sample_area`: Sampling dimensions

## Sampling Methods

### Enclosure Traps
- **Target**: Small benthic gobies (Gobiidae)
- **Design**: 0.43 m² × 0.9 m circular enclosure traps
- **Protocol**: 5 enclosures per location, spaced ~10 m apart
- **Sampling**: Multiple hauls with BINCKE net until 3 consecutive passes with no fish

### Beach Seines
- **Target**: Larger, mobile fishes
- **Design**: 2 m × 7.62 m beach seine with blocking nets
- **Protocol**: 5 hauls through blocked area (~100 m²)
- **Sampling**: Non-goby fishes identified, counted, and released

## Fish Species Recorded

### Gobies (Enclosure Sampling)
| Scientific Name | Common Name | Code |
|----------------|-------------|------|
| *Clevelandia ios* | Arrow Goby | CLIO |
| *Ilypnus gilberti* | Cheekspot Goby | ILGI |
| *Quietula y-cauda* | Shadow Goby | QUYC |
| *Gillichthys mirabilis* | Longjaw Mudsucker | GIMI |
| *Acanthogobius flavimanus* | Yellowfin Goby | ACFV |

### Seine Species (Selection)
| Scientific Name | Common Name | Code |
|----------------|-------------|------|
| *Atherinops affinis* | Topsmelt | ATAF |
| *Fundulus parvipinnis* | California Killifish | FUPA |
| *Paralichthys californicus* | California Halibut | PACA |
| *Hypsopsetta guttulata* | Diamond Turbot | HYGU |
| *Syngnathus leptorhynchus* | Bay Pipefish | SYLE |
| *Mugil cephalus* | Striped Mullet | MUCE |
| *Leptocottus armatus* | Staghorn Sculpin | LEAR |
| *Myliobatis californicus* | Bat Ray | MYCA |
| *Urolophus halleri* | Round Stingray | URHA |

## Study Sites

| Code | Wetland | Location | Coordinates |
|------|---------|----------|-------------|
| **CSM** | Carpinteria Salt Marsh | Santa Barbara County, CA | 34.401°N, 119.538°W |
| MUL | Mugu Lagoon | Ventura County, CA | 34.102°N, 119.097°W |
| SDW | San Dieguito Wetland | San Diego County, CA | 32.970°N, 117.260°W |
| TJE | Tijuana Estuary | San Diego County, CA | 32.570°N, 117.127°W |
| LPL | Los Penasquitos Lagoon | San Diego County, CA | 32.931°N, 117.252°W |

*Note: Tijuana Estuary (TJE) was replaced by Los Penasquitos Lagoon (LPL) in 2024.*

## Current Data Citations

- Wetland survey fish abundance, revision 9 (2026):
  [edi.647.9](https://doi.org/10.6073/pasta/57c6811e9ded961fbd5bdfaa074d6d9f).
- Wetland annual fish abundance and richness, revision 9 (2026):
  [edi.648.9](https://doi.org/10.6073/pasta/fd7423338030a23118de2d5c1ff2aa5e).

## Historical Revision-8 Citations

**Performance Standard Data:**
> Schroeter, S., H. Page, D. Reed, K. Beheshti, R. Smith, and D. Huang. 2025. UCSB SONGS Mitigation Monitoring: Wetland Performance Standard - Fish Abundance and Species Richness. Environmental Data Initiative. DOI: 10.6073/pasta/a573e343e096c65ba5bc58ca25f48fa0

**Survey Data:**
> Schroeter, S., H. Page, D. Reed, K. Beheshti, R. Smith, and D. Huang. 2025. UCSB SONGS Mitigation Monitoring: Wetland Survey - Fish Abundance. Environmental Data Initiative. DOI: 10.6073/pasta/643f86b3043a15cb7d597e10fcff47a2

## License

Data released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**

## Contact

SONGS Mitigation Monitoring Project
Marine Science Institute, UC Santa Barbara
Email: songsmmp@lifesci.ucsb.edu
Website: http://marinemitigation.msi.ucsb.edu/
