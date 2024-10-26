# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EasyTemplatePrintDialog
                                 A QGIS plugin
 This plugin makes it easy to print using templates and text variables. It provides an easy to use interface/dialog for text input and for rotating and placing your template for printing on map canvas.
version=0.1

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-10-02
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Jesper Jøker Eg - GISkonsulenten
        email                : jesper@giskonsulenten.dk

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

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'EasyTemplatePrint_dialog_base.ui'))


class EasyTemplatePrintDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(EasyTemplatePrintDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
