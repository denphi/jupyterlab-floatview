from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import IntText, Dropdown, FloatSlider, Label, BoundedIntText
import plotly.graph_objects as go
import numpy as np
from collections import deque
import colorlover as cl
  
class GlueSankeyPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    default_color = 'Dataset'
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles('', '', '')        
        self.options['grouping_limit'] = IntText(description = 'Group limiy', value = 12)
        self.options['grouping_limit'].observe(lambda v:self.updateRender(), names='value')
        cl_options = list(cl.scales['8']['qual'].keys())
        cl_options.append(GlueSankeyPlotly.default_color)
        self.options['colorscale'] = Dropdown(description = 'Color Palette:', value = GlueSankeyPlotly.default_color, options = cl_options)
        self.options['colorscale'].observe(lambda v:self.updateRender(), names='value')        
        self.DefaultLegend('h', 0.01, -0.05);
        self.updateRender()
        
    def createFigureWidget(self):
        dimensions = self.dimensions
        data_lines = [] 
        sources = []
        targets = []
        nodes = [{} for dim in dimensions]
        nodest = [{} for dim in dimensions]
        values = []
        labels = []
        colors = []
        self.masks = []
        nodes_id = []
        if self.options['colorscale'].value == GlueSankeyPlotly.default_color:
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
                nodes[i]['local_nodes'] = [len(nodes_id)+cnt for cnt in range(len(nodes[i]['values']))]
                nodes[i]['masks'] = []
                for val in nodes[i]['values']:
                     nodes[i]['masks'].append(self.data[dimension] == val)
            else:
                hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins='auto')
                if (len(bin_edges) > self.options['grouping_limit'].value):
                    hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins=self.options['grouping_limit'].value)
                
                nodes[i]['values'] = []
                for edge in range(len(bin_edges)-1):
                    nodes[i]['values'].append( '{:.1f}'.format(bin_edges[edge]) + ' - ' + '{:.1f}'.format(bin_edges[edge+1]))
                nodes[i]['local_nodes'] = [len(nodes_id)+cnt for cnt in range(len(nodes[i]['values']))]
                nodes[i]['masks'] = []
                for edge in range(len(bin_edges)-1):
                    if edge == 0:
                        nodes[i]['masks'].append((self.data[dimension] >= bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1]))      
                    else : 
                        nodes[i]['masks'].append((self.data[dimension] > bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1]))      
                        
            nodes_id.extend(nodes[i]['local_nodes'])                
            labels.extend(nodes[i]['values'])
            colors.extend([color_set[i] for val in nodes[i]['values']])
            self.masks.extend(nodes[i]['masks'])
        link_colors = []
        for i in range(len(dimensions)-1):
            for j in range(len(nodes[i]['local_nodes'])):
                for k in range(len(nodes[i+1]['local_nodes'])):
                    total = np.count_nonzero((nodes[i]['masks'][j] & nodes[i+1]['masks'][k]))
                    if total > 0:
                        mask = nodes[i]['masks'][j] & nodes[i+1]['masks'][k]                
                        for sset in self.data.subsets:
                            if hasattr(sset,"disabled") == False or sset.disabled == False:                                    
                                sset_mask = sset.to_mask()
                                color = sset.style.color
                                settotal = np.count_nonzero(mask & sset_mask)
                                mask = mask & ~sset_mask
                                sources.append(nodes[i]['local_nodes'][j])
                                targets.append(nodes[i+1]['local_nodes'][k])
                                values.append(settotal)
                                link_colors.append(color)
                                total = total - settotal
                        if self.only_subsets == False:
                            sources.append(nodes[i]['local_nodes'][j])
                            targets.append(nodes[i+1]['local_nodes'][k])
                            values.append(total)
                            link_colors.append('rgba(238, 238, 238, 0.6)')                    
                        
                
        traces = []
        
        sankey = {
            'type' : 'sankey',
            #'arrangement' : 'perpendicular',
            'node' : {
              'pad' : 8,
              'thickness' : 15,
              'line' : {
                'color' : 'black',
                'width' : 0.5
              },
              'label' : labels,
              'color' : colors
            },
            'link' : {
              'source' : sources,
              'target' : targets,
              'value' : values,
              'hovertemplate': '%{label}<br><b>Source: %{source.label}<br>Target: %{target.label}<br> %{flow.value}</b>',
              'color' : link_colors,
              'line' : { 
                'color' : 'lightgrey',
                'width' : 0.5
              }
            },
            #'domain':{
            #    'x': [0, 0.9],
            #    'y': [0, 1],
            #},         
        }

        traces.append(sankey)

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
            'font' : {
                'size' : 10,
            },
        }
        

        for i in range(len(self.dimensions)):
            dimension = self.dimensions[i]
            trace = {
                'type': 'scatter',
                'name' : dimension, 
                'textposition' : 'middle right',
                'x' : [-1000],
                'y' : [i],
                'mode' : 'markers',
                'marker': {
                    'color' : color_set[i],
                    'size' : 20,
                    'line': {
                        'width': 0,
                    },
                    'symbol' : 'square'
                }
            }
            traces.append(trace)

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
                        'width': 1,
                        'color' : 'light grey'
                    },
                    'symbol' : 'square'
                }
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
        data = traces
        FigureWidget(data = data, layout = layout)
        return FigureWidget(data = data, layout = layout)
        
    def updateSelection(self, ids):
        #self.parent.printInDebug(self.plotly_fig.data[0])        
        self.plotly_fig.data[0].update(
            selectedpoints=ids
        )
        
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

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            mask = None
            for p in points.point_inds:
                if mask is None:
                    mask = self.masks[p]
                else :
                    mask = mask | self.masks[p]                
            point_inds = np.nonzero(mask)[0]
            self.parent.updateSelection(point_inds)
        pass;    
            
     

class GlueSankeytreePlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    default_color = 'Dataset'
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles('', '', '')
        self.options['grouping_limit'] = IntText(description = 'Group limiy', value = 12)
        self.options['grouping_limit'].observe(lambda v:self.updateRender(), names='value')
        cl_options = list(cl.scales['8']['qual'].keys())
        cl_options.append(GlueSankeytreePlotly.default_color)
        self.options['colorscale'] = Dropdown(description = 'Color Palette:', value = GlueSankeytreePlotly.default_color, options = cl_options)
        self.options['colorscale'].observe(lambda v:self.updateRender(), names='value')
        self.DefaultLegend('v', 1.02, 1.0);
        
        self.updateRender()
        
    def createFigureWidget(self):
        data_lines = []
        traces = []        
        sources = []
        targets = []
        values = []
        labels = []
        parents = []
        self.masks = []
        colors = []
        df = self.data.to_dataframe()
        ids = 0
        queue = deque()
        if self.options['colorscale'].value == GlueSankeytreePlotly.default_color:
            color_set = [self.data.get_component(dim).color for dim in self.dimensions]
        else:
            color_set = cl.scales['8']['qual'][self.options['colorscale'].value]
            if (len(self.dimensions) > 8):
                color_set = cl.interp( color_set, len(self.dimensions) )
            color_set = cl.to_rgb(color_set)

           

        
        queue.append({'id':ids,'dimension':0, 'label':'Data', 'mask':[True for i in range(self.data.size)], 'parent':''})
        while len(queue) > 0:
            toprocess = queue.popleft()
            mask = toprocess['mask']
            id = toprocess['id']
            label = toprocess['label']
            value = np.count_nonzero(mask)
            if True: #value > 0:
                labels.append(label)
                sources.append(toprocess['parent'])
                targets.append(id)
                values.append(value)
                parents.append(toprocess['parent'])
                colors.append(color_set[toprocess['dimension']-1])
                self.masks.append(mask)
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
                            label = '{:.1f}'.format(bin_edges[edge]) + ' - ' + '{:.1f}'.format(bin_edges[edge+1])
                            process = {'id':ids,'dimension':toprocess['dimension']+1, 'label':label, 'parent':toprocess['id']}
                            if edge == 0:
                                process['mask'] = (mask & ((self.data[dimension] >= bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1])))
                            else :
                                process['mask'] = (mask & ((self.data[dimension] > bin_edges[edge])  & (self.data[dimension] <= bin_edges[edge+1])))
                            queue.append(process)

        trace = {
            'type' : 'sankey',
            'node' : {
              'pad' : 15,
              'thickness' : 20,
              'line' : {
                'color' : 'black',
                'width' : 0.5
              },
              'label' : labels[1:],
              'color' : colors[1:],              
            },
            'link' : {
              'source' : [s-1 for s in sources[1:]],
              'target' : [t-1 for t in targets[1:]],
              'value' : values[1:],
              'hovertemplate': '%{label}<br><b>Source: %{source.label}<br>Target: %{target.label}<br> %{flow.value}</b>'             
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
            'legend' : {
                'orientation' : self.margins['legend_orientation'].value,
                'x' : self.margins['legend_xpos'].value,
                'y' : self.margins['legend_ypos'].value
            }
        }
        
        for i in range(len(self.dimensions)):
            dimension = self.dimensions[i]
            trace = {
                'type': 'scatter',
                'name' : dimension, 
                'textposition' : 'middle right',
                'x' : [-1000],
                'y' : [i],
                'mode' : 'markers',
                'marker': {
                    'color' : color_set[i],
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
                if mask is None:
                    mask = self.masks[p+1]
                else :
                    mask = mask | self.masks[p+1]                
            point_inds = np.nonzero(mask)[0]
            self.parent.updateSelection(point_inds)
        pass;    
            
