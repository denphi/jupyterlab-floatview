from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
from ipywidgets import IntText
from IPython.display import clear_output


class GlueScatterPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    options = {}
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], ' '.join([self.dimensions[i] for i in range(1,len(self.dimensions))]))
        self.DefaultLayoutScales("linear","linear");
        self.options['line_width'] = IntText(description = 'Lines width:', value = 1)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = IntText(description = 'Markers size:', value = 3)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max   
        for y_id in y_id_list:
            color = "#444444"
            color = 'rgba'+str(self.getDeltaColor(color, alpha_val))
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': self.data.label + "_" + y_id,
                'marker': dict({
                    'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                    'line' : { 'width' : self.options['line_width'].value, 'color' : color }
                }),
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
                    'type': "scattergl", 'mode': "markers", 'name': sset.label + "_" + y_id,
                    'marker': dict({
                        'symbol':'circle', 'size': self.focused_size_marker, 'color': color,
                        'line' : { 'width' : self.options['line_width'].value, 'color' : color}      
                    }),
                    'selected':{'marker':{'color':color, 'size': self.options['marker_size'].value}},
                    'unselected':{'marker':{'color':color, 'size': self.options['marker_size'].value}},                
                    'x': sset[x_id],
                    'y': sset[y_id],
                }
                traces.append(trace)  
                alpha_val = alpha_val - alpha_delta
                

        layout = {
            'title' : self.options['title'].value,
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
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        if (axis ==  'xaxis'):
            self.options['xscale'].value=type
        if (axis ==  'yaxis'):
            self.options['yscale'].value=type


    def updateRender(self):		
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], [self.dimensions[i] for i in range(1,len(self.dimensions))])
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        #self.parent.printInDebug(ids)        
        self.plotly_fig.data[0].update(
            selectedpoints=ids,
            selected={'marker':{'color':'rgba(0, 0, 0, 0.4)', 'size': self.focused_size_marker}},
            unselected={'marker':{'color':'rgba(0, 0, 0, 0.1)', 'size': self.default_size_marker}}
        )

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)