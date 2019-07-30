from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from plotly import tools
import plotly.graph_objects as go
import numpy as np
from copy import deepcopy

class GlueTablePlotly (GluePlotly):
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)   
        self.updateRender()

    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget()
        GluePlotly.display(self)
        
    def createFigureWidget(self):        
        traces = []        
        dimensions = deepcopy(self.dimensions)
        values = [self.data[col].flatten().tolist() for col in dimensions]  
        header_colors = [self.data.get_component(col).color for col in dimensions]
        coll_fils = ["#F5F5F5" for col in dimensions]
        columnwidth = [80 for col in dimensions]
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
            
                dimensions.append("") #sset.label)
                color = sset.style.color
                header_colors.append(color)
                m = sset.to_mask().flatten()
                v = np.array(["#F5F5F5"]*len(m))
                v2 = np.array([""]*len(m))
                v[m] = color
                values.append(v2)
                coll_fils.append(v)
                columnwidth.append(18)

        trace = {
            'type' : "table",
            'columnwidth' : columnwidth,
            'header' : {
                'values':dimensions,
                'fill' : {'color':header_colors},
                'align' : ['center', 'center'],
                'font' : { 'color' : 'black' },
            },
            'cells' : { 
                'values' : values,
                'fill' : { 'color' : coll_fils },
                'align' : ['left']
            }
        }
        
        traces.append(trace)
        layout = {
            'margin' : {'l':10,'r':10,'b':0,'t':10 },
        }                    
        return go.FigureWidget(traces, layout=layout)

    def updateSelection(self, ids):
        dimensions = self.dimensions
        values = [self.data[col].flatten()[ids].tolist() for col in dimensions]
        coll_fils = ["#F5F5F5" for col in dimensions]        
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                m = sset.to_mask().flatten()
                color = sset.style.color            
                v2 = np.array([""]*len(ids))
                values.append(v2)
                v = np.array(["#F5F5F5"]*len(m))            
                v[m] = color
                coll_fils.append(v[ids])            
        self.plotly_fig.data[0].cells.values = values
        self.plotly_fig.data[0].cells.fill.color = coll_fils

        
