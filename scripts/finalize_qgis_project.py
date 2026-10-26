#!/usr/bin/env python3
"""Apply final styling, build the print layout, and export the Ghana Cocoa Belt map."""

from pathlib import Path
import sys

from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsLayoutItemScaleBar,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsPalLayerSettings,
    QgsPalettedRasterRenderer,
    QgsPrintLayout,
    QgsProject,
    QgsRasterLayer,
    QgsSingleSymbolRenderer,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsUnitTypes,
    QgsVectorLayer,
    QgsVectorLayerSimpleLabeling,
)


ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATH = ROOT / "project" / "ghana-cocoa-belt.qgz"
GPKG = ROOT / "data" / "processed" / "ghana-cocoa-belt.gpkg"
LOSS_RASTER = ROOT / "data" / "processed" / "forest_loss_2021_2024.tif"
EXPORTS = ROOT / "exports"
LAYOUT_NAME = "Ghana Cocoa Belt — Western North"


def layout_units():
    return QgsUnitTypes.LayoutMillimeters


def move_resize(item, x, y, width, height):
    item.attemptMove(QgsLayoutPoint(x, y, layout_units()))
    item.attemptResize(QgsLayoutSize(width, height, layout_units()))


def make_font(size, bold=False):
    font = QFont("Noto Sans")
    font.setPointSizeF(float(size))
    font.setBold(bold)
    return font


def add_label(layout, text, x, y, width, height, size=8, bold=False, color="#29251f"):
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    font = make_font(size, bold)
    label.setFont(font)
    label.setFontColor(QColor(color))
    label.setMarginX(1)
    label.setMarginY(0.5)
    layout.addLayoutItem(label)
    move_resize(label, x, y, width, height)
    return label


def vector_layer(name, table):
    layer = QgsVectorLayer(f"{GPKG}|layername={table}", name, "ogr")
    if not layer.isValid():
        raise RuntimeError(f"Could not load {table} from {GPKG}")
    return layer


def find_or_add(project, name, table):
    for layer in project.mapLayers().values():
        if f"layername={table}" in layer.source():
            layer.setName(name)
            return layer
    layer = vector_layer(name, table)
    project.addMapLayer(layer)
    return layer


def simple_labeling(layer, field, size, color, buffer_color="#fffdf8"):
    settings = QgsPalLayerSettings()
    settings.fieldName = field
    settings.enabled = True
    text = QgsTextFormat()
    text.setFont(make_font(size))
    text.setSize(size)
    text.setColor(QColor(color))
    buffer = QgsTextBufferSettings()
    buffer.setEnabled(True)
    buffer.setSize(0.8)
    buffer.setColor(QColor(buffer_color))
    text.setBuffer(buffer)
    settings.setFormat(text)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    layer.setLabelsEnabled(True)


def main():
    QgsApplication.setPrefixPath("/usr", True)
    app = QgsApplication([], False)
    app.initQgis()

    project = QgsProject.instance()
    if not project.read(str(PROJECT_PATH)):
        raise RuntimeError(f"Could not open {PROJECT_PATH}")
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:32630"))
    try:
        project.setFilePathStorage(Qgis.FilePathType.Relative)
    except AttributeError:
        pass

    study = find_or_add(project, "Western North study region", "study_region_utm30n")
    districts = find_or_add(project, "Districts", "districts_utm30n")
    roads = find_or_add(project, "Major roads", "roads_utm30n")
    places = find_or_add(project, "Towns", "places_utm30n")
    farms = find_or_add(project, "Farm polygons", "farms_with_district")
    markers = find_or_add(project, "Farm locations", "farm_markers")

    loss = None
    for layer in project.mapLayers().values():
        if Path(layer.source().split("|")[0]).name == LOSS_RASTER.name:
            loss = layer
            break
    if loss is None:
        loss = QgsRasterLayer(str(LOSS_RASTER), "Mapped forest loss, 2021–2024")
        if not loss.isValid():
            raise RuntimeError(f"Could not load {LOSS_RASTER}")
        project.addMapLayer(loss)
    loss.setName("Forest loss, 2021–2024")

    # The online basemap is retained as an optional, hidden reference layer.
    osm = None
    for layer in project.mapLayers().values():
        if layer.name() == "OpenStreetMap basemap (online; optional)":
            osm = layer
            break
    if osm is None:
        osm_uri = (
            "type=xyz&url=https://tile.openstreetmap.org/"
            "%7Bz%7D/%7Bx%7D/%7By%7D.png&zmin=0&zmax=19&crs=EPSG3857"
        )
        osm = QgsRasterLayer(osm_uri, "OpenStreetMap basemap (online; optional)", "wms")
        if osm.isValid():
            project.addMapLayer(osm)

    study.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "#f7f3e8",
                    "outline_color": "#2f4f3b",
                    "outline_width": "0.9",
                }
            )
        )
    )
    districts.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "255,255,255,0",
                    "outline_color": "#8d7862",
                    "outline_width": "0.45",
                }
            )
        )
    )
    simple_labeling(districts, "wordwrap(\"adm2_name\", 18)", 6.5, "#4b4034")
    district_settings = districts.labeling().settings()
    district_settings.isExpression = True
    districts.setLabeling(QgsVectorLayerSimpleLabeling(district_settings))

    roads.setSubsetString(
        "\"fclass\" IN ('trunk','trunk_link','primary','primary_link','secondary','tertiary')"
    )
    roads.setRenderer(
        QgsSingleSymbolRenderer(
            QgsLineSymbol.createSimple(
                {"line_color": "#76695b", "line_width": "0.38", "capstyle": "round"}
            )
        )
    )

    places.setSubsetString("\"fclass\" = 'town' AND \"name\" IS NOT NULL")
    places.setRenderer(
        QgsSingleSymbolRenderer(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "circle",
                    "color": "#173f5f",
                    "outline_color": "#ffffff",
                    "outline_width": "0.35",
                    "size": "2.1",
                }
            )
        )
    )
    simple_labeling(places, "name", 6.5, "#173f5f")

    farms.setRenderer(
        QgsSingleSymbolRenderer(
            QgsFillSymbol.createSimple(
                {
                    "color": "#7cb342",
                    "outline_color": "#244b2b",
                    "outline_width": "0.6",
                }
            )
        )
    )
    markers.setRenderer(
        QgsSingleSymbolRenderer(
            QgsMarkerSymbol.createSimple(
                {
                    "name": "diamond",
                    "color": "#ffb300",
                    "outline_color": "#5d3a00",
                    "outline_width": "0.45",
                    "size": "3.2",
                }
            )
        )
    )

    classes = [
        QgsPalettedRasterRenderer.Class(21, QColor("#fee8c8"), "2021"),
        QgsPalettedRasterRenderer.Class(22, QColor("#fdbb84"), "2022"),
        QgsPalettedRasterRenderer.Class(23, QColor("#e34a33"), "2023"),
        QgsPalettedRasterRenderer.Class(24, QColor("#9d1535"), "2024"),
    ]
    loss.setRenderer(QgsPalettedRasterRenderer(loss.dataProvider(), 1, classes))
    loss.renderer().setOpacity(0.72)

    # Keep source and intermediate layers available, but show only final map layers.
    final_layers = {layer.id() for layer in [study, loss, districts, roads, places, farms, markers]}
    root = project.layerTreeRoot()
    for layer in project.mapLayers().values():
        node = root.findLayer(layer.id())
        if node:
            node.setItemVisibilityChecked(layer.id() in final_layers)
    if osm is not None:
        node = root.findLayer(osm.id())
        if node:
            node.setItemVisibilityChecked(False)

    manager = project.layoutManager()
    existing = manager.layoutByName(LAYOUT_NAME)
    if existing:
        manager.removeLayout(existing)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(LAYOUT_NAME)
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(297, 210, layout_units()))

    add_label(layout, "GHANA COCOA BELT", 10, 5, 277, 11, 18, True, "#244b2b")
    add_label(
        layout,
        "Synthetic farm context in Western North Region",
        10,
        16,
        277,
        7,
        9,
        False,
        "#6b5b45",
    )

    map_item = QgsLayoutItemMap(layout)
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeColor(QColor("#5a5146"))
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.35, layout_units()))
    map_item.setBackgroundColor(QColor("#fffdf8"))
    layout.addLayoutItem(map_item)
    move_resize(map_item, 10, 27, 205, 154)
    extent = study.extent()
    extent.grow(max(extent.width(), extent.height()) * 0.035)
    map_item.zoomToExtent(extent)
    map_item.setLayers([markers, farms, places, roads, districts, loss, study])
    map_item.setKeepLayerSet(True)

    north = QgsLayoutItemPicture(layout)
    north.setPicturePath("/usr/share/qgis/svg/arrows/NorthArrow_01.svg")
    north.setResizeMode(QgsLayoutItemPicture.Zoom)
    layout.addLayoutItem(north)
    move_resize(north, 244, 28, 20, 20)

    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("MAP LEGEND")
    legend.setLinkedMap(map_item)
    legend.setAutoUpdateModel(False)
    legend.setResizeToContents(False)
    legend.setBackgroundEnabled(True)
    legend.setBackgroundColor(QColor("#fffdf8"))
    legend.setFrameEnabled(True)
    legend.setFrameStrokeColor(QColor("#c8bdad"))
    legend.style(QgsLegendStyle.Title).setFont(make_font(9, True))
    legend.style(QgsLegendStyle.Subgroup).setFont(make_font(7))
    legend.style(QgsLegendStyle.SymbolLabel).setFont(make_font(7))
    legend_root = legend.model().rootGroup()
    legend_root.clear()
    for layer in [markers, farms, places, roads, districts, loss]:
        legend_root.addLayer(layer)
    layout.addLayoutItem(legend)
    move_resize(legend, 220, 52, 67, 91)

    scale = QgsLayoutItemScaleBar(layout)
    scale.setStyle("Single Box")
    scale.setLinkedMap(map_item)
    scale.setUnits(QgsUnitTypes.DistanceKilometers)
    scale.setUnitLabel("km")
    scale.setUnitsPerSegment(20)
    scale.setNumberOfSegments(3)
    scale.setNumberOfSegmentsLeft(0)
    scale.setHeight(2.2)
    scale.setFont(make_font(7))
    layout.addLayoutItem(scale)
    move_resize(scale, 17, 169, 62, 10)

    add_label(layout, "MAP QUESTION", 221, 146, 65, 6, 8, True, "#244b2b")
    question = add_label(
        layout,
        "Where are the synthetic cocoa farm training plots in relation to districts, major roads, towns and mapped 2021–2024 forest loss?",
        221,
        152,
        65,
        28,
        7,
    )
    question.setMode(QgsLayoutItemLabel.ModeFont)

    footer = (
        "Synthetic training farms — not real farmer data. Diamond markers exaggerate plot locations for visibility.\n"
        "Sources: OCHA COD-AB; © OpenStreetMap contributors (ODbL); Hansen/UMD/Google/USGS/NASA. "
        "Forest loss is a relative indicator, not a deforestation verdict.\n"
        "CRS: WGS 84 / UTM zone 30N (EPSG:32630)  |  Author: Edmund Dogbe  |  26 Oct 2026"
    )
    add_label(layout, footer, 10, 184, 277, 20, 6.5, False, "#49433b")

    manager.addLayout(layout)
    EXPORTS.mkdir(parents=True, exist_ok=True)
    exporter = QgsLayoutExporter(layout)
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = 300
    pdf_result = exporter.exportToPdf(str(EXPORTS / "ghana-cocoa-belt.pdf"), pdf_settings)
    image_settings = QgsLayoutExporter.ImageExportSettings()
    image_settings.dpi = 220
    png_result = exporter.exportToImage(str(EXPORTS / "ghana-cocoa-belt.png"), image_settings)
    if pdf_result != QgsLayoutExporter.Success or png_result != QgsLayoutExporter.Success:
        raise RuntimeError(f"Export failed: PDF={pdf_result}, PNG={png_result}")

    if not project.write(str(PROJECT_PATH)):
        raise RuntimeError(f"Could not save {PROJECT_PATH}")
    print(f"Saved project: {PROJECT_PATH}")
    print(f"Exported: {EXPORTS / 'ghana-cocoa-belt.pdf'}")
    print(f"Exported: {EXPORTS / 'ghana-cocoa-belt.png'}")
    # Do not call exitQgis() here: this QGIS build can segfault while tearing down GDAL.
    return 0


if __name__ == "__main__":
    sys.exit(main())
