# Floatview Stats

<table>
    <tr>
        <td>Latest Release</td>
        <td>
            <a href="https://pypi.org/project/floatview/"/>
            <img src="https://badge.fury.io/py/floatview.svg"/>
        </td>
    </tr>
    <tr>
        <td>PyPI Downloads</td>
        <td>
            <a href="https://pepy.tech/project/floatview"/>
            <img src="https://pepy.tech/badge/floatview/month"/>
        </td>
    </tr>
</table>

# Floatview

A floatview output widget for JupyterLab and a data explorer for glue/iplotly

## Installation

If you use jupyterlab:

```bash
pip install floatview
jupyter labextension install @jupyterlab/plotly-extension@0.18.2
jupyter labextension install plotlywidget@0.9.1
jupyter labextension install @jupyter-widgets/jupyterlab-manager@0.38.1
jupyter labextension install jupyterlab-floatview@0.1.11
```

## Usage

The floatview widget is used as a context manager, just like ipywidgets' output
widget.

```python
from floatview import Floatview
from ipywidgets import IntSlider

sc = Floatview(title='Floatview Output', mode='tab-after')
sl = IntSlider(description='Some slider')
with sc:
    display(sl)
```


When a single output is displayed in a Floatview, it is allowed to occupy all of
the vertical space available. If more content is displayed, the natural height
is used instead.

The gluemanagerwidget is used as a data/visualization manager for a glue dataset.

```python
from floatview import GlueManagerWidget
from pandas import read_csv

data = read_csv('your_data.csv', index_col=False, usecols=cols)
gmw = GlueManagerWidget(data, modal=True, label="Data")
```

![floatview](floatview.png)



## Available Visualizations
```python
#Histogram (support 1 component)
view = gmw.gluemanager.newView("histogram", ["PULocationID"], "Histogram");
```
![histogram](histogram.png)

```python
#Scatter (support 2/n components)
view = gmw.gluemanager.newView("scatter", ["PULocationID", "DOLocationID"], "Scatter");
view = gmw.gluemanager.newView("composed_scatter", ["trip_distance", "payment_type", 'passenger_count'], "Scatter");
```

![scatter](scatter.png)

```python
#ErrorBar (support 2/n components)
view = gmw.gluemanager.newView("errorbar", ["trip_distance", "total_amount"], "Error");
view = gmw.gluemanager.newView("composed_errorbar", ["trip_distance", "payment_type", 'passenger_count'], "Error");
```
![error](error.png)


```python 
#Polynomial Fitting 2-n degree (support n components)
view = gmw.gluemanager.newView("composed_polyfit_3d", ["trip_distance", "total_amount"], "Polyfit");
```
![polyfit](polyfit.png)

```python 
#scatter 3D (support 3 components)
view = gmw.gluemanager.newView("scatter3D", ["trip_distance", "total_amount", "passenger_count"], "Scatter3D");
```
![scatter3d](scatter3d.png)

```python 
#Contours 2D (support 2 components)
view = gmw.gluemanager.newView("contour", ["trip_distance", "total_amount"], "Contour");
```
![contour](contour.png)

```python 
#Table (support n components)
view = gmw.gluemanager.newView("table", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Table");
```
![table](table.png)

```python 
#Parallel coordinatess (support n components)
view = gmw.gluemanager.newView("parallels", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Parallels");
```
![parallels](parallels.png)

```python 
#Parallel categories (support n components)
view = gmw.gluemanager.newView("parallelscat", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Parallels Categ");
```
![parallelscat](parallelscat.png)

```python 
#Sankey (support n components)
view = gmw.gluemanager.newView("sankey", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Sankey");
```
![sankey](sankey.png)

```python 
#Sunburst (support n components)
view = gmw.gluemanager.newView("sunburst", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Sunburst");
```
![sunburst](sunburst.png)

```python 
#Sankey Tree (support n components)
view = gmw.gluemanager.newView("sankeytree", ['total_amount', 'payment_type', 'passenger_count', ], "Sankey Tree");
```
![sankeytree](sankeytree.png)

```python 
#Scatter Matrix (support n components)
view = gmw.gluemanager.newView("scattermatrix", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "scatter Matrix");
```
![scattermatrix](scattermatrix.png)

```python 
#Correlation Matrix (support n components)
view = gmw.gluemanager.newView("corrcoef", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Correlation Matrix");
```
![corrcoef](corrcoef.png)

```python 
#Principal components (support n components)
view = gmw.gluemanager.newView("pca", ['passenger_count', 'trip_distance', 'total_amount', 'payment_type'], "Principal components");
```
![pca](pca.png)


```python 
#Network (support 2 components)
view = gmw.gluemanager.newView("network", ['trip_distance', 'total_amount'], "Network");
```
![network](network.png)


```python 
#Image (support 3 components)
view = gmw.gluemanager.newView("image", ["trip_distance", "total_amount", 'passenger_count'], "Image");
```
![image](image.png)


```python 
#Lines (support n components)
view = gmw.gluemanager.newView("composed_lines", ["trip_distance", "payment_type", 'passenger_count'], "Lines");
```
![lines](lines.png)

