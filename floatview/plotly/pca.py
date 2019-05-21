from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
from ipywidgets import IntText, Dropdown
from IPython.display import clear_output
import numpy as np
from sklearn.decomposition import PCA, IncrementalPCA, KernelPCA

class GluePcaPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    pca = None
    options = {}
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", 'I Component', 'J Component')
        self.DefaultLayoutScales("linear","linear");
        self.options['line_width'] = IntText(description = 'Lines width:', value = 1)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = IntText(description = 'Markers size:', value = 3)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        self.options['pca_method'] = Dropdown(description = 'PCA Method:', value = 'PCA', options = ['PCA','KPCA','IPCA'])
        self.options['pca_method'].observe(lambda v:self.updateRender(), names='value')
        
        self.updateRender()
        
    def createFigureWidget(self):
        traces = []
        Xpca = []
        for x_id in self.dimensions:            
            if hasattr(self.data[x_id].flatten(), 'codes'):
                Xpca.append(self.data[x_id].flatten().codes.tolist())
            else:
                Xpca.append(self.data[x_id].flatten())

        Xpca = np.array(Xpca).transpose()
        self.pca.fit(Xpca)
        Xt = self.pca.transform(Xpca)

        data_l = [self.data[col_id].astype(str) for col_id in self.dimensions]
        data_l = zip(*data_l)
        t_val = [' - '.join( dat ) for dat in data_l]
        x_val = Xt[:,0]
        y_val = Xt[:,1]
        color = "#444444"
    
        trace = {
            'type': "scattergl", 'mode': "markers", 'name': self.data.label,
            'marker': dict({
                'symbol':'circle', 'size': self.options['marker_size'].value, 'color': color,
                'line' : { 'width' : self.options['line_width'].value, 'color' : color }
            }),
            'x': x_val.tolist(),
            'y': y_val.tolist(),
            'text': t_val,
        }
        
        #print(trace)

        if self.only_subsets == False:
            traces.append(trace)
            
        for sset in self.data.subsets:
            sset_mask = sset.to_mask()
            color = sset.style.color
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': sset.label,
                'marker': dict({
                    'symbol':'circle', 'size': self.focused_size_marker, 'color': color,
                    'line' : { 'width' : self.options['line_width'].value, 'color' : color}      
                }),
                'x': (x_val[sset_mask]).tolist(),
                'y': (y_val[sset_mask]).tolist(),
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
                'type' : self.options['xscale'].value,
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
        if self.options['pca_method'].value =="KPCA":
            self.pca = KernelPCA(n_components=2)
        elif self.options['pca_method'].value =="IPCA":
            self.pca = IncrementalPCA(n_components=2, fit_inverse_transform=True)
        else:
            self.pca = PCA(n_components=2)
        self.plotly_fig = self.createFigureWidget()

        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)

        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_selection(self.on_selection_callback, True)
        GluePlotly.display(self)


    def updateSelection(self, ids):
        self.plotly_fig.data[0].update(
            selectedpoints=ids,
        )

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
            
            
    def on_selection(self, callback):
        GluePlotly.on_selection(self, callback)

        bool_value = False
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), bool_value)
            bool_value  = True

        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_selection(self.on_selection_callback, bool_value)
            bool_value = True