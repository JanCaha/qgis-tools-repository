from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsGeometryUtils,
                       QgsPoint, QgsPointXY, qgsfunction)


@qgsfunction(args='auto', group='Label', referenced_columns=[])
def angle_point_outside_polygon(layer_name: str, feature: QgsFeature, parent):
    geometry = feature.geometry()
    project = QgsProject.instance()
    layer: QgsVectorLayer = project.mapLayersByName(layer_name)[0]
    intersecting_feature = QgsFeature()
    intersecting_feature_exists = layer.getFeatures(
        geometry.boundingBox()).nextFeature(intersecting_feature)
    if not intersecting_feature_exists:
        return geometry.centroid()
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
        azimuth = origin_point.azimuth(closest_point)
        return_value = 0
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


@qgsfunction(args='auto', group='Label', referenced_columns=[])
def point_outside_polygon(layer_name: str, offset: float, feature: QgsFeature, parent):
    geometry = feature.geometry()
    project = QgsProject.instance()
    layer: QgsVectorLayer = project.mapLayersByName(layer_name)[0]
    intersecting_feature = QgsFeature()
    intersecting_feature_exists = layer.getFeatures(
        geometry.boundingBox()).nextFeature(intersecting_feature)
    if not intersecting_feature_exists:
        return geometry.centroid()
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
        line = QgsGeometry.fromPolyline([origin_point, closest_point])
        line = line.extendLine(0, offset)
        point = line.vertexAt(1)
        return QgsGeometry.fromPointXY(QgsPointXY(point.x(), point.y()))
