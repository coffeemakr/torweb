#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='torweb',
      version='0.0',
      description='Tor webinterface',
      url='https://github.com/coffeemakr/torweb',
      packages=find_packages(),
      include_package_data = True,
      package_data = {
        'torweb.app': ['*.html', 
                       'partials/*.html',
                       'js/*.js',
                       'css/*.css'],
      }

     )
