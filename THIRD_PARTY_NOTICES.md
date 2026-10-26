# Third-party notices

The [MIT Licence](LICENSE) covers only the original code, documentation and synthetic farm data in this repository.

The processed layers in `data/processed/` and the exported maps in `exports/` contain or derive from third-party datasets. Those datasets keep their original licences. The MIT Licence does not apply to them.

## OpenStreetMap data (roads and places)

- **Copyright:** © OpenStreetMap contributors
- **Extract:** Geofabrik Ghana snapshot, 2026-10-25
- **Licence:** [Open Data Commons Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/)
- **Notice:** https://www.openstreetmap.org/copyright
- **Used in:** `roads_utm30n`, `places_utm30n`, and the optional online OSM basemap

## Ghana administrative boundaries (COD-AB)

- **Publisher:** OCHA, via the Humanitarian Data Exchange
- **Licence:** [Creative Commons Attribution for Intergovernmental Organisations (CC BY-IGO)](https://creativecommons.org/licenses/by/3.0/igo/)
- **Dataset:** https://data.humdata.org/dataset/cod-ab-gha
- **Used in:** `study_region_utm30n`, `districts_utm30n`

## Hansen Global Forest Change v1.12

- **Authors / publishers:** Hansen/UMD/Google/USGS/NASA
- **Licence:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **Citation:** Hansen, M. C. et al. (2013). High-Resolution Global Maps of 21st-Century Forest Cover Change. *Science* 342, 850–853. [doi:10.1126/science.1244693](https://doi.org/10.1126/science.1244693)
- **Used in:** `forest_loss_2021_2024.tif`

See [docs/SOURCES.md](docs/SOURCES.md) for download URLs, versions and the processing log.
