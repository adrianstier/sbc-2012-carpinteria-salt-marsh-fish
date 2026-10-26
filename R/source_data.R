# Shared source resolution. Historical data/raw/ and edi.* packages stay untouched.
read_songs <- function(role) {
  config <- jsonlite::fromJSON(here::here('data', 'metadata', 'current_sources.json'))
  item <- config$sources[[role]]
  if (!file.exists(item$path)) stop('Shared cache unavailable; run scripts/refresh_sources.py with SONGS_CACHE set.')
  stopifnot(digest::digest(file = item$path, algo = 'sha256') == item$sha256)
  readr::read_csv(item$path, show_col_types = FALSE, na = c('', 'NA'))
}
