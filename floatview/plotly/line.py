from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
from ipywidgets import Dropdown, IntText
from IPython.display import clear_output


class GlueLinePlotly (GluePlotly):
    marker_type = 'lines'

    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], ' '.join([self.dimensions[i] for i in range(1,len(self.dimensions))]))
        self.DefaultLayoutScales("linear","linear");
        self.options['marker_type'] = Dropdown( description = 'Marker type:', value = 'lines', options = ['lines','lines+markers','lines+text'])
        self.options['marker_type'].observe(lambda v:self.UpdateTraces({'mode':v['new']}), names='value')        
        self.options['line_width'] = IntText(description = 'Lines width:', value = 1)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.updateRender() 
    
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max        
        for y_id in y_id_list:
            color = "#444444"
            color = 'rgba'+str(self.getDeltaColor(color, alpha_val))
            trace = {
                'type': "scattergl", 'mode': self.options['marker_type'].value, 'name': self.data.label + "_" + y_id,
                'line' : { 'width' : self.options['line_width'].value, 'color' : color },
                'x': self.data[x_id],
                'y': self.data[y_id],
            }
            if self.only_subsets == False:
                traces.append(trace)
            alpha_val = alpha_val - alpha_delta
            
        for sset in self.data.subsets:
            alpha_val = alpha_max        
            for i, y_id in enumerate(y_id_list):
                color = sset.style.color
                color = 'rgba'+str(self.getDeltaColor(color, alpha_val, i))
                trace = {
                    'type': "scattergl", 'mode': self.options['marker_type'].value, 'name': sset.label + "_" + y_id,
                    'line' : { 'width' : self.options['line_width'].value, 'color' : color},
                    'x': sset[x_id],
                    'y': sset[y_id],
                }
                traces.append(trace)  
                alpha_val = alpha_val - alpha_delta
                

        layout = {
            'margin' : {'l':50,'r':0,'b':50,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 
                'title' : self.options['xaxis'].value, 
                'type' : self.options['xscale'].value 
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value, 
                'type' : self.options['yscale'].value
            },            
            'showlegend': True,
        }
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], [self.dimensions[i] for i in range(1,len(self.dimensions))])
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

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
            
