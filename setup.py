#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
from os.path import join as pjoin


from setupbase import (
    create_cmdclass, install_npm, ensure_targets,
    find_packages, combine_commands, ensure_python,
    get_version, HERE
)

from setuptools import setup


# The name of the project
name = 'floatview'

# Ensure a valid python version
ensure_python('>=3.3')

# Get our version
version = get_version(pjoin(name, '_version.py'))

lab_path = pjoin(HERE, name, 'labextension')

# Representative files that should exist after a successful build
jstargets = [
    pjoin(HERE, 'lib', 'plugin.js'),
]

package_data_spec = {
    name: [
        'labextension/*.tgz'
    ]
}

data_files_spec = [
    ('share/jupyter/lab/extensions', lab_path, '*.tgz'),
]


cmdclass = create_cmdclass('jsdeps', package_data_spec=package_data_spec,
    data_files_spec=data_files_spec)
cmdclass['jsdeps'] = combine_commands(
    install_npm(HERE, build_cmd='build:all'),
    ensure_targets(jstargets),
)

long_description = ""
with open("README.md", "r") as fh:
    long_description = fh.read()

setup_args = dict(
    name            = name,
    description     = 'A floatview output widget for JupyterLab + GlueViz Visualization with plotly',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version         = version,
    scripts         = glob(pjoin('scripts', '*')),
    cmdclass        = cmdclass,
    packages        = find_packages(),
    author          = 'Project Jupyter contributor',
    author_email    = 'denphi@denphi.com',
    url             = 'https://github.com/denphi/jupyterlab-floatview',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'Widgets', 'IPython'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Jupyter',
    ],
    include_package_data = True,
    install_requires = [
        'ipywidgets>=7.5.0',
        'plotly>=4.0.0',
        'scikit-learn>=0.19.0',        
        'glueviz>=0.15.2',
        'networkx>=2.2',
        'colorlover>=0.3.0'
    ],
    extras_require = {
        'test': [
            'pytest',
            'pytest-cov',
            'nbval',
        ],
        'examples': [
            # Any requirements for the examples to run
        ],
        'docs': [
            'sphinx>=1.5',
            'recommonmark',
            'sphinx_rtd_theme',
            'nbsphinx>=0.2.13',
            'jupyter_sphinx',
            'nbsphinx-link',
            'pytest_check_links',
            'pypandoc',
        ],
    },
    entry_points = {
    },
)

if __name__ == '__main__':
    setup(**setup_args)
