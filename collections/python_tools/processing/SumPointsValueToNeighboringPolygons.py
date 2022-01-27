from qgis.PyQt.QtCore import QVariant, QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField, QgsProcessingParameterBoolean, QgsVectorLayer,
                       QgsFeature, QgsProcessingFeatureSourceDefinition)

from qgis import processing


class SumPointsValueToNeighboringPolygonsProcessingAlgorithm(QgsProcessingAlgorithm):

    INPUT_POINTS = 'INPUTPOINTS'
    INPUT_POLYGONS = 'INPUTPOLYGONS'
    FIELD_ADD_TO = 'FIELDADDTO'
    FIELD_VALUE = 'FIELDVALUE'
    ZERO_VALUES = 'ZEROVALUES'

    def createInstance(self):
        return SumPointsValueToNeighboringPolygonsProcessingAlgorithm()

    def name(self):
        return 'sumpointsvaluetoneighboringpolygonsprocessingalgorithm'

    def displayName(self):
        return self.tr('Sum Points Value To Neighboring Polygons')

    def group(self):
        return self.tr('Vector Tools')

    def groupId(self):
        return 'vectortools'

    def shortHelpString(self):
        return self.tr("Sum Points Value To Neighboring Polygons")

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(self.INPUT_POINTS, self.tr('Input point layer'),
                                                [QgsProcessing.TypeVectorPoint]))

        self.addParameter(
            QgsProcessingParameterField(self.FIELD_VALUE, self.tr('Field with values'),
                                        QVariant.Double, self.INPUT_POINTS))

        self.addParameter(
            QgsProcessingParameterFeatureSource(self.INPUT_POLYGONS,
                                                self.tr('Input polygon layer'),
                                                [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(
            QgsProcessingParameterField(self.FIELD_ADD_TO, self.tr('Field to add values to'),
                                        QVariant.Double, self.INPUT_POLYGONS))

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.ZERO_VALUES,
                self.tr("Should the values that are added to be set to 0 before calculation?")))

    def processAlgorithm(self, parameters, context, feedback):

        points: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.INPUT_POINTS,
                                                             context)

        polygons: QgsVectorLayer = self.parameterAsVectorLayer(parameters, self.INPUT_POLYGONS,
                                                               context)

        field_add_to: str = self.parameterAsString(parameters, self.FIELD_ADD_TO, context)

        field_values: str = self.parameterAsString(parameters, self.FIELD_VALUE, context)

        zero_values: bool = self.parameterAsBool(parameters, self.ZERO_VALUES, context)

        total = 100.0 / points.dataProvider().featureCount() if points.dataProvider().featureCount(
        ) else 0

        polygons.startEditing()

        feature_polygon: QgsFeature

        if zero_values:

            for feature_polygon in polygons.getFeatures():

                polygons.changeAttributeValue(feature_polygon.id(),
                                              feature_polygon.fieldNameIndex(field_add_to), 0)

        feature_point: QgsFeature

        for number, feature_point in enumerate(points.getFeatures()):

            points.selectByExpression("$id = {}".format(feature_point.id()))

            value_to_add = feature_point.attribute(field_values)

            processing.run(
                "native:selectbylocation", {
                    'INPUT':
                        polygons,
                    'PREDICATE': [1],
                    'INTERSECT':
                        QgsProcessingFeatureSourceDefinition(points.name(),
                                                             selectedFeaturesOnly=True),
                    'METHOD':
                        0
                })

            processing.run(
                "native:selectbylocation", {
                    'INPUT':
                        polygons,
                    'PREDICATE': [4, 5],
                    'INTERSECT':
                        QgsProcessingFeatureSourceDefinition(polygons.name(),
                                                             selectedFeaturesOnly=True),
                    'METHOD':
                        0
                })

            for feature_polygon in polygons.getSelectedFeatures():

                polygons.changeAttributeValue(
                    feature_polygon.id(), feature_polygon.fieldNameIndex(field_add_to),
                    feature_polygon.attribute(field_add_to) + value_to_add)

            feedback.setProgress(int(number * total))

        polygons.commitChanges()

        return {None}

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
