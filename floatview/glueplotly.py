from plotly.offline import  init_notebook_mode, iplot, plot
import plotly.graph_objs as go
import numpy as np
from plotly.graph_objs import FigureWidget
from IPython.display import clear_output
from glue import core as gcore
from .floatview import Floatview
from matplotlib import colors
class GluePlotly():
    window = None
    plotly_fig = None
    data = None
    debug = None
    dimensions = None
    parent = None
    only_subsets = False
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        self.data = data
        self.debug = debug
        self.only_subsets = only_subsets
        self.dimensions = dimensions
        init_notebook_mode(connected=True)
        
        if (self.window == None) :
            self.window = Floatview(title = title, mode = mode)  
    
    def display(self):
        with self.window:
            clear_output()
            display(self.plotly_fig)

            
    def setParent(self, parent): 
        self.parent = parent

    def updateRender():
        pass
		
    def getDeltaFunction(self, size, alpha_min=0.3, alpha_max=0.8):
        if size > 1 :
            alpha_delta = (alpha_max-alpha_min)/(size-1)
        else :
            alpha_delta = (alpha_max-alpha_min)
        return alpha_min, alpha_max, alpha_delta
	
        
class GlueScatterPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
	
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max        
        for y_id in y_id_list:
            color = "#444444"
            color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': self.data.label + "_" + y_id,
                'marker': dict({
                    'symbol':'circle', 'size': self.default_size_marker, 'color': color,
                    'line' : { 'width' : 1, 'color' : color }
                }),
                'x': self.data[x_id],
                'y': self.data[y_id],
            }
            if self.only_subsets == False:
                traces.append(trace)
            alpha_val = alpha_val - alpha_delta
            
        for sset in self.data.subsets:
            alpha_val = alpha_max        
            for y_id in y_id_list:
                color = sset.style.color
                color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))                
                trace = {
                    'type': "scattergl", 'mode': "markers", 'name': sset.label + "_" + y_id,
                    'marker': dict({
                        'symbol':'circle', 'size': self.focused_size_marker, 'color': color,
                        'line' : { 'width' : 2, 'color' : color}      
                    }),
                    'selected':{'marker':{'color':color, 'size': self.focused_size_marker}},
                    'unselected':{'marker':{'color':color, 'size': self.focused_size_marker}},                
                    'x': sset[x_id],
                    'y': sset[y_id],
                }
                traces.append(trace)  
                alpha_val = alpha_val - alpha_delta
                

        layout = {
            'margin' : {'l':50,'r':0,'b':50,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : x_id },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : ' '.join(y_id_list) },
            'showlegend': True,
        }
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def changeAxisScale(self, axis="yaxis",type="linear"):
        self.plotly_fig.layout[axis].type = type

    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], [self.dimensions[i] for i in range(1,len(self.dimensions))])
        if len(self.dimensions) == 2:
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
        from .gluemanager import GlueManager
        if isinstance(self.parent, GlueManager):
            self.parent.updateSelection(points.point_inds)
            
class GlueLinePlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    x_scale_type = 'linear'
    y_scale_type = 'linear'
    marker_type = 'lines'

    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max        
        for y_id in y_id_list:
            color = "#444444"
            color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))
            trace = {
                'type': "scattergl", 'mode': self.marker_type, 'name': self.data.label + "_" + y_id,
                'line' : { 'width' : 1, 'color' : color },
                'x': self.data[x_id],
                'y': self.data[y_id],
            }
            if self.only_subsets == False:
                traces.append(trace)
            alpha_val = alpha_val - alpha_delta
            
        for sset in self.data.subsets:
            alpha_val = alpha_max        
            for y_id in y_id_list:
                color = sset.style.color
                color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))                
                trace = {
                    'type': "scattergl", 'mode': self.marker_type, 'name': sset.label + "_" + y_id,
                    'line' : { 'width' : 1, 'color' : color},
                    'x': sset[x_id],
                    'y': sset[y_id],
                }
                traces.append(trace)  
                alpha_val = alpha_val - alpha_delta
                

        layout = {
            'margin' : {'l':50,'r':0,'b':50,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : x_id, 'type' : self.x_scale_type },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : ' '.join(y_id_list), 'type' : self.y_scale_type },
            'showlegend': True,
        }
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], [self.dimensions[i] for i in range(1,len(self.dimensions))])
        if len(self.dimensions) == 2:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

    def changeAxisScale(self, axis="yaxis",type="linear"):
        self.plotly_fig.layout[axis].type = type
        
    def changeMarker(self, type="lines"):
        if (type == "lines+markers"):
            self.marker_type = type
            self.updateRender()
        elif (type == "lines"):
            self.marker_type = type
            self.updateRender()
        elif (type == "lines+text"):
            self.marker_type = type
            self.updateRender()
        
    def updateSelection(self, ids):
        pass #self.parent.printInDebug(ids)        

    def setSubset(self,trace,points,selector): 
        from .gluemanager import GlueManager
        if isinstance(self.parent, GlueManager):
            self.parent.updateSelection(points.point_inds)
            

class GluePolyFitPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    degree = 2
    def __init__(self, data, dimensions, degree, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.degree = degree
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id_list):
        traces = []
        alpha_min, alpha_max, alpha_delta = self.getDeltaFunction(len(y_id_list))
        alpha_val = alpha_max
        polyfun = {}
        for y_id in y_id_list:
            z = np.polyfit(self.data[x_id], self.data[y_id], self.degree)
            polyfun[y_id] = np.poly1d(z)
            color = "#444444"
            color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': self.data.label + "_" + y_id,
                'marker': dict({
                    'symbol':'circle', 'size': self.default_size_marker, 'color': color,
                    'line' : { 'width' : 1, 'color' : color }
                }),
                'x': self.data[x_id],
                'y': self.data[y_id],
            }
            if self.only_subsets == False:
                traces.append(trace)
            y_new = polyfun[y_id](self.data[x_id])
            trace = {
                'type': "scattergl", 'mode': "lines", 'name': self.data.label + "_fit_" + y_id,
                'line' : { 'width' : 1, 'color' : color }, 
                'x': self.data[x_id],
                'y': y_new,
                'showlegend':False
            }
            if self.only_subsets == False:
                traces.append(trace)
            
            alpha_val = alpha_val - alpha_delta
            
        for sset in self.data.subsets:
            alpha_val = alpha_max        
            for y_id in y_id_list:
                z = np.polyfit(sset[x_id], sset[y_id], self.degree)
                f = np.poly1d(z)
                color = sset.style.color
                color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))
                with self.debug:
                    print(color)
                trace = {
                    'type': "scattergl", 'mode': "markers", 'name': sset.label + "_" + y_id,
                    'marker': dict({
                        'symbol':'circle', 'size': self.focused_size_marker, 'color': color,
                        'line' : { 'width' : 1, 'color' : color}      
                    }),
                    'selected':{'marker':{'color':color, 'size': self.focused_size_marker}},
                    'unselected':{'marker':{'color':color, 'size': self.focused_size_marker}},                
                    'x': sset[x_id],
                    'y': sset[y_id],

                }
                traces.append(trace)  
                y_new = f(sset[x_id])
                trace = {
                    'type': "scattergl", 'mode': "lines", 'name': sset.label + "_fit_" + y_id,
                    'line' : { 'width' : 1, 'color' : color }, 
                    'x': sset[x_id],
                    'y': y_new,
                    'showlegend':False
                }
                traces.append(trace)                
                alpha_val = alpha_val - alpha_delta
                

        layout = {
            'margin' : {'l':50,'r':0,'b':50,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : x_id },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : ' '.join(y_id_list) },
            'showlegend': True,
        }
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], [self.dimensions[i] for i in range(1,len(self.dimensions))])
        if len(self.dimensions) == 2:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        #self.parent.printInDebug(ids)        
        self.plotly_fig.data[0].update(
            selectedpoints=ids,
            selected={'marker':{'color':'rgba(0, 0, 0, 0.4)', 'size': self.focused_size_marker}},
            unselected={'marker':{'color':'rgba(0, 0, 0, 0.1)', 'size': self.default_size_marker}}
        )
		
    def changeAxisScale(self, axis="yaxis",type="linear"):
        self.plotly_fig.layout[axis].type = type


    def setSubset(self,trace,points,selector): 
        from .gluemanager import GlueManager
        if isinstance(self.parent, GlueManager):
            self.parent.updateSelection(points.point_inds)            
            
class GlueErrorBarPlotly (GluePlotly):
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self):
        x_id=self.dimensions[0]
        y_id_list=[self.dimensions[i] for i in range(1,len(self.dimensions))]
        d_val = self.data[x_id]
        if hasattr(self.data[x_id], 'codes'):
            d_val = self.data[x_id].codes
        hist, bin_edges  = np.histogram(d_val, bins='auto')
        bin_list = bin_edges.searchsorted(d_val, 'right')
        
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

            with self.debug:
              for i in range(1, len(bin_edges)):
                d_col = d_val[(bin_list == i)]
                print(d_col)
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
            color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))
            
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
                color = 'rgba'+str(colors.to_rgba(color, alpha=alpha_val))
                with self.debug:
                  print (color)
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
                
        layout = {
            'margin' : {'l':50,'r':0,'b':50,'t':30 },
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : x_id },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : ' '.join(y_id_list) },
            'showlegend': True,
            'barmode': 'overlay',
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

   
class GlueScatter3DPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id, z_id):
        traces = []
        trace = {
            'type': "scatter3d", 'mode': "markers", 'name': self.data.label,
            'marker': dict({
                'symbol':'circle', 'size': self.default_size_marker, 'color': 'rgba(0,0,0,0.8)',
            }),
            'x': self.data[x_id],
            'y': self.data[y_id],
            'z': self.data[z_id],
        }
        if self.only_subsets == False:
            traces.append(trace)
        for sset in self.data.subsets:
            color = sset.style.color
            trace = {
                'type': "scatter3d", 'mode': "markers", 'name': sset.label,
                'marker': dict({
                    'symbol':'circle', 'size': self.focused_size_marker, 'color': color, 'opacity':0.8,
                }),
                'x': sset[x_id],
                'y': sset[y_id],
                'z': sset[z_id],
            }
            traces.append(trace)


        layout = {            
            'margin' : {'l':0,'r':0,'b':0,'t':30 },            
            'xaxis': { 'title' : x_id },
            'yaxis': { 'title' : y_id },
            #'zaxis': { 'title' : z_id },
            'showlegend': True,
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
        #self.parent.printInDebug(self.plotly_fig.data[0])        
        self.plotly_fig.data[0].update(
            selectedpoints=ids
        )

    #def setSubset(self,trace,points,selector): 
    #     from .gluemanager import GlueManager    
    #    if isinstance(self.parent, GlueManager):
    #        self.parent.updateSelection(points.point_inds)
           
            
class GlueContourPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    ncontours = 1
    nbins = 40
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id):
        heatmap, xedges, yedges = np.histogram2d(self.data[x_id], self.data[y_id], bins=self.nbins)
        mod_heatmap = np.zeros((self.nbins+2,self.nbins+2))
        mod_heatmap[1:-1,1:-1] = heatmap.T
        #d_val = self.data[x_id]
        #if hasattr(self.data[x_id], 'codes'):
        #    d_val = self.data[x_id].codes
        
        traces = []
        trace = {
            'type': "contour",
            'colorscale':[[0, 'rgb(255,255,255)'], [1, 'rgb(0,0,0)']],'showlegend':False,
            'autocontour':False,'ncontours':self.ncontours,
            'contours':{'coloring':'heatmap'},
            'x0': xedges[0]-(xedges[1]-xedges[0])/2,
            'dx': xedges[1]-xedges[0],
            'y0': yedges[0]-(yedges[1]-yedges[0])/2,
            'dy': yedges[1]-yedges[0],
            'z':mod_heatmap
        }
        if self.only_subsets == False:
            traces.append(trace)
        trace = {
            'type': "scattergl", 'mode': "markers", 'name': self.data.label,
            'marker': dict({
                'symbol':'circle', 'size': self.default_size_marker, 'color': 'rgba(0, 0, 0, 0.4)',
                'line' : { 'width' : 1, 'color' : 'rgba(0, 0, 0, 0.3)' }
            }),
            'x': self.data[x_id],
            'y': self.data[y_id],
        }
        if self.only_subsets == False:    
            traces.append(trace)
        for sset in self.data.subsets:
            color = sset.style.color
            trace = {
                'type': "scattergl", 'mode': "markers", 'name': sset.label,
                'marker': dict({
                    'symbol':'circle', 'size': self.focused_size_marker, 'color': color,
                    'line' : { 'width' : 1, 'color' : '#000000'}      
                }),
                'selected':{'marker':{'color':color, 'size': self.focused_size_marker}},
                'unselected':{'marker':{'color':color, 'size': self.focused_size_marker}},                 
                'x': sset[x_id],
                'y': sset[y_id],
            }
            traces.append(trace)

        layout = {
            'margin' : {'l':30,'r':0,'b':30,'t':30 },            
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : x_id },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : y_id },
            'showlegend': True,
        }
        return FigureWidget({
                'data': traces,
                'layout': layout
        })
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], self.dimensions[1])     
        self.plotly_fig.data[1].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        self.plotly_fig.data[1].update(
            selectedpoints=ids,
            selected={'marker':{'color':'rgba(0, 0, 0, 0.4)', 'size': self.focused_size_marker}},
            unselected={'marker':{'color':'rgba(0, 0, 0, 0.1)', 'size': self.default_size_marker}}
        )
		
    def changeAxisScale(self, axis="yaxis",type="linear"):
        self.plotly_fig.layout[axis].type = type


    def setSubset(self,trace,points,selector): 
        from .gluemanager import GlueManager
        if isinstance(self.parent, GlueManager):
            self.parent.updateSelection(points.point_inds)
            

class GlueHistogramPlotly (GluePlotly):
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self):
        x_id=self.dimensions[0]
        d_val = self.data[x_id]
        if hasattr(self.data[x_id], 'codes'):
            d_val = self.data[x_id].codes
        hist, bin_edges  = np.histogram(d_val, bins='auto')
        xedges = []
        for i in range(len(bin_edges)-1):
            xedges.append((bin_edges[i+1]+bin_edges[i])/2)
        traces = []
        trace = {
            'type': "bar", 'name': self.data.label,
            'marker' : {'color': 'rgba(0, 0, 0, 0.1)'},
            'x': xedges,
            'y': hist,
        }
        if self.only_subsets == False:        
            traces.append(trace)
        for sset in self.data.subsets:
            s_val = sset[x_id]
            if hasattr(sset[x_id], 'codes'):
                s_val = sset[x_id].codes
            hist, bin_edges  = np.histogram(s_val, range=(bin_edges[0], bin_edges[len(bin_edges)-1]),bins=len(bin_edges))
            color = sset.style.color
            trace = {
                'type': "bar", 'name': sset.label,
                'marker' : {'color': color},
                'x': xedges,
                'y': hist,
            }
            traces.append(trace)

        layout = {
            'margin' : {'l':30,'r':0,'b':30,'t':30 },
            'xaxis': { 'autorange' : True, 'zeroline': True, 'title' : x_id },
            'yaxis': { 'autorange':True, 'zeroline': True, 'title' : 'total' },
            'showlegend': True,
            'barmode': 'overlay',
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
            
class GlueTablePlotly (GluePlotly):
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False): 
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)      
        values = [self.data[col].tolist() for col in self.dimensions]   
        layout = {
            'margin' : {'l':10,'r':10,'b':0,'t':10 },     
        }        
        self.plotly_fig = go.FigureWidget([go.Table(
            header=dict(values=dimensions,
                        fill = dict(color='#C2D4FF'),
                        align = ['left'] * 5),
            cells=dict(values=values,
                       fill = dict(color='#F5F8FF'),
                       align = ['left'] * 5))], layout=layout)
        GluePlotly.display(self)

    def updateSelection(self, ids):
        dimensions = self.plotly_fig.data[0].header.values
        values = [self.data[col][ids].tolist() for col in dimensions]
        self.plotly_fig.data[0].cells.values = values
        
      
            
class GlueParallelCoordinatesPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    def __init__(self, data, dimensions, title, mode, debug=None, only_subsets=False):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug, only_subsets)
        self.updateRender()
        
    def createFigureWidget(self):
        dimensions = self.dimensions
        data_lines = [] 
        i=0
        if self.only_subsets == False:
            colors = [i for r in range(self.data.size)]
            colorscale = [[0,'#EEEEEE']]
        else:
            colors = []
            colorscale = []
            i=-1
            
        for sset in self.data.subsets:
            i = i+1
            tmplist = [i for r in range(len(sset.to_index_list()))]
            colors.extend(tmplist)
            colorscale.append([i,sset.style.color])
        t_color = len(colorscale)        
        if (t_color > 1):
            for c in colorscale:
                c[0] = c[0]/(t_color-1)
        else:
            colorscale = [[0,'#EEEEEE'], [1,'#EEEEEE']] 

        for dimension in dimensions:
            line={}
            line['values'] = self.data[dimension].tolist()
            line['label'] = dimension
            for sset in self.data.subsets:
                tmplist = sset[dimension].tolist()
                line['values'].extend(tmplist)
            data_lines.append(line);
        data = [
            go.Parcoords(
                line = dict(color = colors, colorscale = colorscale),
                dimensions = data_lines
            ),    
        ]
        layout = go.Layout()
        return FigureWidget(data = data, layout = layout)
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget()     
        #self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)            
        GluePlotly.display(self)

    def updateSelection(self, ids):
        #self.parent.printInDebug(self.plotly_fig.data[0])        
        self.plotly_fig.data[0].update(
            selectedpoints=ids
        )

    #def setSubset(self,trace,points,selector): 
    #   from .gluemanager import GlueManager
    #   if isinstance(self.parent, GlueManager):
    #        self.parent.updateSelection(points.point_inds)   
            
        
        
