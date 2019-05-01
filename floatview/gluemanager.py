from ipywidgets import widgets
from .floatview import Floatview
from .plotly.scatter import GlueScatterPlotly
from .plotly.network import GlueNetworkPlotly
from .plotly.scatter3d import GlueScatter3DPlotly
from .plotly.contour import GlueContourPlotly
from .plotly.table import GlueTablePlotly
from .plotly.histogram import GlueHistogramPlotly
from .plotly.parallelcoordinates import GlueParallelCoordinatesPlotly
from .plotly.errorbar import GlueErrorBarPlotly
from .plotly.polyfit import GluePolyFitPlotly
from .plotly.line import GlueLinePlotly
from .plotly.image import GlueImagePlotly
from .plotly.sankey import GlueParallelSankeyPlotly
from .plotly.pca import GluePcaPlotly
from glue import core as gcore

import itertools

class GlueManagerFactory:
    plot_list = {}
    
    def __init__(self):   
        self.registerGluePlot("scatter", GlueScatterPlotly,2)
        self.registerGluePlot("errorbar", GlueErrorBarPlotly,2)                
        self.registerGluePlot("composed_polyfit_2d", GluePolyFitPlotly, None, {'degree':2})
        self.registerGluePlot("composed_polyfit_3d", GluePolyFitPlotly, None, {'degree':3})
        self.registerGluePlot("scatter3D", GlueScatter3DPlotly, 3)                
        self.registerGluePlot("contour", GlueContourPlotly, 2)                
        self.registerGluePlot("table", GlueTablePlotly)
        self.registerGluePlot("parallels", GlueParallelCoordinatesPlotly)
        self.registerGluePlot("histogram", GlueHistogramPlotly, 1)                             
        self.registerGluePlot("composed_errorbar", GlueErrorBarPlotly)                
        self.registerGluePlot("composed_scatter", GlueScatterPlotly)                            
        self.registerGluePlot("composed_errorbar", GlueScatterPlotly)                                
        self.registerGluePlot("composed_lines", GlueLinePlotly)
        self.registerGluePlot("image", GlueImagePlotly, 3)
        self.registerGluePlot("sankey", GlueParallelSankeyPlotly)
        self.registerGluePlot("network", GlueNetworkPlotly, 2)
        self.registerGluePlot("pca", GluePcaPlotly)
    
    def listPlots(self):    
        return list(self.plot_list.keys());
        
    def registerGluePlot(self, type, func, dim=None, kwargs={}):
        self.plot_list[type] = {'dim': dim, 'func' : func, 'kwargs':kwargs}

    def createGluePlot(self, type, data, components, title="New View", **kwargs):
        if type in self.plot_list:
            dimensions = self.getDimensions(components,self.plot_list[type]['dim'])         
            for key, value in self.plot_list[type]['kwargs'].items():
                kwargs.setdefault(key, value)
            return self.plot_list[type]['func'](data, dimensions, title=title, **kwargs);
        return None;

    def getDimensions(self, components, dim=None):
        if dim is None:
            return components
        total_dimensions = len(components)
        req_dimensions = dim
        min_dimensions = min(req_dimensions,total_dimensions)
        dimensions = []
        for i in range(min_dimensions):
            dimensions.append(components[i])
        for i in range(min_dimensions, req_dimensions):
            dimensions.insert(0,components[0])            
        return dimensions
    

class GlueManager:
    data = None
    debug = None
    selection = []
    views = {}
    active_views = {}
    parent = None
    factory = None

    def __init__(self, data):
        self.data = data
        self.parent = None
        self.selection = []
        self.debug = widgets.Output()
        self.views = {}
        self.active_views = {}
        self.factory = GlueManagerFactory()
        
    def setNewData(self, data):
        self.data = data

    def setParent(self, parent):    
        if isinstance(parent, GlueManagerWidget):
            self.parent = parent
        
    def newView(self, type="scatter", components=[], title="New View", **kwargs):
        only_subsets = kwargs.get('only_subsets', False)
        if (self.parent is not None):
            kwargs.setdefault('modal', self.parent.modal)
        if (self.debug is not None):
            kwargs.setdefault('debug', self.debug)
                
        gp = None
        mode = "tab-after"
        if (len(self.active_views.values()) == 0):
            mode = "split-bottom"                    
        kwargs.setdefault('mode', mode)        

        gp = self.factory.createGluePlot(type, self.data, components, title, **kwargs)
        
        
        if gp is not None:
            gp.setParent(self)
            key = id(gp.window)
            self.active_views[key] = gp
            if isinstance(gp.window, Floatview):                
                gp.window.observe(lambda changes : GlueManager.removeViewIfDisposed(self,gp.window),'uid')           
                self.parent.updateHistory()
            self.views[key]={'type':type,'components':components,'title':title, 'kwargs':kwargs }
        return gp

    def removeViewIfDisposed(self,window):
        key = id(window)
        if(window.uid == "disposed"):
            self.active_views.pop(key)
            self.parent.updateHistory()
    
    def listPlots(self):    
        return self.factory.listPlots();
            

    def printInDebug(self, var):
        if self.debug is not None:
            with self.debug:
                print (var);
                
    def updateSelection(self,ids):
        self.selection = ids
        for view in self.active_views.values():
            view.updateSelection(ids)

    def updateTraces(self):
        for view in self.active_views.values():
            view.updateRender()

    def createSubsetFromSelection(self, label = 'data'):
        if (len(self.selection) > 0):
            state = gcore.subset.ElementSubsetState(indices=self.selection)
            self.data.new_subset(state, label=label)
            self.updateTraces()
            if isinstance(self.parent, GlueManagerWidget):
                self.parent.updateSubsets()
        
        
    def deleteSubsetFromSelection(self, labels):
        for label in labels:
            value = next((i for i in self.data.subsets if i.label == label), None)
            if (value is not None):
                value.delete()
        self.updateTraces()                
        if isinstance(self.parent, GlueManagerWidget):
            self.parent.updateSubsets()                


class GlueManagerWidget(widgets.Tab):
    gluemanager = None
    subsets = None
    debug = None
    plots = None
    subsetsui = None
    modal = False
    def __init__(self, gluemanager, modal=False, label=None):
        widgets.Tab.__init__(self);
        if isinstance(gluemanager, GlueManager):
            self.gluemanager = gluemanager
        elif isinstance(gluemanager, gcore.Data):
            self.gluemanager = GlueManager(gluemanager)
        else:
            self.gluemanager = GlueManager(gcore.Data(**gluemanager))

        if (label is not None):
            self.gluemanager.data.label=label
        
        self.gluemanager.setParent(self)
        self.subsets = self.createSubsetsPanel()
        self.plots = self.createPlotsPanel()
        self.history = self.createHistoryPanel()
        self.modal = modal
        self.debug = self.gluemanager.debug
        
        self.children = [self.plots, self.subsets, self.history, self.debug]
        self.set_title(0, 'Plots')
        self.set_title(1, 'Subsets')
        self.set_title(2, 'History')
        self.set_title(3, 'Debug')
        if (self.modal):
            modal_window = Floatview(title = "GMW("+str(id(self))+")", mode = "split-top")  
            with modal_window:
                display(self)
        else:
            display(self)

    def createSubsetsPanel(self):
        self.subsetsui = widgets.SelectMultiple(
            options=[sset.label for sset in self.gluemanager.data.subsets],
            value=[],
            rows=4,
            disabled=False
        )
        self.subsetsui.layout = widgets.Layout(width='99%')

        bt = widgets.Button(
            description='Create new Subset.',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='createa new subset from current selection',
        )
        
        bt.layout = widgets.Layout(width='99%')

        tx = widgets.Text(
            value='',
            placeholder='new subset name',
            disabled=False
        )
        tx.layout = widgets.Layout(width='99%')

        bt.on_click(lambda e : GlueManagerWidget.createSubsetFromSelection(self, tx))

        dl = widgets.Button(
            description='remove selected Subsets',
            disabled=False,
            button_style='danger',
            tooltip='Removes active subsets from the data workspace',
        )
               
        dl.layout = widgets.Layout(width='99%')
        dl.on_click(lambda e : GlueManagerWidget.deleteSubsetFromSelection(self))


        sl = widgets.Button(
            description='Hide selected subsets',
            disabled=False,
            button_style='warning',
            tooltip='',
        )
        
        
        sl.layout = widgets.Layout(width='99%')

        vb = widgets.VBox([dl, sl])

        vb2 = widgets.VBox([tx, bt])

        hb1 = widgets.HBox([vb2,self.subsetsui,vb])


        vb3 = widgets.VBox([hb1])
        
        return vb3

    def createHistoryPanel(self):
        self.activeui = widgets.SelectMultiple(
            options=[],
            value=[],
            rows=4,
            disabled=False
        )
        self.activeui.layout = widgets.Layout(width='99%')       
        
        self.historyui = widgets.SelectMultiple(
            options=[],
            value=[],
            rows=4,
            disabled=False
        )
        self.historyui.layout = widgets.Layout(width='99%')

        bt = widgets.Button(
            description = 'Recreate plot',
            disabled=False,
            button_style='', # 'success', 'info', 'warning', 'danger' or ''
            tooltip='re creates plot',
        )        
        bt.on_click(lambda e : GlueManagerWidget.restorePlot(self))

        hb4 = widgets.HBox([self.historyui, bt])        
        vb4 = widgets.VBox([self.activeui, hb4])        
        return vb4

    def restorePlot(self):
            list_val = list(self.gluemanager.views.values())
            plot = list_val[self.historyui.index[0]]
            self.gluemanager.newView(plot['type'], plot['components'], 'copy_' + plot['title'], **plot['kwargs'])
        
    def createPlotsPanel(self):
        components = self.gluemanager.data.components
        pixel_component_ids = self.gluemanager.data.pixel_component_ids
        world_component_ids = self.gluemanager.data.world_component_ids
        
        v = []
        for k in components:
            if k not in world_component_ids: #k not in pixel_component_ids and
                kt = str(k)
                vv = widgets.ToggleButton(
                    value=False, tooltip=kt, description=kt
                )
                v.append(vv)

        tb = widgets.HBox(v)

        cr = widgets.Button(
            description='Create new visualization',
            disabled=False,
            button_style='',
            tooltip='',
        )

        views = self.gluemanager.listPlots()

        dd = widgets.Dropdown(
            options=views,
            value=views[0],
            disabled=False,
        )

        ss = widgets.Checkbox(
            value=False,
            description='Only subsets',
            disabled=False
        )

        tx = widgets.Text(
            value='',
            placeholder='New_Visualization',
            disabled=False
        )
        
        
        hb1 = widgets.HBox([dd,tx,ss,cr])
        vb1 = widgets.VBox([tb,hb1])
        
        from IPython.display import display
        cr.on_click(lambda e : GlueManagerWidget.createNewView(self,e, dd, tb.children, tx, ss))

        return vb1    
    def _repr_html_(self):
        return widgets.Tab._repr_html_(self)

    def createNewView(self,e,dd, tb, tx, ss):
        list_comp = []
        for vv in tb:
            if vv.value == True:
                list_comp.append(vv.description)                        
        self.gluemanager.newView(dd.value, list_comp, tx.value, only_subsets=ss.value)
            
    def createSubsetFromSelection(self, tx):        
        self.gluemanager.createSubsetFromSelection(tx.value)

    def deleteSubsetFromSelection(self):
        self.gluemanager.deleteSubsetFromSelection(self.subsetsui.value)
        
    def updateSubsets(self):
        self.subsetsui.options = [sset.label for sset in self.gluemanager.data.subsets]

    def updateHistory(self):        
        self.activeui.options = [s.window.title for s in self.gluemanager.active_views.values() if isinstance(s.window, Floatview)]
        self.historyui.options = [(s['title'] + " - " + s['type']) for s in self.gluemanager.views.values()]
