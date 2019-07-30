from .glueplotly import GluePlotly
from plotly.graph_objects import FigureWidget
from ipywidgets import IntText, Dropdown, BoundedIntText
from IPython.display import clear_output
import numpy as np
import pandas as pd
import networkx as nx
import math
import re

class GlueNetworkPlotly (GluePlotly):
    default_size_marker = 5
    #'planar_layout' 'bipartite_layout'
    layout_options = ['spring_layout', 'circular_layout', 'kamada_kawai_layout', 'random_layout', 'shell_layout', 'spectral_layout']
    default_layout_type = layout_options[0]
    focused_size_marker = 3    
    options = {}
    G = None
    
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", "", "")
        self.options['line_width'] = BoundedIntText(description = 'Lines width:', value = 1, min=0, max=10)
        self.options['line_width'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')        
        self.options['marker_size'] = BoundedIntText(description = 'Markers size:', value = 3, min=0, max=15)
        self.options['marker_size'].observe(lambda v:self.UpdateTraces({'marker.size':v['new']}), names='value')        
        self.options['layout_type'] = Dropdown(description = 'Layout type:', value = self.default_layout_type, options=self.layout_options)
        self.options['layout_type'].observe(lambda v:self.updateRender(), names='value')        
        self.options['layout_k'] = BoundedIntText(description = 'Layout k:', value = 5, min=1,max=10)
        self.options['layout_k'].observe(lambda v:self.updateRender(), names='value')        
        self.options['layout_iter'] = BoundedIntText(description = 'Layout Iter:', value = 100, min=20,max=250)
        self.options['layout_iter'].observe(lambda v:self.updateRender(), names='value')        
        self.DefaultLegend('v', 1.02, 1.0);
        
        self.updateRender()
        
    def createFigureWidget(self, x_id, y_id):
   
        traces = []
        
        color = "#444444"        
        df = self.data.to_dataframe()
        df_merge = df.merge(df, on=y_id)
        dfo = pd.crosstab(df_merge[x_id + '_x'], df_merge[x_id + '_y'])
        idx = dfo.columns.union(dfo.index)
        dfo = dfo.reindex(index = idx, columns=idx, fill_value=0)
        self.G = nx.convert_matrix.from_pandas_adjacency(dfo)
        if self.options['layout_type'].value == 'bipartite_layout':
            pos = nx.bipartite_layout(self.G)
        elif self.options['layout_type'].value == 'circular_layout':
            pos = nx.circular_layout(self.G)
        elif self.options['layout_type'].value == 'kamada_kawai_layout':
            pos = nx.kamada_kawai_layout(self.G)
        elif self.options['layout_type'].value == 'planar_layout':
            pos = nx.planar_layout(self.G)
        elif self.options['layout_type'].value == 'random_layout':
            pos = nx.random_layout(self.G)
        elif self.options['layout_type'].value == 'shell_layout':
            pos = nx.shell_layout(self.G)
        elif self.options['layout_type'].value == 'spectral_layout':
            pos = nx.spectral_layout(self.G)
        elif self.options['layout_type'].value == 'shell_layout':
            pos = nx.shell_layout(self.G)
        else:
            pos = nx.spring_layout(self.G, k=self.options['layout_k'].value, iterations=self.options['layout_iter'].value)

        degree = dict(nx.degree(self.G))

        n_x = [0 for i in range(len(self.G.nodes()))]
        n_y = [0 for i in range(len(self.G.nodes()))]
        n_t = ['' for i in range(len(self.G.nodes()))]
        n_s = [0 for i in range(len(self.G.nodes()))]
        for i, node in enumerate(self.G.nodes()):
            n_x[i] = pos[node][0]
            n_y[i] = pos[node][1]
            n_t[i] = node
            n_s[i] = degree[node]

        max_degree = max(n_s)
        min_degree = min(n_s)
        n_s = [math.ceil((n-min_degree)/(max_degree-min_degree)*self.focused_size_marker*self.options['marker_size'].value) + self.options['marker_size'].value for n in n_s]
        
        node_trace = {
            'type' : "scatter",
            'name': self.data.label + "_" + x_id,
            'x' : n_x,
            'y' : n_y,
            'text' : n_t,
            'mode' : 'markers',
            'hoverinfo' :'text',
            'marker' : {
                'size' : n_s,
                'color' : self.data.get_component(x_id).color,
                'line' : {
                    'width' : self.options['line_width'].value,
                    'color' : self.data.get_component(x_id).color,
                }
            },
            'showlegend' : True,
        }

        e_x = [0 for i in range(2*len(self.G.edges()))]
        e_y = [0 for i in range(2*len(self.G.edges()))]

        for i, edge in enumerate(self.G.edges()):
            e_x[2*i] = pos[edge[0]][0]
            e_y[2*i] = pos[edge[0]][1]
            e_x[2*i+1] = pos[edge[1]][0]
            e_y[2*i+1] = pos[edge[1]][1]

        color = self.data.get_component(y_id).color        
        color = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)" , color)
        color = (int(color[1]),int(color[2]),int(color[3]))
        color = '#%02x%02x%02x' % color        
        color = 'rgba'+ str(self.getDeltaColor(color, 0.2))

        
        edge_trace = {
            'type' : "scatter",
            'name': self.data.label + "_" + y_id,
            'x' : e_x,
            'y' : e_y,
            'line' : {
                'width': self.options['line_width'].value,
                'color' : color,
            },
            'hoverinfo' : 'none',
            'mode' : 'lines',
            'showlegend' : True,
        }
        
        
        if self.only_subsets == False:
            traces.append(edge_trace)
            
        for sset in self.data.subsets:
            if hasattr(sset,"disabled") == False or sset.disabled == False:            
                color = sset.style.color

                dfs = df[sset.to_mask()]
                df_merge = dfs.merge(dfs, on=y_id)
                dfs = pd.crosstab(df_merge[x_id + '_x'], df_merge[x_id + '_y'])
                idx = dfs.columns.union(dfs.index)
                dfs = dfs.reindex(index = idx, columns=idx, fill_value=0)
                G = nx.convert_matrix.from_pandas_adjacency(dfs)

                e_x = [0 for i in range(2*len(G.edges()))]
                e_y = [0 for i in range(2*len(G.edges()))]

                for i, edge in enumerate(G.edges()):
                    e_x[2*i] = pos[edge[0]][0]
                    e_y[2*i] = pos[edge[0]][1]
                    e_x[2*i+1] = pos[edge[1]][0]
                    e_y[2*i+1] = pos[edge[1]][1]
                   
                trace = {
                    'type' : "scatter",           
                    'name': str(sset.label) + "_" + str(y_id),
                    'x' : e_x,
                    'y' : e_y,
                    'line' : {
                        'width': self.options['line_width'].value,
                        'color' : color
                    },
                    
                    'hoverinfo' : 'none',
                    'mode' : 'lines',
                    'showlegend' : True,
                }            

                traces.append(trace)  
               
        traces.append(node_trace)
        
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
                'autorange' : True ,
                'zeroline' : False,
                'showticklabels' : False,
                'showline' : True,
                'showgrid' : False,
            },
            'yaxis': { 'autorange':True, 'zeroline': True, 
                'title' : self.options['yaxis'].value, 
                'autorange' : True ,
                'zeroline' : False,
                'showticklabels' : False,
                'showline' : True,
                'showgrid' : False,
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
        self.plotly_fig = self.createFigureWidget(self.dimensions[0], self.dimensions[1])
        if self.only_subsets == False:
            self.plotly_fig.data[0].on_selection(lambda x,y,z : self.setSubset(x,y,z), True)
        if self.on_selection_callback is not None:
            self.plotly_fig.data[0].on_selection(self.on_selection_callback, True)
            
        GluePlotly.display(self)

    def updateSelection(self, ids):
        #self.parent.printInDebug(ids)        
        self.plotly_fig.data[0].update(
            selectedpoints=ids
        )

    def setSubset(self,trace,points,selector): 
        if(self.parent is not None):
            self.parent.updateSelection(points.point_inds)
