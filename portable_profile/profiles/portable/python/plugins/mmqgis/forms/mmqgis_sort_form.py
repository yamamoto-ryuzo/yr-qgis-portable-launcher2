# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/mmqgis_sort_form.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mmqgis_sort_form(object):
    def setupUi(self, mmqgis_sort_form):
        mmqgis_sort_form.setObjectName("mmqgis_sort_form")
        mmqgis_sort_form.resize(426, 260)
        self.verticalLayout = QtWidgets.QVBoxLayout(mmqgis_sort_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(mmqgis_sort_form)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.input_layer_name = QtWidgets.QComboBox(mmqgis_sort_form)
        self.input_layer_name.setObjectName("input_layer_name")
        self.verticalLayout.addWidget(self.input_layer_name)
        self.label_2 = QtWidgets.QLabel(mmqgis_sort_form)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.sort_fields = QtWidgets.QComboBox(mmqgis_sort_form)
        self.sort_fields.setObjectName("sort_fields")
        self.verticalLayout.addWidget(self.sort_fields)
        self.label_3 = QtWidgets.QLabel(mmqgis_sort_form)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.sort_direction = QtWidgets.QComboBox(mmqgis_sort_form)
        self.sort_direction.setObjectName("sort_direction")
        self.verticalLayout.addWidget(self.sort_direction)
        self.label_4 = QtWidgets.QLabel(mmqgis_sort_form)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.output_file_name = gui.QgsFileWidget(mmqgis_sort_form)
        self.output_file_name.setObjectName("output_file_name")
        self.verticalLayout.addWidget(self.output_file_name)
        self.status = QtWidgets.QProgressBar(mmqgis_sort_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.buttonBox = QtWidgets.QDialogButtonBox(mmqgis_sort_form)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(mmqgis_sort_form)
        self.buttonBox.accepted.connect(mmqgis_sort_form.accept)
        self.buttonBox.rejected.connect(mmqgis_sort_form.reject)
        QtCore.QMetaObject.connectSlotsByName(mmqgis_sort_form)

    def retranslateUi(self, mmqgis_sort_form):
        _translate = QtCore.QCoreApplication.translate
        mmqgis_sort_form.setWindowTitle(_translate("mmqgis_sort_form", "Sort"))
        self.label.setText(_translate("mmqgis_sort_form", "Source Layer Name"))
        self.label_2.setText(_translate("mmqgis_sort_form", "Sort Attribute"))
        self.label_3.setText(_translate("mmqgis_sort_form", "Direction"))
        self.label_4.setText(_translate("mmqgis_sort_form", "Output File Name"))

from qgis import gui
