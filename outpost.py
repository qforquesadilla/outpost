import os
import sys
import json
from functools import partial
from collections import OrderedDict

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QFileDialog, QMessageBox, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QSizePolicy, QSpacerItem
from PySide2.QtCore import QFile

#from sgUtil import SgUtil

'''
Outpost
'''


class Outpost(object):

    def __init__(self):
        '''
        '''

        # variables
        #self.__settings = OrderedDict()
        #self.__demo = True

        # config
        self.__toolRootDir = os.path.normpath(os.path.join(os.path.dirname(__file__)))
        self.__configPath = os.path.normpath(os.path.join(self.__toolRootDir, 'data/config.json'))
        self.__logDir = os.path.normpath(os.path.join(self.__toolRootDir, 'data/log'))

        if not self.__setupConfig():
            return

        if not self.__registerSettings():
            return

        self.__setupLogger()


        # ui & commands
        self.__buildUi()
        self.__buildSettings()
        self.__linkCommands()


        # startup
        self.__startup()

        print('\n\n########\n# OUTPOST #\n########\n')
        sys.exit(self.__app.exec_())


    def __setupConfig(self):
        '''
        '''

        # load config
        try:
            configData = self.__readJson(self.__configPath)
        except Exception as err:
            print('Failed to load config: {}'.format(self.__configPath))
            print(str(err))
            return False

        # restore values
        self.__settingsDir = configData.get('settingsDir', None)
        self.__configEnviron = configData.get('configEnviron', None)

        return True


    def __registerSettings(self):
        '''
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
                print('Failed to load config: {}'.format(settingPath))
                print(str(err))

        sortedSettings = sorted(sortedSettings.items(), key=lambda x: int(x[1]['order']))
        for sortedSetting in sortedSettings:
            settingName = sortedSetting[0]
            settingData = sortedSetting[1]
            self.__settings[settingName] = settingData

        return True


    def __buildUi(self):
        '''
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


    def __buildSettings(self):
        '''
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
            
            launchButton = QPushButton(name.upper())
            launchButton.setMinimumHeight(50)
            launchButton.setMinimumWidth(180)
            launchButton.setMaximumHeight(50)
            launchButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)#
            launchButton.setToolTip(description)
            launchButton.clicked.connect(partial(self.__onLaunchPressed, settingName))
            
            styleSheet = 'QPushButton {font-size: 18pt; color: %s; background-color: %s} ' % (color, backgroundColor)
            styleSheet += 'QToolTip {color: #FFFFFF; background-color: #313333; border: 0px;}'
            launchButton.setStyleSheet(styleSheet)

            optionButton = QPushButton('⚙️')
            optionButton.setMinimumHeight(50)
            optionButton.setMinimumWidth(25)
            optionButton.setMaximumHeight(50)
            optionButton.setMaximumWidth(25)
            optionButton.clicked.connect(partial(self.__onOptionPressed, settingName))

            #self.iconQLabel = QLabel()
            #self.iconQLabel.setPixmap(QtGui.QPixmap(icon))

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
        '''

        # main ui
        self.__mainUi.preferencePB.clicked.connect(self.__onPreferencePressed)

        # option ui
        self.__optionUi.iconPathTB.clicked.connect(partial(self.__onSetPath, self.__optionUi.iconPathLE))
        self.__optionUi.executablePathTB.clicked.connect(partial(self.__onSetPath, self.__optionUi.executablePathLE))
        self.__optionUi.beforeLaunchHookTB.clicked.connect(partial(self.__onSetPath, self.__optionUi.beforeLaunchHookLE))

        self.__optionUi.savePB.clicked.connect(self.__onOptionSavePressed)
        self.__optionUi.cancelPB.clicked.connect(self.__onOptionCancelPressed)
        self.__optionUi.openPB.clicked.connect(self.__onOptionOpenPressed)
        self.__optionUi.duplicatePB.clicked.connect(self.__onOptionDuplicatePressed)
        self.__optionUi.deletePB.clicked.connect(self.__onOptionDeletePressed)

        # preference ui
        self.__preferenceUi.settingsDirTB.clicked.connect(partial(self.__onSetPath, self.__preferenceUi.settingsDirLE))
        self.__preferenceUi.savePB.clicked.connect(self.__onPreferenceSavePressed)
        self.__preferenceUi.cancelPB.clicked.connect(self.__onPreferenceCancelPressed)
        self.__preferenceUi.logPB.clicked.connect(self.__onPreferenceLogPressed)
        self.__preferenceUi.openPB.clicked.connect(self.__onPreferenceOpenPressed)


    def __startup(self):
        '''
        Check Shotgun credentials and authenticate.
        Show auth interface if credentials do not exist. 
        '''
        
        if None in [self.__settingsDir]:
            self.__authUi.show()
        else:
            self.__mainUi.show()


    def __setupLogger(self):
        '''
        '''
        pass
        # create log folder
        # start logging


    def dummy(self, *args):
        print('ahoy')


    def __onLaunchPressed(self, *args):
        name = args[0]
        return

        from outpostApi import OutpostApi
        outpostApi = OutpostApi(self.__settings[name], self.__configEnviron)
        outpostApi.launch()


    def __onOptionPressed(self, *args):
        name = args[0]

        settingData = self.__settings[name]
        self.__setLabel(self.__optionUi.fileNameL, name)
        self.__setLineEdit(self.__optionUi.orderLE, str(settingData['order']))
        self.__setLineEdit(self.__optionUi.nameLE, settingData['name'])
        self.__setLineEdit(self.__optionUi.descriptionLE, settingData['description'])
        self.__setLineEdit(self.__optionUi.colorLE, settingData['color'])
        self.__setLineEdit(self.__optionUi.backgroundColorLE, settingData['background-color'])
        self.__setLineEdit(self.__optionUi.iconPathLE, settingData['iconPath'])
        self.__setLineEdit(self.__optionUi.executablePathLE, settingData['executablePath'])

        self.__optionUi.show()


    def __onAddPressed(self):
        print('add')


    def __onPreferencePressed(self):
        self.__setLineEdit(self.__preferenceUi.settingsDirLE, self.__settingsDir)

        self.__preferenceUi.show()


    ###################
    # OPTION COMMANDS #
    ###################


    def __onSetPath(self, qLineEdit):
        objectName = qLineEdit.objectName()

        if objectName == 'iconPathLE':
            caption = 'File Selection'
            fileFlt = 'Images (*.png *.xpm *.jpg)'
    
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


    def __onOptionSavePressed(self):
        settingData = {}
        settingData['order'] = self.__getLineEdit(self.__optionUi.orderLE)
        settingData['name'] = self.__getLineEdit(self.__optionUi.nameLE)
        settingData['description'] = self.__getLineEdit(self.__optionUi.descriptionLE)
        settingData['color'] = self.__getLineEdit(self.__optionUi.colorLE)
        settingData['background-color'] = self.__getLineEdit(self.__optionUi.backgroundColorLE)
        settingData['iconPath'] = self.__getLineEdit(self.__optionUi.iconPathLE)
        settingData['executablePath'] = self.__getLineEdit(self.__optionUi.executablePathLE)
        settingData['beforeLaunchHook'] = self.__getLineEdit(self.__optionUi.beforeLaunchHookLE)
        settingData['keepGlobalEnviron'] = self.__getCheckBox(self.__optionUi.keepOriginalEnvironCB)###############global env vars, launcher level, aplication level

        settingEnviron = {}



        settingName = self.__getLabel(self.__optionUi.fileNameL)
        settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))
        self.__updateJson(settingPath, settingData)

        if not self.__registerSettings():
            return

        self.__buildSettings()
        self.__optionUi.close()


    def __onOptionCancelPressed(self):
        self.__optionUi.close()


    def __onOptionOpenPressed(self):
        settingName = self.__getLabel(self.__optionUi.fileNameL)
        settingPath = os.path.normpath(os.path.join(self.__settingsDir, settingName))
        os.startfile(settingPath)


    def __onOptionDuplicatePressed(self):
        QMessageBox.question(None, '', 'Duplicate this setting?', QMessageBox.Ok, QMessageBox.Cancel)###############



    def __onOptionDeletePressed(self):
        pass


    #######################
    # PREFERENCE COMMANDS #
    #######################


    def __onPreferenceSavePressed(self):
        configData = {}
        configData['settingsDir'] = self.__getLineEdit(self.__preferenceUi.settingsDirLE)
        #configEnviron

        self.__updateJson(self.__configPath, configData)
        # copy settings; copy if folder does not exist

        self.__preferenceUi.close()


    def __onPreferenceCancelPressed(self):
        self.__preferenceUi.close()


    def __onPreferenceLogPressed(self):
        os.startfile(self.__logDir)


    def __onPreferenceOpenPressed(self):
        os.startfile(self.__configPath)





    ########
    # MISC #
    ########

    def __readJson(self, jsonPath):
        with open(jsonPath) as d:
            data = json.load(d)
        return data

    def __writeJson(self, jsonPath, dict):
        with open(jsonPath, 'w') as d:
            dump = json.dumps(dict, indent=4, sort_keys=True, ensure_ascii=False)
            d.write(dump)

    def __updateJson(self, jsonPath, dict):
        data = self.__readJson(jsonPath)
        for key in dict:
            value = dict[key]
            data[key] = value
        self.__writeJson(jsonPath, data)


    def __getLabel(self, qLabel):
        return qLabel.text()

    def __setLabel(self, qLabel, value):
        return qLabel.setText(value)

    def __getLineEdit(self, qLineEdit):
        return qLineEdit.text()

    def __setLineEdit(self, qLineEdit, value):
        return qLineEdit.setText(value)

    def __getCheckBox(self, qCheckBox):
        return qCheckBox.isChecked()

    def __setCheckBox(self, qCheckBox, bool):
        return qCheckBox.setChecked(bool)


    @staticmethod
    def launchOnCommandline(self):
        pass

if __name__ == "__main__":
    Outpost()