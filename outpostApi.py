import os
import sys
import subprocess

'''
Outpost API
'''


class OutpostApi(object):

    def __init__(self, settingData, additionalEnv):
        '''
        TBA
        '''

        self.__executablePath = settingData['executablePath']
        self.__beforeLaunchHook = settingData['beforeLaunchHook']
        self.__keepOriginalEnv = bool(settingData['keepGlobalEnv'])
        self.__settingEnv = settingData['settingEnv']
        self.__additionalEnv = additionalEnv


    def launch(self):
        '''
        TBA
        '''
        
        environ = self.createEnviron()
        if self.__beforeLaunchHook:
            execfile(self.__beforeLaunchHook)

        self.__setCurrentDir()

        command = '{}'.format(self.__executablePath)
        subprocess.Popen(command, env=environ, creationflags=subprocess.CREATE_NEW_CONSOLE)
        print('\nLaunching {}'.format(command))


    def createEnviron(self):
        '''
        TBA
        '''

        if self.__keepOriginalEnv:
            environ = os.environ.copy()  # TODO: This should not change when launching multiple times (prepend/append bug)
        else:
            environ = {}

        for env in [self.__additionalEnv, self.__settingEnv]:  # TODO: Confirm order
            for key, valueTyp in env.items():
                value = valueTyp[0]
                typ = valueTyp[1]
                currentValue = environ.get(key, '')

                if typ == 'set':
                    environ[key] = value
                elif typ == 'prepend':
                    environ[key] = value + os.path.pathsep + currentValue
                elif typ == 'append':
                    environ[key] = currentValue + os.path.pathsep + value

        return environ


    def __setCurrentDir(self):
        '''
        TBA
        '''

        if os.name == 'nt':
            path = os.environ['USERPROFILE']
        elif os.name == 'posix':
            path = os.path.expanduser('~')

        os.chdir(path)


if __name__ == "__main__":
    executablePath = sys.argv[1]
    envVars = sys.argv[2]

    from outpostApi import OutpostApi
    outpostApi = OutpostApi(executablePath, envVars)
    outpostApi.launch()
