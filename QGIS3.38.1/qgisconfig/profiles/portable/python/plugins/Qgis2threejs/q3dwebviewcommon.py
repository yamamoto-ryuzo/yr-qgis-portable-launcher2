# -*- coding: utf-8 -*-
# (C) 2023 Minoru Akagi
# SPDX-License-Identifier: GPL-2.0-or-later
# begin: 2023-10-03

from datetime import datetime
import os

from PyQt5.QtCore import Qt, QDir, QEventLoop, QTimer, pyqtSignal, qDebug
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QVBoxLayout

from .conf import DEBUG_MODE

from .tools import hex_color, js_bool, logMessage, pluginDir
from .q3dconst import Script
from .q3dwebbridge import Bridge


class Q3DWebPageCommon:

    ready = pyqtSignal()
    sceneLoaded = pyqtSignal()
    sceneLoadError = pyqtSignal()

    def __init__(self, _=None):

        self.loadedScripts = {}

        if DEBUG_MODE == 2:
            # open log file
            self.logfile = open(pluginDir("q3dview.log"), "w")

    def setup(self, settings, wnd=None, exportMode=False):
        """wnd: Q3DWindow or None (off-screen mode)"""
        self.expSettings = settings
        self.wnd = wnd or DummyWindow()
        self.offScreen = bool(wnd is None)
        self.exportMode = exportMode

        self.bridge = Bridge(self)
        self.bridge.initialized.connect(self.initialized)
        self.bridge.initialized.connect(self.ready)
        self.bridge.sceneLoaded.connect(self.sceneLoaded)
        self.bridge.sceneLoadError.connect(self.sceneLoadError)
        self.bridge.modelDataReady.connect(self.saveModelData)
        self.bridge.imageReady.connect(self.saveImage)
        self.bridge.statusMessage.connect(self.wnd.showStatusMessage)

        self.loadFinished.connect(self.pageLoaded)

    def reload(self):
        self.wnd.showStatusMessage("Initializing preview...")

    def pageLoaded(self, ok):
        self.loadedScripts = {}

        # configuration
        if self.exportMode:
            self.runScript("Q3D.Config.exportMode = true;")

        if self.expSettings.isOrthoCamera():
            self.runScript("Q3D.Config.orthoCamera = true;")

        p = self.expSettings.widgetProperties("NorthArrow")
        if p.get("visible"):
            self.runScript("Q3D.Config.northArrow.enabled = true;")
            self.runScript("Q3D.Config.northArrow.color = {};".format(hex_color(p.get("color", 0), prefix="0x")))

        # navigation widget
        if not self.expSettings.isNavigationEnabled():
            self.runScript("Q3D.Config.navigation.enabled = false;")

        # call init()
        self.runScript("init({}, {}, {})".format(js_bool(self.offScreen), DEBUG_MODE, js_bool(self.isWebEnginePage)))

    def initialized(self):
        # labels
        header = self.expSettings.headerLabel()
        footer = self.expSettings.footerLabel()
        if header or footer:
            self.runScript('setHFLabel(pyData())', data={"Header": header, "Footer": footer})

        self.wnd.showStatusMessage("")

    def runScript(self, string, data=None, message="", sourceID="q3dview.py", callback=None, wait=False):
        if not DEBUG_MODE or message is None:
            return

        self.wnd.printConsoleMessage(message if message else string, sourceID=sourceID)
        qDebug("runScript: {}".format(message if message else string).encode("utf-8"))

        if DEBUG_MODE == 2:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logfile.write("{} runScript: {}\n".format(now, message if message else string))
            self.logfile.flush()

    def loadScriptFile(self, id, force=False):
        """evaluate a script file without using a script tag. script is loaded synchronously"""
        if id in self.loadedScripts and not force:
            return

        filename = pluginDir("js", Script.PATH[id])

        with open(filename, "r", encoding="utf-8") as f:
            script = f.read()

        self.runScript(script, message="{} loaded.".format(os.path.basename(filename)))
        self.loadedScripts[id] = True

    def loadScriptFiles(self, ids, force=False):
        for id in ids:
            self.loadScriptFile(id, force)

    def cameraState(self, flat=False):
        return self.runScript("cameraState({})".format(1 if flat else 0), wait=True)

    def setCameraState(self, state):
        """set camera position and camera target"""
        self.runScript("setCameraState(pyData())", data=state)

    def resetCameraState(self):
        self.runScript("app.controls.reset()")

    def waitForSceneLoaded(self, cancelSignal=None, timeout=None):
        loading = self.runScript("app.loadingManager.isLoading")

        if DEBUG_MODE:
            logMessage("waitForSceneLoaded: loading={}".format(loading), False)

        if not loading:
            return False

        loop = QEventLoop()

        def error():
            loop.exit(1)

        def userCancel():
            loop.exit(2)

        def timeOut():
            loop.exit(3)

        self.sceneLoaded.connect(loop.quit)
        self.sceneLoadError.connect(error)

        if cancelSignal:
            cancelSignal.connect(userCancel)

        if timeout:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(timeOut)
            timer.start(timeout)

        err = loop.exec_()
        if err:
            return {1: "error", 2: "canceled", 3: "timeout"}[err]
        return False

    def saveModelData(self, data, filename):
        try:
            with open(filename, "wb") as f:
                f.write(data)

            logMessage("Successfully saved model data: " + filename, False)
        except Exception as e:
            QMessageBox.warning(self, "Failed to save model data.", str(e))

    def saveImage(self, width, height, image):
        filename, _ = QFileDialog.getSaveFileName(self.wnd, self.tr("Save As"), QDir.homePath(), "PNG files (*.png)")
        if filename:
            image.save(filename)

    def javaScriptConsoleMessage(self, message, lineNumber, sourceID):
        self.wnd.printConsoleMessage(message, lineNumber, sourceID)

        if DEBUG_MODE == 2:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logfile.write("{} {} ({}: {})\n".format(now, message, sourceID, lineNumber))
            self.logfile.flush()


class Q3DWebViewCommon:

    def __init__(self, _=None):
        self.setAcceptDrops(True)

    def setup(self, iface, settings, wnd=None, enabled=True):
        self.iface = iface
        self.wnd = wnd
        self._enabled = enabled     # whether preview is enabled at start

        self._page.ready.connect(self.pageReady)
        self._page.setup(settings, wnd)

    def pageReady(self):
        # start app
        self.runScript("app.start()")

        if self._enabled:
            self.iface.requestBuildScene()
        else:
            self.iface.previewStateChanged.emit(False)

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # logMessage(event.mimeData().formats())
        for url in event.mimeData().urls():
            filename = url.fileName()
            if filename in ("cloud.js", "ept.json"):
                self.wnd.addPointCloudLayer(url.toString())
            else:
                self.runScript("loadModel('{}')".format(url.toString()))

        event.acceptProposedAction()

    def sendData(self, data):
        self._page.sendData(data)

    def runScript(self, string, data=None, message="", sourceID="q3dview.py", callback=None, wait=False):
        return self._page.runScript(string, data, message, sourceID, callback, wait)

    def showJSInfo(self):
        info = self.runScript("app.renderer.info", wait=True)
        QMessageBox.information(self, "three.js Renderer Info", str(info))


class DummyWindow:

    def printConsoleMessage(self, message, lineNumber="", sourceID=""):
        logMessage(message, False)

    def showStatusMessage(self, message, duration=0):
        logMessage(message, False)
