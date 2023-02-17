#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

from __future__ import print_function
from glob import glob
import os


from jupyter_packaging import (
    create_cmdclass, install_npm, ensure_targets,
    combine_commands, ensure_python,
    get_version, skip_if_exists
)

from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

# The name of the project
name = 'floatview'
labext_name = 'jupyterlab-floatview'


# Get our version
version = get_version(os.path.join(name, '_version.py'))

lab_path = os.path.join(HERE, name, 'labextension')

# Representative files that should exist after a successful build
jstargets = [
    os.path.join(lab_path, "package.json"), 
]

package_data_spec = {
    name: [
        '*'
    ]
}

data_files_spec = [
    ("share/jupyter/labextensions/%s" % labext_name, lab_path, "**"),
    ("share/jupyter/labextensions/%s" % labext_name, HERE, "install.json")
]


cmdclass = create_cmdclass(
    'jsdeps',
    package_data_spec=package_data_spec,
    data_files_spec=data_files_spec
)

js_command = combine_commands(
    install_npm(HERE, build_cmd='build', npm=["jlpm"]),
    ensure_targets(jstargets),
)

is_repo = os.path.exists(os.path.join(HERE, ".git"))
if is_repo:
    cmdclass["jsdeps"] = js_command
else:
    cmdclass["jsdeps"] = skip_if_exists(jstargets, js_command)


setup_args = dict(
    name            = name,
    description     = 'A floatview output widget for JupyterLab + GlueViz Visualization with plotly',
    version         = version,
    scripts=glob(os.path.join('scripts', '*')),
    cmdclass=cmdclass,
    packages        = find_packages(),
    author          = 'Daniel Mejia',
    author_email    = 'denphi@denphi.com',
    url             = 'https://github.com/denphi/jupyterlab-floatview',
    license         = 'BSD',
    python_requires = ">=3.7",
    platforms       = "Linux, Mac OS X, Windows",
    keywords        = ['Jupyter', 'Widgets', 'IPython'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Jupyter',
        'Framework :: Jupyter :: JupyterLab',
        'Framework :: Jupyter :: JupyterLab :: 3',
        'Framework :: Jupyter :: JupyterLab :: Extensions',
        'Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt',
    ],
    include_package_data = True,
    install_requires = [
        'jupyter_packaging',
        'ipywidgets>=7.5.0,<9.0.0',
        'jupyterlab>=3.0.0,<4'
        'plotly>=4.0.0',
        'scikit-learn>=0.19.0',        
        'glueviz>=0.15.2',
        'networkx>=2.2',
        'colorlover>=0.3.0',
        'qgrid>=1.3.0'
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
