import os
import sys
import subprocess

'''
Outpost API
'''


class OutpostApi(object):

    def __init__(self, settingData, additionalEnviron):
        '''
        "AHOY": ["PUPU", "set"]
        '''
        self.__executablePath = settingData['executablePath']
        self.__beforeLaunchHook = settingData['beforeLaunchHook']
        self.__keepOriginalEnviron = bool(settingData['keepGlobalEnviron'])
        self.__settingEnviron = settingData['settingEnviron']
        self.__additionalEnviron = additionalEnviron

        self.__createEnviron()


    def launch(self):

        if self.__beforeLaunchHook:
            execfile(self.__beforeLaunchHook)

        command = '{}'.format( self.__executablePath)


        subprocess.Popen(command, shell=True, env=environ)


    def __createEnviron(self):

        print('self.__settingEnviron:')
        print(self.__settingEnviron)
        print('self.__additionalEnviron:')
        print(self.__additionalEnviron)

        if self.__keepOriginalEnviron:
            environ = os.environ
        else:
            environ = {}

        for key, value in self.__additionalEnviron.items():

            if value[1] == 'set':
                environ[key] = value[0]

            elif value[1] == 'prepend':
                environ[key] = value[0] + os.path.pathsep + environ[key]

            elif value[1] == 'append':
                environ[key] = environ[key] + os.path.pathsep + value[0]


        #for self.__settingEnviron





if __name__ == "__main__":

    executablePath = sys.argv[1]
    envVars = sys.argv[2]

    from outpostApi import OutpostApi
    outpostApi = OutpostApi(executablePath, envVars)
    outpostApi.launch()