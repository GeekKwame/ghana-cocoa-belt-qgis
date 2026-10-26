# Data sources and processing log

This manifest records every third-party dataset used in the Ghana Cocoa Belt map, its licence, and each processing step.

**Included in this repository:** only the processed outputs in `data/processed/`, which are `ghana-cocoa-belt.gpkg` (six layers in EPSG:32630) and `forest_loss_2021_2024.tif`. The raw downloads listed under "Local raw file", the intermediate WGS 84 layers, `synthetic_farms` and `hansen_lossyear_2001_2024.tif` are not redistributed. Download the raw data from the publisher URLs below to repeat the processing.

The farm polygons are **synthetic**. They were drawn for training and do not represent real farms, farmers or survey records.

| Dataset | Publisher | Source URL | Downloaded | Version/date | Licence | Original CRS | Local raw file | Used for | Limitations |
| ------- | --------- | ---------- | ---------- | ------------ | ------- | ------------ | -------------- | -------- | ----------- |
| Ghana administrative boundaries (ADM0–ADM2) | OCHA Field Information Services Section (FISS) | [HDX GeoJSON resource](https://data.humdata.org/dataset/cod-ab-gha/resource/c8d647a7-f396-4108-9fe4-cf7b31731a73) | 2026-10-26 | Resource updated 2026-08-14; dataset coverage through 2025-10-30 | CC BY-IGO | EPSG:4326 (WGS 84) | `data/raw/gha_admin_boundaries.geojson/` | National, regional and district context; P-code joins | 16 ADM1 and 260 ADM2 features. The evolved COD-AB structure does not fully match the older 2010 census COD-PS structure. |
| Ghana OpenStreetMap extract | Geofabrik GmbH / OpenStreetMap contributors | [Geofabrik Ghana download](https://download.geofabrik.de/africa/ghana.html) | 2026-10-26 | Data snapshot 2026-10-25T21:21:21Z | ODbL 1.0 | WGS 84 (CRS84; longitude/latitude) | `data/raw/ghana-261025-free.gpkg/ghana.gpkg` | Roads and settlement/place context | Completeness and tags vary by location and mapper activity; this daily extract will change over time. |
| Global Forest Change loss year | GLAD, University of Maryland / Google / USGS / NASA | [Global Forest Change v1.12 downloads](https://storage.googleapis.com/earthenginepartners-hansen/GFC-2024-v1.12/download.html) | 2026-10-26 | v1.12, covering loss years 2001–2024 | CC BY 4.0 | Geographic WGS 84, 1 arc-second grid | Versioned source tile `Hansen_GFC-2024-v1.12_lossyear_10N_010W.tif`; AOI extracts under `data/processed/` | Introductory 2021–2024 forest-loss context | A relative indicator of stand-replacement disturbance, not a legal deforestation verdict. Pixel counts should not be treated as definitive area estimates. |

## Checks before use

- [x] I opened the publisher's dataset page, rather than relying only on a copied download.
- [x] I verified the licence permits the way I will publish the result.
- [x] I recorded the dataset's date or version; "latest" is not a reproducible version.
- [x] I checked geometry type, feature count, extent, CRS and units in QGIS.
- [x] I checked important fields, missing values and whether the supposed ID is unique.
- [x] I kept the downloaded HDX and Geofabrik archives unchanged under `data/raw/`; the large Hansen tile is referenced by its immutable versioned URL instead of duplicated locally.
- [x] I recorded every material cleaning, repair, join or reprojection below.

## Processing log

| Date | Input | Operation | Output | Reason/check |
| ---- | ----- | --------- | ------ | ------------ |
| 2026-10-26 | HDX `gha_admin1.geojson`, `gha_admin2.geojson` | Select Western North and its districts, then reproject to EPSG:32630 | `study_region_utm30n`, `districts_utm30n` in `ghana-cocoa-belt.gpkg` | 1 region and 9 districts; extents and names checked |
| 2026-10-26 | Geofabrik `gis_osm_roads_free`, `gis_osm_places_free` | Clip to Western North and reproject to EPSG:32630 | `roads_utm30n`, `places_utm30n` | 6,074 road features and 546 place features before display filters |
| 2026-10-26 | Synthetic farm polygons | Calculate `$area / 10000`, validate, check pairwise overlaps and spatially join districts | `farms_with_district`, `farm_markers` | 20 valid polygons; 0 overlaps; 0 missing areas; all inside the study region and joined across 9 districts |
| 2026-10-26 | Hansen v1.12 `lossyear_10N_010W` | Window, clip to the study boundary, reproject with nearest-neighbour resampling, then retain values 21–24 | `hansen_lossyear_2001_2024.tif`, `forest_loss_2021_2024.tif` | EPSG:32630; 27.6 m pixels; nodata 255; loss-year values 21–24 |

## Decisions and caveats

### Ghana administrative boundaries

- Use `gha_admin1.geojson` for regions and `gha_admin2.geojson` for districts. `gha_admin0.geojson` is optional national context.
- Preserve the ADM P-code fields for joins; do not join datasets solely by place name.
- The `_em` variants are edge-matched products. Start with the standard files above and document a change if the project later requires an edge-matched variant.

### Ghana OpenStreetMap extract

- Use `gis_osm_roads_free` for roads and `gis_osm_places_free` for settlement/place points. The downloaded snapshot contains 387,914 roads and 11,519 place points.
- Filter by `fclass` and the study-area boundary before copying these national layers into the processed project GeoPackage.
- Attribute the map with `© OpenStreetMap contributors` and retain the ODbL 1.0 notice. Geofabrik created the extract; OpenStreetMap contributors created the data.
- Keep the dated archive and extracted GeoPackage unchanged. A future `ghana-latest` download may contain different features, tags and geometries.

### Global Forest Change

- The displayed values 21–24 mean loss detected in 2021–2024. Values 1–20 and no-loss pixels are not displayed in the final thematic layer.
- Reprojection used nearest-neighbour resampling so categorical year codes were not averaged into new values.
- Use the map credit `Hansen/UMD/Google/USGS/NASA` and cite Hansen et al. (2013), *Science* 342, 850–853, doi:10.1126/science.1244693.
- The dataset measures tree-cover loss, which can include plantation harvest, fire or other disturbance. It does not by itself establish EUDR non-compliance.
