'''
Purpose: Easy access to run remote ssh commands.
Original Author: David V. Hill
'''

import os

import paramiko
from api.system.logger import ilogger as logger


class RemoteHost(object):
    client = None

    def __init__(self, host, user, pw=None, debug=False, timeout=None):
        """ """
        self.host = host
        self.user = user
        self.debug = debug

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(hostname=host,
                            username=user,
                            password=pw,
                            timeout=timeout)

    def execute(self, command):
        """ """
        try:
            if self.debug is True:
                logger.debug("Attempting to run [%s] on %s as %s" % (command,
                                                                     self.host,
                                                                     self.user))

            stdin, stdout, stderr = self.client.exec_command(command)
            stdin.close()

            return {'stdout': stdout.readlines(), 'stderr': stderr.readlines()}

        except paramiko.SSHException as e:
            logger.debug('Failed running [{}]'
                         ' on {} as {} exception: {}'.format(command,
                                                             self.host,
                                                             self.user,
                                                             e))

            return e

    def execute_script(self, script, interpreter):
        raise NotImplementedError

    def put(self, localpath, remotepath, mkdirs=True):
        raise NotImplementedError

    def get(self, remotepath, localpath, mkdirs=True):
        if mkdirs:
            path = os.path.split(localpath)[0]
            if not os.path.exists(path):
                os.makedirs(path)

        sftp = self.client.open_sftp()

        sftp.get(remotepath, localpath)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client is not None:
            self.client.close()
            self.client = None
