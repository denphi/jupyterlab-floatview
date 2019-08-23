from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import IntText, BoundedIntText
import numpy as np

class GluePolyFitPlotly (GluePlotly):
    polyfun = {}
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], ' '.join([self.dimensions[i] for i in range(1,len(self.dimensions))]))
        self.options['line_width'] = BoundedIntText(description = 'Lines width:', value = 1, min=0, max=10)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = BoundedIntText(description = 'Markers size:', value = 3, min=0, max=15)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        degree = kwargs.get('degree', 2)        
        self.options['fit_degree'] = BoundedIntText(description = 'Fitting degree:', value = degree,min=2,max=20)
        self.options['fit_degree'].observe(lambda v:self.updateRender(), names='value')                
        self.DefaultLegend('v', 1.02, 1.0);        
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max
        self.polyfun = {}
        for step, y_id in enumerate(y_id_list):
            z = np.polyfit(self.data[x_id].flatten().astype('float'), self.data[y_id].flatten().astype('float'), self.options['fit_degree'].value)
            f = np.poly1d(z)
            color = "#444444"
            color = 'rgba'+str(self.getDeltaColor(color, alpha_val, step))
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': self.data.label + "_" + y_id,
                'marker': dict({
                    'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                    'line' : { 'width' : self.options['line_width'].value, 'color' : color }
                }),
                'x': self.data[x_id].flatten(),
                'y': self.data[y_id].flatten(),
            }
            if self.only_subsets == False:
                traces.append(trace)
            x_new=self.data[x_id].flatten().astype('float').tolist()
            x_new.sort()
            y_new = f(x_new)
            trace = {
                'type': "scattergl", 'mode': "lines", 'name': self.data.label + "_fit_" + y_id,
                'line' : { 'width' : self.options['line_width'].value, 'color' : color }, 
                'x': x_new,
                'y': y_new,
                'showlegend':False
            }
            if self.only_subsets == False:
                traces.append(trace)
            
            alpha_val = alpha_val - alpha_delta
            self.polyfun[y_id] = f
            
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                alpha_val = alpha_max        
                for step, y_id in enumerate(y_id_list):
                    z = np.polyfit(sset[x_id].flatten().astype('float'), sset[y_id].flatten().astype('float'), self.options['fit_degree'].value)
                    f = np.poly1d(z)
                    color = sset.style.color
                    color = 'rgba'+str(self.getDeltaColor(color, alpha_val, step))
                    trace = {
                        'type': "scattergl", 'mode': "markers", 'name': sset.label + "_" + y_id,
                        'marker': dict({
                            'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                            'line' : { 'width' : self.options['line_width'].value, 'color' : color}      
                        }),
                        'x': sset[x_id].flatten(),
                        'y': sset[y_id].flatten(),

                    }
                    traces.append(trace)  
                    
                    x_new=sset[x_id].flatten().astype('float').tolist()
                    x_new.sort()
                    y_new = f(x_new)
                    trace = {
                        'type': "scattergl", 'mode': "lines", 'name': sset.label + "_fit_" + y_id,
                        'line' : { 'width' : self.options['line_width'].value, 'color' : color }, 
                        'x': x_new,
                        'y': y_new,
                        'showlegend':False
                    }
                    traces.append(trace)                
                    alpha_val = alpha_val - alpha_delta
                    self.polyfun[sset.label + "_" + y_id] = f

        y_color = 'rgb(0,0,0)'
        if len(y_id_list) == 1:
            y_color = self.data.get_component(y_id_list[0]).color

        layout = {
            'title' : self.options['title'].value,
            'margin' : {'l':50,'r':0,'b':50,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 
                'title' : self.options['xaxis'].value,
                'linecolor' : self.data.get_component(x_id).color,
                'tickcolor' : self.data.get_component(x_id).color,
                'ticklen' : 4,
                'linewidth' : 4,                
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value,
                'linecolor' : y_color,
                'tickcolor' : y_color,
                'ticklen' : 4,
                'linewidth' : 4,                                               
            },
            'showlegend': self.margins['showlegend'].value,
            'legend' : {
                'orientation' : self.margins['legend_orientation'].value,
                'x' : self.margins['legend_xpos'].value,
                'y' : self.margins['legend_ypos'].value
            },               
        }        
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
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
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.x_scale_type = type
        if (axis ==  'yaxis'):
            self.y_scale_type = type
        self.plotly_fig.layout[axis].type = type


    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)           
            
