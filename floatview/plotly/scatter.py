from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import BoundedIntText, Text
from IPython.display import clear_output
import numpy as np
from matplotlib import colors

class GlueScatterPlotly (GluePlotly):
    options = {}
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], ' '.join([self.dimensions[i] for i in range(1,len(self.dimensions))]))
        self.DefaultLayoutScales("linear","linear");
        self.options['line_width'] = BoundedIntText(description = 'Lines width:', value = 1, min=0, max=10)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = BoundedIntText(description = 'Markers size:', value = 3, min=0, max=15)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        self.DefaultLegend('v', 1.02, 1.0);                
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max   
        xtickmode = "auto"
        xtickvals = None
        xticktext = None    
        if hasattr(self.data[x_id].flatten(), 'codes'):
            x_val = self.data[x_id].flatten().codes.tolist()
            tickvals, tickmask = np.unique(self.data[x_id].flatten().codes, return_index=True)
            ticktext = self.data[x_id][tickmask]
            xtickmode = "array"
            xtickvals = tickvals.tolist()
            xticktext = ticktext.tolist()            
        else:
            x_val = self.data[x_id].flatten()
        for step, y_id in enumerate(y_id_list):
            color = "#444444"
            color = 'rgba'+str(self.getDeltaColor(color, alpha_val, step))                        
            if hasattr(self.data[y_id].flatten(), 'codes'):
                y_val = self.data[y_id].flatten().codes.tolist()
            else:
                y_val = self.data[y_id].flatten()
                
            trace = {
                'type': "scattergl", 
                'mode': "markers", 
                'name': self.data.label + "_" + y_id,
                'marker': {
                    'symbol':'circle', 
                    'size': self.options['marker_size'].value, 
                    'color': color,
                    'line' : { 
                        'width' : self.options['line_width'].value, 
                        'color' : color 
                    }
                },
                'x': x_val,
                'y': y_val,
            }
            if self.only_subsets == False:
                traces.append(trace)
            alpha_val = alpha_val - alpha_delta
            
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                alpha_val = alpha_max        
                if hasattr(sset[x_id].flatten(), 'codes'):
                    x_val = sset[x_id].flatten().codes.tolist()
                else:
                    x_val = sset[x_id].flatten()
                for step, y_id in enumerate(y_id_list):
                    if hasattr(sset[y_id].flatten(), 'codes'):
                        y_val = sset[y_id].flatten().codes.tolist()
                    else:
                        y_val = sset[y_id].flatten().astype('float')
                    color = sset.style.color
                    color = 'rgba'+str(self.getDeltaColor(color, alpha_val, step))
                    trace = {
                        'type': "scattergl", 
                        'mode': "markers", 
                        'name': sset.label + "_" + y_id,
                        'marker': {
                            'symbol':'circle', 
                            'size': self.options['marker_size'].value, 
                            'color': color,
                            'line' : { 
                                'width' : self.options['line_width'].value, 
                                'color' : color
                            }      
                        },
                        'x': x_val,
                        'y': y_val,
                    }
                    traces.append(trace)  
                    alpha_val = alpha_val - alpha_delta
                
        y_fid = y_id_list[0]
        layout = {
            'title' : self.options['title'].value,
            'margin' : {
                'l':self.margins['left'].value,
                'r':self.margins['right'].value,
                'b':self.margins['bottom'].value,
                't':self.margins['top'].value 
            },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 
                'title' : self.options['xaxis'].value, 
                'type' : self.options['xscale'].value,
                'tickmode' : xtickmode,
                'tickvals' : xtickvals,
                'ticktext' : xticktext,
                'linecolor' : self.data.get_component(x_id).color,
                'tickcolor' : self.data.get_component(x_id).color,
                'ticklen' : 4,
                'linewidth' : 4,                
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value, 
                'type' : self.options['yscale'].value,
                'linecolor' : self.data.get_component(y_fid).color,
                'tickcolor' : self.data.get_component(y_fid).color,
                'ticklen' : 4,
                'linewidth' : 4,
            },
            'showlegend': self.margins['showlegend'].value,            
            'legend' : {
                'orientation' : self.margins['legend_orientation'].value,
                'x' : self.margins['legend_xpos'].value,
                'y' : self.margins['legend_ypos'].value
            }
            
        }
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.options['xscale'].value=type
        if (axis ==  'yaxis'):
            self.options['yscale'].value=type


    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], [self.dimensions[i] for i in range(1,len(self.dimensions))])
        self.updateCallbacks()
        GluePlotly.display(self)

    def updateCallbacks(self):	
        append = False
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), append)
            append = True
        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_selection(self.on_selection_callback, append)

    def on_selection(self, callback):
        GluePlotly.on_selection(self, callback)
        self.updateCallbacks()
        
    def updateSelection(self, ids):
        #self.parent.printInDebug(ids)        
        self.plotly_fig.data[0].update(
            selectedpoints=ids,
        )

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
            
            
class GlueScatterMatrixPlotly (GluePlotly):
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.options['title'] = Text( description = 'Title:', value = "" )
        self.options['title'].observe(lambda v:self.UpdateLayout( {'title':v['new']} ), names='value')        
        self.options['line_width'] = BoundedIntText(description = 'Lines width:', value = 1, min=0, max=10)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = BoundedIntText(description = 'Markers size:', value = 3, min=0, max=15)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        self.DefaultLegend('v', 0.6, 0.95);                
        self.updateRender()
        
    def createFigureWidget(self):
        traces = []  
        xtickmode = "auto"
        xtickvals = None
        xticktext = None   
        dimensions = []
        color = "#444444"        
        for dimension in self.dimensions:
            value = {'label':dimension}
            if hasattr(self.data[dimension].flatten(), 'codes'):
                val = self.data[dimension].flatten().codes.tolist()
            else:
                val = self.data[dimension].flatten()
            value["values"] = val
            dimensions.append(value)
                
        trace = {        
            'type': "splom", 'name': self.data.label,
            'dimensions' : dimensions,
            'marker': dict({
                'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                'line' : { 'width' : self.options['line_width'].value, 'color' : color }
            }),
            'showupperhalf' : False,
            'diagonal' : { 'visible' : False },
        }
        if self.only_subsets == False:
            traces.append(trace)
            
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                color = sset.style.color
                dimensions = []            
                for dimension in self.dimensions:
                    value = {'label':dimension}
                    if hasattr(sset[dimension].flatten(), 'codes'):
                        val = sset[dimension].flatten().codes.tolist()
                    else:
                        val = sset[dimension].flatten()
                    value["values"] = val
                    dimensions.append(value)
                trace = {        
                    'type': "splom", 'name': sset.label,
                    'dimensions' : dimensions,
                    'marker': dict({
                        'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                        'line' : { 'width' : self.options['line_width'].value, 'color' : color }
                    }),
                    'showupperhalf' : False,
                    'diagonal' : { 'visible' : False },
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
            'showlegend': self.margins['showlegend'].value,            
            'legend' : {
                'orientation' : self.margins['legend_orientation'].value,
                'x' : self.margins['legend_xpos'].value,
                'y' : self.margins['legend_ypos'].value
            },
            'plot_bgcolor' : 'rgba(245,245,245, 0.95)',
        }
        for i, dimension in enumerate(self.dimensions):
            layout['xaxis'+str(i+1)] = { 
                'autorange' : True, 
                'zeroline': False,
                'showline' : True, 
                #'mirror' : 'ticks',
                'linecolor' : self.data.get_component(dimension).color,
                'tickcolor' : self.data.get_component(dimension).color,
                'ticklen' : 4,
                'linewidth' : 4,
            }
            layout['yaxis'+str(i+1)] = { 
                'autorange':True, 
                'zeroline': False, 
                'showline' : True, 
                #'mirror' : 'ticks',
                'linecolor' : self.data.get_component(dimension).color,
                'tickcolor' : self.data.get_component(dimension).color,
                'ticklen' : 4,
                'linewidth' : 4,
            }
        
        
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.options['xscale'].value=type
        if (axis ==  'yaxis'):
            self.options['yscale'].value=type


    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget()
        self.updateCallbacks()
        GluePlotly.display(self)

    def updateCallbacks(self):	
        append = False
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), append)
            append = True
        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_selection(self.on_selection_callback, append)

    def on_selection(self, callback):
        GluePlotly.on_selection(self, callback)
        self.updateCallbacks()
        
    def updateSelection(self, ids):
        self.plotly_fig.data[0].update(
            selectedpoints=ids,
        )

    def setSubset(self,trace,points,selector):
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
