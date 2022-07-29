from typing import Tuple

from qgis.core import (QgsFeature, QgsPoint, QgsPointXY, QgsProject, QgsVectorLayer, QgsGeometry,
                       QgsGeometryUtils, qgsfunction)


def point_on_border(feature: QgsFeature, layer_name: str) -> Tuple[bool, QgsPoint, QgsPoint]:
    project = QgsProject.instance()
    layer: QgsVectorLayer = project.mapLayersByName(layer_name)[0]
    geometry = feature.geometry()
    intersecting_feature = QgsFeature()
    intersecting_feature_exists = layer.getFeatures(
        geometry.boundingBox()).nextFeature(intersecting_feature)
    if not intersecting_feature_exists:
        return (intersecting_feature_exists, geometry.centroid(), None)
    else:
        intersecting_geom = intersecting_feature.geometry().constGet()
        for part in intersecting_geom.parts():
            g = QgsGeometry(part.clone())
            if g.intersects(geometry):
                intersecting_geom = g
                break
        else:
            intersecting_geom = intersecting_feature.geometry()
        p = geometry.centroid().asPoint()
        origin_point = QgsPoint(p.x(), p.y())
        closest_point = QgsGeometryUtils.closestPoint(intersecting_geom.get(), origin_point)
        return (intersecting_feature_exists, closest_point, origin_point)


@qgsfunction(args='auto', group='Labels Placement', referenced_columns=[])
def azimuth_point_covering_outside_polygon(layer_name: str, feature, parent) -> int:
    intersecting, closest_point, origin_point = point_on_border(feature, layer_name)
    azimuth = origin_point.azimuth(closest_point)
    return_value = 4
    if intersecting:
        if azimuth >= -180 and azimuth < -135:
            return_value = 7
        elif azimuth >= -135 and azimuth < -45:
            return_value = 3
        elif azimuth >= -45 or azimuth < 45:
            return_value = 1
        elif azimuth >= 45 and azimuth < 135:
            return_value = 5
        elif azimuth >= 135 and azimuth < 225:
            return_value = 7
    return return_value


@qgsfunction(args='auto', group='Labels Placement', referenced_columns=[])
def point_outside_covering_polygon(layer_name: str, offset: float, feature, parent):
    intersecting, closest_point, origin_point = point_on_border(feature, layer_name)
    if not intersecting:
        geom = QgsGeometry.fromPointXY(QgsPointXY(closest_point.x(), closest_point.y()))
        return geom
    line = QgsGeometry.fromPolyline([origin_point, closest_point])
    line = line.extendLine(0, offset)
    point = line.vertexAt(1)
    return QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y()))
