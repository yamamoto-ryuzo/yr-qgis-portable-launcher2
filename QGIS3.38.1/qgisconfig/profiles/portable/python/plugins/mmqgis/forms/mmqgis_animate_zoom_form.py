# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'forms/mmqgis_animate_zoom_form.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mmqgis_animate_zoom_form(object):
    def setupUi(self, mmqgis_animate_zoom_form):
        mmqgis_animate_zoom_form.setObjectName("mmqgis_animate_zoom_form")
        mmqgis_animate_zoom_form.setWindowModality(QtCore.Qt.ApplicationModal)
        mmqgis_animate_zoom_form.setEnabled(True)
        mmqgis_animate_zoom_form.resize(504, 358)
        mmqgis_animate_zoom_form.setMouseTracking(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(mmqgis_animate_zoom_form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_5 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_5.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.print_layout = QtWidgets.QComboBox(mmqgis_animate_zoom_form)
        self.print_layout.setObjectName("print_layout")
        self.verticalLayout.addWidget(self.print_layout)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.end_zoom = QtWidgets.QComboBox(mmqgis_animate_zoom_form)
        self.end_zoom.setObjectName("end_zoom")
        self.gridLayout.addWidget(self.end_zoom, 5, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.start_zoom = QtWidgets.QComboBox(mmqgis_animate_zoom_form)
        self.start_zoom.setObjectName("start_zoom")
        self.gridLayout.addWidget(self.start_zoom, 5, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_6.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 4, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_4.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.start_long = QtWidgets.QLineEdit(mmqgis_animate_zoom_form)
        self.start_long.setObjectName("start_long")
        self.gridLayout.addWidget(self.start_long, 3, 0, 1, 1)
        self.start_lat = QtWidgets.QLineEdit(mmqgis_animate_zoom_form)
        self.start_lat.setObjectName("start_lat")
        self.gridLayout.addWidget(self.start_lat, 1, 0, 1, 1)
        self.end_lat = QtWidgets.QLineEdit(mmqgis_animate_zoom_form)
        self.end_lat.setObjectName("end_lat")
        self.gridLayout.addWidget(self.end_lat, 1, 1, 1, 1)
        self.end_long = QtWidgets.QLineEdit(mmqgis_animate_zoom_form)
        self.end_long.setObjectName("end_long")
        self.gridLayout.addWidget(self.end_long, 3, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label_7 = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.frame_count = QtWidgets.QLineEdit(mmqgis_animate_zoom_form)
        self.frame_count.setReadOnly(False)
        self.frame_count.setObjectName("frame_count")
        self.verticalLayout.addWidget(self.frame_count)
        self.label = QtWidgets.QLabel(mmqgis_animate_zoom_form)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.frame_directory = gui.QgsFileWidget(mmqgis_animate_zoom_form)
        self.frame_directory.setObjectName("frame_directory")
        self.verticalLayout.addWidget(self.frame_directory)
        self.status = QtWidgets.QProgressBar(mmqgis_animate_zoom_form)
        self.status.setProperty("value", 24)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.buttonBox = QtWidgets.QDialogButtonBox(mmqgis_animate_zoom_form)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(mmqgis_animate_zoom_form)
        self.buttonBox.accepted.connect(mmqgis_animate_zoom_form.accept)
        self.buttonBox.rejected.connect(mmqgis_animate_zoom_form.reject)
        QtCore.QMetaObject.connectSlotsByName(mmqgis_animate_zoom_form)

    def retranslateUi(self, mmqgis_animate_zoom_form):
        _translate = QtCore.QCoreApplication.translate
        mmqgis_animate_zoom_form.setWindowTitle(_translate("mmqgis_animate_zoom_form", "Animate Zoom"))
        self.label_5.setText(_translate("mmqgis_animate_zoom_form", "Print Layout"))
        self.label_2.setText(_translate("mmqgis_animate_zoom_form", "Start Zoom Level"))
        self.label_6.setText(_translate("mmqgis_animate_zoom_form", "End Latitude"))
        self.label_9.setText(_translate("mmqgis_animate_zoom_form", "End Zoom Level"))
        self.label_3.setText(_translate("mmqgis_animate_zoom_form", "Start Longitude"))
        self.label_4.setText(_translate("mmqgis_animate_zoom_form", "Start Latitude"))
        self.label_8.setText(_translate("mmqgis_animate_zoom_form", "End Longitude"))
        self.label_7.setText(_translate("mmqgis_animate_zoom_form", "Frame Count"))
        self.frame_count.setText(_translate("mmqgis_animate_zoom_form", "50"))
        self.label.setText(_translate("mmqgis_animate_zoom_form", "Frame Image Output Directory"))

from qgis import gui
