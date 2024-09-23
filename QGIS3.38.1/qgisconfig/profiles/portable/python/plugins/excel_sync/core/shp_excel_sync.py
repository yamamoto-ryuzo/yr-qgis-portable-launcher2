# -*- coding: utf-8 -*-
"""
/***************************************************************************
 shp_excel_sync.py
                             -------------------
        begin                : 2016
        git sha              : $Format:%H$
        copyright            : (C) 2016 by OPENGIS.ch
        email                : info@opengis.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from collections import namedtuple

from qgis.core import (
    QgsMessageLog, QgsProject, QgsFeatureRequest, QgsEditFormConfig,
    QgsVectorLayerJoinInfo, QgsExpression, QgsExpressionContext, Qgis)
from qgis.utils import iface

from qgis.PyQt.QtCore import QFileSystemWatcher, QObject, QVariant
from qgis.PyQt.QtWidgets import QMessageBox
from xlrd import open_workbook
import xlwt


MSG_DURATION_SECS = 4


def layer_from_name(layerName):
    # Important: If multiple layers with same name exist, it will return the
    # first one it finds
    for (id, layer) in QgsProject.instance().mapLayers().items():
        if layer.name() == layerName:
            return layer
    return None


def query_layer_for_fids(layerName, fids):
    layer = layer_from_name(layerName)
    freq = QgsFeatureRequest()
    freq.setFilterFids(list(fids))
    return list(layer.getFeatures(freq))


def get_fields(layerName):
    return layer_from_name(layerName).fields()


def field_idx_from_name(layerName, fieldName):
    idx = layer_from_name(layerName).fields().indexFromName(fieldName)
    if idx != -1:
        return idx
    else:
        raise Exception(
            "Layer {} doesn't have field {}".format(layerName, fieldName))


def field_name_from_idx(layerName, idx):
    fields = get_fields(layerName)
    return fields.at(idx).name()


# configurable
logTag = "excel_sync"  # in which tab log messages appear
Settings = namedtuple(
    "Settings",
    "excelName excelSheetName excelKeyName skipLines shpName shpKeyName \
    expressions hideDialog")


def showWarning(msg):
    QMessageBox.information(iface.mainWindow(), 'Warning', msg)


def get_fk_set(layerName, fkName, skipFirst=1, fids=None, useProvider=False):
    """
        skipFirst: number of initial lines to skip (header lines in excel)
    """
    layer = layer_from_name(layerName)
    freq = QgsFeatureRequest()
    if fids is not None:
        freq.setFilterFids(fids)
    if not useProvider:
        feats = [f for f in layer.getFeatures(freq)]
    else:
        feats = [f for f in layer.dataProvider().getFeatures(freq)]
    fkSet = []
    for f in feats[skipFirst:]:
        fk = f.attribute(fkName)
        if fk:  # Skip NULL ids that may be reported from excel files
            fkSet.append(fk)
    return fkSet


def info(msg):
    QgsMessageLog.logMessage(str(msg), logTag, Qgis.Info)


def warn(msg):
    QgsMessageLog.logMessage(str(msg), logTag)
    showWarning(str(msg))


def error(msg):
    QgsMessageLog.logMessage(str(msg), logTag, Qgis.Critical)


def show_message_bar(status_msgs):
    if isinstance(status_msgs, str):
        text = status_msgs
    else:
        text = '<br>'.join(status_msgs)
    iface.messageBar().pushMessage(
        u'Message from {}'.format(logTag), text,
        Qgis.Info, MSG_DURATION_SECS)


class Syncer(QObject):

    def __init__(self, settings):
        QObject.__init__(self)
        self.s = settings
        self.filewatcher = None
        self.excelName = settings.excelName  # the layer name
        self.excelSheetName = settings.excelSheetName
        self.excelKeyName = settings.excelKeyName
        self.excelFkIdx = field_idx_from_name(
            self.excelName, self.excelKeyName)
        self.excelPath = layer_from_name(self.excelName).publicSource().split('|')[0]
        self.excelKeyName = field_name_from_idx(
            self.excelName, self.excelFkIdx)
        # shpfile layer
        self.shpName = settings.shpName
        self.shpKeyName = settings.shpKeyName
        self.shpKeyIdx = field_idx_from_name(self.shpName, self.shpKeyName)
        self.skipLines = settings.skipLines

        layer = layer_from_name(self.shpName)
        editFormConfig = layer.editFormConfig()
        editFormConfig.setSuppress(
            QgsEditFormConfig.SuppressOn if settings.hideDialog else
            QgsEditFormConfig.SuppressOff)
        layer.setEditFormConfig(editFormConfig)

        self.join()
        self.clear_edit_state()
        self.initialSync()

    def join(self):
        # join the shp layer to the excel layer, non cached
        # TODO: Ignore if already joined?
        shpLayer = layer_from_name(self.shpName)
        jinfo = QgsVectorLayerJoinInfo()
        jinfo.setJoinFieldName(self.excelKeyName)
        jinfo.setTargetFieldName(self.shpKeyName)
        jinfo.setJoinLayer(layer_from_name(self.excelName))
        jinfo.setUsingMemoryCache(False)
        jinfo.setPrefix('')
        for jinfo2 in shpLayer.vectorJoins():
            if jinfo2 == jinfo:
                info("Join already exists. Will not create it again")
                return
        info("Adding join between master and slave layers")
        shpLayer.addJoin(jinfo)

    def reload_excel(self):
        layer = layer_from_name(self.excelName)
        fsize = os.stat(self.excelPath).st_size
        info("fsize " + str(fsize))
        if fsize == 0:
            info("File empty. Won't reload yet")
            return
        layer.dataProvider().forceReload()
        show_message_bar("Excel reloaded from disk.")

    def excel_changed(self):
        info("Excel changed on disk - need to sync")
        self.reload_excel()
        self.update_shp_from_excel()

    def get_max_id(self):

        layer = layer_from_name(self.shpName)
        if layer.dataProvider().featureCount() == 0:
            return 0
        maxVal = layer.maximumValue(self.shpKeyIdx)
        if maxVal is None:
            return 0
        elif type(maxVal) == QVariant and maxVal.isNull():
            return 0
        else:
            return maxVal

    def renameIds(self, fidToId):
        layer = layer_from_name(self.shpName)
        layer.startEditing()
        feats = query_layer_for_fids(self.shpName, fidToId.keys())
        for f in feats:
            layer.changeAttributeValue(
                f.id(), self.shpKeyIdx, fidToId[f.id()])
        layer.commitChanges()

    def added_geom(self, layerId, feats):
        info("added feats " + str(feats))
        layer = layer_from_name(self.shpName)
        maxFk = self.get_max_id()
        for i, new_feat in enumerate(
                layer.getFeatures(
                    QgsFeatureRequest().setFilterFids(
                        [f.id() for f in feats]))):
            _id = maxFk + i + 1
            new_feat.setAttribute(self.shpKeyName, _id)
            self.shpAdd.append(new_feat)

    def removed_geom_precommit(self, fids):
        # info("Removed fids"+str(fids))
        fks_to_remove = get_fk_set(
            self.shpName, self.shpKeyName, skipFirst=0, fids=fids,
            useProvider=True)
        self.shpRemove = self.shpRemove.union(fks_to_remove)
        info("feat ids to remove" + str(self.shpRemove))

    def changed_geom(self, layerId, geoms):
        fids = list(geoms.keys())
        feats = query_layer_for_fids(self.shpName, fids)
        fks_to_change = get_fk_set(self.shpName, self.shpKeyName, skipFirst=0, fids=fids)
        self.shpChange = {k: v for (k, v) in zip(fks_to_change, feats)}
        # info("changed"+str(shpChange))

    def get_ignore_indices(self):
        return [field_idx_from_name(
            self.excelName, field) for field in self.s.expressions.keys()]

    def write_feature_to_excel(self, sheet, idx, feat):
        sheet.write(idx, self.excelFkIdx, feat[self.shpKeyName])
        for (fieldName, exp) in self.s.expressions.items():
            fieldIdx = field_idx_from_name(self.excelName, fieldName)
            exp = QgsExpression(exp)
            context = QgsExpressionContext()
            context.setFeature(feat)
            sheet.write(idx, fieldIdx, exp.evaluate(context))

    def write_rowvals_to_excel(self, sheet, idx, vals, ignore=None):
        if ignore is None:
            ignore = []
        for i, v in enumerate(vals):
            if i not in ignore:
                sheet.write(idx, i, v)

    def update_excel_programmatically(self):

        status_msgs = []

        rb = open_workbook(self.excelPath, formatting_info=True)
        r_sheet = rb.sheet_by_name(self.excelSheetName)  # read only copy
        wb = xlwt.Workbook()
        w_sheet = wb.add_sheet(self.excelSheetName, cell_overwrite_ok=True)
        write_idx = 0

        for row_index in range(r_sheet.nrows):
            if row_index < self.skipLines:  # copy header and/or dummy lines
                vals = r_sheet.row_values(row_index)
                self.write_rowvals_to_excel(w_sheet, write_idx, vals)
                write_idx += 1
                continue
            # print(r_sheet.cell(row_index,1).value)
            fk = r_sheet.cell(row_index, self.excelFkIdx).value
            if fk in self.shpRemove:
                status_msgs.append("Removing feature with id {}".format(fk))
                continue
            if fk in self.shpChange.keys():
                status_msgs.append(
                    "Syncing geometry change to feature with id {}".format(fk))
                shpf = self.shpChange[fk]
                self.write_feature_to_excel(w_sheet, write_idx, shpf)
                vals = r_sheet.row_values(row_index)
                self.write_rowvals_to_excel(w_sheet, write_idx, vals,
                                            ignore=self.get_ignore_indices())
            else:  # else just copy the row
                vals = r_sheet.row_values(row_index)
                self.write_rowvals_to_excel(w_sheet, write_idx, vals)

            write_idx += 1

        fidToId = {}
        for shpf in self.shpAdd:
            status_msgs.append(
                "Adding new feature with id {}".format(
                    shpf.attribute(self.shpKeyName)))
            fidToId[shpf.id()] = shpf.attribute(self.shpKeyName)
            self.write_feature_to_excel(w_sheet, write_idx, shpf)
            write_idx += 1

        info('\n'.join(status_msgs))
        wb.save(self.excelPath)
        if status_msgs:
            show_message_bar(status_msgs)
        else:
            show_message_bar("No changes to shapefile to sync.")
        return fidToId

    def clear_edit_state(self):
        info("Clearing edit state")
        self.shpAdd = []
        self.shpChange = {}
        self.shpRemove = set([])

    def update_excel_from_shp(self):
        info("Will now update excel from edited shapefile")
        info("changing:" + str(self.shpChange))
        info("adding:" + str(self.shpAdd))
        info("removing" + str(self.shpRemove))
        self.deactivateFileWatcher()  # so that we don't sync back and forth
        fidToId = self.update_excel_programmatically()
        # need to alter the ids(not fids) of the new features after, because
        # editing the features after they've been commited doesn't work
        if fidToId:
            self.deactivateShpConnections()
            self.renameIds(fidToId)
            self.activateShpConnections()
        self.reload_excel()
        self.activateFileWatcher()
        self.clear_edit_state()

    def updateShpLayer(self, fksToRemove):
        if not fksToRemove:
            return

        prompt_msg = ("Attempt to synchronize between Excel and Shapefile. "
                      "Shapefile has features with ids: ({}) that don't "
                      "appear in the Excel. Delete those features from the "
                      "shapefile? ").format(
                          ','.join([str(fk) for fk in fksToRemove]))
        reply = QMessageBox.question(
            iface.mainWindow(), 'Message',
            prompt_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            layer = layer_from_name(self.shpName)
            feats = [f for f in layer.getFeatures()]
            layer.startEditing()
            for f in feats:
                if f.attribute(self.shpKeyName) in fksToRemove:
                    layer.deleteFeature(f.id())
            layer.commitChanges()
        else:
            return

    def update_shp_from_excel(self):
        excelFks = set(get_fk_set(
            self.excelName, self.excelKeyName, skipFirst=self.skipLines))
        shpFks = set(get_fk_set(self.shpName, self.shpKeyName, skipFirst=0))
        # TODO also special warning if shp layer is in edit mode
        info("Keys in excel" + str(excelFks))
        info("Keys in shp" + str(shpFks))
        if shpFks == excelFks:
            info("Excel and Shp layer have the same rows. No update necessary")
            return
        inShpButNotInExcel = shpFks - excelFks
        inExcelButNotInShp = excelFks - shpFks
        if inExcelButNotInShp:
            warn(("There are rows in the excel file with no matching "
                  "geometry {}.").format(
                      inExcelButNotInShp))
            # FIXME: if those are added later then they will be added twice..
            # However, having an autoincrement id suggests features would be
            # added first from shp only?

        if inShpButNotInExcel:
            self.updateShpLayer(inShpButNotInExcel)

    def activateFileWatcher(self):
        self.filewatcher = QFileSystemWatcher([self.excelPath])
        self.filewatcher.fileChanged.connect(self.excel_changed)

    def deactivateFileWatcher(self):
        self.filewatcher.fileChanged.disconnect(self.excel_changed)
        self.filewatcher.removePath(self.excelPath)

    def activateShpConnections(self):
        shpLayer = layer_from_name(self.shpName)
        shpLayer.committedFeaturesAdded.connect(self.added_geom)
        shpLayer.featuresDeleted.connect(self.removed_geom_precommit)
        shpLayer.committedGeometriesChanges.connect(self.changed_geom)
        shpLayer.editingStopped.connect(self.update_excel_from_shp)
        shpLayer.beforeRollBack.connect(self.clear_edit_state)

    def deactivateShpConnections(self):
        shpLayer = layer_from_name(self.shpName)
        shpLayer.committedFeaturesAdded.disconnect(self.added_geom)
        # shpLayer.featureAdded.disconnect(added_geom_precommit)
        shpLayer.featuresDeleted.disconnect(self.removed_geom_precommit)
        shpLayer.committedGeometriesChanges.disconnect(self.changed_geom)
        shpLayer.editingStopped.disconnect(self.update_excel_from_shp)
        shpLayer.beforeRollBack.disconnect(self.clear_edit_state)

    def initialSync(self):
        info("Initial Syncing excel to shp")
        self.update_shp_from_excel()
        self.activateFileWatcher()
        self.activateShpConnections()

    def __del__(self):
        self.deactivateFileWatcher()
        self.deactivateShpConnections()
