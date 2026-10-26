#!/usr/bin/env Rscript
# Validate revision-9 inputs held in the shared SONGS catalogue. Historical
# data/raw/ packages remain immutable. See README for access/revision policy.
status <- system2("python3", here::here("scripts", "refresh_sources.py"))
if (status != 0) stop("Source-cache validation failed; analysis was not run.")
