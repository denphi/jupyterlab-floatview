from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
import plotly.graph_objs as go

class GlueTablePlotly (GluePlotly):
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)   
        values = [self.data[col].tolist() for col in self.dimensions]   
        layout = {
            'margin' : {'l':10,'r':10,'b':0,'t':10 },     
        }        
        self.plotly_fig = go.FigureWidget([go.Table(
            header=dict(values=dimensions,
                        fill = dict(color='#C2D4FF'),
                        align = ['left'] * 5),
            cells=dict(values=values,
                       fill = dict(color='#F5F8FF'),
                       align = ['left'] * 5))], layout=layout)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        dimensions = self.plotly_fig.data[0].header.values
        values = [self.data[col][ids].tolist() for col in dimensions]
        self.plotly_fig.data[0].cells.values = values
        