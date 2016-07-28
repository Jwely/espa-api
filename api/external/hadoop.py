from api.providers.configuration.configuration_provider import ConfigurationProvider
from api.util.sshcmd import RemoteHost
import socket
config = ConfigurationProvider()


class HadoopHandler(object):

    def list_jobs(self):
        return self._remote_cmd('hadoop job -list')

    def kill_job(self, jobid):
        return self._remote_cmd('hadoop job -kill {}'.format(jobid))

    def job_names_ids(self):
        cmd = "hadoop job -list | egrep '^job' | awk '{print $1}' | " \
              "xargs -n 1 -I {} sh -c \"hadoop job -status {} | " \
              "egrep '^tracking' | awk '{print \$3}'\" | " \
              "xargs -n 1 -I{} sh -c \" echo -n {} | " \
              "sed 's/.*jobid=//'; echo -n ' ';curl -s -XGET {} | " \
              "grep 'Job Name' | sed 's/.* //' | sed 's/<br>//'\""
        _stdout = self._remote_cmd(cmd)['stdout']
        _id_name_list = [str(i).rstrip('\n') for i in _stdout]
        resp = {}
        for ids in _id_name_list:
            ids_list = ids.split(' ')
            resp[ids_list[1]] = ids_list[0]
        return resp

    def slave_ips(self):
        _stdout = self._remote_cmd("cat ~/bin/hadoop/conf/slaves")['stdout']
        _host_list = [str(i).rstrip('\n') for i in _stdout]
        return [socket.gethostbyname(i) for i in _host_list]

    def master_ip(self):
        master_host = config.get('hadoop.master')
        return socket.gethostbyname(master_host)

    def _remote_cmd(self, cmd):
        params = ('hadoop.master',
                  'landsatds.username',
                  'landsatds.password')

        remote = RemoteHost(*config.get(params))
        resp = remote.execute(cmd)
        return resp
