from plotly.offline import  init_notebook_mode, iplot, plot
import plotly.graph_objs as go
import numpy as np
from plotly.graph_objs import FigureWidget
from IPython.display import clear_output
from glue import core as gcore
from .floatview import Floatview

class GluePlotly():
    window = None
    plotly_fig = None
    data = None
    debug = None
    dimensions = None
    parent = None
    def __init__(self, data, dimensions, title, mode, debug=None):
        self.data = data
        self.debug = debug
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
        
class GlueScatterPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    def __init__(self, data, dimensions, title, mode, debug=None):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug)
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id):
        traces = []
        trace = {
            'type': "scattergl", 'mode': "markers", 'name': self.data.label,
            'marker': dict({
                'symbol':'circle', 'size': self.default_size_marker, 'color': 'rgba(0, 0, 0, 0.6)',
                'line' : { 'width' : 1, 'color' : '#000000' }
            }),
            'x': self.data[x_id],
            'y': self.data[y_id],
        }
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
            
            
class GlueScatter3DPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    def __init__(self, data, dimensions, title, mode, debug=None):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug)
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
    def __init__(self, data, dimensions, title, mode, debug=None):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug)
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

    def setSubset(self,trace,points,selector): 
        from .gluemanager import GlueManager
        if isinstance(self.parent, GlueManager):
            self.parent.updateSelection(points.point_inds)
            

class GlueHistogramPlotly (GluePlotly):
    def __init__(self, data, dimensions, title, mode, debug=None):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug)
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
    def __init__(self, data, dimensions, title, mode, debug=None): 
        GluePlotly.__init__(self, data, dimensions, title, mode, debug)      
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
    def __init__(self, data, dimensions, title, mode, debug=None):
        GluePlotly.__init__(self, data, dimensions, title, mode, debug)
        self.updateRender()
        
    def createFigureWidget(self):
        dimensions = self.dimensions
        data_lines = [] 
        i=0
        colors = [i for r in range(self.data.size)]
        colorscale = [[0,'#EEEEEE']]
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
            
        
        
