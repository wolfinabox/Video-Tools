# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_ui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from app.custom_widgets import Droppable_button
from app.custom_widgets import Droppable_lineEdit


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(590, 401)
        MainWindow.setMinimumSize(QSize(440, 0))
        self.load_preset = QAction(MainWindow)
        self.load_preset.setObjectName(u"load_preset")
        self.action_ee = QAction(MainWindow)
        self.action_ee.setObjectName(u"action_ee")
        self.action_reload_config = QAction(MainWindow)
        self.action_reload_config.setObjectName(u"action_reload_config")
        self.action_set_threads = QAction(MainWindow)
        self.action_set_threads.setObjectName(u"action_set_threads")
        self.action_save_config = QAction(MainWindow)
        self.action_save_config.setObjectName(u"action_save_config")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.text_output = QTextEdit(self.centralwidget)
        self.text_output.setObjectName(u"text_output")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_output.sizePolicy().hasHeightForWidth())
        self.text_output.setSizePolicy(sizePolicy)
        self.text_output.setMaximumSize(QSize(16777215, 125))
        self.text_output.setReadOnly(True)

        self.gridLayout.addWidget(self.text_output, 1, 0, 1, 1)

        self.tabs = QTabWidget(self.centralwidget)
        self.tabs.setObjectName(u"tabs")
        self.tabs.setTabBarAutoHide(False)
        self.workflow_tab = QWidget()
        self.workflow_tab.setObjectName(u"workflow_tab")
        self.gridLayout_3 = QGridLayout(self.workflow_tab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_8 = QLabel(self.workflow_tab)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setTextFormat(Qt.AutoText)
        self.label_8.setScaledContents(True)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_8, 0, 0, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.tabs.addTab(self.workflow_tab, "")
        self.tools_tab = QWidget()
        self.tools_tab.setObjectName(u"tools_tab")
        self.horizontalLayout_2 = QHBoxLayout(self.tools_tab)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 4, -1, -1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.tools_tab_layout = QFormLayout()
        self.tools_tab_layout.setObjectName(u"tools_tab_layout")
        self.tools_tab_layout.setVerticalSpacing(0)
        self.label_2 = QLabel(self.tools_tab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.tools_tab_layout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.tools_tab_layout.setItem(2, QFormLayout.SpanningRole, self.horizontalSpacer)


        self.horizontalLayout.addLayout(self.tools_tab_layout)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = QLabel(self.tools_tab)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.tools_list = QListWidget(self.tools_tab)
        self.tools_list.setObjectName(u"tools_list")

        self.verticalLayout_3.addWidget(self.tools_list)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 2)

        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.tabs.addTab(self.tools_tab, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_4 = QHBoxLayout(self.tab)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.info_browser_button = Droppable_button(self.tab)
        self.info_browser_button.setObjectName(u"info_browser_button")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.info_browser_button)

        self.info_file_text = Droppable_lineEdit(self.tab)
        self.info_file_text.setObjectName(u"info_file_text")
        self.info_file_text.setReadOnly(True)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.info_file_text)

        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.info_type_line = QLineEdit(self.tab)
        self.info_type_line.setObjectName(u"info_type_line")
        self.info_type_line.setReadOnly(True)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.info_type_line)

        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.info_length_line = QLineEdit(self.tab)
        self.info_length_line.setObjectName(u"info_length_line")
        self.info_length_line.setReadOnly(True)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.info_length_line)

        self.label_5 = QLabel(self.tab)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.info_size_line = QLineEdit(self.tab)
        self.info_size_line.setObjectName(u"info_size_line")
        self.info_size_line.setReadOnly(True)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.info_size_line)

        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_6)

        self.info_bitrate_line = QLineEdit(self.tab)
        self.info_bitrate_line.setObjectName(u"info_bitrate_line")
        self.info_bitrate_line.setReadOnly(True)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.info_bitrate_line)

        self.label_7 = QLabel(self.tab)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.label_7)

        self.info_audiotracks_line = QLineEdit(self.tab)
        self.info_audiotracks_line.setObjectName(u"info_audiotracks_line")
        self.info_audiotracks_line.setReadOnly(True)

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.info_audiotracks_line)


        self.horizontalLayout_3.addLayout(self.formLayout_2)

        self.info_text_edit = QTextEdit(self.tab)
        self.info_text_edit.setObjectName(u"info_text_edit")
        self.info_text_edit.setFrameShape(QFrame.StyledPanel)
        self.info_text_edit.setFrameShadow(QFrame.Sunken)
        self.info_text_edit.setLineWidth(1)
        self.info_text_edit.setReadOnly(True)

        self.horizontalLayout_3.addWidget(self.info_text_edit)

        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 4)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)

        self.tabs.addTab(self.tab, "")

        self.gridLayout.addWidget(self.tabs, 0, 0, 1, 1)

        self.progress_bar = QProgressBar(self.centralwidget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setEnabled(False)
        self.progress_bar.setValue(0)

        self.gridLayout.addWidget(self.progress_bar, 2, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 590, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuTools = QMenu(self.menubar)
        self.menuTools.setObjectName(u"menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menuFile.addAction(self.action_reload_config)
        self.menuFile.addAction(self.action_save_config)
        self.menuTools.addAction(self.action_set_threads)
        self.menuTools.addAction(self.action_ee)

        self.retranslateUi(MainWindow)

        self.tabs.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Ultimate Workflow Tool", None))
        self.load_preset.setText(QCoreApplication.translate("MainWindow", u"Load preset...", None))
#if QT_CONFIG(statustip)
        self.load_preset.setStatusTip(QCoreApplication.translate("MainWindow", u"Load a settings preset", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.load_preset.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+L", None))
#endif // QT_CONFIG(shortcut)
        self.action_ee.setText(QCoreApplication.translate("MainWindow", u"Don't click this...", None))
#if QT_CONFIG(statustip)
        self.action_ee.setStatusTip(QCoreApplication.translate("MainWindow", u"???????????????????", None))
#endif // QT_CONFIG(statustip)
        self.action_reload_config.setText(QCoreApplication.translate("MainWindow", u"Reload Config...", None))
#if QT_CONFIG(statustip)
        self.action_reload_config.setStatusTip(QCoreApplication.translate("MainWindow", u"Reload config file", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.action_reload_config.setShortcut(QCoreApplication.translate("MainWindow", u"Alt+C", None))
#endif // QT_CONFIG(shortcut)
        self.action_set_threads.setText(QCoreApplication.translate("MainWindow", u"Set #Threads...", None))
#if QT_CONFIG(statustip)
        self.action_set_threads.setStatusTip(QCoreApplication.translate("MainWindow", u"Set number of threads to use", None))
#endif // QT_CONFIG(statustip)
        self.action_save_config.setText(QCoreApplication.translate("MainWindow", u"Save Config", None))
#if QT_CONFIG(statustip)
        self.action_save_config.setStatusTip(QCoreApplication.translate("MainWindow", u"Save the current settings to the config file", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(statustip)
        self.text_output.setStatusTip(QCoreApplication.translate("MainWindow", u"Command/program output", None))
#endif // QT_CONFIG(statustip)
        self.text_output.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
#if QT_CONFIG(statustip)
        self.tabs.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Under Construction", None))
        self.tabs.setTabText(self.tabs.indexOf(self.workflow_tab), QCoreApplication.translate("MainWindow", u"Workflow", None))
#if QT_CONFIG(statustip)
        self.tools_tab.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"No tool selected...", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Tools:", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tools_tab), QCoreApplication.translate("MainWindow", u"Tools", None))
        self.info_browser_button.setText(QCoreApplication.translate("MainWindow", u"Browse...", None))
        self.info_file_text.setPlaceholderText(QCoreApplication.translate("MainWindow", u"File to get info on...", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Type: ", None))
        self.info_type_line.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type of file...", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Length:", None))
        self.info_length_line.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Length of media...", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Size:", None))
        self.info_size_line.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Size of file...", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Video Bitrate:", None))
        self.info_bitrate_line.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Bitrate of media...", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Audio Tracks:", None))
        self.info_audiotracks_line.setPlaceholderText(QCoreApplication.translate("MainWindow", u"# of audio tracks...", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Video Info", None))
#if QT_CONFIG(statustip)
        self.menuFile.setStatusTip(QCoreApplication.translate("MainWindow", u"Settings and stuff", None))
#endif // QT_CONFIG(statustip)
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
#if QT_CONFIG(statustip)
        self.menuTools.setStatusTip(QCoreApplication.translate("MainWindow", u"Other things", None))
#endif // QT_CONFIG(statustip)
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
    # retranslateUi

