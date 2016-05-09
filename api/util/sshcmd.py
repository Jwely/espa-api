'''
Purpose: Easy access to run remote ssh commands.
Original Author: David V. Hill
'''

import paramiko
from api.system.logger import ilogger as logger


class RemoteHost(object):
    client = None

    def __init__(self, host, user, pw=None, debug=False, timeout=None):
        """ """
        self.host = host
        self.user = user
        self.pw = pw
        self.debug = debug
        self.timeout = timeout

    def execute(self, command):
        """ """
        try:
            if self.debug is True:
                logger.debug("Attempting to run [%s] on %s as %s" % (command,
                                                                     self.host,
                                                                     self.user))

            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.pw is not None:
                self.client.connect(self.host,
                                    username=self.user,
                                    password=self.pw,
                                    timeout=self.timeout)
            else:
                self.client.connect(self.host,
                                    username=self.user,
                                    timeout=self.timeout)

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

        finally:
            if self.client is not None:
                self.client.close()
                self.client = None

    def execute_script(self, script, interpreter):
        raise NotImplementedError

    def put(self, localpath, remotepath, mkdirs=True):
        raise NotImplementedError

    def get(self, remotepath, localpath, mkdirs=True):
        raise NotImplementedError
