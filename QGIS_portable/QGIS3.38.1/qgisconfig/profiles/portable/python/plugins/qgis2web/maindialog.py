# -*- coding: utf-8 -*-

# qgis-ol3 Creates OpenLayers map from QGIS layers
# Copyright (C) 2014 Victor Olaya (volayaf@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import os
import sys
from collections import defaultdict, OrderedDict
import webbrowser

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
from qgis.core import (Qgis,
                       QgsWkbTypes,
                       QgsProject,
                       QgsMapLayer,
                       QgsVectorLayer,
                       QgsNetworkAccessManager,
                       QgsMessageLog)

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import (QObject,
                              QSettings,
                              pyqtSignal,
                              pyqtSlot,
                              QUrl,
                              QRect,
                              QByteArray,
                              QEvent,
                              Qt)
from qgis.PyQt.QtGui import (QIcon,
                             QFont)
from qgis.PyQt.QtWidgets import (QAction,
                                 QAbstractItemView,
                                 QDialog,
                                 QHBoxLayout,
                                 QTreeWidgetItem,
                                 QComboBox,
                                 QListWidget,
                                 QCheckBox,
                                 QToolButton,
                                 QWidget,
                                 QTextBrowser)
from qgis.PyQt.uic import loadUiType
try:
    from qgis.PyQt.QtWebKitWidgets import QWebView, QWebInspector, QWebPage
    from qgis.PyQt.QtWebKit import QWebSettings
    webkit_available = True
except ImportError:
    webkit_available = False
    
import traceback

from . import utils
from qgis2web.configparams import (getParams,
                                   specificParams,
                                   specificOptions)
from qgis2web.olwriter import OpenLayersWriter
from qgis2web.leafletWriter import LeafletWriter
#from qgis2web.mapboxWriter import MapboxWriter
from qgis2web.writerRegistry import (WRITER_REGISTRY)
from qgis2web.exporter import (EXPORTER_REGISTRY)
from qgis2web.feedbackDialog import FeedbackDialog

from qgis.gui import QgsColorButton

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FORM_CLASS, _ = loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_maindialog.ui'))

italic_font = QFont()
italic_font.setItalic(True)

class MainDialog(QDialog, FORM_CLASS):
    """The main dialog of QGIS2Web plugin."""
    items = {}

    def __init__(self, iface, parent=None):
        super(MainDialog, self).__init__(parent)
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface

        self.previewUrl = None
        
        # Set All
        self.setAllLayersExportValue = "default"
        self.setAllLayersVisibleValue = "default"
        self.setAllLayersPopupsValue = "default"
        self.setAllLayersClusterValue = "default"
        self.setAllLayersGetFeatureInfo = "default"
        self.setAllLayersEncodeValue = "default"
        self.setAllPopupFieldsComboValue = None
        self.setAllApplyButton.clicked.connect(self.setAllApplyClicked)
        
        self.layer_search_combo = None
        self.layer_filter_select = None
        self.exporter_combo = None

        self.feedback = FeedbackDialog(self)
        self.feedback.setModal(True)
        
        stgs = QSettings()

        self.restoreGeometry(stgs.value("qgis2web/MainDialogGeometry",
                                        QByteArray(), type=QByteArray))

        self.verticalLayout_2.addStretch()
        self.horizontalLayout_6.addStretch()

        if stgs.value("qgis2web/previewOnStartup", Qt.Checked) == Qt.Checked:
            self.previewOnStartup.setCheckState(Qt.Checked)
        else:
            self.previewOnStartup.setCheckState(Qt.Unchecked)
        if stgs.value("qgis2web/closeFeedbackOnSuccess",
                      Qt.Checked) == Qt.Checked:
            self.closeFeedbackOnSuccess.setCheckState(Qt.Checked)
        else:
            self.closeFeedbackOnSuccess.setCheckState(Qt.Unchecked)
        self.previewFeatureLimit.setText(
            stgs.value("qgis2web/previewFeatureLimit", "1000"))

        self.appearanceParams.setSelectionMode(
            QAbstractItemView.SingleSelection)
        self.preview = None
        if webkit_available:
            widget = QWebView()
            self.preview = widget
            try:
                # if os.environ["TRAVIS"]:
                self.preview.setPage(WebPage())
            except Exception:
                print("Failed to set custom webpage")
            webview = self.preview.page()
            webview.setNetworkAccessManager(QgsNetworkAccessManager.instance())
            self.preview.settings().setAttribute(
                QWebSettings.DeveloperExtrasEnabled, True)
            self.preview.settings().setAttribute(
                QWebSettings.DnsPrefetchEnabled, True)
        else:
            widget = QTextBrowser()
            widget.setText(self.tr('Preview is not available since QtWebKit '
                                   'dependency is missing on your system'))
        self.right_layout.insertWidget(0, widget)
        self.populateConfigParams(self)
        self.populate_layers_and_groups(self)
        self.populateSetAllCombo()
        self.populateLayerSearch()
        self.populateAttrFilter()


        writer = WRITER_REGISTRY.createWriterFromProject()
        self.setStateToWriter(writer)

        self.exporter = EXPORTER_REGISTRY.createFromProject()
        self.exporter_combo.setCurrentIndex(
            self.exporter_combo.findText(self.exporter.name()))
        self.exporter_combo.currentIndexChanged.connect(
            self.exporterTypeChanged)

        self.toggleOptions()
        if webkit_available:
            if self.previewOnStartup.checkState() == Qt.Checked:
                self.autoUpdatePreview()
            self.buttonPreview.clicked.connect(self.previewMap)
        else:
            self.buttonPreview.setDisabled(True)
        QgsProject.instance().cleared.connect(self.reject)
        self.layersTree.model().dataChanged.connect(self.populateLayerSearch)
        self.layersTree.model().dataChanged.connect(self.populateAttrFilter)
        self.ol3.clicked.connect(self.changeFormat)
        self.leaflet.clicked.connect(self.changeFormat)
        #self.mapbox.clicked.connect(self.changeFormat)
        self.buttonExport.clicked.connect(self.saveMap)
        
        #helpText = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        #                        "helpFile.md")
        #self.helpField.setSource(QUrl.fromLocalFile(helpText))
        
        if webkit_available:
            QWebSettings.clearMemoryCaches()
            self.webViewWiki = QWebView()
            wikiText = os.path.join(os.path.dirname(os.path.realpath(__file__)), "./docs/index.html")
            self.webViewWiki.load(QUrl.fromLocalFile(wikiText))
            self.helpField.addWidget(self.webViewWiki)
        else:
            self.webViewWiki = QTextBrowser()
            self.webViewWiki.setText(self.tr('Preview is not available since QtWebKit '
                                   'dependency is missing on your system'))
            self.helpField.addWidget(self.webViewWiki)
            
        if webkit_available:
            self.devConsole = QWebInspector(self.preview)
            self.devConsole.setFixedHeight(0)
            self.devConsole.setObjectName("devConsole")
            self.devConsole.setPage(self.preview.page())
            self.devConsole.hide()
            self.right_layout.insertWidget(1, self.devConsole)
        self.filter = devToggleFilter()
        self.filter.devToggle.connect(self.showHideDevConsole)
        self.installEventFilter(self.filter)
        self.setModal(False)

    @pyqtSlot(bool)

    def showHideDevConsole(self, visible):
        self.devConsole.setVisible(visible)

    def changeFormat(self):
        self.autoUpdatePreview()
        self.toggleOptions()

    def exporterTypeChanged(self):
        new_exporter_name = self.exporter_combo.currentText()
        try:
            self.exporter = [
                e for e in EXPORTER_REGISTRY.getExporters()
                if e.name() == new_exporter_name][0]()
        except Exception:
            pass

    def currentMapFormat(self):
        """
        Returns the currently selected map writer type
        """
        return self.getWriterFactory().type()

    def getWriterFactory(self):
        """
        Returns a factory to create the currently selected map writer
        """
        if self.mapFormat.checkedButton() == self.ol3:
            return OpenLayersWriter
        elif self.mapFormat.checkedButton() == self.leaflet:
            return LeafletWriter
        #elif self.mapFormat.checkedButton() == self.mapbox:
            #return MapboxWriter

    def createWriter(self):
        """
        Creates a writer object reflecting the current settings
        in the dialog
        """
        writer = self.getWriterFactory()()
        (writer.layers, writer.groups, writer.popup,
         writer.visible, writer.interactive, writer.json,
         writer.cluster, writer.getFeatureInfo) = self.getLayersAndGroups()
        writer.params = self.getParameters()
        return writer

    def showErrorMessage(self, error):
        """
        Shows an error message in the preview window
        """
        html = "<html>"
        html += "<head></head>"
        html += "<style>body {font-family: sans-serif;}</style>"
        html += "<body><h1>Error</h1>"
        html += "<p>qgis2web produced an error:</p><code>"
        html += error
        html += "</code></body></html>"
        if self.preview:
            self.preview.setHtml(html)

    def showFeedbackMessage(self, title, message):
        """
        Shows a feedback message in the preview window
        """
        html = "<html>"
        html += "<head></head>"
        html += "<style>body {font-family: sans-serif;}</style>"
        html += "<body><h1>{}</h1>".format(title)
        html += "<p>{}</p>".format(message)
        html += "</body></html>"
        if self.preview:
            self.preview.setHtml(html)

    def toggleOptions(self):
        currentWriter = self.getWriterFactory()
        for param, value in specificParams.items():
            treeParam = self.appearanceParams.findItems(
                param, Qt.MatchExactly | Qt.MatchRecursive)[0]
            if currentWriter == OpenLayersWriter:
                if value == "OL3":
                    treeParam.setDisabled(False)
                    if treeParam.combo:
                        treeParam.combo.setEnabled(True)
                else:
                    treeParam.setDisabled(True)
                    if treeParam.combo:
                        treeParam.combo.setEnabled(False)

            else:
                if value == "OL3":
                    treeParam.setDisabled(True)
                    if treeParam.combo:
                        treeParam.combo.setEnabled(False)
                else:
                    treeParam.setDisabled(False)
                    if treeParam.combo:
                        treeParam.combo.setEnabled(True)
        for option, value in specificOptions.items():
            treeOptions = self.layersTree.findItems(option, Qt.MatchExactly |
                                                    Qt.MatchRecursive)
            for treeOption in treeOptions:
                if currentWriter == OpenLayersWriter:
                    if value == "OL3":
                        treeOption.setDisabled(False)
                    else:
                        treeOption.setDisabled(True)
                else:
                    if value == "OL3":
                        treeOption.setDisabled(True)
                    else:
                        treeOption.setDisabled(False)

    def createPreview(self):
        writer = self.createWriter()
        return writer.write(self.iface,
                            dest_folder=utils.tempFolder()).index_file

    def shouldAutoPreview(self):
        """
        Returns a tuple, with a bool for whether the preview should
        automatically be generated, and a string for explanations
        as to why the preview cannot be automatically generated
        """
        writer = self.createWriter()
        total_features = 0
        for layer in writer.layers:
            if isinstance(layer, QgsVectorLayer):
                total_features += layer.featureCount()

        if total_features > int(self.previewFeatureLimit.text()):
            # Too many features => too slow!
            return (False, self.tr('<p>A large number of features are '
                                   'present in the map. Generating the '
                                   'preview may take some time.</p>'
                                   '<p>Click Update Preview to generate the '
                                   'preview anyway.</p>'))

        return (True, None)

    def autoUpdatePreview(self):
        """
        Triggered when a preview will be automatically generated, i.e.
        not as a result of the user manually clicking the
        Update Preview button.
        """
        (auto_preview, message) = self.shouldAutoPreview()
        if not auto_preview:
            self.showFeedbackMessage(self.tr('Preview Map'), message)
        else:
            self.previewMap()

    def previewMap(self):
        preview_file = self.createPreview()
        self.loadPreviewFile(preview_file)

    def saveMap(self):
        writer = self.createWriter()
        write_folder = self.exporter.exportDirectory()
        if not write_folder:
            return

        self.feedback.reset()
        self.feedback.show()
        results = writer.write(self.iface,
                               dest_folder=write_folder,
                               feedback=self.feedback)
        self.feedback.showFeedback('Success')
        if self.closeFeedbackOnSuccess.checkState() == Qt.Checked:
            self.feedback.close()
        result = self.exporter.postProcess(results, feedback=self.feedback)
        if result and (not os.environ.get('CI') and
                       not os.environ.get('TRAVIS')):
            webbrowser.open_new_tab(self.exporter.destinationUrl())
            
    

    def populate_layers_and_groups(self, dlg):
        """Populate layers on QGIS into our layers and group tree view."""
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        self.layers_item = QTreeWidgetItem()
        self.layers_item.setText(0, "Layers and Groups")
        self.layersTree.setColumnCount(3)

        group_dict = {}

        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if (layer.type() != QgsMapLayer.PluginLayer and
                    (layer.type() != QgsMapLayer.VectorLayer or
                     layer.wkbType() != QgsWkbTypes.NoGeometry) and
                    layer.customProperty("ol_layer_type") is None):
                try:
                    layer_parent = tree_layer.parent()
                    if layer_parent.parent() is None:
                        item = TreeLayerItem(self.iface, layer, self.layersTree, dlg)
                        self.layers_item.addChild(item)
                    else:
                        if layer_parent not in group_dict:
                            group_name = layer_parent.name()
                            group_item = TreeGroupItem(group_name, [], self.layersTree)
                            group_dict[layer_parent] = group_item
                        else:
                            group_item = group_dict[layer_parent]
                    
                        layer_item = TreeLayerItem(self.iface, layer, self.layersTree, dlg)
                        group_item.addChild(layer_item)
                        self.layers_item.addChild(group_item)

                except Exception as e:
                    QgsMessageLog.logMessage(traceback.format_exc(), "qgis2web", level=Qgis.Critical)
             
        self.layersTree.addTopLevelItem(self.layers_item)
        self.layersTree.expandAll()
        self.layersTree.resizeColumnToContents(0)
        self.layersTree.resizeColumnToContents(1)
        
        def find_items_recursively(root_item, target_text, found_items=None):
            """Recursively search for items with a specific text."""
            if found_items is None:
                found_items = []

            if root_item.text(0) == target_text:
                found_items.append(root_item)
            # elif root_item.text(0) != "":
                # found_items.append(root_item) 

            for i in range(root_item.childCount()):
                child_item = root_item.child(i)
                find_items_recursively(child_item, target_text, found_items)

            if found_items:
                return found_items
            else:
                return None
                    
        for i in range(self.layers_item.childCount()): 
            layersItem = self.layers_item.child(i)
            if layersItem.checkState(0) != Qt.Checked: 
                layersItem.setExpanded(False)
            for group in range(layersItem.childCount()):
                layersInGroup = layersItem.child(group)
                if layersInGroup.checkState(0) != Qt.Checked: 
                    layersInGroup.setExpanded(False)

            popups_items = find_items_recursively(layersItem, "Popups")
            if popups_items is not None:
                for popups_item in popups_items:
                    widget = self.layersTree.itemWidget(popups_item, 1)
                    if widget:
                        if not widget.isChecked():
                            popups_item.setExpanded(False)
                        else:
                            popups_item.setExpanded(True)
                        for k in range(popups_item.childCount()):
                            popupFieldsItem = popups_item.child(k) 
                            if popupFieldsItem.text(0) == "":
                                popups_item.setHidden(True)

    def populateSetAllCombo(self):
        self.setAllCombo.addItem("Layers to: Export Checked/Unchecked")
        self.setAllCombo.addItem("Layers to: Visible Checked/Unchecked")
        self.setAllCombo.addItem("Layers to: Popups Checked/Unchecked")
        self.setAllCombo.addItem("Layers to: Cluster Checked/Unchecked")
        self.setAllCombo.addItem("Layers to: Encode JSON Checked/Unchecked")
        self.setAllCombo.addItem("Layers to: GetFeatureInfo Checked/Unchecked")
        self.setAllCombo.addItem("Popup fields to: no label")
        self.setAllCombo.addItem("Popup fields to: inline label - always visible")
        self.setAllCombo.addItem("Popup fields to: inline label - visible with data")
        self.setAllCombo.addItem("Popup fields to: hidden field")
        self.setAllCombo.addItem("Popup fields to: header label - always visible")
        self.setAllCombo.addItem("Popup fields to: header label - visible with data")

    def setAllApplyClicked(self):
        try:
            selected_value = self.setAllCombo.currentText()

            # Depending on the value chosen, set dedicated variables present in MainDialog
            if selected_value == "Layers to: Export Checked/Unchecked":
                if self.setAllLayersExportValue == "unchecked" or self.setAllLayersExportValue == "default":
                    self.setAllLayersExportValue = "checked"
                else:
                    self.setAllLayersExportValue = "unchecked"

            if selected_value == "Layers to: Visible Checked/Unchecked":
                if self.setAllLayersVisibleValue == "unchecked" or self.setAllLayersVisibleValue == "default":
                    self.setAllLayersVisibleValue = "checked"
                else:
                    self.setAllLayersVisibleValue = "unchecked"
                    
            if selected_value == "Layers to: Popups Checked/Unchecked":
                if self.setAllLayersPopupsValue == "unchecked" or self.setAllLayersPopupsValue == "default":
                    self.setAllLayersPopupsValue = "checked"
                else:
                    self.setAllLayersPopupsValue = "unchecked"
                    
            if selected_value == "Layers to: Cluster Checked/Unchecked":
                if self.setAllLayersClusterValue == "unchecked" or self.setAllLayersClusterValue == "default":
                    self.setAllLayersClusterValue = "checked"
                else:
                    self.setAllLayersClusterValue = "unchecked"
                    
            if selected_value == "Layers to: Encode JSON Checked/Unchecked":
                if self.setAllLayersEncodeValue == "unchecked" or self.setAllLayersEncodeValue == "default":
                    self.setAllLayersEncodeValue = "checked"
                else:
                    self.setAllLayersEncodeValue = "unchecked"
                    
            if selected_value == "Layers to: GetFeatureInfo Checked/Unchecked":
                if self.setAllLayersGetFeatureInfo == "unchecked" or self.setAllLayersGetFeatureInfo == "default":
                    self.setAllLayersGetFeatureInfo = "checked"
                else:
                    self.setAllLayersGetFeatureInfo = "unchecked"
                    
            if selected_value == "Popup fields to: no label":
                self.setAllPopupFieldsComboValue = "no label"
            if selected_value == "Popup fields to: inline label - always visible":
                self.setAllPopupFieldsComboValue = "inline label - always visible"
            if selected_value == "Popup fields to: inline label - visible with data":
                self.setAllPopupFieldsComboValue = "inline label - visible with data"
            if selected_value == "Popup fields to: hidden field":
                self.setAllPopupFieldsComboValue = "hidden field"
            if selected_value == "Popup fields to: header label - always visible":
                self.setAllPopupFieldsComboValue = "header label - always visible"
            if selected_value == "Popup fields to: header label - visible with data":
                self.setAllPopupFieldsComboValue = "header label - visible with data"

            self.layersTree.clear() # Delete layers tree
            self.populate_layers_and_groups(self) # Populate layers tree configured in TreeLayerItem class

        except Exception as e:
            print("Error in layersSettingsApplyClicked:", str(e))

    def populateLayerSearch(self):
        self.layer_search_combo.clear()
        self.layer_search_combo.addItem("None")
        (layers, groups, popup, visible, interactive,
         json, cluster, getFeatureInfo) = self.getLayersAndGroups()
        for count, layer in enumerate(layers):
            if layer.type() == layer.VectorLayer:
                options = []
                fields = layer.fields()
                for f in fields:
                    fieldIndex = fields.indexFromName(f.name())
                    editorWidget = layer.editorWidgetSetup(fieldIndex).type()
                    if editorWidget == 'Hidden':
                        continue
                    options.append(f.name())
                for option in options:
                    displayStr = layer.name() + ": " + option
                    self.layer_search_combo.insertItem(0, displayStr)
                    sln = utils.safeName(layer.name())
                    self.layer_search_combo.setItemData(
                        self.layer_search_combo.findText(displayStr),
                        sln + "_" + str(count))

    def populateAttrFilter(self):
        self.layer_filter_select.clear()
        (layers, groups, popup, visible, interactive,
         json, cluster, getFeatureInfo) = self.getLayersAndGroups()
        options = []
        for count, layer in enumerate(layers):
            if layer.type() == layer.VectorLayer:
                fields = layer.fields()
                for f in fields:
                    fieldIndex = fields.indexFromName(f.name())
                    editorWidget = layer.editorWidgetSetup(fieldIndex).type()
                    if editorWidget == 'Hidden':
                        continue
                    if utils.boilType(f.typeName()) in ["int", "str", "real",
                                                        "date", "bool",
                                                        "time", "datetime"]:
                        options.append([f.name() + ": " +
                                        utils.boilType(f.typeName()),
                                        layer.name()])
        preCleanOptions = {}
        for entry in options:
            if entry[0] not in list(preCleanOptions.keys()):
                preCleanOptions[entry[0]] = ": " + entry[1]
            else:
                preCleanOptions[entry[0]] = "| ".join(
                    [preCleanOptions[entry[0]], entry[1]])
        options = []
        for key, value in preCleanOptions.items():
            options.append(key + value)
        cleanOptions = list(set(options))
        for option in cleanOptions:
            self.layer_filter_select.insertItem(0, option)

    def configureExporter(self):
        self.exporter.configure()

    def populateConfigParams(self, dlg):
        """ Populates the dialog with option items and widgets """
        self.items = defaultdict(dict)
        tree = dlg.appearanceParams

        configure_export_action = QAction('...', self)
        configure_export_action.triggered.connect(self.configureExporter)

        params = getParams(configure_exporter_action=configure_export_action)
        for group, settings in params.items():
            if group != "Data export":
                item = QTreeWidgetItem()
                item.setText(0, group)
                for param, value in settings.items():
                    subitem = self.createOptionItem(tree_widget=tree,
                                                    parent_item=item,
                                                    parameter=param,
                                                    default_value=value)
                    item.addChild(subitem)
                    self.items[group][param] = subitem
                self.appearanceParams.addTopLevelItem(item)
                #item.sortChildren(0, Qt.AscendingOrder)
        self.appearanceParams.expandAll()
        self.appearanceParams.resizeColumnToContents(0)
        self.appearanceParams.resizeColumnToContents(1)
        self.layer_search_combo.removeItem(1)
        self.layer_filter_select.takeItem(1)

        # configure export params in separate tab
        exportTree = dlg.exportParams
        for group, settings in params.items():
            if group == "Data export":
                item = QTreeWidgetItem()
                item.setText(0, group)
                for param, value in settings.items():
                    subitem = self.createOptionItem(tree_widget=exportTree,
                                                    parent_item=item,
                                                    parameter=param,
                                                    default_value=value)
                    item.addChild(subitem)
                    self.items[group][param] = subitem
                self.exportParams.addTopLevelItem(item)
                item.sortChildren(0, Qt.AscendingOrder)
        self.exportParams.expandAll()
        self.exportParams.resizeColumnToContents(0)
        self.exportParams.resizeColumnToContents(1)

    def createOptionItem(self, tree_widget, parent_item,
                         parameter, default_value):
        """create the tree item corresponding to an option parameter"""
        action = None
        if isinstance(default_value, dict):
            action = default_value['action']
            default_value = default_value['option']

        subitem = TreeSettingItem(parent_item, tree_widget,
                                  parameter, default_value, action)
        if parameter == 'Layer search':
            self.layer_search_combo = subitem.combo
        if parameter == 'Attribute filter':
            self.layer_filter_select = subitem.list
        elif parameter == 'Exporter':
            self.exporter_combo = subitem.combo

        return subitem

    def setStateToWriter(self, writer):
        """
        Sets the dialog state to match the specified writer
        """
        self.selectMapFormat(writer)
        self.setStateToParams(writer.params)

    def setStateToParams(self, params):
        """
        Sets the dialog state to match the specified parameters
        """
        for group, settings in self.items.items():
            for param, item in settings.items():
                value = params[group][param]
                item.setValue(value)

    def selectMapFormat(self, writer):
        """
        Updates dialog state to match the specified writer format
        """
        self.ol3.setChecked(isinstance(writer, OpenLayersWriter))
        self.leaflet.setChecked(isinstance(writer, LeafletWriter))
        #self.mapbox.setChecked(isinstance(writer, MapboxWriter))

    def loadPreviewFile(self, file):
        """
        Loads a web based preview from a local file path
        """
        self.previewUrl = QUrl.fromLocalFile(file)
        if self.preview:
            self.preview.settings().clearMemoryCaches()
            self.preview.setUrl(self.previewUrl)

    def getParameters(self):
        parameters = defaultdict(dict)
        for group, settings in self.items.items():
            for param, item in settings.items():
                if param in ('Widget Icon', 'Widget Background'):
                    parameters[group][param] = item._value.color().name()
                else:
                    parameters[group][param] = item.value()
                    if param == "Layer search":
                        parameters["Appearance"]["Search layer"] = (
                            self.layer_search_combo.itemData(
                                self.layer_search_combo.currentIndex()))
                    if param == "Attribute filter":
                        parameters["Appearance"]["Attribute filter"] = (
                            self.layer_filter_select.selectedItems())

        return parameters

    def saveParameters(self):
        """
        Saves current dialog state to project
        """
        WRITER_REGISTRY.saveWriterToProject(self.createWriter())
        EXPORTER_REGISTRY.writeToProject(self.exporter)

    def getLayersAndGroups(self):
        layers = []
        groups = {}
        popup = []
        visible = []
        interactive = []
        json = []
        cluster = []
        getFeatureInfo = []
        for i in range(self.layers_item.childCount()):
            item = self.layers_item.child(i)
            if isinstance(item, TreeLayerItem):
                if item.checkState(0) == Qt.Checked:
                    layers.append(item.layer)
                    popup.append(item.popup)
                    visible.append(item.visible)
                    interactive.append(item.interactive)
                    json.append(item.json)
                    cluster.append(item.cluster)
                    getFeatureInfo.append(item.getFeatureInfo)
            else:
                group = item.name
                groupLayers = []
                if item.checkState(0) != Qt.Checked:
                    continue
                for allGroups in range(item.childCount()):
                    allLayers = item.child(allGroups)
                    if isinstance(allLayers, TreeLayerItem):
                        if allLayers.checkState(0) == Qt.Checked:
                            groupLayers.append(allLayers.layer)
                            layers.append(allLayers.layer)
                            popup.append(allLayers.popup)
                            visible.append(allLayers.visible)
                            interactive.append(allLayers.interactive)
                            json.append(allLayers.json)
                            cluster.append(allLayers.cluster)
                            getFeatureInfo.append(allLayers.getFeatureInfo)
                groups[group] = groupLayers[::-1]

        layers = layers[::-1]
        groups = groups
        popup = popup[::-1]
        visible = visible[::-1]
        interactive = interactive[::-1]
        json = json[::-1]
        cluster = cluster[::-1]
        getFeatureInfo = getFeatureInfo[::-1]

        return (layers, groups, popup, visible, interactive, json, cluster, getFeatureInfo)

    def reject(self):
        self.saveParameters()
        (layers, groups, popup, visible, interactive,
         json, cluster, getFeatureInfo) = self.getLayersAndGroups()
        try:
            for layer, pop, vis, int in zip(layers, popup, visible,
                                            interactive):
                attrDict = {}
                for attr in pop:
                    attrDict['attr'] = pop[attr]
                    layer.setCustomProperty("qgis2web/popup/" + attr,
                                            pop[attr])
                layer.setCustomProperty("qgis2web/Visible", vis)
                layer.setCustomProperty("qgis2web/Interactive", int)
        except Exception:
            pass

        QSettings().setValue(
            "qgis2web/MainDialogGeometry", self.saveGeometry())

        QSettings().setValue("qgis2web/previewOnStartup",
                             self.previewOnStartup.checkState())
        QSettings().setValue("qgis2web/closeFeedbackOnSuccess",
                             self.closeFeedbackOnSuccess.checkState())
        QSettings().setValue("qgis2web/previewFeatureLimit",
                             self.previewFeatureLimit.text())

        QDialog.close(self)

    def closeEvent(self, event):
        try:
            if self.devConsole or self.devConsole.isVisible() and self.preview:
                del self.devConsole
                del self.preview

            self.reject()
            event.accept()
        except Exception:
            pass


class devToggleFilter(QObject):
    devToggle = pyqtSignal(bool)

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_F12:
                    self.devToggle.emit(not obj.devConsole.isVisible())
                    if obj.devConsole.height() != 0:
                        obj.devConsole.setFixedHeight(0)
                    else:
                        obj.devConsole.setFixedHeight(168)
                    return True
        except Exception:
            pass
        return False


class TreeGroupItem(QTreeWidgetItem):
    groupIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons",
                                   "group.gif"))

    def __init__(self, name, layers, tree):
        QTreeWidgetItem.__init__(self)
        self.layers = layers
        self.name = name
        self.setText(0, name)
        self.setIcon(0, self.groupIcon)
        self.setCheckState(0, Qt.Checked)
        
        # self.visibleItem = QTreeWidgetItem(self)
        # self.visibleCheck = QCheckBox()
        # self.visibleCheck.setChecked(True)
        # self.visibleItem.setText(0, "Visibility")
        # self.addChild(self.visibleItem)
        # tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)
        
        # self.interactiveItem = QTreeWidgetItem(self)
        # self.interactiveCheck = QCheckBox()
        # self.interactiveCheck.setChecked(True)
        # self.interactiveItem.setText(0, "Popups")        
        # self.addChild(self.interactiveItem)
        # tree.setItemWidget(self.interactiveItem, 1, self.interactiveCheck)

    @property
    def visible(self):
        return self.visibleCheck.isChecked()

    @property
    def interactive(self):
        return self.interactiveCheck.isChecked()


class TreeLayerItem(QTreeWidgetItem):
    layerIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons",
                                   "layer.png"))

    def __init__(self, iface, layer, tree, dlg):
        QTreeWidgetItem.__init__(self)
        self.iface = iface
        self.layer = layer
        self.setText(0, layer.name())
        self.setIcon(0, self.layerIcon)
        project = QgsProject.instance()
        if project.layerTreeRoot().findLayer(layer.id()).isVisible():
            self.setCheckState(0, Qt.Checked)
        else:
            self.setCheckState(0, Qt.Unchecked)
        # set all
        if dlg.setAllLayersExportValue == "checked":
            self.setCheckState(0, Qt.Checked)
        if dlg.setAllLayersExportValue == "unchecked":
            self.setCheckState(0, Qt.Unchecked)

        self.visibleItem = QTreeWidgetItem(self)
        self.visibleCheck = QCheckBox()
        vis = layer.customProperty("qgis2web/Visible", True)
        if vis == 0 or str(vis).lower() == "false":
            self.visibleCheck.setChecked(False)
        else:
            self.visibleCheck.setChecked(True)
        # set all
        if dlg.setAllLayersVisibleValue == "checked":
            self.visibleCheck.setChecked(True)
        if dlg.setAllLayersVisibleValue == "unchecked":
            self.visibleCheck.setChecked(False)
        self.visibleItem.setText(0, "Visible")
        self.addChild(self.visibleItem)
        tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)
                
        if layer.type() == layer.VectorLayer:
            if layer.providerType() == 'WFS':
                self.jsonItem = QTreeWidgetItem(self)
                self.jsonCheck = QCheckBox()
                if layer.customProperty("qgis2web/Encode to JSON") == 2:
                    self.jsonCheck.setChecked(True)
                # set all
                if dlg.setAllLayersEncodeValue == "checked":
                    self.jsonCheck.setChecked(True)
                if dlg.setAllLayersEncodeValue == "unchecked":
                    self.jsonCheck.setChecked(False)

                self.jsonItem.setText(0, "Encode to JSON")
                self.jsonCheck.stateChanged.connect(self.changeJSON)
                self.addChild(self.jsonItem)
                tree.setItemWidget(self.jsonItem, 1, self.jsonCheck)
            if layer.geometryType() == QgsWkbTypes.PointGeometry and layer.renderer().type() == 'singleSymbol':
                self.clusterItem = QTreeWidgetItem(self)
                self.clusterCheck = QCheckBox()
                if layer.customProperty("qgis2web/Cluster") == 2:
                    self.clusterCheck.setChecked(True)
                # set all
                if dlg.setAllLayersClusterValue == "checked":
                    self.clusterCheck.setChecked(True)
                if dlg.setAllLayersClusterValue == "unchecked":
                    self.clusterCheck.setChecked(False)

                self.clusterItem.setText(0, "Cluster")
                self.clusterCheck.stateChanged.connect(self.changeCluster)
                self.addChild(self.clusterItem)
                tree.setItemWidget(self.clusterItem, 1, self.clusterCheck)
        else:
            if layer.providerType() == 'wms':
                self.getFeatureInfoItem = QTreeWidgetItem(self)
                self.getFeatureInfoCheck = QCheckBox()
                if layer.customProperty("qgis2web/GetFeatureInfo") == 2:
                    self.getFeatureInfoCheck.setChecked(True)
                # set all
                if dlg.setAllLayersGetFeatureInfo == "checked":
                    self.getFeatureInfoCheck.setChecked(True)
                if dlg.setAllLayersGetFeatureInfo == "unchecked":
                    self.getFeatureInfoCheck.setChecked(False)

                self.getFeatureInfoItem.setText(0, "Enable GetFeatureInfo?")
                self.getFeatureInfoCheck.stateChanged.connect(
                    self.changeGetFeatureInfo)
                self.addChild(self.getFeatureInfoItem)
                tree.setItemWidget(self.getFeatureInfoItem, 1,
                                   self.getFeatureInfoCheck)
                                       
        self.interactiveItem  = QTreeWidgetItem(self)
        self.interactiveCheck = QCheckBox()
        if layer.type() == layer.VectorLayer:
            int = True
            if int == 0 or str(int).lower() == "false":
                self.interactiveCheck.setChecked(False)
            else:
                self.interactiveCheck.setChecked(True)
            # set all
            if dlg.setAllLayersPopupsValue == "checked":
                self.interactiveCheck.setChecked(True)
            if dlg.setAllLayersPopupsValue == "unchecked":
                self.interactiveCheck.setChecked(False)
                
            self.interactiveItem.setText(0, "Popups")
            tree.setItemWidget(self.interactiveItem, 1, self.interactiveCheck)
            self.interactiveCheck.stateChanged.connect(self.togglePopups)  
        
            self.popupItem = QTreeWidgetItem(self.interactiveItem)
            self.popupItem.setText(0, "Popup fields:")
            options = []
            fields = self.layer.fields()
            for f in fields:
                fieldIndex = fields.indexFromName(f.name())
                editorWidget = layer.editorWidgetSetup(fieldIndex).type()
                if editorWidget == 'Hidden':
                    continue
                options.append(f.name())
            if options:
                for option in options:
                    self.attr = QTreeWidgetItem(self.popupItem)
                    self.attrWidget = QComboBox()
                    self.attrWidget.addItem("no label")
                    self.attrWidget.addItem("inline label - always visible")
                    self.attrWidget.addItem("inline label - visible with data")
                    self.attrWidget.addItem("hidden field")
                    self.attrWidget.addItem("header label - always visible")
                    self.attrWidget.addItem("header label - visible with data")
                    custProp = layer.customProperty("qgis2web/popup/" + option)
                    if (custProp != "" and custProp is not None):
                        self.attrWidget.setCurrentIndex(
                            self.attrWidget.findText(
                                layer.customProperty("qgis2web/popup/" + option)))
                    self.attr.setText(0, option)
                    self.attr.setFont(0, italic_font)
                    self.popupItem.addChild(self.attr)
                    tree.setItemWidget(self.attr, 1, self.attrWidget)
                    # set all
                    if dlg.setAllPopupFieldsComboValue is not None:
                        self.attrWidget.setCurrentIndex(
                            self.attrWidget.findText(dlg.setAllPopupFieldsComboValue))
                self.addChild(self.popupItem)
            else:
                self.popupItem.setText(0, "")
        
        self.emptyRow = QTreeWidgetItem()
        self.addChild(self.emptyRow)
        
    @property
    def popup(self):
        popup = []
        self.tree = self.treeWidget()
        for p in range(self.childCount()):
            optionItem = self.child(p)
            if optionItem.text(0) == "Popups":
                for n in range(optionItem.childCount()):
                    popupFieldsItem = optionItem.child(n)
                    for m in range(popupFieldsItem.childCount()):
                        widgetItem = popupFieldsItem.child(m)
                        widgetText = widgetItem.text(0)
                        if widgetText != "":
                            popupVal = self.tree.itemWidget(widgetItem, 1).currentText()
                            pair = (widgetText, popupVal)
                            popup.append(pair)
        popup = OrderedDict(popup)
        return popup

    @property
    def visible(self):
        return self.visibleCheck.isChecked()

    @property
    def interactive(self):
        return self.interactiveCheck.isChecked()

    @property
    def json(self):
        try:
            return self.jsonCheck.isChecked()
        except Exception:
            return False

    @property
    def cluster(self):
        try:
            return self.clusterCheck.isChecked()
        except Exception:
            return False

    @property
    def getFeatureInfo(self):
        try:
            return self.getFeatureInfoCheck.isChecked()
        except Exception:
            return False

    def changeJSON(self, isJSON):
        self.layer.setCustomProperty("qgis2web/Encode to JSON", isJSON)

    def changeCluster(self, isCluster):
        self.layer.setCustomProperty("qgis2web/Cluster", isCluster)

    def changeGetFeatureInfo(self, isGetFeatureInfo):
        self.layer.setCustomProperty("qgis2web/GetFeatureInfo",
                                     isGetFeatureInfo)

    def togglePopups(self, state):
        if state == Qt.Unchecked:
            self.interactiveItem.setExpanded(False)
        else:
            self.interactiveItem.setExpanded(True)
   

class TreeSettingItem(QTreeWidgetItem):

    def __init__(self, parent, tree, name, value, action=None):
        QTreeWidgetItem.__init__(self, parent)
        self.parent = parent
        self.tree = tree
        self.name = name
        self._value = value
        self.combo = None
        self.list = None
        self.setText(0, name)
        widget = None
        if isinstance(value, QgsColorButton):
            widget = value
        elif isinstance(value, bool):
            if value:
                self.setCheckState(1, Qt.Checked)
            else:
                self.setCheckState(1, Qt.Unchecked)
        elif isinstance(value, tuple):
            self.combo = QComboBox()
            self.combo.setSizeAdjustPolicy(0)
            for option in value:
                self.combo.addItem(option)
            widget = self.combo
        elif isinstance(value, list):
            self.list = QListWidget()
            self.list.setSizeAdjustPolicy(0)
            self.list.setSelectionMode(QListWidget.MultiSelection)
            for option in value:
                self.list.addItem(option)
            widget = self.list
        else:
            self.setText(1, unicode(value))

        if action:
            layout = QHBoxLayout()
            layout.setMargin(0)
            if widget:
                layout.addWidget(widget)
            button = QToolButton()
            button.setDefaultAction(action)
            button.setText(action.text())
            layout.addWidget(button)
            layout.addStretch(1)
            widget = QWidget()
            widget.setLayout(layout)

        if widget:
            self.tree.setItemWidget(self, 1, widget)

    def setValue(self, value):
        if isinstance(value, bool):
            if value:
                self.setCheckState(1, Qt.Checked)
            else:
                self.setCheckState(1, Qt.Unchecked)
        elif self.combo:
            index = self.combo.findText(value)
            if index != -1:
                self.combo.setCurrentIndex(index)
        else:
            self.setText(1, str(value))

    def value(self):
        if isinstance(self._value, bool):
            return self.checkState(1) == Qt.Checked
        elif isinstance(self._value, (int, float)):
            return float(self.text(1))
        elif isinstance(self._value, tuple):
            return self.combo.currentText()
        else:
            return self.text(1)

if webkit_available:
    class WebPage(QWebPage):
        """
        Makes it possible to use a Python logger to print javascript
        console messages
        """

        def __init__(self, logger=None, parent=None):
            super(WebPage, self).__init__(parent)

        def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
            if (msg != ("Unable to get image data from canvas because "
                        "the canvas has been tainted by cross-origin data.") and
                    msg != ("Deprecated include of L.Mixin.Events: this property "
                            "will be removed in future releases, please inherit "
                            "from L.Evented instead.") and
                    os.environ.get('CI') and os.environ.get('TRAVIS')):
                raise jsException("JS %s:%d\n%s" % (sourceID, lineNumber, msg),
                                  Exception())


class jsException(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(jsException, self).__init__(message)

        # Now for your custom code...
        self.errors = errors
