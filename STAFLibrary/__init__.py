# -*- coding: UTF-8 -*-
"""
Package: robotframework-STAFLibrary
Module:  STAFLibrary
"""
__version__ = '1.0'
__author__  = 'Zhe Li <zhe.li@lavasoft.com>'
#append STAF lib path into sys.path if it is not there.
import sys
STAF_LIB_PATH = '/opt/staf/lib'
if not '/opt/staf/lib' in sys.path:
    sys.path.append(STAF_LIB_PATH)
import os, PySTAF

class STAFLibrary:
    """
    STAF Library is a test library for robot framework.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = __version__
    _default_log_level = 'INFO'

    def __init__(self):
        import PySTAF, sys
        reload(PySTAF)
        reload(sys)

        try:
            self._handle = PySTAF.STAFHandle("staf_library")
        except PySTAF.STAFException, e:
            print('Error registering with STAF, RC: %d' % e.rc)
            sys.exit(e.rc)
        self._dst_ip = ''

    def staf_conf(self, dst_ip):
        self._dst_ip = dst_ip

    def release_staf_handle(self):
        self._handle.unregister()

    def copy_directory_remote(self, source, dst, dst_ip = None):
        """
        Copy local directory to the remote machine

        Parameters:
        | source=<string>   | path to the source folder                                              |
        | dst=<string>      | the target folder path                                                 |
        | [dst_ip=<string>] | Optional overide to the default destination IP address set in __init__ |
        """
        import os
        reload(os)

        if not dst_ip:
            dst_ip = self._dst_ip
        source = self._wrap(os.path.abspath(source))
        dst    = self._wrap(dst.replace('\\', '\\\\'))

        return self._submit_request('FS', 'COPY DIRECTORY %s TODIRECTORY %s TOMACHINE %s RECURSE KEEPEMPTYDIRECTORIES'
                % (source, dst, self._wrap(dst_ip)))

    def copy_file_remote(self, source, dst, dst_ip = None):
        """
        Copy local file to remote machine

        Parameters:
        | source=<string>   | path to the source file                                                |
        | dst=<string>      | the target path                                                        |
        | [dst_ip=<string>] | Optional overide to the default destination IP address set in __init__ |
        """
        import os
        reload(os)

        if not dst_ip:
            dst_ip = self._dst_ip
        source = self._wrap(os.path.abspath(source))
        dst    = self._wrap(self._double_the_slash(dst))

        return self._submit_request('FS', 'COPY FILE %s TOFILE %s TOMACHINE %s'
                % (source, dst, self._wrap(dst_ip)))

    def run_command_remote(self, cmd, params, workdir, dst_ip = None):
        """
        run command on remote machine

        Parameters:
        | cmd=<string>       | full path to the command                                               |
        | params=<string>]   | command parameters                                                     |
        | [workdir=<string>] | Optional command work folder                                           |
        | [dst_ip=<string>]  | Optional overide to the default destination IP address set in __init__ |
        """

        if cmd and workdir:
            request = ['START COMMAND "%s"' % self._double_the_slash(cmd), 
                    'WORKDIR "%s"' % self._double_the_slash(workdir),
                    'SAMECONSOLE']
            if params:
                request.insert(1, 'PARMS "%s"' % self._double_the_slash(params))
            if not dst_ip:
                dst_ip = self._dst_ip
            return self._submit_request('PROCESS', ' '.join(request), dst_ip)

    def _submit_request(self, service = None, params = None, machine ='local'):
        if service:
            self._debug('Sending command: [staf %s %s %s]' % (machine, service, params))
            try:
                result = self._handle.submit(machine, service, params)
            except:
                raise Exception('Failed to send request: [staf %s %s %s]' 
                        % (machine, service, params))
            else:
                return self._check_result(result)

    def _double_the_slash(self, s):
        return s.replace('\\', '\\\\')

    def _check_result(self, result):
        import PySTAF
        reload(PySTAF)

        assert result.rc == PySTAF.STAFResult.Ok, 'Request returned an error!'
        if result.resultObj:
            #check exit code as well
            try:
                exitcode = int(result.resultObj['rc']) 
                assert 0 == exitcode, 'Error! Exit code: [%d]' % exitcode
            except:
                pass

        return True

    def _wrap(self, data):
        return ':%d:%s' % (len(data), data)

    def _warn(self, msg):
        self._log(msg, 'WARN')

    def _debug(self, msg):
        self._log(msg, 'DEBUG')

    def _info(self, msg):
        self._log(msg, 'INFO')

    def _log(self, msg, level = None):
        msg = msg.strip()
        if not level:
            level = self._default_log_level
        if msg:
            print('*%s* %s' % (level.upper(), msg))

if __name__== '__main__':
    from robotremoteserver import RobotRemoteServer
    RobotRemoteServer(STAFLibrary(), *sys.argv[1:])
