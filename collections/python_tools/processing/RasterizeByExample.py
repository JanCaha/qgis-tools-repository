from qgis.core import (QgsProcessingAlgorithm, QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer, QgsProcessingParameterField,
                       QgsProcessingParameterRasterDestination, QgsRectangle,
                       QgsCoordinateReferenceSystem, QgsRasterDataProvider, QgsRasterInterface)

from qgis import processing


class RasterizeByExampleAlgorithm(QgsProcessingAlgorithm):

    INPUT = 'INPUT'
    EXAMPLE = 'EXAMPLE'
    OUTPUT = 'OUTPUT'
    FIELD = 'FIELD'

    def createInstance(self):
        return RasterizeByExampleAlgorithm()

    def name(self):
        return 'rasterizevectorbyexampleraster'

    def displayName(self):
        return 'Rasterize vector by example raster'

    def group(self):
        return self.tr('Raster Tools')

    def groupId(self):
        return 'rastetools'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(self.INPUT, 'Vector layer', defaultValue=None))

        self.addParameter(
            QgsProcessingParameterField(self.FIELD, 'Field to rasterize',
                                        QgsProcessingParameterField.Numeric, self.INPUT))

        self.addParameter(
            QgsProcessingParameterRasterLayer(self.EXAMPLE,
                                              'Raster layer to use as example raster',
                                              defaultValue=None))

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT, 'Output raster'))

    def processAlgorithm(self, parameters, context, feedback):

        input = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        raster_template = self.parameterAsRasterLayer(parameters, self.EXAMPLE, context)
        field_name_vectorize = self.parameterAsString(parameters, self.FIELD, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        extent: QgsRectangle = raster_template.extent()

        raster_data_provider: QgsRasterDataProvider = raster_template.dataProvider()
        no_data = raster_data_provider.sourceNoDataValue(1)

        result = processing.run(
            "gdal:rasterize", {
                'INPUT': input,
                'FIELD': field_name_vectorize,
                'BURN': 0,
                'UNITS': 0,
                'WIDTH': raster_data_provider.xSize(),
                'HEIGHT': raster_data_provider.ySize(),
                'EXTENT': extent,
                'NODATA': no_data,
                'OPTIONS': '',
                'DATA_TYPE': 5,
                'INIT': None,
                'INVERT': False,
                'EXTRA': '',
                'OUTPUT': output
            })

        return {self.OUTPUT: result["OUTPUT"]}
