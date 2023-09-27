import json
import tempfile
import urllib
from pathlib import Path
from zipfile import ZipFile

point_cloud_layer = True
try:
    from qgis.core import QgsPointCloudLayer
except:
    point_cloud_layer = False

import processing
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingOutputPointCloudLayer,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterExtent,
    QgsProcessingParameterFolderDestination,
    QgsProject,
)


class DownloadCuzkElevationData(QgsProcessingAlgorithm):
    EXTENT = "EXTENT"
    OUTPUT = "OUTPUT"
    DATA_TYPE = "DATA_TYPE"
    LOAD_LAYERS = "LOAD_LAYERS"
    VPC_LYR = "VPC_LYR"

    DATA_TYPES = ["DMP1G", "DMR5G", "DMR4G"]

    def createInstance(self):
        return DownloadCuzkElevationData()

    def name(self):
        return "downloadcuzkelevationdata"

    def displayName(self):
        return "Download CUZK Elevation Data"

    def group(self):
        return "Point Cloud Tools"

    def groupId(self):
        return "pointcloudtools"

    def shortHelpString(self):
        return "Download CUZK Elevation Data"

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterEnum(
                self.DATA_TYPE, "Data To Download", self.DATA_TYPES, allowMultiple=False, defaultValue=0
            )
        )

        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, "Extent"))

        self.addParameter(QgsProcessingParameterBoolean(self.LOAD_LAYERS, "Load Layers?", defaultValue=False))

        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT, "Output destination"))

        self.addOutput(QgsProcessingOutputPointCloudLayer(self.VPC_LYR, "Virtual Point Cloud"))

    def processAlgorithm(self, parameters, context, feedback):
        extent_wgs84 = self.parameterAsExtent(
            parameters, self.EXTENT, context, QgsCoordinateReferenceSystem("EPSG:4326")
        )

        out_folder = self.parameterAsString(parameters, self.OUTPUT, context)

        data_to_download = self.DATA_TYPES[self.parameterAsEnum(parameters, self.DATA_TYPE, context)]

        bbox = (
            f"{extent_wgs84.xMinimum()},{extent_wgs84.yMinimum()},{extent_wgs84.xMaximum()},{extent_wgs84.yMaximum()}"
        )

        load_layers = self.parameterAsBool(parameters, self.LOAD_LAYERS, context)

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

            with ZipFile(temp_path, "r") as zipFile:
                zipFile.extractall(path=out_folder)

            temp_path.unlink()

            feedback.setProgress((i / len(urls)) * 100)

        if point_cloud_layer and load_layers:
            # crs = QgsCoordinateReferenceSystem("ESPG:5514")
            path = Path(out_folder)

            result_vpc_path = path / "all.vpc"

            layers = []
            for file in path.iterdir():
                layers.append(file.as_posix())

            result = processing.run(
                "pdal:virtualpointcloud",
                {
                    "LAYERS": layers,
                    "BOUNDARY": False,
                    "STATISTICS": False,
                    "OVERVIEW": False,
                    "OUTPUT": result_vpc_path.as_posix(),  # "TEMPORARY_OUTPUT",
                },
            )

            # result = processing.run(
            #     "pdal:assignprojection",
            #     {
            #         "INPUT": result["OUTPUT"],
            #         "CRS": crs,
            #         "OUTPUT": result_vpc_path.as_posix(),
            #     },
            # )

            return {self.OUTPUT: out_folder, self.VPC_LYR: result["OUTPUT"]}

        return {self.OUTPUT: out_folder}
