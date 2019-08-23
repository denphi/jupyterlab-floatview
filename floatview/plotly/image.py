from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
import numpy as np
from ipywidgets import IntText, Dropdown, FloatText, BoundedIntText

class GlueImagePlotly (GluePlotly):
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)       
        self.DefaultLayoutTitles("", self.dimensions[0], self.dimensions[1])
        z_id = self.dimensions[2]
        self.max_color = max(self.data[z_id].flatten())
        self.min_color = min(self.data[z_id].flatten())
        color_options = ['Greys','YlGnBu','Greens','YlOrRd','Bluered','RdBu','Reds','Blues','Picnic','Rainbow','Portland','Jet','Hot','Blackbody','Earth','Electric','Viridis','Cividis']
        self.options['line_width'] = BoundedIntText(description = 'Lines width:', value = 1, min=0, max=10)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = BoundedIntText(description = 'Markers size:', value = 3, min=0, max=15)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        self.options['color_range_min'] = FloatText(description = 'Color min:', value = self.min_color)
        self.options['color_range_min'].observe(lambda v:self.UpdateTraces({'zmin':v['new']}), names='value')                
        self.options['color_range_max'] = FloatText(description = 'Color max:', value = self.max_color)
        self.options['color_range_max'].observe(lambda v:self.UpdateTraces({'zmax':v['new']}), names='value')                
        self.options['color_scale'] = Dropdown(description = 'Color scale:', value = 'Greys', options=color_options)
        self.options['color_scale'].observe(lambda v:self.UpdateTraces({'colorscale':v['new']}), names='value') 
        self.DefaultLegend('v', 1.02, 1.0);
        
        self.updateRender()
        
    def createFigureWidget(self):
        x_id = self.dimensions[0]
        y_id = self.dimensions[1]
        z_id = self.dimensions[2] 
        x_value = self.data[x_id].flatten().astype('float')
        y_value = self.data[y_id].flatten().astype('float')
        x_value, x_inv = np.unique(x_value, return_inverse=True)
        y_value, y_inv = np.unique(y_value, return_inverse=True)
        try:
            z_value = np.reshape(self.data[z_id].flatten(), (len(x_value), len(y_value)))
        except:
            t_value = self.data[z_id].flatten()            
            x_value = np.sort(x_value)
            y_value = np.sort(y_value)
            z_value = np.zeros((len(x_value), len(y_value)))
            for i, value in enumerate(t_value):
                z_value[x_inv[i]][y_inv[i]] = value                
        #with self.debug:
        #    print (x_value,y_value,z_value)
        
        traces = []
        trace = {
            'type': "contour",
            'colorscale':self.options['color_scale'].value,
            'showlegend':False,
            'autocontour':False,'ncontours':1,
            'contours':{'coloring':'heatmap'},
            'x':x_value.tolist(),
            'y':y_value.tolist(),
            'z':z_value.tolist(),
            'zauto':False,
            'zmin':self.options['color_range_min'].value,
            'zmax':self.options['color_range_max'].value,
        }
        if self.only_subsets == False:
            traces.append(trace)

        for sset in self.data.subsets:     
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                color = sset.style.color
                color = 'rgba'+str(self.getDeltaColor(color, 0.6))             
                trace = {
                    'type': "scattergl", 'mode': "markers", 'name': sset.label + "_" + y_id,
                    'marker': dict({
                        'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                        'line' : { 'width' : self.options['line_width'].value, 'color' : color}      
                    }),
                    'selected':{'marker':{'color':color, 'size': self.options['marker_size'].value}},
                    'unselected':{'marker':{'color':color, 'size': self.options['marker_size'].value}},                
                    'x': sset[x_id].flatten(),
                    'y': sset[y_id].flatten(),
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
            'xaxis': { 'autorange' : True, 'zeroline': True, 
                'title' : self.options['xaxis'].value, 
                'linecolor' : self.data.get_component(x_id).color,
                'tickcolor' : self.data.get_component(x_id).color,
                'ticklen' : 4,
                'linewidth' : 4,                
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value, 
                'linecolor' : self.data.get_component(y_id).color,
                'tickcolor' : self.data.get_component(y_id).color,
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
        self.plotly_fig = self.createFigureWidget()    
        #if self.only_subsets == False:
        #    self.plotly_fig.data[1].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        #self.plotly_fig.data[1].update(
        #    selectedpoints=ids,
        #    selected={'marker':{'color':'rgba(0, 0, 0, 0.4)', 'size': self.options['marker_size'].value}},
        #    unselected={'marker':{'color':'rgba(0, 0, 0, 0.1)', 'size': self.options['marker_size'].value}}
        #)
        pass
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.x_scale_type = type
        if (axis ==  'yaxis'):
            self.y_scale_type = type
        self.plotly_fig.layout[axis].type = type

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
