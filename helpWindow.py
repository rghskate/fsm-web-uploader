# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'helpWindow.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QTabWidget, QTextBrowser, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(461, 413)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_2 = QHBoxLayout(self.tab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.textBrowser = QTextBrowser(self.tab)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setFrameShape(QFrame.Shape.NoFrame)
        self.textBrowser.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_2.addWidget(self.textBrowser)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_3 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.textBrowser_2 = QTextBrowser(self.tab_2)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        self.textBrowser_2.setFrameShape(QFrame.Shape.NoFrame)
        self.textBrowser_2.setFrameShadow(QFrame.Shadow.Plain)

        self.horizontalLayout_3.addWidget(self.textBrowser_2)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.pushButtonClose = QPushButton(Form)
        self.pushButtonClose.setObjectName(u"pushButtonClose")

        self.verticalLayout.addWidget(self.pushButtonClose)


        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.textBrowser.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:700;\">FSM Web Uploader</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:700;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-rig"
                        "ht:0px; -qt-block-indent:0; text-indent:0px;\">FSM Web Uploader is an FTP-based application for managing and automating the upload of the website files produced by the FS Manager software used in judging figure skating competitions.</p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:700;\">Functionality</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The core functionality of this program is as follows:</p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin"
                        "-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Allows secure connections to FTP sites that support FTP over TLS, in addition to allowing insecure connections when this is not available.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Monitors the website output folder of FS Manager for new files and uploads new files as they are made available.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Stores the state of the folder between runs to avoid reuploading duplicate files.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Makes arbitrary edits to the uploaded HTML files as defined in provided replacements file, and does so non-destructively by making the edits in memory only.</li>\n"
"<li align="
                        "\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Selectively uploads pages displaying judging panels, accommodating last minute changes without having to manually manage the contents of the website output directory.</li></ul>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:700;\">Use</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The program is designed to be as simple to use as possible. Simply fill the information fields and click run! The fields are as follows:</p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li align=\"justify\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-bl"
                        "ock-indent:0; text-indent:0px;\">Hostname: the hostname or IP address of the FTP server (e.g., bisresults.co.uk)</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Port: the port of the FTP server (e.g., 21)</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Username: your FTP username</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Password: your FTP account password (NOTE: saving the config of your setup save the password in plain text. Store your files securely!)</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Timeout duration: the timeout duration of the server in minutes. See the footnote for an explanation of this"
                        " functionality.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Local website folder: the folder that FSM outputs your site files to. The directory will have the same name as the competition code of the competition you are running.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remote directory: the folder on the FTP server that your files will be uploaded to. This folder MUST exist before using this program.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Edits file: a JSON file specifying edits to be made to the HTML files when they are uploaded. The keys specify the text to be replaced, and the values the text it will be replaced with.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px;"
                        " margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Save file: a JSON file saving the state of the folder at the start and end of each program run. This can be either a path to an existing file or a path to save a new file to.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copy PDFs?: This option specifies whether the program should search for PDFs to upload to the site. Currently, only Judges Details Per Skater are supported.</li>\n"
"<li align=\"justify\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">FS Manager Folder: The root directory of FS Manager that the program will search for PDFs. The default location is C:\\SwissTiming\\OVR\\FSManager.</li></ul>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" fon"
                        "t-weight:700;\">Note:</span> as there is no universal keepalive standard amongst FTP servers, this program uses the broadest possible approach of sending a file (.keep) consisting of a single byte of data to the remote server one minute before the specified timeout duration.</p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:700;\">DISCLAIMER</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">FS Manager is the sole proper"
                        "ty of Swiss Timing. This application does not in any way replicate or replace the functionality or purpose of FS Manager. This application is in no way endorsed by Swiss Timing.</p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"About this program", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("Form", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:700;\">Common issues</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:700;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight"
                        ":700;\">Error: Upload retry limit exceeded</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The FTP uploader has retried uploading a file more than 5 times and failed on each attempt. This typically happens when the underlying FTP connection is terminated. Just try running the uploader again. If the problem persists, your internet connection may be too weak to support reliable file transfer.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Error: X file not found</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The uploader attempts to verify filepaths before commencing"
                        ". Double check the paths you entered to make sure there are no mistakes.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Error when opening config file: 'hostname'</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This error is shown when the program tries to open a JSON in a format other than the specific save format of the JSON files used by the program. Make sure you selected the correct file when trying to load a config.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; m"
                        "argin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:700;\">Futher help</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Unfortunately, I don't have time to offer one to one help on resolving issues. If you encounter an issue with the program, please open an issue on its GitHub repository: <a href=\"https://github.com/rghskate/fsm-web-uploader/issues\"><span style=\" text-decoration: underline; color:#99ebff;\">GitHub Issues Page</span></a></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Form", u"Troubleshooting", None))
        self.pushButtonClose.setText(QCoreApplication.translate("Form", u"Close", None))
    # retranslateUi

