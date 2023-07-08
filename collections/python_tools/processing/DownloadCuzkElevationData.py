import urllib
import json
from pathlib import Path
import tempfile
from zipfile import ZipFile

from qgis.core import (QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterEnum,
                       QgsCoordinateReferenceSystem)


class DownloadCuzkElevationData(QgsProcessingAlgorithm):

    EXTENT = 'EXTENT'
    OUTPUT = 'OUTPUT'
    DATA_TYPE = 'DATA_TYPE'

    DATA_TYPES = ["DMP1G", "DMR5G", "DMR4G"]

    def createInstance(self):
        return DownloadCuzkElevationData()

    def name(self):
        return 'downloadcuzkelevationdata'

    def displayName(self):
        return self.tr('Download CUZK Elevation Data')

    def group(self):
        return self.tr('Point Cloud Tools')

    def groupId(self):
        return 'pointcloudtools'

    def shortHelpString(self):
        return self.tr("Download CUZK Elevation Data")

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterEnum(self.DATA_TYPE, "Data To Download", self.DATA_TYPES, allowMultiple=False, defaultValue=0))

        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, self.tr('Extent')))

        self.addParameter(
            QgsProcessingParameterFolderDestination(self.OUTPUT, self.tr('Output destination')))

    def processAlgorithm(self, parameters, context, feedback):

        extent_wgs84 = self.parameterAsExtent(parameters, self.EXTENT, context,
                                              QgsCoordinateReferenceSystem("EPSG:4326"))

        out_folder = self.parameterAsString(parameters, self.OUTPUT, context)

        data_to_download = self.DATA_TYPES[self.parameterAsEnum(parameters, self.DATA_TYPE, context)]

        bbox = f"{extent_wgs84.xMinimum()},{extent_wgs84.yMinimum()},{extent_wgs84.xMaximum()},{extent_wgs84.yMaximum()}"

        url = f"https://atom.cuzk.cz/get.ashx?format=json&title=&theme={data_to_download}-SJTSK&crs=JTSK&bbox={bbox}"

        response = urllib.request.urlopen(url)
        data_json = json.loads(response.read())

        urls = []
        if "entry" in data_json.keys():
            for i in range(len(data_json["entry"])):
                urls.append(data_json["entry"][i]["id"])

        temp_download_dir = Path(tempfile.gettempdir()) / "cuzk_data"
        temp_download_dir.mkdir(parents=True, exist_ok=True)

        for i, link in enumerate(urls):

            if feedback.isCanceled():
                break

            path = Path(link)
            temp_path = temp_download_dir / path.name
            urllib.request.urlretrieve(link, temp_path)

            with ZipFile(temp_path, 'r') as zipFile:
                zipFile.extractall(path=out_folder)

            temp_path.unlink()

            feedback.setProgress((i / len(urls)) * 100)

        return {self.OUTPUT: out_folder}
