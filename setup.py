"""
Make polls for wiki polling for house meetings.
	
Amy Chern <chernamy@umich.edu>
Nilay Muchhala <nilaym@umich.edu>
"""

from setuptools import setup

setup(
	  name='make_poll',
	  version='0.1.0',
	  packages=['make_poll'],
	  include_package_data=True,
	  install_requires=[
						'click==6.7',
						'sh==1.12.14',
						'pylint==2.1.1',
						'pydocstyle==2.0.0',
						'google-api-python-client==1.7.5',
						],
	  entry_points={
	  'console_scripts': [
						  'make_poll = make_poll.__main__:main',
        ]
	  },
	  )
