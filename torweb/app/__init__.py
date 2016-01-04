import os


def get_path(self):
    '''
    Returns the path of the static folder
    '''
    os.path.abspath(os.path.split(__file__)[0])
