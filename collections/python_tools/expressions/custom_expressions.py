from qgis.core import (QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject,
                       qgsfunction)


@qgsfunction(args='auto', group='Custom', referenced_columns=[])
def point_to_wgs84_coordinate(crs, geometry, feature, parent):
    """
    Transforms centroid of geometry from coordinate given as crs to WGS84.
    <h2>Example usage:</h2>
    <ul>
      <li>point_to_wgs84_coordinate(@layer_crs, $geometry)</li>
      <li>point_to_wgs84_coordinate("EPSG:5514", make_point(-546005, -1148968))</li>
    </ul>
    """
    crs_in = QgsCoordinateReferenceSystem(crs)
    crs_wgs84 = QgsCoordinateReferenceSystem("EPSG:4326")
    transform = QgsCoordinateTransform(crs_in, crs_wgs84, QgsProject.instance())

    geom = geometry.centroid()

    geom.transform(transform)

    return geom
