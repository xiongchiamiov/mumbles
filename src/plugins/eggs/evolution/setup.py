#------------------------------------------------------------------------
# A Mumbles Plugin for Evolution
#   Copyright (c) 2007 dot_j <dot_j[AT]mumbles-project[DOT]org>
#   Lisenced under the GPL
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j[AT]mumbles-project[DOT]org'
__doc__ = 'An Evolution plugin for mumbles'
__version__ = '0.1'

setup(
    name='EvolutionMumbles',
    version=__version__,
    description=__doc__,
    author=__author__,
    packages=['evolutionmumbles'],
    package_dir={'evolutionmumbles':'src'},
    entry_points='''
    [mumbles.plugins]
    EvolutionMumbles = evolutionmumbles:EvolutionMumbles
    '''
)

# copy egg file to plugin directory
copy("dist/EvolutionMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")
