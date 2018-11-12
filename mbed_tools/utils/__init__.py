from subprocess import Popen, PIPE

def _run_cli_process(cmd, shell=True):
    '''! Runs command as a process and return stdout, stderr and ret code
    @param cmd Command to execute
    @return Tuple of (stdout, stderr, returncode)
    '''

    p = Popen(cmd, shell=shell, stdout=PIPE, stderr=PIPE)
    _stdout, _stderr = p.communicate()
    return _stdout, _stderr, p.returncode
