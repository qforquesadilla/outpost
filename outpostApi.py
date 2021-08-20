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
        self.__keepOriginalEnviron = bool(settingData['keepOriginalEnviron'])
        self.__settingEnviron = settingData['settingEnviron']
        self.__additionalEnviron = additionalEnviron



        self.__setEnviron()


    def launch(self):

        if self.__beforeLaunchHook:
            execfile(self.__beforeLaunchHook)

        command = '{}'.format( self.__executablePath)


        subprocess.Popen(command, shell=True, env=environ)


    def __setEnviron(self):

        if self.__keepOriginalEnviron:
            environ = os.environ
        else:
            environ = {}







if __name__ == "__main__":

    executablePath = sys.argv[1]
    envVars = sys.argv[2]

    from outpostApi import OutpostApi
    outpostApi = OutpostApi(executablePath, envVars)
    outpostApi.launch()