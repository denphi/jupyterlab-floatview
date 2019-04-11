from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
import plotly.graph_objs as go
import numpy as np
  
class GlueParallelSankeyPlotly (GluePlotly):
    default_size_marker = 3
    focused_size_marker = 4
    def __init__(self, data, dimensions, **kwargs):
        GluePlotly.__init__(self, data, dimensions, **kwargs)
        self.DefaultLayoutTitles("", "", "")        
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
        #for sset in self.data.subsets: #self.data.subsets
        #

        sources = []
        targets = []
        nodes = [{} for dim in dimensions]
        nodest = [{} for dim in dimensions]
        values = []
        labels = []
        nodes_id = []
        for i, dimension in enumerate(dimensions):
            if hasattr(self.data[dimension].flatten(), 'codes'):
                nodes[i]['values'] = np.unique(self.data[dimension].flatten())
                nodes[i]['local_nodes'] = [len(nodes_id)+cnt for cnt in range(len(nodes[i]['values']))]
                nodes[i]['masks'] = []
                for val in nodes[i]['values']:
                     nodes[i]['masks'].append(self.data[dimension] == val)
            else:
                hist, bin_edges  = np.histogram(self.data[dimension].flatten(), bins='auto')
                nodes[i]['values'] = []
                for edge in range(len(bin_edges)-1):
                    nodes[i]['values'].append( "{:.1f}".format(bin_edges[edge]) + " - " + "{:.1f}".format(bin_edges[edge+1]))
                nodes[i]['local_nodes'] = [len(nodes_id)+cnt for cnt in range(len(nodes[i]['values']))]
                nodes[i]['masks'] = []
                for edge in range(len(bin_edges)-1):
                    if edge == 0:
                        nodes[i]['masks'].append((self.data[dimension] >= bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1]))      
                    else : 
                        nodes[i]['masks'].append((self.data[dimension] > bin_edges[edge]) & (self.data[dimension] <= bin_edges[edge+1]))      
                        
            nodes_id.extend(nodes[i]['local_nodes'])                
            labels.extend(nodes[i]['values'])

                
        for i in range(len(dimensions)-1):
            for j in range(len(nodes[i]['local_nodes'])):
                for k in range(len(nodes[i+1]['local_nodes'])):
                    total = np.count_nonzero((nodes[i]['masks'][j] & nodes[i+1]['masks'][k]))
                    if total > 0:
                        sources.append(nodes[i]['local_nodes'][j])
                        targets.append(nodes[i+1]['local_nodes'][k])
                        values.append(total)
                

        sankey = {
            'type' : 'sankey',
            'node' : {
              'pad' : 15,
              'thickness' : 20,
              'line' : {
                'color' : "black",
                'width' : 0.5
              },
              'label' : labels,
              'color' : ["blue" for i in labels]
            },
            'link' : {
              'source' : sources,
              'target' : targets,
              'value' : values,
              "hovertemplate": "%{label}<br><b>Source: %{source.label}<br>Target: %{target.label}<br> %{flow.value}</b>"
             
            }
        }

        data = [sankey]
        layout = {
            'title' : self.options['title'].value,
            'xaxis': {
                'title' : self.options['xaxis'].value,
            },
            'yaxis': {
                'title' : self.options['yaxis'].value,
            }
        }
        FigureWidget(data = data, layout = layout)
        return FigureWidget(data = data, layout = layout)
        
    def updateRender(self):
        self.plotly_fig = self.createFigureWidget()     
        GluePlotly.display(self)

    def updateSelection(self, ids):
        #self.parent.printInDebug(self.plotly_fig.data[0])        
        self.plotly_fig.data[0].update(
            selectedpoints=ids
        )

    #def setSubset(self,trace,points,selector): 
    #    if(self.parent is not None):
    #        self.parent.updateSelection(points.point_inds)
            
        
        