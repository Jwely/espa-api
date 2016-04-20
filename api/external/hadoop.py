from api.util.dbconnect import db_instance
from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util.sshcmd import RemoteHost


class HadoopHandler(object):
    config = ConfigurationProvider()
    db = db_instance()

    def list_jobs(self):
        return self._remote_cmd(['hadoop', 'job', '-list'])

    def kill_job(self, jobid):
        return self._remote_cmd('hadoop job -kill {}'.format(jobid))

    def _remote_cmd(self, cmd):
        params = ('hadoop.master',
                  'landsatds.username',
                  'landsatds.password')

        vals = self.config.get(params)

        remote = RemoteHost(host=vals[0], user=vals[1], pw=vals[2])

        resp = remote.execute(cmd)

        return resp
