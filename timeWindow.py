# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'timeWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDateTimeEdit,
    QDialog, QDialogButtonBox, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(182, 145)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.checkBoxUseCustom = QCheckBox(Dialog)
        self.checkBoxUseCustom.setObjectName(u"checkBoxUseCustom")

        self.verticalLayout.addWidget(self.checkBoxUseCustom)

        self.labelSetTime = QLabel(Dialog)
        self.labelSetTime.setObjectName(u"labelSetTime")
        self.labelSetTime.setEnabled(False)

        self.verticalLayout.addWidget(self.labelSetTime)

        self.dateTimeEditCustom = QDateTimeEdit(Dialog)
        self.dateTimeEditCustom.setObjectName(u"dateTimeEditCustom")
        self.dateTimeEditCustom.setEnabled(False)

        self.verticalLayout.addWidget(self.dateTimeEditCustom)

        self.checkBoxUploadAll = QCheckBox(Dialog)
        self.checkBoxUploadAll.setObjectName(u"checkBoxUploadAll")
        self.checkBoxUploadAll.setEnabled(False)

        self.verticalLayout.addWidget(self.checkBoxUploadAll)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.checkBoxUseCustom.setText(QCoreApplication.translate("Dialog", u"Use custom time?", None))
        self.labelSetTime.setText(QCoreApplication.translate("Dialog", u"Set custom upload time:", None))
        self.checkBoxUploadAll.setText(QCoreApplication.translate("Dialog", u"Upload all segments", None))
    # retranslateUi

