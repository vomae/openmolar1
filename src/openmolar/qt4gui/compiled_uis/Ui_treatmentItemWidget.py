# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'treatmentItemWidget.ui'
#
# Created: Sun Oct  4 20:51:34 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(553, 30)
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setContentsMargins(-1, 3, -1, 3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.spinBox = QtGui.QSpinBox(Form)
        self.spinBox.setMaximumSize(QtCore.QSize(60, 16777215))
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout.addWidget(self.spinBox)
        self.label = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.doubleSpinBox.setMaximum(2000.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        self.chain_frame = QtGui.QFrame(Form)
        self.chain_frame.setMinimumSize(QtCore.QSize(24, 0))
        self.chain_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.chain_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.chain_frame.setObjectName("chain_frame")
        self.horizontalLayout.addWidget(self.chain_frame)
        self.pt_doubleSpinBox = QtGui.QDoubleSpinBox(Form)
        self.pt_doubleSpinBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.pt_doubleSpinBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.pt_doubleSpinBox.setMaximum(2000.0)
        self.pt_doubleSpinBox.setObjectName("pt_doubleSpinBox")
        self.horizontalLayout.addWidget(self.pt_doubleSpinBox)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_( u"Form"))
        self.label.setText(_( u"TextLabel"))
