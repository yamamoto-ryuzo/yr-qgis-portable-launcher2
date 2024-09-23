# -*- coding: utf-8 -*-
# (C) 2016 Minoru Akagi
# SPDX-License-Identifier: GPL-2.0-or-later
# begin: 2016-02-10

import time
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot, qDebug
from qgis.core import QgsApplication

from .conf import DEBUG_MODE
from .build import ThreeJSBuilder
from .exportsettings import ExportSettings
from .q3dcore import Layer
from .q3dconst import LayerType, Script
from .tools import hex_color, js_bool, logMessage


class Q3DControllerInterface(QObject):

    # signals
    dataReady = pyqtSignal(dict)                 # data
    scriptReady = pyqtSignal(str, object, str)   # script, data, msg_shown_in_log_panel
    messageReady = pyqtSignal(str, int, bool)    # message, timeout, show_in_msg_bar
    progressUpdated = pyqtSignal(int, str)
    loadScriptsRequest = pyqtSignal(list, bool)  # list of script ID, force (if False, do not load a script that is already loaded)
    readyToQuit = pyqtSignal()

    def __init__(self, controller=None):
        super().__init__(parent=controller)

        self.controller = controller
        self.iface = None

    def connectToIface(self, iface):
        """iface: web view side interface (Q3DInterface or its subclass)"""
        self.iface = iface

        self.dataReady.connect(iface.loadJSONObject)
        self.scriptReady.connect(iface.runScript)
        self.loadScriptsRequest.connect(iface.loadScriptFiles)
        self.messageReady.connect(iface.showMessage)
        self.progressUpdated.connect(iface.progress)

        if hasattr(iface, "abortRequest"):
            iface.abortRequest.connect(self.controller.abort)
            iface.buildSceneRequest.connect(self.controller.requestBuildScene)
            iface.buildLayerRequest.connect(self.controller.requestBuildLayer)
            iface.updateWidgetRequest.connect(self.controller.requestUpdateWidget)
            iface.runScriptRequest.connect(self.controller.requestRunScript)

            iface.updateExportSettingsRequest.connect(self.controller.updateExportSettings)
            iface.cameraChanged.connect(self.controller.switchCamera)
            iface.navStateChanged.connect(self.controller.setNavigationEnabled)
            iface.previewStateChanged.connect(self.controller.setPreviewEnabled)
            iface.layerAdded.connect(self.controller.addLayer)
            iface.layerRemoved.connect(self.controller.removeLayer)

    def disconnectFromIface(self):
        self.dataReady.disconnect(self.iface.loadJSONObject)
        self.scriptReady.disconnect(self.iface.runScript)
        self.loadScriptsRequest.disconnect(self.iface.loadScriptFiles)
        self.messageReady.disconnect(self.iface.showMessage)
        self.progressUpdated.disconnect(self.iface.progress)

        if hasattr(self.iface, "abortRequest"):
            self.iface.abortRequest.disconnect(self.controller.abort)
            self.iface.buildSceneRequest.disconnect(self.controller.requestBuildScene)
            self.iface.buildLayerRequest.disconnect(self.controller.requestBuildLayer)
            self.iface.updateWidgetRequest.disconnect(self.controller.requestUpdateWidget)
            self.iface.runScriptRequest.disconnect(self.controller.requestRunScript)

            self.iface.updateExportSettingsRequest.disconnect(self.controller.updateExportSettings)
            self.iface.cameraChanged.disconnect(self.controller.switchCamera)
            self.iface.navStateChanged.disconnect(self.controller.setNavigationEnabled)
            self.iface.previewStateChanged.disconnect(self.controller.setPreviewEnabled)
            self.iface.layerAdded.disconnect(self.controller.addLayer)
            self.iface.layerRemoved.disconnect(self.controller.removeLayer)

        self.iface = None

    def loadJSONObject(self, obj):
        self.dataReady.emit(obj)

    def runScript(self, string, data=None, msg=""):
        self.scriptReady.emit(string, data, msg)

    def showMessage(self, msg, timeout=0):
        """show message in status bar. timeout: in milli-seconds"""
        self.messageReady.emit(msg, timeout, False)

    def clearMessage(self):
        """clear message in status bar"""
        self.messageReady.emit("", 0, False)

    def showMessageBar(self, msg="", timeout=10):
        """show message bar (error message only). timeout: in seconds"""
        msg = msg or "An error has occurred. See log messages panel for details."
        self.messageReady.emit(msg, timeout, True)

    def progress(self, percentage=100, msg=""):
        self.progressUpdated.emit(int(percentage), msg)

    def loadScriptFile(self, id, force=False):
        self.loadScriptsRequest.emit([id], force)

    def loadScriptFiles(self, ids, force=False):
        self.loadScriptsRequest.emit(ids, force)


class Q3DController(QObject):

    # requests
    BUILD_SCENE_ALL = 1   # build scene
    BUILD_SCENE = 2       # build scene, but do not update background color, coordinates display mode and so on
    RELOAD_PAGE = 3

    def __init__(self, settings=None, thread=None, parent=None):
        super().__init__(parent)

        if settings is None:
            defaultSettings = {}
            settings = ExportSettings()
            settings.loadSettings(defaultSettings)

            err_msg = settings.checkValidity()
            if err_msg:
                logMessage("Invalid settings: " + err_msg)

        self.settings = settings
        self.builder = ThreeJSBuilder(settings)

        self.iface = Q3DControllerInterface(self)
        self.enabled = True
        self.aborted = False  # layer export aborted
        self.buildingLayer = None
        self.mapCanvas = None

        self.requestQueue = []
        self.timer = QTimer(self)
        self.timer.setInterval(1)
        self.timer.setSingleShot(True)

        # move to worker thread
        if thread:
            self.moveToThread(thread)

        self.timer.timeout.connect(self._processRequests)

    def __del__(self):
        self.timer.stop()

    def connectToIface(self, iface):
        """iface: Q3DInterface or its subclass"""
        self.iface.connectToIface(iface)

    def disconnectFromIface(self):
        self.iface.disconnectFromIface()
        # self.iface = Mock()

    def connectToMapCanvas(self, canvas):
        self.mapCanvas = canvas
        self.mapCanvas.renderComplete.connect(self._requestBuildScene)
        # self.mapCanvas.extentsChanged.connect(self.updateExtent)

    def disconnectFromMapCanvas(self):
        if self.mapCanvas:
            self.mapCanvas.renderComplete.disconnect(self._requestBuildScene)
            # self.mapCanvas.extentsChanged.disconnect(self.updateExtent)
            self.mapCanvas = None

    def buildScene(self, update_scene_opts=True, build_layers=True, update_extent=True):
        if self.buildingLayer:
            logMessage("Previous building is still in progress. Cannot start to build scene.")
            return False

        self.aborted = False

        self.iface.progress(0, "Building scene")

        if update_extent and self.mapCanvas:
            self.builder.settings.setMapSettings(self.mapCanvas.mapSettings())

        self.iface.loadJSONObject(self.builder.buildScene(False))

        if update_scene_opts:
            sp = self.settings.sceneProperties()

            # outline effect
            self.iface.runScript("setOutlineEffectEnabled({})".format(js_bool(sp.get("checkBox_Outline"))))

            # update background color
            params = "{0}, 1".format(hex_color(sp.get("colorButton_Color", 0), prefix="0x")) if sp.get("radioButton_Color") else "0, 0"
            self.iface.runScript("setBackgroundColor({0})".format(params))

            # coordinate display
            self.iface.runScript("Q3D.Config.coord.visible = {};".format(js_bool(self.settings.coordDisplay())))

            latlon = self.settings.isCoordLatLon()
            self.iface.runScript("Q3D.Config.coord.latlon = {};".format(js_bool(latlon)))
            if latlon:
                self.iface.loadScriptFile(Script.PROJ4)

        if build_layers:
            self.buildLayers()

        self.iface.progress()
        self.iface.clearMessage()
        return not self.aborted

    def buildLayers(self):
        self.aborted = False
        self.iface.runScript('loadStart("LYRS", true)')

        ret = True
        layers = self.settings.layers()
        for layer in sorted(layers, key=lambda lyr: lyr.type):
            if layer.visible:
                if not self._buildLayer(layer) or self.aborted:
                    ret = False
                    break

        self.iface.runScript('loadEnd("LYRS")')
        return ret

    def buildLayer(self, layer):
        self.aborted = False
        if isinstance(layer, dict):
            layer = Layer.fromDict(layer)

        if self.buildingLayer:
            logMessage('Previous building is still in progress. Cannot start building layer "{}".'.format(layer.name))
            return False

        ret = self._buildLayer(layer)

        self.iface.progress()
        self.iface.clearMessage()

        if ret and len(self.settings.layersToExport()) == 1:
            self.iface.runScript("adjustCameraPos()")

        return ret

    def _buildLayer(self, layer):
        self.buildingLayer = layer

        pmsg = "Building {0}...".format(layer.name)
        self.iface.progress(0, pmsg)

        if layer.type == LayerType.POINT and layer.properties.get("comboBox_ObjectType") == "3D Model":
            self.iface.loadScriptFiles([Script.COLLADALOADER,
                                        Script.GLTFLOADER])

        elif layer.type == LayerType.LINESTRING and layer.properties.get("comboBox_ObjectType") == "Thick Line":
            self.iface.loadScriptFiles([Script.MESHLINE])

        elif layer.type == LayerType.POINTCLOUD:
            self.iface.loadScriptFiles([Script.FETCH,
                                        Script.POTREE,
                                        Script.PCLAYER])

        t0 = t4 = time.time()
        dlist = []
        i = 0
        for builder in self.builder.layerBuilders(layer):
            self.iface.progress(i / (i + 4) * 100, pmsg)
            if self.aborted:
                logMessage("***** layer building aborted *****", False)
                self.buildingLayer = None
                return False

            t1 = time.time()
            obj = builder.build()
            t2 = time.time()

            if obj:
                self.iface.loadJSONObject(obj)

            QgsApplication.processEvents()      # NOTE: process events only for the calling thread
            i += 1

            t3 = time.time()
            dlist.append([t1 - t4, t2 - t1, t3 - t2])
            t4 = t3

        if DEBUG_MODE:
            dlist = "\n".join([" {:.3f} {:.3f} {:.3f}".format(d[0], d[1], d[2]) for d in dlist])
            qDebug("{0} layer updated: {1:.3f}s\n{2}\n".format(layer.name,
                                                               time.time() - t0,
                                                               dlist).encode("utf-8"))
        self.buildingLayer = None
        return True

    def hideLayer(self, layer):
        """hide layer and remove all objects from the layer"""
        self.iface.runScript('hideLayer("{}", true)'.format(layer.jsLayerId))

    def hideAllLayers(self):
        """hide all layers and remove all objects from the layers"""
        self.iface.runScript("hideAllLayers(true)")

    def processRequests(self):
        self.timer.stop()
        if self.requestQueue:
            self.timer.start()

    def _processRequests(self):
        if not self.enabled or self.buildingLayer or not self.requestQueue:
            return

        try:
            if self.BUILD_SCENE_ALL in self.requestQueue:
                self.requestQueue.clear()
                self.buildScene()

            elif self.BUILD_SCENE in self.requestQueue:
                self.requestQueue.clear()
                self.buildScene(update_scene_opts=False)

            elif self.RELOAD_PAGE in self.requestQueue:
                self.requestQueue.clear()
                self.iface.runScript("location.reload()")

            else:
                item = self.requestQueue.pop(0)
                if isinstance(item, Layer):
                    if item.visible:
                        self.buildLayer(item)
                    else:
                        self.hideLayer(item)
                else:
                    self.iface.runScript(item.get("string"), item.get("data"))

        except Exception as e:
            import traceback
            logMessage(traceback.format_exc())

            self.iface.showMessageBar()

        self.processRequests()

    @pyqtSlot(bool)
    def abort(self, clear_queue=True):
        if clear_queue:
            self.requestQueue.clear()

        if not self.aborted:
            self.aborted = True
            self.iface.showMessage("Aborting processing...")

    @pyqtSlot()
    def quit(self):
        self.abort()
        self.iface.readyToQuit.emit()

    @pyqtSlot(object, bool, bool)
    def requestBuildScene(self, properties=None, update_all=True, reload=False):
        if DEBUG_MODE:
            logMessage("Scene update requested: {}".format(properties), False)

        if properties:
            self.settings.setSceneProperties(properties)

        if reload:
            r = self.RELOAD_PAGE
        elif update_all:
            r = self.BUILD_SCENE_ALL
        else:
            r = self.BUILD_SCENE

        self.requestQueue.append(r)

        if self.buildingLayer:
            self.abort(clear_queue=False)
        else:
            self.processRequests()

    @pyqtSlot(Layer)
    def requestBuildLayer(self, layer):
        if DEBUG_MODE:
            logMessage("Layer update for {} requested ({}).".format(layer.layerId, "visible" if layer.visible else "hidden"), False)

        # update layer properties and layer state in worker side export settings
        lyr = self.settings.getLayer(layer.layerId)
        if not lyr:
            return
        layer.copyTo(lyr)

        q = []
        for i in self.requestQueue:
            if isinstance(i, Layer) and i.layerId == layer.layerId:
                if not i.opt.onlyMaterial:
                    layer.opt.onlyMaterial = False
            else:
                q.append(i)

        self.requestQueue = q

        if self.buildingLayer and self.buildingLayer.layerId == layer.layerId:
            self.abort(clear_queue=False)
            if not self.buildingLayer.opt.onlyMaterial:
                layer.opt.onlyMaterial = False

        if layer.visible:
            self.requestQueue.append(layer)

            if not self.buildingLayer:
                self.processRequests()
        else:
            # immediately hide layer without adding layer to queue
            self.hideLayer(layer)

    @pyqtSlot(str, dict)
    def requestUpdateWidget(self, name, properties):
        if name == "NorthArrow":
            self.iface.runScript("setNorthArrowColor({0})".format(properties.get("color", 0)))
            self.iface.runScript("setNorthArrowVisible({0})".format(js_bool(properties.get("visible"))))

        elif name == "Label":
            self.iface.runScript('setHFLabel(pyData());', data=properties)

        else:
            return

        self.settings.setWidgetProperties(name, properties)

    @pyqtSlot(str, object)
    def requestRunScript(self, string, data=None):
        self.requestQueue.append({"string": string, "data": data})

        if not self.buildingLayer:
            self.processRequests()

    @pyqtSlot(ExportSettings)
    def updateExportSettings(self, settings):
        if self.buildingLayer:
            self.abort()

        self.hideAllLayers()
        settings.copyTo(self.settings)

        # reload page
        self.iface.runScript("location.reload()")

    @pyqtSlot(bool)
    def switchCamera(self, is_ortho=False):
        self.settings.setCamera(is_ortho)
        self.iface.runScript("switchCamera({0})".format(js_bool(is_ortho)))

    @pyqtSlot(bool)
    def setNavigationEnabled(self, enabled):
        self.settings.setNavigationEnabled(enabled)
        self.iface.runScript("setNavigationEnabled({0})".format(js_bool(enabled)))

    @pyqtSlot(bool)
    def setPreviewEnabled(self, enabled):
        self.enabled = enabled
        self.iface.runScript("setPreviewEnabled({})".format(js_bool(enabled)))

        if enabled:
            self.buildScene()
        else:
            self.abort()

    @pyqtSlot(Layer)
    def addLayer(self, layer):
        layer = self.settings.addLayer(layer)
        self.buildLayer(layer)

    @pyqtSlot(str)
    def removeLayer(self, layerId):
        layer = self.settings.getLayer(layerId)
        if layer:
            self.hideLayer(layer)
            self.settings.removeLayer(layerId)

    # @pyqtSlot(QPainter)
    def _requestBuildScene(self, _=None):
        self.requestBuildScene(update_all=False)

    # @pyqtSlot()
    # def updateExtent(self):
    #     if self.settings.sceneProperties().get("radioButton_FixedExtent"):
    #         return
    #     self.requestQueue.clear()
    #     if self.buildingLayer:
    #         self.abort(clear_queue=False)


class Mock:

    def __init__(self, *args, **kwargs):
        pass

    def __getattr__(self, attr):
        if DEBUG_MODE:
            logMessage("Mock: {}".format(attr), False)
        return Mock

    def __bool__(self):
        return False
