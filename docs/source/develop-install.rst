
Developer install
=================


To install a developer version of floatview, you will first need to clone
the repository::

    git clone https://github.com/denphi/jupyterlab-floatview
    cd floatview

Next, install it with a develop install using pip::

    pip3 install -e .


Install the JupyterLab extension with::

    jupyter labextension install @jupyter-widgets/jupyterlab-manager@3.0.0
    jupyter labextension install jupyterlab-plotly@5.12.0
    jupyter labextension install plotlywidget@4.14.3
    jupyter labextension install .
    

.. links

.. _`appropriate flag`: https://jupyter-notebook.readthedocs.io/en/stable/extending/frontend_extensions.html#installing-and-enabling-extensions
