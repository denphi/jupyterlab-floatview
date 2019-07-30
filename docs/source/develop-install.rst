
Developer install
=================


To install a developer version of floatview, you will first need to clone
the repository::

    git clone https://github.com/denphi/jupyterlab-floatview
    cd floatview

Next, install it with a develop install using pip::

    pip3 install -e .


Install the JupyterLab extension with::

    jupyter labextension install @jupyter-widgets/jupyterlab-manager@1.0.1
    jupyter labextension install jupyterlab-datawidgets@6.2.0
    jupyter labextension install jupyterlab-plotly@1.0.0
    jupyter labextension install plotlywidget@1.0.0
    jupyter labextension install .


older versions::

    jupyter labextension install @jupyterlab/plotly-extension@0.18.2
    jupyter labextension install plotlywidget@0.9.1
    jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.38.1
    jupyter labextension install jupyterlab-floatview@0.1.11

.. links

.. _`appropriate flag`: https://jupyter-notebook.readthedocs.io/en/stable/extending/frontend_extensions.html#installing-and-enabling-extensions
