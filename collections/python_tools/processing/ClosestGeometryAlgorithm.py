import sys

from qgis.PyQt.QtCore import QVariant, QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField, QgsFeature, QgsProcessingParameterFeatureSink,
                       QgsProcessingException, QgsFields, QgsField, QgsPoint, QgsWkbTypes,
                       QgsGeometryUtils, QgsLineString, QgsPolygon, QgsProcessingFeedback,
                       QgsCoordinateTransform, QgsProject)


class ClosestGeometryAlgorithm(QgsProcessingAlgorithm):

    INPUT_POINTS = 'INPUTPOINTS'
    INPUT_POINTS_ID = 'INPUTPOINTSID'
    CLOSEST_GEOM = 'CLOSESTGEOM'
    CLOSEST_GEOM_ID = 'CLOSESTGEOMID'
    OUTPUT = 'OUTPUT'

    def createInstance(self):
        return ClosestGeometryAlgorithm()

    def name(self):
        return 'closestgeometryalgorithm'

    def displayName(self):
        return self.tr('Closest Geometry')

    def group(self):
        return self.tr('Vector Tools')

    def groupId(self):
        return 'vectortools'

    def shortHelpString(self):
        return self.tr("Closest Geometry")

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(self.INPUT_POINTS, self.tr('Input layer'),
                                                [QgsProcessing.TypeVectorPoint]))

        self.addParameter(
            QgsProcessingParameterField(self.INPUT_POINTS_ID,
                                        self.tr('Field with identification values for points'),
                                        parentLayerParameterName=self.INPUT_POINTS))

        self.addParameter(
            QgsProcessingParameterFeatureSource(self.CLOSEST_GEOM,
                                                self.tr('Closest feature layer')))

        self.addParameter(
            QgsProcessingParameterField(
                self.CLOSEST_GEOM_ID,
                self.tr('Field with identification values for closest geometry'),
                parentLayerParameterName=self.CLOSEST_GEOM))

        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT, self.tr('Output layer')))

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):

        input_points = self.parameterAsSource(parameters, self.INPUT_POINTS, context)

        id_field_name_input_points = self.parameterAsString(parameters, self.INPUT_POINTS_ID,
                                                            context)

        if input_points is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_POINTS))

        closest_layer = self.parameterAsSource(parameters, self.CLOSEST_GEOM, context)

        if closest_layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.CLOSEST_GEOM))

        crs_transformer = None

        if input_points.sourceCrs().toWkt() != closest_layer.sourceCrs().toWkt():

            crs_transformer = QgsCoordinateTransform(closest_layer.sourceCrs(),
                                                     input_points.sourceCrs(),
                                                     QgsProject.instance())

        id_field_name = self.parameterAsString(parameters, self.CLOSEST_GEOM_ID, context)

        id_field_closest_geometry = closest_layer.fields().field(id_field_name)
        id_field_input_points = input_points.fields().field(id_field_name_input_points)

        distance_field = QgsField("distance_closest", QVariant.Double)

        all_fields = QgsFields()

        all_fields.append(id_field_closest_geometry)
        all_fields.append(id_field_input_points)
        all_fields.append(distance_field)

        (sink, sink_dest) = self.parameterAsSink(parameters, self.OUTPUT, context, all_fields,
                                                 QgsWkbTypes.LineString, input_points.sourceCrs())

        total = 100.0 / (input_points.featureCount() * closest_layer.featureCount()
                        ) if input_points.featureCount() and closest_layer.featureCount() else 0

        start_feature: QgsFeature
        closest_geom_feature: QgsFeature

        for start_feature_count, start_feature in enumerate(input_points.getFeatures()):

            smallest_distance = sys.float_info.max

            for closest_geom_count, closest_geom_feature in enumerate(closest_layer.getFeatures()):

                if feedback.isCanceled():
                    break

                result_feature = QgsFeature(all_fields)

                result_feature.clearGeometry()

                point_geom = start_feature.geometry()

                closest_geom = closest_geom_feature.geometry()

                if crs_transformer:
                    closest_geom.transform(crs_transformer)

                distance_bbox = closest_geom.boundingBox().distance(point_geom.asPoint())

                if distance_bbox < smallest_distance:

                    if closest_layer.wkbType() == QgsWkbTypes.Polygon or closest_layer.wkbType(
                    ) == QgsWkbTypes.MultiPolygon:
                        geom_to_check = QgsPolygon()
                        geom_to_check.fromWkt(closest_geom.asWkt())

                    if closest_layer.wkbType() == QgsWkbTypes.LineString or closest_layer.wkbType(
                    ) == QgsWkbTypes.MultiLineString:
                        geom_to_check = QgsLineString()
                        geom_to_check.fromWkt(closest_geom.asWkt())

                    if closest_layer.wkbType() == QgsWkbTypes.Point or closest_layer.wkbType(
                    ) == QgsWkbTypes.MultiPoint:
                        geom_to_check = QgsPoint()
                        geom_to_check.fromWkt(closest_geom.asWkt())

                    point = QgsPoint(point_geom.asPoint().x(), point_geom.asPoint().y())

                    closest_point = QgsGeometryUtils.closestPoint(geom_to_check, point)

                    distance = point.distance(closest_point)

                    if distance < smallest_distance:

                        smallest_distance = distance

                        geom = QgsLineString([point, closest_point])

            feedback.setProgress(int((start_feature_count * closest_geom_count) * total))

            result_feature.setGeometry(geom)

            result_feature.setAttribute(all_fields.lookupField(id_field_name_input_points),
                                        start_feature.attribute(id_field_name_input_points))
            result_feature.setAttribute(all_fields.lookupField(id_field_name),
                                        closest_geom_feature.attribute(id_field_name))
            result_feature.setAttribute(all_fields.lookupField(distance_field.name()),
                                        smallest_distance)

            sink.addFeature(result_feature)

        return {self.OUTPUT: sink_dest}

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
