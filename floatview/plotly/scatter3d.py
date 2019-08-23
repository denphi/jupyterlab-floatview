from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import Text, IntText, BoundedIntText


class GlueScatter3DPlotly (GluePlotly):
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.options['title'] = Text( description = 'Title:', value = "" )
        self.options['title'].observe(lambda v:self.UpdateLayout( {'title':v['new']} ), names='value')
        self.options['xaxis'] = Text( description = 'Xaxis Title:', value = self.dimensions[0] )
        self.options['xaxis'].observe(lambda v:self.UpdateLayout( {'scene.xaxis.title':v['new']} ), names='value')
        self.options['yaxis'] = Text( description = 'Yaxis Title:', value = self.dimensions[1] )
        self.options['yaxis'].observe(lambda v:self.UpdateLayout( {'scene.yaxis.title':v['new']} ), names='value')
        self.options['zaxis'] = Text( description = 'Zaxis Title:', value = self.dimensions[2] )
        self.options['zaxis'].observe(lambda v:self.UpdateLayout( {'scene.zaxis.title':v['new']} ), names='value')
        self.options['marker_size'] = BoundedIntText(description = 'Markers size:', value = 3, min=0, max=15)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        self.DefaultLegend('v', 1.02, 1.0);
        
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id, z_id):
        traces = []
        color = "#444444"
        color = 'rgba'+str(self.getDeltaColor(color, .8))        
        trace = {
            'type': "scatter3d", 'mode': "markers", 'name': self.data.label,
            'marker': dict({
                'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
            }),
            'x': self.data[x_id].flatten(),
            'y': self.data[y_id].flatten(),
            'z': self.data[z_id].flatten(),
        }
        if self.only_subsets == False:
            traces.append(trace)
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:
                color = sset.style.color
                color = 'rgba'+str(self.getDeltaColor(color, .8))
                trace = {
                    'type': "scatter3d", 'mode': "markers", 'name': sset.label,
                    'marker': dict({
                        'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                    }),
                    'x': sset[x_id].flatten(),
                    'y': sset[y_id].flatten(),
                    'z': sset[z_id].flatten(),
                }
                traces.append(trace)

        layout = {            
            'margin' : {'l':0,'r':0,'b':0,'t':30 },            
            'scene' : {
                'xaxis': { 
                    'title' : self.options['xaxis'].value,
                    'linecolor' : self.data.get_component(x_id).color,
                    'tickcolor' : self.data.get_component(x_id).color,
                    'ticklen' : 4,
                    'linewidth' : 4,                
                    
                },
                'yaxis': { 
                    'title' : self.options['yaxis'].value,
                    'linecolor' : self.data.get_component(y_id).color,
                    'tickcolor' : self.data.get_component(y_id).color,
                    'ticklen' : 4,
                    'linewidth' : 4,                
                    
                },
                'zaxis': { 
                    'title' : self.options['zaxis'].value,
                    'linecolor' : self.data.get_component(z_id).color,
                    'tickcolor' : self.data.get_component(z_id).color,
                    'ticklen' : 4,
                    'linewidth' : 4,                                    
                }
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
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], self.dimensions[1], self.dimensions[2])     
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
           
            
