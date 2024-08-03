# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/mmqgis_geometry_convert_form.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mmqgis_geometry_convert_form(object):
    def setupUi(self, mmqgis_geometry_convert_form):
        mmqgis_geometry_convert_form.setObjectName("mmqgis_geometry_convert_form")
        mmqgis_geometry_convert_form.resize(494, 282)
        self.verticalLayout = QtWidgets.QVBoxLayout(mmqgis_geometry_convert_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(mmqgis_geometry_convert_form)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.input_layer_name = QtWidgets.QComboBox(mmqgis_geometry_convert_form)
        self.input_layer_name.setObjectName("input_layer_name")
        self.verticalLayout.addWidget(self.input_layer_name)
        self.old_geometry = QtWidgets.QLabel(mmqgis_geometry_convert_form)
        self.old_geometry.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.old_geometry.setObjectName("old_geometry")
        self.verticalLayout.addWidget(self.old_geometry)
        self.label_3 = QtWidgets.QLabel(mmqgis_geometry_convert_form)
        self.label_3.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.new_geometry = QtWidgets.QComboBox(mmqgis_geometry_convert_form)
        self.new_geometry.setObjectName("new_geometry")
        self.verticalLayout.addWidget(self.new_geometry)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(mmqgis_geometry_convert_form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(mmqgis_geometry_convert_form)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.merge_field = QtWidgets.QComboBox(mmqgis_geometry_convert_form)
        self.merge_field.setObjectName("merge_field")
        self.gridLayout.addWidget(self.merge_field, 1, 0, 1, 1)
        self.attribute_handling = QtWidgets.QComboBox(mmqgis_geometry_convert_form)
        self.attribute_handling.setObjectName("attribute_handling")
        self.gridLayout.addWidget(self.attribute_handling, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label_6 = QtWidgets.QLabel(mmqgis_geometry_convert_form)
        self.label_6.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.output_file_name = gui.QgsFileWidget(mmqgis_geometry_convert_form)
        self.output_file_name.setObjectName("output_file_name")
        self.verticalLayout.addWidget(self.output_file_name)
        self.status = QtWidgets.QProgressBar(mmqgis_geometry_convert_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.buttonBox = QtWidgets.QDialogButtonBox(mmqgis_geometry_convert_form)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(mmqgis_geometry_convert_form)
        self.buttonBox.accepted.connect(mmqgis_geometry_convert_form.accept)
        self.buttonBox.rejected.connect(mmqgis_geometry_convert_form.reject)
        QtCore.QMetaObject.connectSlotsByName(mmqgis_geometry_convert_form)

    def retranslateUi(self, mmqgis_geometry_convert_form):
        _translate = QtCore.QCoreApplication.translate
        mmqgis_geometry_convert_form.setWindowTitle(_translate("mmqgis_geometry_convert_form", "Geometry Convert"))
        self.label.setText(_translate("mmqgis_geometry_convert_form", "Input Layer Name"))
        self.old_geometry.setText(_translate("mmqgis_geometry_convert_form", "Geometry Type"))
        self.label_3.setText(_translate("mmqgis_geometry_convert_form", "New Geometry Type"))
        self.label_5.setText(_translate("mmqgis_geometry_convert_form", "Merge Attribute Handling"))
        self.label_4.setText(_translate("mmqgis_geometry_convert_form", "Merge Field"))
        self.label_6.setText(_translate("mmqgis_geometry_convert_form", "Output FIle Name"))

from qgis import gui
