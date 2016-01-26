import os

__all__ = ['get_path', 'get_app_dir']

_BASEDIR = os.path.abspath(os.path.split(__file__)[0])

_APP_DIR = os.path.join(_BASEDIR, 'app')


def get_path():
    '''
    Returns the path of the static folder
    '''
    return _BASEDIR


def get_app_dir():
    return _APP_DIR
