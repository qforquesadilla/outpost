import os
import sys
import subprocess

'''
Outpost API
'''


class OutpostApi(object):

    def __init__(self, executablePath, envVars):
        '''
        '''
        self.__executablePath = executablePath
        self.__envVars = envVars

        self.__setEnvVars()


    def launch(self):
        
        command = '{}'.format( self.__executablePath)
        environ = self.__envVars

        subprocess.Popen(command, shell=True, env=environ)


    def __setEnvVars(self):
        pass



if __name__ == "__main__":

    executablePath = sys.argv[1]
    envVars = sys.argv[2]

    from outpostApi import OutpostApi
    outpostApi = OutpostApi(executablePath, envVars)
    outpostApi.launch()