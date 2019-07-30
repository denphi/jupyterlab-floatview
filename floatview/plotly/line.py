from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import Dropdown, IntText, BoundedIntText
from IPython.display import clear_output


class GlueLinePlotly (GluePlotly):
    marker_type = 'lines'

    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], ' '.join([self.dimensions[i] for i in range(1,len(self.dimensions))]))
        self.DefaultLayoutScales("linear","linear");
        self.options['marker_type'] = Dropdown( description = 'Marker type:', value = 'lines', options = ['lines','lines+markers','lines+text'])
        self.options['marker_type'].observe(lambda v:self.UpdateTraces({'mode':v['new']}), names='value')       
        self.options['line_width'] = BoundedIntText(description = 'Lines width:', value = 1, min=0, max=10)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.DefaultLegend('v', 1.02, 1.0);                
        self.updateRender() 
    
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max    
        x_values = self.data[x_id].flatten()        
        x_sort = x_values.argsort()
        for y_id in y_id_list:
            y_values = self.data[y_id].flatten()
            color = "#444444"
            color = 'rgba'+str(self.getDeltaColor(color, alpha_val))
            trace = {
                'type': "scattergl", 'mode': self.options['marker_type'].value, 'name': self.data.label + "_" + y_id,
                'line' : { 'width' : self.options['line_width'].value, 'color' : color },
                'x': x_values[x_sort],
                'y': y_values[x_sort],
            }
            if self.only_subsets == False:
                traces.append(trace)
            alpha_val = alpha_val - alpha_delta
            
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                alpha_val = alpha_max   
                x_values = sset[x_id].flatten()    
                x_sort = x_values.argsort()
                for step, y_id in enumerate(y_id_list):
                    y_values = sset[y_id].flatten()            
                    color = sset.style.color
                    color = 'rgba'+str(self.getDeltaColor(color, alpha_val, step))
                    trace = {
                        'type': "scattergl", 'mode': self.options['marker_type'].value, 'name': sset.label + "_" + y_id,
                        'line' : { 'width' : self.options['line_width'].value, 'color' : color},
                        'x': x_values[x_sort],
                        'y': y_values[x_sort],
                    }
                    traces.append(trace)  
                    alpha_val = alpha_val - alpha_delta                
        y_color = 'rgb(0,0,0)'
        if len(y_id_list) == 1:
            y_color = self.data.get_component(y_id_list[0]).color

        layout = {
            'margin' : {'l':50,'r':0,'b':50,'t':30 },
            'xaxis': { 'autorange' : True, 'zeroline': True, 
                'title' : self.options['xaxis'].value, 
                'type' : self.options['xscale'].value ,
                'linecolor' : self.data.get_component(x_id).color,
                'tickcolor' : self.data.get_component(x_id).color,
                'ticklen' : 4,
                'linewidth' : 4,                
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value, 
                'type' : self.options['yscale'].value,
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
        GluePlotly.display(self)

    def updateCallbacks(self):	
        append = False
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), append)
            append = True
        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_click(self.on_selection_callback, append)

    def on_selection(self, callback):
        GluePlotly.on_selection(self, callback)
        self.updateCallbacks()        

    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.options['xscale'].value=type
        if (axis ==  'yaxis'):
            self.options['yscale'].value=type

        
    def changeMarker(self, type="lines"):
        if (type in ["lines+markers", "lines", "lines+text"]):
            self.options['marker_type'].value = type
            self.updateRender()
        
    def updateSelection(self, ids):
        pass #self.parent.printInDebug(ids)        

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
            
