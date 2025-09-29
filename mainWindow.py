# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListView, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QSpinBox,
    QStatusBar, QTextBrowser, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(781, 589)
        self.actionLoad_configuration = QAction(MainWindow)
        self.actionLoad_configuration.setObjectName(u"actionLoad_configuration")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.actionLoad_configuration.setIcon(icon)
        self.actionSave_configuration = QAction(MainWindow)
        self.actionSave_configuration.setObjectName(u"actionSave_configuration")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.actionSave_configuration.setIcon(icon1)
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit))
        self.actionExit.setIcon(icon2)
        self.actionExit.setMenuRole(QAction.MenuRole.QuitRole)
        self.actionManual_upload_time = QAction(MainWindow)
        self.actionManual_upload_time.setObjectName(u"actionManual_upload_time")
        self.actionLicenses = QAction(MainWindow)
        self.actionLicenses.setObjectName(u"actionLicenses")
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.actionLicenses.setIcon(icon3)
        self.actionHelp = QAction(MainWindow)
        self.actionHelp.setObjectName(u"actionHelp")
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpFaq))
        self.actionHelp.setIcon(icon4)
        self.actionTemporary_folder = QAction(MainWindow)
        self.actionTemporary_folder.setObjectName(u"actionTemporary_folder")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 761, 515))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBoxEdits = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxEdits.setObjectName(u"groupBoxEdits")
        self.formLayout_3 = QFormLayout(self.groupBoxEdits)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.labelEditsFile = QLabel(self.groupBoxEdits)
        self.labelEditsFile.setObjectName(u"labelEditsFile")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelEditsFile)

        self.labelSaveFile = QLabel(self.groupBoxEdits)
        self.labelSaveFile.setObjectName(u"labelSaveFile")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelSaveFile)

        self.labelCopyPDFs = QLabel(self.groupBoxEdits)
        self.labelCopyPDFs.setObjectName(u"labelCopyPDFs")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelCopyPDFs)

        self.horizontalLayoutEditsFile = QHBoxLayout()
        self.horizontalLayoutEditsFile.setObjectName(u"horizontalLayoutEditsFile")
        self.lineEditEditsFile = QLineEdit(self.groupBoxEdits)
        self.lineEditEditsFile.setObjectName(u"lineEditEditsFile")

        self.horizontalLayoutEditsFile.addWidget(self.lineEditEditsFile)

        self.pushButtonBrowseEditsFile = QPushButton(self.groupBoxEdits)
        self.pushButtonBrowseEditsFile.setObjectName(u"pushButtonBrowseEditsFile")

        self.horizontalLayoutEditsFile.addWidget(self.pushButtonBrowseEditsFile)


        self.formLayout_3.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayoutEditsFile)

        self.horizontalLayoutSaveFile = QHBoxLayout()
        self.horizontalLayoutSaveFile.setObjectName(u"horizontalLayoutSaveFile")
        self.lineEditSaveFile = QLineEdit(self.groupBoxEdits)
        self.lineEditSaveFile.setObjectName(u"lineEditSaveFile")

        self.horizontalLayoutSaveFile.addWidget(self.lineEditSaveFile)

        self.pushButtonBrowseSaveFile = QPushButton(self.groupBoxEdits)
        self.pushButtonBrowseSaveFile.setObjectName(u"pushButtonBrowseSaveFile")

        self.horizontalLayoutSaveFile.addWidget(self.pushButtonBrowseSaveFile)


        self.formLayout_3.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayoutSaveFile)

        self.checkBoxCopyPDFs = QCheckBox(self.groupBoxEdits)
        self.checkBoxCopyPDFs.setObjectName(u"checkBoxCopyPDFs")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.checkBoxCopyPDFs)

        self.labelFSMDir = QLabel(self.groupBoxEdits)
        self.labelFSMDir.setObjectName(u"labelFSMDir")
        self.labelFSMDir.setEnabled(False)

        self.formLayout_3.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelFSMDir)

        self.horizontalLayoutFSMDir = QHBoxLayout()
        self.horizontalLayoutFSMDir.setObjectName(u"horizontalLayoutFSMDir")
        self.lineEditFSMDir = QLineEdit(self.groupBoxEdits)
        self.lineEditFSMDir.setObjectName(u"lineEditFSMDir")
        self.lineEditFSMDir.setEnabled(False)

        self.horizontalLayoutFSMDir.addWidget(self.lineEditFSMDir)

        self.pushButtonBrowseFSMDir = QPushButton(self.groupBoxEdits)
        self.pushButtonBrowseFSMDir.setObjectName(u"pushButtonBrowseFSMDir")
        self.pushButtonBrowseFSMDir.setEnabled(False)

        self.horizontalLayoutFSMDir.addWidget(self.pushButtonBrowseFSMDir)


        self.formLayout_3.setLayout(4, QFormLayout.ItemRole.FieldRole, self.horizontalLayoutFSMDir)


        self.gridLayout.addWidget(self.groupBoxEdits, 2, 0, 1, 1)

        self.groupBoxDirectories = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxDirectories.setObjectName(u"groupBoxDirectories")
        self.formLayout_2 = QFormLayout(self.groupBoxDirectories)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.labelLocalFolder = QLabel(self.groupBoxDirectories)
        self.labelLocalFolder.setObjectName(u"labelLocalFolder")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelLocalFolder)

        self.horizontalLayoutLocalFolder = QHBoxLayout()
        self.horizontalLayoutLocalFolder.setObjectName(u"horizontalLayoutLocalFolder")
        self.lineEditLocalFolder = QLineEdit(self.groupBoxDirectories)
        self.lineEditLocalFolder.setObjectName(u"lineEditLocalFolder")

        self.horizontalLayoutLocalFolder.addWidget(self.lineEditLocalFolder)

        self.pushButtonBrowseLocalFolder = QPushButton(self.groupBoxDirectories)
        self.pushButtonBrowseLocalFolder.setObjectName(u"pushButtonBrowseLocalFolder")

        self.horizontalLayoutLocalFolder.addWidget(self.pushButtonBrowseLocalFolder)


        self.formLayout_2.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayoutLocalFolder)

        self.labelRemoteDir = QLabel(self.groupBoxDirectories)
        self.labelRemoteDir.setObjectName(u"labelRemoteDir")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelRemoteDir)

        self.lineEditRemoteDir = QLineEdit(self.groupBoxDirectories)
        self.lineEditRemoteDir.setObjectName(u"lineEditRemoteDir")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEditRemoteDir)


        self.gridLayout.addWidget(self.groupBoxDirectories, 1, 0, 1, 1)

        self.pushButtonRun = QPushButton(self.scrollAreaWidgetContents)
        self.pushButtonRun.setObjectName(u"pushButtonRun")

        self.gridLayout.addWidget(self.pushButtonRun, 3, 0, 1, 1)

        self.groupBoxUploadQueue = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxUploadQueue.setObjectName(u"groupBoxUploadQueue")
        self.verticalLayout = QVBoxLayout(self.groupBoxUploadQueue)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listViewUploadQueue = QListView(self.groupBoxUploadQueue)
        self.listViewUploadQueue.setObjectName(u"listViewUploadQueue")

        self.verticalLayout.addWidget(self.listViewUploadQueue)


        self.gridLayout.addWidget(self.groupBoxUploadQueue, 2, 1, 2, 1)

        self.groupBoxFtpConfig = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxFtpConfig.setObjectName(u"groupBoxFtpConfig")
        self.formLayout = QFormLayout(self.groupBoxFtpConfig)
        self.formLayout.setObjectName(u"formLayout")
        self.labelHostname = QLabel(self.groupBoxFtpConfig)
        self.labelHostname.setObjectName(u"labelHostname")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelHostname)

        self.labelPort = QLabel(self.groupBoxFtpConfig)
        self.labelPort.setObjectName(u"labelPort")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelPort)

        self.labelUsername = QLabel(self.groupBoxFtpConfig)
        self.labelUsername.setObjectName(u"labelUsername")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelUsername)

        self.labelPassword = QLabel(self.groupBoxFtpConfig)
        self.labelPassword.setObjectName(u"labelPassword")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelPassword)

        self.lineEditHostname = QLineEdit(self.groupBoxFtpConfig)
        self.lineEditHostname.setObjectName(u"lineEditHostname")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEditHostname)

        self.spinBoxPort = QSpinBox(self.groupBoxFtpConfig)
        self.spinBoxPort.setObjectName(u"spinBoxPort")
        self.spinBoxPort.setMinimum(1)
        self.spinBoxPort.setMaximum(65535)
        self.spinBoxPort.setValue(21)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinBoxPort)

        self.lineEditUsername = QLineEdit(self.groupBoxFtpConfig)
        self.lineEditUsername.setObjectName(u"lineEditUsername")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEditUsername)

        self.lineEditPassword = QLineEdit(self.groupBoxFtpConfig)
        self.lineEditPassword.setObjectName(u"lineEditPassword")
        self.lineEditPassword.setEchoMode(QLineEdit.EchoMode.Password)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEditPassword)

        self.labelTimeout = QLabel(self.groupBoxFtpConfig)
        self.labelTimeout.setObjectName(u"labelTimeout")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelTimeout)

        self.spinBoxTimeout = QSpinBox(self.groupBoxFtpConfig)
        self.spinBoxTimeout.setObjectName(u"spinBoxTimeout")
        self.spinBoxTimeout.setMaximum(999)
        self.spinBoxTimeout.setValue(15)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinBoxTimeout)


        self.gridLayout.addWidget(self.groupBoxFtpConfig, 0, 0, 1, 1)

        self.groupBoxServerMessages = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxServerMessages.setObjectName(u"groupBoxServerMessages")
        self.verticalLayout_2 = QVBoxLayout(self.groupBoxServerMessages)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.textBrowserServerMessages = QTextBrowser(self.groupBoxServerMessages)
        self.textBrowserServerMessages.setObjectName(u"textBrowserServerMessages")

        self.verticalLayout_2.addWidget(self.textBrowserServerMessages)


        self.gridLayout.addWidget(self.groupBoxServerMessages, 1, 1, 1, 1)

        self.groupBoxStatus = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBoxStatus.setObjectName(u"groupBoxStatus")
        self.formLayout_4 = QFormLayout(self.groupBoxStatus)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.labelConnectionStatus = QLabel(self.groupBoxStatus)
        self.labelConnectionStatus.setObjectName(u"labelConnectionStatus")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelConnectionStatus)

        self.labelConnectionStatusDisplay = QLabel(self.groupBoxStatus)
        self.labelConnectionStatusDisplay.setObjectName(u"labelConnectionStatusDisplay")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelConnectionStatusDisplay)

        self.labelLastUpdate = QLabel(self.groupBoxStatus)
        self.labelLastUpdate.setObjectName(u"labelLastUpdate")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelLastUpdate)

        self.labelLastUpdateDisplay = QLabel(self.groupBoxStatus)
        self.labelLastUpdateDisplay.setObjectName(u"labelLastUpdateDisplay")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.labelLastUpdateDisplay)

        self.labelLastUpdateDelta = QLabel(self.groupBoxStatus)
        self.labelLastUpdateDelta.setObjectName(u"labelLastUpdateDelta")

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelLastUpdateDelta)

        self.labelLastUpdateDeltaDisplay = QLabel(self.groupBoxStatus)
        self.labelLastUpdateDeltaDisplay.setObjectName(u"labelLastUpdateDeltaDisplay")

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.FieldRole, self.labelLastUpdateDeltaDisplay)

        self.labelCustomTime = QLabel(self.groupBoxStatus)
        self.labelCustomTime.setObjectName(u"labelCustomTime")

        self.formLayout_4.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelCustomTime)

        self.labelCustomTimeDisplay = QLabel(self.groupBoxStatus)
        self.labelCustomTimeDisplay.setObjectName(u"labelCustomTimeDisplay")

        self.formLayout_4.setWidget(3, QFormLayout.ItemRole.FieldRole, self.labelCustomTimeDisplay)


        self.gridLayout.addWidget(self.groupBoxStatus, 0, 1, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 781, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOptions = QMenu(self.menubar)
        self.menuOptions.setObjectName(u"menuOptions")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionSave_configuration)
        self.menuFile.addAction(self.actionLoad_configuration)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuOptions.addAction(self.actionManual_upload_time)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionLicenses)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionLoad_configuration.setText(QCoreApplication.translate("MainWindow", u"Load configuration", None))
#if QT_CONFIG(shortcut)
        self.actionLoad_configuration.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionSave_configuration.setText(QCoreApplication.translate("MainWindow", u"Save configuration", None))
#if QT_CONFIG(shortcut)
        self.actionSave_configuration.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
#if QT_CONFIG(shortcut)
        self.actionExit.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+W", None))
#endif // QT_CONFIG(shortcut)
        self.actionManual_upload_time.setText(QCoreApplication.translate("MainWindow", u"Manual upload time", None))
#if QT_CONFIG(shortcut)
        self.actionManual_upload_time.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+M", None))
#endif // QT_CONFIG(shortcut)
        self.actionLicenses.setText(QCoreApplication.translate("MainWindow", u"Licenses", None))
        self.actionHelp.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.actionTemporary_folder.setText(QCoreApplication.translate("MainWindow", u"Temporary folder", None))
        self.groupBoxEdits.setTitle(QCoreApplication.translate("MainWindow", u"File management and edits", None))
        self.labelEditsFile.setText(QCoreApplication.translate("MainWindow", u"Edits file", None))
        self.labelSaveFile.setText(QCoreApplication.translate("MainWindow", u"Save file", None))
        self.labelCopyPDFs.setText(QCoreApplication.translate("MainWindow", u"Copy PDFs?", None))
        self.lineEditEditsFile.setPlaceholderText(QCoreApplication.translate("MainWindow", u"File containing edits to make to HTML files", None))
        self.pushButtonBrowseEditsFile.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.lineEditSaveFile.setPlaceholderText(QCoreApplication.translate("MainWindow", u"File to save upload state to", None))
        self.pushButtonBrowseSaveFile.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.checkBoxCopyPDFs.setText("")
        self.labelFSMDir.setText(QCoreApplication.translate("MainWindow", u"FS Manager Folder", None))
        self.lineEditFSMDir.setText(QCoreApplication.translate("MainWindow", u"C:\\SwissTiming\\OVR\\FSManager", None))
        self.pushButtonBrowseFSMDir.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.groupBoxDirectories.setTitle(QCoreApplication.translate("MainWindow", u"Directories", None))
        self.labelLocalFolder.setText(QCoreApplication.translate("MainWindow", u"Local website folder", None))
        self.lineEditLocalFolder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Folder containing FS Manger results site files", None))
        self.pushButtonBrowseLocalFolder.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.labelRemoteDir.setText(QCoreApplication.translate("MainWindow", u"Remote directory", None))
        self.lineEditRemoteDir.setText("")
        self.lineEditRemoteDir.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Directory on FTP host", None))
        self.pushButtonRun.setText(QCoreApplication.translate("MainWindow", u"Run!", None))
        self.groupBoxUploadQueue.setTitle(QCoreApplication.translate("MainWindow", u"Upload Queue", None))
        self.groupBoxFtpConfig.setTitle(QCoreApplication.translate("MainWindow", u"FTP Configuration", None))
        self.labelHostname.setText(QCoreApplication.translate("MainWindow", u"Hostname", None))
        self.labelPort.setText(QCoreApplication.translate("MainWindow", u"Port", None))
        self.labelUsername.setText(QCoreApplication.translate("MainWindow", u"Username", None))
        self.labelPassword.setText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.lineEditHostname.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter your FTP hostname", None))
        self.lineEditUsername.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter your FTP username", None))
        self.lineEditPassword.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter your FTP password", None))
        self.labelTimeout.setText(QCoreApplication.translate("MainWindow", u"Timeout duration", None))
        self.spinBoxTimeout.setSuffix(QCoreApplication.translate("MainWindow", u" minutes", None))
        self.groupBoxServerMessages.setTitle(QCoreApplication.translate("MainWindow", u"Status Messages", None))
        self.groupBoxStatus.setTitle(QCoreApplication.translate("MainWindow", u"Status", None))
        self.labelConnectionStatus.setText(QCoreApplication.translate("MainWindow", u"Connection status:", None))
        self.labelConnectionStatusDisplay.setText(QCoreApplication.translate("MainWindow", u"Disconnected", None))
        self.labelLastUpdate.setText(QCoreApplication.translate("MainWindow", u"Time of last update:", None))
        self.labelLastUpdateDisplay.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.labelLastUpdateDelta.setText(QCoreApplication.translate("MainWindow", u"Time since last update:", None))
        self.labelLastUpdateDeltaDisplay.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.labelCustomTime.setText(QCoreApplication.translate("MainWindow", u"Custom upload time:", None))
        self.labelCustomTimeDisplay.setText(QCoreApplication.translate("MainWindow", u"Not set (using current time)", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOptions.setTitle(QCoreApplication.translate("MainWindow", u"Options", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

