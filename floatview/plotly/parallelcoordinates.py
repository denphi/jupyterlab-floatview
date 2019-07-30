from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
import plotly.graph_objects as go
import numpy as np
from ipywidgets import IntText, Dropdown, FloatSlider, Label, BoundedIntText
import colorlover as cl


  
class GlueParallelCoordinatesPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", "", "") 
        self.DefaultLegend('h', 0.01, -0.05);        
        self.updateRender()
        
    def createFigureWidget(self):
        dimensions = self.dimensions
        data_lines = [] 
        i=0
        if self.only_subsets == False:
            colors = [i for r in range(self.data.size)]
            colorscale = [[0,'#EEEEEE']]
        else:
            colors = []
            colorscale = []
            i=-1
            
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                i = i+1
                tmplist = [i for r in range(len(sset.to_index_list()))]
                colors.extend(tmplist)
                colorscale.append([i,sset.style.color])
        t_color = len(colorscale)        
        if (t_color > 1):
            for c in colorscale:
                c[0] = c[0]/(t_color-1)
        else:
            colorscale = [[0,'#EEEEEE'], [1,'#EEEEEE']] 
        traces = []

        for dimension in dimensions:
            line={}
            if hasattr(self.data[dimension].flatten(), 'codes'):
                line['values'] = self.data[dimension].flatten().codes.tolist()
                tickvals, tickmask = np.unique(self.data[dimension].flatten().codes, return_index=True)
                ticktext = self.data[dimension][tickmask]
                line['tickvals'] = tickvals.tolist()
                line['ticktext'] = ticktext.tolist()
            else:
                line['values'] = self.data[dimension].flatten().tolist()
            
            line['label'] = dimension
            for sset in self.data.subsets:
                if hasattr(sset,"disabled") == False or sset.disabled == False:            
                    if hasattr(sset[dimension].flatten(), 'codes'):
                        tmplist = sset[dimension].codes.tolist()
                    else:
                        tmplist = sset[dimension].tolist()
                    line['values'].extend(tmplist)
            data_lines.append(line);
        trace = {
            'type' : 'parcoords',
            'line' : {
                'color' : colors, 
                'colorscale' : colorscale
            },
            'dimensions' : data_lines,
        }
        traces.append(trace)
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:                    
                color = sset.style.color
                trace = {
                    'type': "scatter",
                    'name' : sset.label, 
                    'textposition' : 'middle right',
                    'x' : [-1000],
                    'y' : [i],
                    'mode' : 'markers',
                    'marker': {
                        'color' : color,
                        'size' : 20,
                        'line': {
                            'width': 1,
                            'color' : 'light grey'
                        },
                        'symbol' : 'square'
                    }
                }
                traces.append(trace)
        
        layout = {
            'title' : self.options['title'].value,
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
            },  
        }
        return FigureWidget(data = traces, layout = layout)
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget()     
        #self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)            
        GluePlotly.display(self)

    def updateSelection(self, ids):
        pass;
        #self.parent.printInDebug(self.plotly_fig.data[0])        
        #self.plotly_fig.data[0].update(
        #    selectedpoints=ids
        #)

    #def setSubset(self,trace,points,selector): 
    #    if(self.parent is not None):
    #        self.parent.updateSelection(points.point_inds)
            
        

class GlueParallelCategoriesPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    default_color = "Dataset"
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", "", "")        
        self.options['grouping_limit'] = IntText(description = 'Group limiy', value = 12)
        self.options['grouping_limit'].observe(lambda v:self.updateRender(), names='value')
        cl_options = list(cl.scales['8']['qual'].keys())
        cl_options.append(GlueParallelCategoriesPlotly.default_color)
        self.options['colorscale'] = Dropdown(description = 'Color Palette:', value = GlueParallelCategoriesPlotly.default_color, options = cl_options)
        self.options['colorscale'].observe(lambda v:self.updateRender(), names='value')        
        self.DefaultLegend('h', 0.01, -0.05);
        self.updateRender()
        
    def createFigureWidget(self):
        dimensions = self.dimensions
        data_lines = [] 
        nodes = [{} for dim in dimensions]
        values = []
        colors = []
        traces = []
        if self.options['colorscale'].value == GlueParallelCategoriesPlotly.default_color:
            color_set = [self.data.get_component(dim).color for dim in dimensions]
        else:
            color_set = cl.scales['8']['qual'][self.options['colorscale'].value]
            if (len(self.dimensions) > 8):
                color_set = cl.interp( color_set, len(dimensions) )
            color_set = cl.to_rgb(color_set)
        for i, dimension in enumerate(dimensions):
            dvalues = np.unique(self.data[dimension].flatten())            
            if len(dvalues) < self.options['grouping_limit'].value or hasattr(self.data[dimension].flatten(), 'codes'):
                nodes[i]['values'] = np.unique(self.data[dimension].flatten())
                nodes[i]['masks'] = []
                for val in nodes[i]['values']:
                     nodes[i]['masks'].append(self.data[dimension] == val)
            else:
                hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins='auto')
                if (len(bin_edges) > self.options['grouping_limit'].value):
                    hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins=self.options['grouping_limit'].value)
                
                nodes[i]['values'] = []
                for edge in range(len(bin_edges)-1):
                    nodes[i]['values'].append( "{:.1f}".format(bin_edges[edge]) + " - " + "{:.1f}".format(bin_edges[edge+1]))
                nodes[i]['masks'] = []
                for edge in range(len(bin_edges)-1):
                    if edge == 0:
                        nodes[i]['masks'].append((self.data[dimension] >= bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1]))      
                    else : 
                        nodes[i]['masks'].append((self.data[dimension] > bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1]))      
                        
            line = {}
            
            line['values'] = np.array(['' for i in range(self.data.size)], dtype = 'object')
            colorv = np.array(['#EEEEEE' for i in range(self.data.size)])
            for k, value in enumerate(nodes[i]['values']):
                mask = nodes[i]['masks'][k] 
                line['values'][mask] = value
                for sset in self.data.subsets:
                    if hasattr(sset,"disabled") == False or sset.disabled == False:            
                        sset_mask = sset.to_mask()
                        color = sset.style.color
                        colorv[mask & sset_mask] = color
                        mask = mask & ~sset_mask
            colors.extend(colorv)
            line['values'] = line['values'].tolist()
            line['label'] = dimension            
            data_lines.append(line);
            
        
            
        parcats = {
            'type' : 'parcats',
            'dimensions' : data_lines,
            'line' :  {
                'color' : colors,
                'shape': 'hspline'
            }
            
        }

        traces.append(parcats)

        layout = {
            'title' : self.options['title'].value,
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
        

        if self.only_subsets == False:
            trace = {
                'type': "scatter",
                'name' : self.data.label, 
                'textposition' : 'middle right',
                'x' : [-1000],
                'y' : [i],
                'mode' : 'markers',
                'marker': {
                    'color' : "#EEEEEE",
                    'size' : 20,
                    'line': {
                        'width': 0,
                    },
                    'symbol' : 'square'
                }
            }
            traces.append(trace)

        for sset in self.data.subsets:
            color = sset.style.color
            trace = {
                'type': "scatter",
                'name' : sset.label, 
                'textposition' : 'middle right',
                'x' : [-1000],
                'y' : [i],
                'mode' : 'markers',
                'marker': {
                    'color' : color,
                    'size' : 20,
                    'line': {
                        'width': 0,
                    },
                    'symbol' : 'square'
                }
            }
            traces.append(trace)

            
        data = traces
        FigureWidget(data = data, layout = layout)
        return FigureWidget(data = data, layout = layout)
        
    def updateSelection(self, ids):
        pass;
        
    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget()
        self.updateCallbacks();
        GluePlotly.display(self)

    def updateCallbacks(self):	
        append = False
        self.plotly_fig.data[0].on_click(lambda x,y,z,this=self : this.setSubset(x,y,z), append)
        append = True
        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_click(self.on_selection_callback, append)

    def on_selection(self, callback):
        GluePlotly.on_selection(self, callback)
        self.updateCallbacks()        

    def setSubset(self,trace,points,selector): 
        self.parent.printInDebug(points)
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
