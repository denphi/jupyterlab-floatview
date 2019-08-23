from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import IntText, Dropdown
from IPython.display import clear_output
import numpy as np
from collections import deque
import colorlover as cl

class GlueSunburstPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    pca = None
    options = {}
    default_color = "Dataset"
   
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        
        self.DefaultLayoutTitles('', '', '')
        self.options['grouping_limit'] = IntText(description = 'Group limiy', value = 12)
        self.options['grouping_limit'].observe(lambda v:self.updateRender(), names='value')
        cl_options = list(cl.scales['8']['qual'].keys())
        cl_options.append(GlueSunburstPlotly.default_color)
        self.options['colorscale'] = Dropdown(description = 'Color Palette:', value = GlueSunburstPlotly.default_color, options = cl_options)
        self.options['colorscale'].observe(lambda v:self.updateRender(), names='value')
        self.DefaultLegend('v', 1.02, 1.0);
        
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
        if self.options['colorscale'].value == GlueSunburstPlotly.default_color:
            color_set = [self.data.get_component(dim).color for dim in self.dimensions]
        else:
            color_set = cl.scales['8']['qual'][self.options['colorscale'].value]
            if (len(self.dimensions) > 8):
                color_set = cl.interp( color_set, len(dimensions) )
            color_set = cl.to_rgb(color_set)
        color_set.insert(0,'rgb(255,255,255)')    
        
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
                                          
                    elif len(dvalues) < self.options['grouping_limit'].value:
                        for val in dvalues:
                            ids += 1
                            process = {'id':ids,'dimension':toprocess['dimension']+1, 'label':str(val), 'parent':toprocess['id']}
                            process['mask'] = (mask & (self.data[dimension] == val))
                            queue.append(process)
                    else:    
                        hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins='auto')
                        if (len(bin_edges) > self.options['grouping_limit'].value):
                            hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins=self.options['grouping_limit'].value)                        
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
            'showlegend': self.margins['showlegend'].value,
            'legend' : {
                'orientation' : self.margins['legend_orientation'].value,
                'x' : self.margins['legend_xpos'].value,
                'y' : self.margins['legend_ypos'].value
            }
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
        self.updateCallbacks();
        GluePlotly.display(self)

    def updateCallbacks(self):	
        append = False
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_click(lambda x,y,z : self.setSubset(x,y,z), append)
            append = True
        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_click(self.on_selection_callback, append)

    def on_selection(self, callback):
        GluePlotly.on_selection(self, callback)
        self.updateCallbacks()

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
