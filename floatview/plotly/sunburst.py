from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
from ipywidgets import IntText, Dropdown
from IPython.display import clear_output
import numpy as np
from collections import deque

class GlueSunburstPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    pca = None
    options = {}
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles('', '', '')        
        self.updateRender()
        
    def createFigureWidget(self):
        data_lines = []
        traces = []
        i=0
        if self.only_subsets == False:
            colors = [i for r in range(self.data.size)]
            colorscale = [[0,'#EEEEEE']]
        else:
            colors = []
            colorscale = []
            i=-1

        values = []
        labels = []
        nodes_id = []
        parents = []
        self.masks = []
        colors = []
        df = self.data.to_dataframe()
        ids = 1
        queue = deque()
        color_set = [
            'rgb(255,255,255)',
            'rgb(49,54,149)',
            'rgb(165,0,38)',
            'rgb(69,117,180)',
            'rgb(215,48,39)',
            'rgb(116,173,209)',
            'rgb(244,109,67)',
            'rgb(171,217,233)',
            'rgb(253,174,97)',
            'rgb(224,243,248)',
            'rgb(254,224,144)',
        ]
        c_diff = len(self.dimensions) - len(color_set)
        if (c_diff >= 0):
            color_set.extend(['rgb(254,224,144)' for c in range(c_diff+1)])
        
        queue.append({'id':ids,'dimension':0, 'label':"Data", 'mask':[True for i in range(self.data.size)], 'parent':''})
        while len(queue) > 0:
            toprocess = queue.popleft()
            mask = toprocess['mask']
            id = toprocess['id']
            label = toprocess['label']
            value = np.count_nonzero(mask)
            if value > 0:
                labels.append(label)
                values.append(value)
                parents.append(toprocess['parent'])
                nodes_id.append(id)
                self.masks.append(mask)
                colors.append(color_set[toprocess['dimension']])
                data = df[mask]
                if toprocess['dimension'] < len(self.dimensions):
                    dimension = self.dimensions[toprocess['dimension']]
                    dvalues = np.unique(data[dimension].ravel())
                    if hasattr(self.data[dimension].flatten(), 'codes'):
                        for val in dvalues:
                            ids += 1
                            process = {'id':ids,'dimension':toprocess['dimension']+1, 'label':str(val), 'parent':toprocess['id']}
                            process['mask'] = (mask & (self.data[dimension] == val))
                            queue.append(process)
                                          
                    elif len(dvalues) < 15:
                        for val in dvalues:
                            ids += 1
                            process = {'id':ids,'dimension':toprocess['dimension']+1, 'label':str(val), 'parent':toprocess['id']}
                            process['mask'] = (mask & (self.data[dimension] == val))
                            queue.append(process)
                    else:    
                        hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins='auto')
                        for edge in range(len(bin_edges)-1):
                            ids += 1
                            label = "{:.1f}".format(bin_edges[edge]) + " - " + "{:.1f}".format(bin_edges[edge+1])
                            process = {'id':ids,'dimension':toprocess['dimension']+1, 'label':label, 'parent':toprocess['id']}
                            if edge == 0:
                                process['mask'] = (mask & ((self.data[dimension] >= bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1])))
                            else :
                                process['mask'] = (mask & ((self.data[dimension] > bin_edges[edge])  & (self.data[dimension] <= bin_edges[edge+1])))
                            queue.append(process)
        trace = {
            'type': "sunburst",
            'ids': nodes_id,
            'labels': labels,
            'parents': parents,
            'values':  values,
            'branchvalues' : 'total',
            'maxdepth' : 4,
            'outsidetextfont': {
                'size': 20, 
                'color': "#377eb8"
            },
            'leaf': {
                'opacity' : 1
            },
            'marker': {
                'line': {
                    'width': 2
                },
                'colors' : colors
            },
            'domain':{
                'x': [0, 0.9],
                'y': [0, 1],
            },              
        }
        traces.append(trace)
        
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
                'title' : self.options['xaxis'].value,
                'range' : [0,1],
                'showgrid':False,
                'showline':False,
                'showticklabels':False,
                'zeroline':False
            },
            'yaxis': {
                'title' : self.options['yaxis'].value,
                'range' : [0,1],
                'showgrid':False,
                'showline':False,
                'showticklabels':False,
                'zeroline':False                
            },            
        }
        
        for i in range(len(self.dimensions)):
            dimension = self.dimensions[i]
            trace = {
                'type': "scatter",
                'name' : dimension, 
                'textposition' : 'middle right',
                'x' : [-1000],
                'y' : [i],
                'mode' : 'markers',
                'marker': {
                    'color' : color_set[i+1],
                    'size' : 20,
                    'line': {
                        'width': 0,
                    },
                    'symbol' : 'square'
                }
            }
            traces.append(trace)




            
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        

    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget()
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_click(lambda x,y,z : self.setSubset(x,y,z), True)

        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_click(self.on_selection_callback, True)
        GluePlotly.display(self)


    def updateSelection(self, ids):
        #self.plotly_fig.data[0].update(
        #    selectedpoints=ids,
        #)
        pass;

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            mask = None
            for p in points.point_inds:
                if p > 0:
                    if mask is None:
                        mask = self.masks[p]
                    else :
                        mask = mask | self.masks[p+1]                        
            if mask is not None:
                point_inds = np.nonzero(mask)[0]
                self.parent.updateSelection(point_inds)
