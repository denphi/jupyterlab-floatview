from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import IntText, Dropdown, BoundedIntText
from IPython.display import clear_output
import numpy as np

class GlueCorrelationsPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    pca = None
    options = {}
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", 'Dimensions', 'Dimensions')        
        self.updateRender()
        
    def createFigureWidget(self):
        traces = []
        params = []
        for param in self.dimensions:
            if hasattr(self.data[param].flatten(), 'codes'):
                params.append(self.data[param].flatten().codes.tolist())
            else:
                params.append(self.data[param].flatten())

        self.mat = np.corrcoef(params)
        self.mat = np.nan_to_num(self.mat)
        self.mat = np.flip(self.mat, axis=1)
        
        trace = {
            'type' : 'heatmap',
            'x' : self.dimensions[::-1],
            'y' : self.dimensions,
            'z' : self.mat,
            'colorscale': 'RdBu',
            'autocolorscale' : False,
            'reversescale' : True,
            'zauto' : False,
            'zmin' : -1,
            'zmax' : 1, 
        }

        layout = {
            'title' : self.options['title'].value,
            'margin' : {
                'l':self.margins['left'].value,
                'r':self.margins['right'].value,
                'b':self.margins['bottom'].value,
                't':self.margins['top'].value
            },
            'showlegend': True,
            'xaxis': {
                'side': 'top'
            },
            'annotations' : []
        }
            
        if self.only_subsets == False:
            traces.append(trace)
            for i in range (len(self.dimensions)):
                for j in range (len(self.dimensions)):
                    currentValue = self.mat[i][j]
                    if abs(currentValue) > 0.6 : 
                        textColor = 'white';
                    else:
                        textColor = 'black';
                        
                    result = {
                        'xref': 'x1',
                        'yref': 'y1',
                        'x': j,
                        'y': i,
                        'text': round(currentValue,2),
                        'showarrow': False,
                        'font': {
                            'color': textColor
                        }
                    }
                    layout['annotations'].append(result);

        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                params = []
                for param in self.dimensions:
                    if hasattr(sset[param].flatten(), 'codes'):
                        params.append(sset[param].flatten().codes.tolist())
                    else:
                        params.append(sset[param].flatten())
                mat = np.corrcoef(params)
                mat = np.nan_to_num(mat, 1)
                mat = np.flip(mat, axis=1)
                trace = {
                    'type' : 'heatmap',
                    'x' : self.dimensions[::-1],
                    'y' : self.dimensions,
                    'z' : mat,
                    'colorscale': 'RdBu',
                    'autocolorscale' : False,
                    'reversescale' : True,
                    'zauto' : False,
                    'zmin' : -1,
                    'zmax' : 1,
                }
                traces.append(trace)

                for i in range (len(self.dimensions)):
                    for j in range (len(self.dimensions)):
                        currentValue = mat[i][j]
                        if abs(currentValue) > 0.6 : 
                            textColor = 'white';
                        else:
                            textColor = 'black';
                            
                            result = {
                                'xref': 'x1',
                                'yref': 'y1',
                                'x': j,
                                'y': i,
                                'text': round(currentValue,2),
                                'showarrow': False,
                                'font': {
                                    'color': textColor
                                }
                            }
                        layout['annotations'].append(result);
            
            
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        

    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget()
        #if self.only_subsets == False:
        #    self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)

        #if self.on_selection_callback is not None:
        #    self.plotly_fig.data[0].on_selection(self.on_selection_callback, True)
        GluePlotly.display(self)


    def updateSelection(self, ids):
        #self.plotly_fig.data[0].update(
        #    selectedpoints=ids,
        #)
        pass;

    def setSubset(self,trace,points,selector): 
        #if(self.parent is not None):
        #    self.parent.updateSelection(points.point_inds)
        pass;    
            
