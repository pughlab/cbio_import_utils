import os
import errno
import subprocess
import shlex


class DirectoryExists(Exception):

    def __init__(self, message, path):
        self.message = message
        self.path = path


def make_dir(path, mode=0755):
    """
    create a new directory if not already exist
    """
    try:
        os.makedirs(path, mode)
    except OSError as e:
        if e.errno == errno.EEXIST:
            raise DirectoryExists("Directory already exists: {}".format(path), path)
        raise


def run(cmd, cwd=None, shell=False):
    """
    execute command on shell terminal

    :param cmd: command to run
    :type cmd: string
    :param cwd: the working directory
    :type cwd: string
    :param bool shell: allow shell features

    :return triple of exit_code, stdout, stderr
    """
    p = subprocess.Popen(shlex.split(cmd), cwd=cwd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    exit_code = p.poll()

    return exit_code, stdout, stderr