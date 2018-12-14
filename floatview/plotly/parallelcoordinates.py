from .glueplotly import GluePlotly
from plotly.graph_objs import FigureWidget
import plotly.graph_objs as go
  
class GlueParallelCoordinatesPlotly (GluePlotly):
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
            line['values'] = self.data[dimension].flatten().tolist()
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
        layout = {
            'title' : self.options['title'].value,
            'xaxis': {
                'title' : self.options['xaxis'].value, 
            },
            'yaxis': {
                'title' : self.options['yaxis'].value, 
            }
        }
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
    #    if(self.parent is not None):
    #        self.parent.updateSelection(points.point_inds)
            
        
        