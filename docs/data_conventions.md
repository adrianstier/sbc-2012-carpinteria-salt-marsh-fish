# SONGS fish data: revision-9 update

Updated 26 October 2026. Source packages are `edi.647.9` (raw surveys) and
`edi.648.9` (annual performance summaries), listed on the public
[SONGS data page](https://marinemitigation.msi.ucsb.edu/data).
Authenticated PASTA revision-list requests on 26 October confirmed revision 9
is the latest available for both packages. Remote EML matches the shared cached
EML. The timestamp and revision lists are recorded in
`data/metadata/current_sources.json`. No newer source files were needed.

## Source files and reproducibility

The shared local SONGS catalogue already contained all three revision-9 CSVs,
their EML and download manifest. No duplicate download was necessary. Original
revision-8 files in this repository are unchanged. The NAS was not mounted;
no substitute mount directory was created.

Run `make all` to validate the shared cache, run analyses, export matching JSON
feeds, refresh embedded dashboard data, render the guide, and verify outputs.
`SONGS_CACHE` can point to another complete copy of the shared catalogue.
Run `python3 scripts/refresh_sources.py --verify-remote` for a fresh authenticated
revision/EML check using the private shared session. A plain local rebuild
preserves the recorded verification date; it does not claim a new remote check.
`data/metadata/current_sources.json` records absolute input paths, source URLs,
SHA256 hashes, EML hashes, header checks, and Carp-only data profiles. Hashes
detect local changes after this baseline; they are not independently obtained
repository checksums. Cache sizes agree with the existing download manifest.

## Conventions checked before analysis

- EML attribute order matches each CSV header exactly.
- Blanks and the EML missing-value code `.` mean not recorded/not available,
  not a zero catch. Physical sample keys and response values have no missing
  values in the Carp subset. The profile records missingness in all columns.
- Recorded zero catches remain zero; they do not establish species occurrence.
  Inventories use positive counts. Counts of taxon codes include unresolved
  family/genus identifications and are not confirmed biological species counts.
- No duplicate physical record keys were found. Enclosure keys retain enclosure,
  station, survey and haul; seine keys retain section/label, survey and haul.
  Date/location aggregation for accumulation intentionally combines those
  sub-samples and must not be called a count of individual hauls.
- Shared species codes agree on genus/species across the two raw tables. The
  manually curated advanced-analysis dictionary previously mislabeled LEAR,
  PACA, POMY and SPAR; these now match the raw records. Guild assignments are
  provisional and exclude unassigned taxa from their denominator.
- Raw record years agree with calendar dates. Annual performance summaries have
  no date column: their key is year + location, not year + date + location.
- Carp has 12 fixed monitoring locations (6 per habitat) repeated annually over
  2012–2025: 168 annual location summaries, not 168 independent visits. The
  published performance estimates combine method-specific estimates under the
  original protocol. Raw enclosure and seine counts are not interchangeable.
- Monthly summaries reflect an uneven annual survey calendar, not seasonal
  population sampling. Catch per haul uses location, section and haul in its
  effort denominator; it is not density or a correction for gear selectivity.
- No generated row-number IDs are used to join source tables.

## Interpretation limits

The refreshed positive-catch inventory contains 43 taxon codes across methods,
including unresolved identifications. The former 71-code headline included
taxa represented only by zero catches in Carp.

Legacy GLM/GAM/LMM fits are retained for reproducibility, not validated inference.
A read-only diagnostic review found skewed/unequal residuals, repeated-location
and shared-year dependence, and a negative GAM fitted density (~−4.95 fish/m²).
The LMM converged and was not singular, but annual-mean residual lag-1
autocorrelation remained ~0.43. The GLM habitat contrast is tidal creek minus
main channel; the old coefficient name reversed that interpretation.

No significant monotonic trend does not mean ecological stability. Summed
catches are not marsh-wide population estimates. Event-overlap graphics cannot
identify climate or storm effects. Nursery-function proportions are withheld:
taxon identity does not supply juvenile size, age, survival, or adult recruitment.

This is observational monitoring at fixed locations, with gear selectivity,
uneven survey dates, unresolved taxa, and unmodeled environmental covariates.
Use descriptive annual and habitat figures for teaching. A later inferential
analysis needs a suitable response distribution, repeated-location/shared-year
structure, temporal dependence checks and diagnostics before interpretation.
