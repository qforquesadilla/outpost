import os
import sys
import json
import logging
from datetime import datetime
from functools import partial
from collections import OrderedDict

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget, QLabel, QSizePolicy
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QTableWidgetItem
from PySide2.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide2.QtCore import QFile, QSize


'''
Outpost
'''


class Outpost(object):

    def __init__(self):
        '''
        TBA
        '''

        # config
        self.__toolRootDir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        self.__configPath = os.path.normpath(os.path.join(self.__toolRootDir, 'data/config.json'))
        logDir = os.path.normpath(os.path.join(self.__toolRootDir, 'data/log'))

        self.__logger = self.__setupLogger(logDir)

        self.__setupConfig()
        self.__registerSettings()

        # ui & commands
        self.__buildUi()
        self.__buildSettings()
        self.__linkCommands()

        # startup
        self.__mainUi.show()

        print('\n\n###########\n# OUTPOST #\n###########\n')
        sys.exit(self.__app.exec_())


    def __setupConfig(self):
        '''
        TBA
        '''

        # load config
        try:
            configData = self.__readJson(self.__configPath)
        except Exception as err:
            self.__logger.warning('Failed to load config: {}'.format(self.__configPath)) # TODO: Prompt
            self.__logger.warning(str(err)) # TODO: Prompt
            return False

        # restore values
        self.__settingsDir = configData.get('settingsDir', None)
        if self.__settingsDir == 'demo':
            self.__settingsDir = os.path.normpath(os.path.join(self.__toolRootDir, 'data/settings'))
        self.__configEnv = configData.get('configEnv', None)

        return True


    def __registerSettings(self):
        '''
        Register each app settings...
        '''

        self.__settings = OrderedDict()

        sortedSettings = {}
        settingNames = os.listdir(self.__settingsDir)
        for settingName in settingNames:
            settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))

            try:
                settingData = self.__readJson(settingPath)
                sortedSettings[settingName] = settingData
            except Exception as err:
                self.__logger.warning('Failed to load setting: {}'.format(settingPath)) # TODO: Prompt
                self.__logger.warning(str(err)) # TODO: Prompt

        sortedSettings = sorted(sortedSettings.items(), key=lambda x: int(x[1]['order']))
        for sortedSetting in sortedSettings:
            settingName = sortedSetting[0]
            settingData = sortedSetting[1]
            self.__settings[settingName] = settingData

        return True


    def __buildUi(self):
        '''
        TBA
        '''

        # define ui file paths
        self.__app = QApplication(sys.argv)
        mainUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/main.ui')).replace('\\', '/')
        preferenceUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/preference.ui')).replace('\\', '/')
        optionUiPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/option.ui')).replace('\\', '/')

        # open ui files
        loader = QUiLoader()
        mainUiFile = QFile(mainUiPath)
        mainUiFile.open(QFile.ReadOnly)
        preferenceUiFile = QFile(preferenceUiPath)
        preferenceUiFile.open(QFile.ReadOnly)
        optionUiFile = QFile(optionUiPath)
        optionUiFile.open(QFile.ReadOnly)

        # create ui objects
        self.__mainUi = loader.load(mainUiFile)
        self.__preferenceUi = loader.load(preferenceUiFile)
        self.__optionUi = loader.load(optionUiFile)

        # set icon
        iconPath = os.path.normpath(os.path.join(self.__toolRootDir, 'interface/icon.png')).replace('\\', '/')
        iconFile = QIcon(iconPath)
        self.__mainUi.setWindowIcon(iconFile)
        self.__preferenceUi.setWindowIcon(iconFile)
        self.__optionUi.setWindowIcon(iconFile)


    def __buildSettings(self):
        '''
        TBA
        '''

        scrollBar = self.__mainUi.settingsSA.verticalScrollBar()
        scrollBar.setStyleSheet('QScrollBar {height: 0px;}')
        scrollBar.setStyleSheet('QScrollBar {width: 0px;}')
        
        qVBoxLayout = QVBoxLayout()
        qWidget = QWidget()

        for settingName, settingData in self.__settings.items():

            name = settingData['name']
            description = settingData['description']
            color = settingData['color']
            backgroundColor = settingData['background-color']
            iconPath = settingData['iconPath']  # TODO: imagePath?
            launchButton = QPushButton(name.upper())
            launchButton.setMinimumHeight(50)
            launchButton.setMinimumWidth(180)
            launchButton.setMaximumHeight(50)
            #launchButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)#
            launchButton.setToolTip(description)
            launchButton.clicked.connect(partial(self.__onLaunchPressed, settingName))

            # TODO: Background image
            #if iconPath:
            #    qPixmap = QPixmap(iconPath)
            #    qIcon = QIcon(qPixmap)
            #    launchButton.setIcon(qIcon)
            #    launchButton.setIconSize(QSize(500, 500))

            if iconPath:
                qPainter = QPainter()
                qPixmap = QPixmap(iconPath)
                #qPainter.begin(qPixmap);
                #qPainter.setOpacity(0.50)
                #qPainter.drawPixmap(qPixmap.rect(), qPixmap)
                print(qPixmap)
                #qPainter.end()
                qIcon = QIcon(qPixmap)
                launchButton.setIcon(qIcon)

            styleSheet = 'QPushButton {font-size: 18pt; color: %s; background-color: %s} ' % (color, backgroundColor)
            styleSheet += 'QToolTip {color: #FFFFFF; background-color: #313333; border: 0px;border-top: 3px transparent;}'

            #if iconPath:
            #    styleSheet += 'QPushButton{background-image: url(%s); opacity: 0.4}' % iconPath
            #    styleSheet += 'html{opacity: 0.5;}'
            
            launchButton.setStyleSheet(styleSheet)

            optionButton = QPushButton('⚙️')
            optionButton.setMinimumHeight(50)
            optionButton.setMinimumWidth(25)
            optionButton.setMaximumHeight(50)
            optionButton.setMaximumWidth(25)
            optionButton.clicked.connect(partial(self.__onOptionPressed, settingName))

            qHBoxLayout = QHBoxLayout()
            qHBoxLayout.setContentsMargins(0, 2.5, 0, 2.5)
            qHBoxLayout.setStretchFactor(launchButton, 1)#
            qHBoxLayout.setSpacing(0)

            qHBoxLayout.addWidget(launchButton)
            qHBoxLayout.addWidget(optionButton)
            qVBoxLayout.addLayout(qHBoxLayout)

        # always add '+' button
        addButton = QPushButton('+')
        addButton.setMinimumHeight(50)
        addButton.setMinimumWidth(180)
        addButton.clicked.connect(self.__onAddPressed)
        styleSheet = 'QPushButton {font-size: 18pt; color: #FFFFFF; background-color: #202222; border: transparent}'
        addButton.setStyleSheet(styleSheet)

        qHBoxLayout = QHBoxLayout()
        qHBoxLayout.setSpacing(0)
        qHBoxLayout.addWidget(addButton)
        qVBoxLayout.addLayout(qHBoxLayout)

        # add spacer
        qSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        qVBoxLayout.addItem(qSpacer)

        qWidget.setLayout(qVBoxLayout)
        self.__mainUi.settingsSA.setWidget(qWidget)


    def __linkCommands(self):
        '''
        TBA
        '''

        # main ui
        self.__mainUi.preferencePB.clicked.connect(self.__onPreferencePressed)

        # option ui
        self.__optionUi.optionUpPB.clicked.connect(partial(self.__onMoveSetting, self.__optionUi.optionUpPB))
        self.__optionUi.optionDownPB.clicked.connect(partial(self.__onMoveSetting, self.__optionUi.optionDownPB))
        self.__optionUi.iconPathTB.clicked.connect(partial(self.__onSetPath, self.__optionUi.iconPathLE))
        self.__optionUi.executablePathTB.clicked.connect(partial(self.__onSetPath, self.__optionUi.executablePathLE))
        self.__optionUi.beforeLaunchHookTB.clicked.connect(partial(self.__onSetPath, self.__optionUi.beforeLaunchHookLE))
        self.__optionUi.settingEnvAddPB.clicked.connect(partial(self.__onAddEnvPressed, self.__optionUi.settingEnvTW))
        self.__optionUi.settingEnvRemovePB.clicked.connect(partial(self.__onRemoveEnvPressed, self.__optionUi.settingEnvTW))

        # TODO: LE color change
        # TODO: LE background-color change

        self.__optionUi.savePB.clicked.connect(self.__onOptionSavePressed)
        self.__optionUi.cancelPB.clicked.connect(self.__onOptionCancelPressed)
        self.__optionUi.previewPB.clicked.connect(self.__onOptionPreviewPressed)
        self.__optionUi.openPB.clicked.connect(self.__onOptionOpenPressed)
        self.__optionUi.duplicatePB.clicked.connect(self.__onOptionDuplicatePressed)
        self.__optionUi.deletePB.clicked.connect(self.__onOptionDeletePressed)

        # preference ui
        self.__preferenceUi.settingsDirTB.clicked.connect(partial(self.__onSetPath, self.__preferenceUi.settingsDirLE))
        self.__preferenceUi.configEnvAddPB.clicked.connect(partial(self.__onAddEnvPressed, self.__preferenceUi.configEnvTW))
        self.__preferenceUi.configEnvRemovePB.clicked.connect(partial(self.__onRemoveEnvPressed, self.__preferenceUi.configEnvTW))

        self.__preferenceUi.savePB.clicked.connect(self.__onPreferenceSavePressed)
        self.__preferenceUi.cancelPB.clicked.connect(self.__onPreferenceCancelPressed)
        self.__preferenceUi.openSettingsPB.clicked.connect(self.__onPreferenceOpenSettingsPressed)
        self.__preferenceUi.openToolRootPB.clicked.connect(self.__onPreferenceOpenToolRootPressed)
        self.__preferenceUi.logPB.clicked.connect(self.__onPreferenceLogPressed)


    def __setupLogger(self, logDir):
        '''
        TBA
        '''

        currentTime = datetime.now().strftime("%Y%m%d_%H%M%S")
        logName = "outpost_{}.txt".format(currentTime)
        self.__logPath = os.path.normpath(os.path.join(logDir, logName))

        formatter = logging.Formatter('%(levelname)s:%(message)s')
        handler = logging.FileHandler(self.__logPath)
        handler.setFormatter(formatter)
        logger = logging.getLogger("outpostLogger")

        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("START")

        return logger


    def __onLaunchPressed(self, *args):
        '''
        TBA
        '''

        settingName = args[0]
        from outpostApi import OutpostApi
        outpostApi = OutpostApi(self.__settings[settingName], self.__configEnv)
        environ = outpostApi.createEnviron()
        self.__logger.info(self.__formatEnviron(environ))
        outpostApi.launch()


    def __onOptionPressed(self, *args):
        '''
        TBA
        '''

        settingName = args[0]

        settingData = self.__settings[settingName]
        self.__setLabel(self.__optionUi.fileNameL, settingName)
        self.__setLineEdit(self.__optionUi.orderLE, str(settingData['order']))
        self.__setLineEdit(self.__optionUi.nameLE, settingData['name'])
        self.__setLineEdit(self.__optionUi.descriptionLE, settingData['description'])
        self.__setLineEdit(self.__optionUi.colorLE, settingData['color'])
        self.__setLineEdit(self.__optionUi.backgroundColorLE, settingData['background-color'])
        self.__setLineEdit(self.__optionUi.iconPathLE, settingData['iconPath'])
        self.__setLineEdit(self.__optionUi.executablePathLE, settingData['executablePath'])
        self.__setLineEdit(self.__optionUi.beforeLaunchHookLE, settingData['beforeLaunchHook'])
        self.__setCheckBox(self.__optionUi.keepGlobalEnvCB, settingData['keepGlobalEnv'])
        self.__setTableWidget(self.__optionUi.settingEnvTW, settingData['settingEnv'])

        self.__optionUi.fileNameLE.setVisible(False)
        self.__optionUi.optionUpPB.setVisible(True)
        self.__optionUi.optionDownPB.setVisible(True)
        self.__optionUi.openPB.setVisible(True)
        self.__optionUi.duplicatePB.setVisible(True)
        self.__optionUi.deletePB.setVisible(True)

        self.__optionUi.show()


    def __onAddPressed(self):
        '''
        TBA
        '''

        self.__setLabel(self.__optionUi.fileNameL, 'File Name:')
        self.__setLineEdit(self.__optionUi.orderLE, str(len(self.__settings) + 1))
        self.__setLineEdit(self.__optionUi.nameLE, '')
        self.__setLineEdit(self.__optionUi.descriptionLE, '')
        self.__setLineEdit(self.__optionUi.colorLE, '#FFFFFF')
        self.__setLineEdit(self.__optionUi.backgroundColorLE, '#313333')
        self.__setLineEdit(self.__optionUi.iconPathLE, '')
        self.__setLineEdit(self.__optionUi.executablePathLE, '')
        self.__setLineEdit(self.__optionUi.beforeLaunchHookLE, '')
        self.__setCheckBox(self.__optionUi.keepGlobalEnvCB, True)
        self.__setTableWidget(self.__optionUi.settingEnvTW, {})

        self.__optionUi.fileNameLE.setVisible(True)
        self.__optionUi.optionUpPB.setVisible(False)
        self.__optionUi.optionDownPB.setVisible(False)
        self.__optionUi.openPB.setVisible(False)
        self.__optionUi.duplicatePB.setVisible(False)
        self.__optionUi.deletePB.setVisible(False)

        self.__optionUi.show()


    def __onPreferencePressed(self):
        '''
        TBA
        '''

        self.__setLineEdit(self.__preferenceUi.settingsDirLE, self.__settingsDir)
        self.__setTableWidget(self.__preferenceUi.configEnvTW, self.__configEnv)
        self.__preferenceUi.show()


    ###################
    # COMMON COMMANDS #
    ###################

    
    def __onMoveSetting(self, qPushButton):
        '''
        TBA
        '''

        objectName = qPushButton.objectName()
        settingNames = list(self.__settings.keys())
        settingName = self.__getLabel(self.__optionUi.fileNameL)
        currentIndex = settingNames.index(settingName)

        if objectName == 'optionUpPB':
            nextIndex = currentIndex + 1
            if nextIndex > len(settingNames) - 1:
                nextIndex = 0

        elif objectName == 'optionDownPB':
            nextIndex = currentIndex - 1

        self.__onOptionPressed(settingNames[nextIndex])


    def __onSetPath(self, qLineEdit):
        '''
        TBA
        '''

        objectName = qLineEdit.objectName()

        if objectName == 'iconPathLE':
            caption = 'File Selection'
            fileFlt = 'Images (*.png *.xpm *.jpg *.ico)'
    
        elif objectName == 'executablePathLE':
            caption = 'File Selection'
            fileFlt = 'All Files (*)'
    
        elif objectName == 'beforeLaunchHookLE':
            caption = 'File Selection'
            fileFlt = 'Python Script (*.py)'
    
        else:
            caption = 'Folder Selection'
            fileFlt = ''

        if caption == 'File Selection':
            path, flt = QFileDialog.getOpenFileName(caption=caption,
                                                    dir='.',
                                                    filter=fileFlt)
        else:
            path = QFileDialog.getExistingDirectory()

        if not path:
            return

        self.__setLineEdit(qLineEdit, path)


    def __onAddEnvPressed(self, qTableWidget):
        '''
        TBA
        '''

        qTableWidget.insertRow(0)


    def __onRemoveEnvPressed(self, qTableWidget):
        '''
        TBA
        '''

        row = qTableWidget.currentRow()
        if row != -1:
            qTableWidget.removeRow(row)


    #######################
    # PREFERENCE COMMANDS #
    #######################


    def __onPreferenceSavePressed(self):
        '''
        TBA
        '''

        configData = {}
        configData['settingsDir'] = self.__getLineEdit(self.__preferenceUi.settingsDirLE)
        configData['configEnv'] = self.__getTableWidget(self.__preferenceUi.configEnvTW)

        if self.__settingsDir != configData['settingsDir']:
            pass
            # TODO: Copy setting JSONS to the new folder

        self.__updateJson(self.__configPath, configData)
        self.__preferenceUi.close()
        self.__setupConfig()


    def __onPreferenceCancelPressed(self):
        '''
        TBA
        '''

        self.__preferenceUi.close()


    def __onPreferenceOpenSettingsPressed(self):
        '''
        TBA
        '''

        os.startfile(self.__settingsDir)


    def __onPreferenceOpenToolRootPressed(self):
        '''
        TBA
        '''

        os.startfile(self.__toolRootDir)


    def __onPreferenceLogPressed(self):
        '''
        TBA
        '''

        print(self.__logPath)
        os.startfile(self.__logPath)


    ###################
    # OPTION COMMANDS #
    ###################


    def __onOptionSavePressed(self):
        '''
        TBA
        '''

        settingData = {}
        settingData['order'] = self.__getLineEdit(self.__optionUi.orderLE)
        settingData['name'] = self.__getLineEdit(self.__optionUi.nameLE)
        settingData['description'] = self.__getLineEdit(self.__optionUi.descriptionLE)
        settingData['color'] = self.__getLineEdit(self.__optionUi.colorLE)
        settingData['background-color'] = self.__getLineEdit(self.__optionUi.backgroundColorLE)
        settingData['iconPath'] = self.__getLineEdit(self.__optionUi.iconPathLE)
        settingData['executablePath'] = self.__getLineEdit(self.__optionUi.executablePathLE)
        settingData['beforeLaunchHook'] = self.__getLineEdit(self.__optionUi.beforeLaunchHookLE)
        settingData['keepGlobalEnv'] = self.__getCheckBox(self.__optionUi.keepGlobalEnvCB)
        settingData['settingEnv'] = self.__getTableWidget(self.__optionUi.settingEnvTW)

        settingName = self.__getLabel(self.__optionUi.fileNameL)
        if settingName.endswith('.json'):
            settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))
            self.__updateJson(settingPath, settingData)
        else:
            settingNameValue = self.__getLineEdit(self.__optionUi.fileNameLE)
            if not settingNameValue:
                print('Empty string') # TODO: This should be rejected in UI side
                return
            settingName = '{}.json'.format(settingNameValue)
            settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))
            self.__writeJson(settingPath, settingData)

        self.__refresh()


    def __onOptionCancelPressed(self):
        '''
        TBA
        '''

        self.__optionUi.close()


    def __onOptionPreviewPressed(self):
        '''
        TBA
        '''

        settingName = self.__getLabel(self.__optionUi.fileNameL)

        from outpostApi import OutpostApi
        outpostApi = OutpostApi(self.__settings[settingName], self.__configEnv)
        environ = outpostApi.createEnviron()
        self.__logger.warning(self.__formatEnviron(environ)) # TODO: Prompt


    def __onOptionOpenPressed(self):
        '''
        TBA
        '''

        settingName = self.__getLabel(self.__optionUi.fileNameL)
        settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))
        os.startfile(settingPath)


    def __onOptionDuplicatePressed(self):
        '''
        TBA
        '''

        result = QMessageBox.question(None, '', 'Duplicate this setting?', QMessageBox.Ok, QMessageBox.Cancel)  # TODO: Implement
        if result == QMessageBox.Ok:
            pass


    def __onOptionDeletePressed(self):
        '''
        TBA
        '''

        result = QMessageBox.question(None, '', 'Delete this setting?', QMessageBox.Ok, QMessageBox.Cancel)  # TODO: Implement
        if result == QMessageBox.Ok:
            settingName = self.__getLabel(self.__optionUi.fileNameL)
            settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))
            os.remove(settingPath)
            self.__refresh()


    def __refresh(self):
        '''
        TBA
        '''

        self.__registerSettings()
        self.__buildSettings()
        self.__optionUi.close()


    ########
    # MISC #
    ########


    def __formatEnviron(self, environ):
        '''
        TBA
        '''

        text =''
        for key in environ:
            text += '\n\n'
            text += '='*100
            text += '\n'
            text += key
            text += '\n'
            text += '='*100
            text += '\n\n'

            value = environ[key]
            sep = os.path.pathsep
            if sep in value:
                for v in value.split(sep):
                    if v == '':
                        continue
                    text += '{}\n'.format(v)
            else:
                text += '{}\n'.format(value)

        return text


    def __readJson(self, jsonPath):
        '''
        TBA
        '''

        with open(jsonPath) as d:
            data = json.load(d)
        return data


    def __writeJson(self, jsonPath, keyValue):
        '''
        TBA
        '''

        with open(jsonPath, 'w') as d:
            dump = json.dumps(keyValue, indent=4, sort_keys=True, ensure_ascii=False)
            d.write(dump)


    def __updateJson(self, jsonPath, keyValue):
        '''
        TBA
        '''

        data = self.__readJson(jsonPath)
        for key in keyValue:
            value = keyValue[key]
            data[key] = value
        self.__writeJson(jsonPath, data)


    def __getLabel(self, qLabel):
        '''
        TBA
        '''

        return qLabel.text()


    def __setLabel(self, qLabel, value):
        '''
        TBA
        '''

        return qLabel.setText(value)


    def __getLineEdit(self, qLineEdit):
        '''
        TBA
        '''

        return qLineEdit.text()


    def __setLineEdit(self, qLineEdit, value):
        '''
        TBA
        '''

        return qLineEdit.setText(value)


    def __getCheckBox(self, qCheckBox):
        '''
        TBA
        '''

        return qCheckBox.isChecked()


    def __setCheckBox(self, qCheckBox, bool):
        '''
        TBA
        '''

        return qCheckBox.setChecked(bool)


    def __getTableWidget(self, qTableWidget):
        '''
        TBA
        '''

        keyValue = {}
        rowCount = qTableWidget.rowCount()
        for row in range(rowCount):

            key = qTableWidget.item(row, 0)
            value = qTableWidget.item(row, 1)
            typ = qTableWidget.item(row, 2)

            try:
                key = key.text()
            except AttributeError:
                continue  # TODO: UI should not allow this to be empty

            try:
                value = value.text()
            except AttributeError:
                value = ''

            typ = typ.text()

            keyValue[key] = [value, typ]

        return keyValue


    def __setTableWidget(self, qTableWidget, keyValue):
        '''
        TBA
        '''

        for i in range(qTableWidget.rowCount() + 1):
            qTableWidget.removeRow(0)

        for i in range(len(keyValue)):
            qTableWidget.insertRow(0)

        if len(keyValue) == 0:
            qTableWidget.insertRow(0)
            return keyValue

        row = 0
        for key, valueTyp in keyValue.items():
            value = valueTyp[0]
            typ = valueTyp[1]
            
            keyItem = QTableWidgetItem()
            valueItem = QTableWidgetItem()
            typItem = QTableWidgetItem()

            for kvt, item in zip([key, value, typ], [keyItem, valueItem, typItem]):
                item.setText(kvt)

            qTableWidget.setItem(row, 0, keyItem)
            qTableWidget.setItem(row, 1, valueItem)
            qTableWidget.setItem(row, 2, typItem)
            row += 1

        return keyValue


    @staticmethod
    def launchOnCommandline(self):
        '''
        TBA
        '''

        pass


if __name__ == '__main__':
    Outpost()
