import os

from qgis.core import (QgsRasterFileWriter, QgsVectorFileWriter, QgsProcessingException,
                       QgsProcessingParameterDefinition, QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterEnum, QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterString, QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean, QgsProcessingParameterRasterDestination)

from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
from processing.algs.gdal.GdalUtils import GdalUtils


class ClipRasterByExtent(GdalAlgorithm):

    INPUT = 'INPUT'
    CLIP_LAYER = 'CLIP_LAYER'
    OVERCRS = 'OVERCRS'
    NODATA = 'NODATA'
    OPTIONS = 'OPTIONS'
    DATA_TYPE = 'DATA_TYPE'
    EXTRA = 'EXTRA'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def name(self):
        return 'cliprasterbylayer'

    def displayName(self):
        return self.tr('Clip raster by layer')

    def group(self):
        return self.tr('Raster Tools')

    def groupId(self):
        return 'rastetools'

    def commandName(self):
        return "gdalwarp"

    def initAlgorithm(self, config=None):

        self.TYPES = [
            self.tr('Use Input Layer Data Type'), 'Byte', 'Int16', 'UInt16', 'UInt32', 'Int32',
            'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64'
        ]

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT, self.tr('Input layer')))

        self.addParameter(
            QgsProcessingParameterVectorLayer(self.CLIP_LAYER, self.tr('Clipping layer')))

        self.addParameter(
            QgsProcessingParameterBoolean(self.OVERCRS,
                                          self.tr('Override the projection for the output file'),
                                          defaultValue=False))

        self.addParameter(
            QgsProcessingParameterNumber(
                self.NODATA,
                self.tr('Assign a specified nodata value to output bands'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=None,
                optional=True))

        options_param = QgsProcessingParameterString(self.OPTIONS,
                                                     self.tr('Additional creation options'),
                                                     defaultValue='',
                                                     optional=True)

        options_param.setFlags(options_param.flags() |
                               QgsProcessingParameterDefinition.FlagAdvanced)

        options_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.algs.gdal.ui.RasterOptionsWidget.RasterOptionsWidgetWrapper'
            }
        })

        self.addParameter(options_param)

        dataType_param = QgsProcessingParameterEnum(self.DATA_TYPE,
                                                    self.tr('Output data type'),
                                                    self.TYPES,
                                                    allowMultiple=False,
                                                    defaultValue=0)
        dataType_param.setFlags(dataType_param.flags() |
                                QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(dataType_param)

        extra_param = QgsProcessingParameterString(self.EXTRA,
                                                   self.tr('Additional command-line parameters'),
                                                   defaultValue=None,
                                                   optional=True)
        extra_param.setFlags(extra_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(extra_param)

        self.addParameter(
            QgsProcessingParameterRasterDestination(self.OUTPUT, self.tr('Clipped raster')))

    def checkParameterValues(self, parameters, context):

        vector = self.parameterAsVectorLayer(parameters, self.CLIP_LAYER, context)

        vector_crs = vector.crs()

        if not vector_crs.isValid():

            return False, "Vector layer CRS must be valid."

        return super().checkParameterValues(parameters, context)

    def getConsoleCommands(self, parameters, context, feedback, executing=True):

        inLayer = self.parameterAsRasterLayer(parameters, self.INPUT, context)

        if inLayer is None:
            raise QgsProcessingException('Invalid input layer {}'.format(
                parameters[self.INPUT] if self.INPUT in parameters else 'INPUT'))

        data_path, layer_name = self.parameterAsCompatibleSourceLayerPathAndLayerName(
            parameters, self.CLIP_LAYER, context, QgsVectorFileWriter.supportedFormatExtensions())

        override_crs = self.parameterAsBoolean(parameters, self.OVERCRS, context)

        if self.NODATA in parameters and parameters[self.NODATA] is not None:
            nodata = self.parameterAsDouble(parameters, self.NODATA, context)
        else:
            nodata = None

        options = self.parameterAsString(parameters, self.OPTIONS, context)

        out = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

        self.setOutputValue(self.OUTPUT, out)

        arguments = [
            '-cutline',
            data_path,
            '-cl',
            layer_name,
            '-crop_to_cutline',
        ]

        crs = inLayer.crs()

        if override_crs and crs.isValid():
            arguments.append('-s_srs {}'.format(GdalUtils.gdal_crs_string(crs)))

        if nodata is not None:
            arguments.append('-srcnodata {}'.format(nodata))

        data_type = self.parameterAsEnum(parameters, self.DATA_TYPE, context)

        if data_type:
            arguments.append('-ot ' + self.TYPES[data_type])

        arguments.append('-of')
        arguments.append(QgsRasterFileWriter.driverForExtension(os.path.splitext(out)[1]))

        if options:
            arguments.extend(GdalUtils.parseCreationOptions(options))

        if self.EXTRA in parameters and parameters[self.EXTRA] not in (None, ''):
            extra = self.parameterAsString(parameters, self.EXTRA, context)
            arguments.append(extra)

        arguments.append(inLayer.source())
        arguments.append(out)

        return [self.commandName(), GdalUtils.escapeAndJoin(arguments)]
