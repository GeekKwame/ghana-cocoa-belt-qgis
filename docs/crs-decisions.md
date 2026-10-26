# CRS decisions for Ghana

**Project decision:** exchange data in WGS 84 (EPSG:4326), and measure, analyse and map in WGS 84 / UTM zone 30N (EPSG:32630). Every layer in `data/processed/` is stored in EPSG:32630.

## Quick decisions

| Task | CRS / method | Why |
| --- | --- | --- |
| Store GPS coordinates and exchange GeoJSON | WGS 84, EPSG:4326 | Global latitude/longitude system; GeoJSON uses longitude, latitude order |
| Display web basemap tiles | Web Mercator, EPSG:3857 | Standard tiled-web-map display CRS; do not use it for farm area |
| Measure Western North farms | WGS 84 / UTM zone 30N, EPSG:32630 | Western North lies in UTM zone 30N; coordinates are metres and local distortion is low |
| Measure far-eastern Ghana | WGS 84 / UTM zone 31N, EPSG:32631 | Better local fit east of the zone boundary near 0° longitude |
| Combine older Ghana survey maps | Inspect EPSG:2136 or EPSG:25000 and the datum transformation | A legacy grid cannot safely be relabelled as WGS 84 |
| Store data for an application | Preserve the source CRS or standardise deliberately; transform at the boundary | The database CRS is a design decision, not a styling choice |

## Terms

- A **datum** defines the reference ellipsoid and how coordinates relate to the Earth.
- A **projection** converts the curved Earth to a flat coordinate plane.
- A **CRS** combines the datum, coordinate system, units and, when relevant, a projection. An EPSG code identifies a registered CRS definition.
- **Assign/set CRS** changes only the metadata describing existing numbers. Use it only when the correct CRS metadata is missing.
- **Reproject/transform** calculates new coordinate values in another CRS. Use it when creating a UTM analysis layer from WGS 84 data.

## Measurement experiment

`FARM-001` was measured three ways:

| Method | Reported area | Interpretation |
| --- | ---: | --- |
| Raw planar calculation in EPSG:4326 | 0.0000006537 degree² | Not hectares or square metres; unsuitable for a farm-area result |
| EPSG:32630, UTM zone 30N | 8,000.00 m² / 0.80 ha | Trusted result for this Western North plot |
| EPSG:32631, UTM zone 31N | 8,086.86 m² / 0.8087 ha | About 1.09% larger because this plot is outside zone 31's best-fit area |

The experiment shows why a layer appearing in the right place is not enough: area depends on the coordinate system and its units. For this project, geometry was transformed to EPSG:32630 before calculating `$area / 10000`.

## Common diagnostics

- A Ghana point should be near longitude −3° to 1° and latitude 4.5° to 11.5°. A swapped pair often appears far from Ghana or produces an impossible extent.
- If a layer is displaced, inspect its declared CRS and sample coordinate values before changing anything.
- Never make a misplaced layer line up by guessing and using **Set CRS**. Identify the real source CRS, then transform it.
- WGS 84 coordinates may display correctly over an OSM basemap because QGIS reprojects on the fly; that does not make degrees valid area units.
- For multi-zone or national calculations, evaluate a suitable national/equal-area projection or use geodesic area rather than blindly applying one UTM zone.
