from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
import numpy as np
from ipywidgets import IntText, BoundedIntText


class GlueErrorBarPlotly (GluePlotly):
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", self.dimensions[0], ' '.join([self.dimensions[i] for i in range(1,len(self.dimensions))]))        
        self.DefaultLegend('v', 1.02, 1.0);
        self.updateRender()
        
    def createFigureWidget(self):
        x_id=self.dimensions[0]
        y_id_list=[self.dimensions[i] for i in range(1,len(self.dimensions))]
        d_val = self.data[x_id]
        if hasattr(self.data[x_id], 'codes'):
            d_val = self.data[x_id].codes.flatten()
        hist, bin_edges  = np.histogram(d_val.flatten(), bins='auto')
        bin_list = bin_edges.searchsorted(d_val.flatten(), 'right')
        
        xedges = []
        for i in range(len(bin_edges)-1):
            xedges.append((bin_edges[i+1]+bin_edges[i])/2)
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list), 0.1, 0.5)
        alpha_val = alpha_max
        for y_id in y_id_list:
        
            d_val = self.data[y_id]
            if hasattr(self.data[y_id], 'codes'):
                d_val = self.data[y_id].codes
        
            y_mean = []
            y_std_u = []
            y_std_l = []
            y_min = []
            y_max = []

            for i in range(1, len(bin_edges)):
                d_col = d_val[(bin_list == i)].flatten()
                if len(d_col) > 0:
                    i_mean = d_col.mean()
                    i_min = d_col.min()
                    i_max = d_col.max()
                    i_std = d_col.std()
                else:
                    i_mean = 0
                    i_std = 0
                    i_min = 0
                    i_max = 0
                y_mean.append(i_mean)
                y_std_u.append(i_mean+i_std)
                y_std_l.append(i_mean-i_std)
                y_min.append(i_min)
                y_max.append(i_max)

            color = "#444444"
            color = 'rgba'+str(self.getDeltaColor(color, alpha_val))
            
            trace = {
                'type': "scatter", 'name':'-',
                'marker' : {'color': color},
                'line': {'width': 0},
                'x': xedges,
                'y': y_min,
                'mode':'lines',
                'showlegend':False
            }
            if self.only_subsets == False:            
                traces.append(trace)
            
            trace = {
                'type': "scatter", 'name': self.data.label + "_" + y_id,
                'marker' : {'color': color},
                'fillcolor':color,
                'fill':'tonexty',
                'line': {'color': color},
                'x': xedges,
                'y': y_mean,
                'mode':'lines',
            }
            if self.only_subsets == False:    
                traces.append(trace)
            
            trace = {
                'type': "scatter", 'name':'+',
                'marker' : {'color': color},
                'fillcolor':color,
                'fill':'tonexty',
                'line': {'width': 0},
                'x': xedges,
                'y': y_max,
                'mode':'lines',
                'showlegend':False
            }
            if self.only_subsets == False:
                traces.append(trace)
            alpha_val = alpha_val - alpha_delta            
            
        
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                s_val = sset[x_id]
                if hasattr(sset[x_id], 'codes'):
                    s_val = sset[x_id].codes
                bin_list = bin_edges.searchsorted(s_val, 'right')
                alpha_val = alpha_max        
                for y_id in y_id_list:
                
                    s_val = sset[y_id]
                    if hasattr(sset[y_id], 'codes'):
                        s_val = sset[y_id].codes
                
                    y_s_mean = []
                    y_s_std_u = []
                    y_s_std_l = []

                    
                    for i in range(1, len(bin_edges)):
                        s_col = s_val[(bin_list == i)]
                        if len(s_col) > 0:
                            i_mean = s_col.mean()
                            i_std = s_col.std()
                            i_min = s_col.min()
                            i_max = s_col.max()
                        else:
                            i_mean = 0
                            i_std = 0  
                            i_min = 0
                            i_max = 0                        
                        y_s_mean.append(i_mean)
                        y_s_std_u.append(i_mean+i_std)
                        y_s_std_l.append(i_mean-i_std)
                        
                    color = sset.style.color
                    color = 'rgba'+str(self.getDeltaColor(color, alpha_val))
                    trace = {
                        'type': "scatter", 'name':'-',
                        'marker' : {'color': color},
                        'line': {'width': 0},
                        'x': xedges,
                        'y': y_s_std_l,
                        'mode':'lines',
                        'showlegend':False
                    }
                    traces.append(trace)            

                    
                    trace = {
                        'type': "scatter", 'name': sset.label + "_" + y_id,
                        'marker' : {'color': color},
                        'fillcolor':color,
                        'fill':'tonexty',
                        'line': {'color': color},
                        'x': xedges,
                        'y': y_s_mean,
                        'mode':'lines',
                    }
                    traces.append(trace)
                    
                    trace = {
                        'type': "scatter", 'name':'+',
                        'marker' : {'color': color},
                        'fillcolor':color,
                        'fill':'tonexty',
                        'line': {'width': 0},
                        'x': xedges,
                        'y': y_s_std_u,
                        'mode':'lines',
                        'showlegend':False
                    }
                    traces.append(trace)
                    alpha_val = alpha_val - alpha_delta
        y_color = 'rgb(0,0,0)'
        if len(y_id_list) == 1:
            y_color = self.data.get_component(y_id_list[0]).color
        layout = {
            'title' : self.options['title'].value,
            'margin' : {'l':50,'r':0,'b':50,'t':30 },
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : self.options['xaxis'].value, 
                'linecolor' : self.data.get_component(x_id).color,
                'tickcolor' : self.data.get_component(x_id).color,
                'ticklen' : 4,
                'linewidth' : 4,
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : self.options['yaxis'].value, 
                'linecolor' : y_color,
                'tickcolor' : y_color,
                'ticklen' : 4,
                'linewidth' : 4,
            },
            'showlegend': self.margins['showlegend'].value,
            'barmode': 'overlay',
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
        GluePlotly.display(self)

    def updateSelection(self, ids):
        pass       
