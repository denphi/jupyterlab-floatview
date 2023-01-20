from ipywidgets import widgets
from .floatview import Floatview
from .plotly.scatter import GlueScatterPlotly, GlueScatterMatrixPlotly
from .plotly.network import GlueNetworkPlotly
from .plotly.scatter3d import GlueScatter3DPlotly
from .plotly.contour import GlueContourPlotly
from .plotly.table import GlueTablePlotly
from .plotly.histogram import GlueHistogramPlotly
from .plotly.parallelcoordinates import GlueParallelCoordinatesPlotly, GlueParallelCategoriesPlotly
from .plotly.errorbar import GlueErrorBarPlotly
from .plotly.polyfit import GluePolyFitPlotly
from .plotly.line import GlueLinePlotly
from .plotly.image import GlueImagePlotly
from .plotly.sankey import GlueSankeyPlotly, GlueSankeytreePlotly
from .plotly.pca import GluePcaPlotly
from .plotly.corrcoef import GlueCorrelationsPlotly
from .plotly.sunburst import GlueSunburstPlotly
from glue import core as gcore
from glue.core.data import Data
import colorlover as cl
import re

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
        self.registerGluePlot("composed_lines", GlueLinePlotly)
        self.registerGluePlot("image", GlueImagePlotly, 3)
        self.registerGluePlot("sankey", GlueSankeyPlotly)
        self.registerGluePlot("network", GlueNetworkPlotly, 2)
        self.registerGluePlot("pca", GluePcaPlotly)
        self.registerGluePlot("corrcoef", GlueCorrelationsPlotly)
        self.registerGluePlot("sunburst", GlueSunburstPlotly)
        self.registerGluePlot("sankeytree", GlueSankeytreePlotly)
        self.registerGluePlot("scattermatrix", GlueScatterMatrixPlotly)  
        self.registerGluePlot("parallelscat", GlueParallelCategoriesPlotly)       
    
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
        self.colorset = ('12', 'qual', 'Paired')
        self.setColorSet(*self.colorset)

    def setColorSet(self, dimensions='12', type='qual', dataset='Paired'):
        if dimensions in cl.scales:
            if type in cl.scales[dimensions]:
                if dataset in cl.scales[dimensions][type]:                    
                    color_set = cl.scales[dimensions][type][dataset]
                    self.colorset = (dimensions, type, dataset)
                    if (len(self.data.components) > len(color_set)):
                        color_set = cl.interp( color_set, len(self.data.components) )
                    color_set = cl.to_rgb(color_set)
                    for i, component in enumerate(self.data.components):
                        self.data.get_component(component).color = color_set[i]
                    return True
        return False

    def listColorByType(self, type):
        listcolorset = []
        for dimension in cl.scales:
            if type in cl.scales[dimension]:
                for colorset in cl.scales[dimension][type]:
                    listcolorset.append((dimension, colorset))
        return listcolorset
        
    def setNewData(self, data):
        self.data = data

    def setParent(self, parent):    
        if isinstance(parent, GlueManagerWidget):
            self.parent = parent
        
    def newView(self, type="scatter", components=[], title="New View", **kwargs):
        only_subsets = kwargs.get('only_subsets', False)
        only_view = kwargs.get('only_view', False)
        if (self.parent is not None):
            kwargs.setdefault('modal', self.parent.modal)
        if (self.debug is not None):
            kwargs.setdefault('debug', self.debug)
                
        gp = None
        mode = "tab-after"
        if (len(self.active_views.values()) == 0):
            mode = "split-bottom"                    
        kwargs.setdefault('mode', mode)        

        
        if only_view is False:
            gp = self.factory.createGluePlot(type, self.data, components, title, **kwargs)
        else:
            data = Data(label=self.data.label)
            for c in components:
                data.add_component(self.data[c, self.selection], label=c)   
                data.get_component(c).color = self.data.get_component(c).color

            if (data.size > 0):
                gp = self.factory.createGluePlot(type, data, components, title, **kwargs)

        if gp is not None:
            if only_view is False:        
                gp.setParent(self)
                key = id(gp.window)
                self.active_views[key] = gp
                self.views[key]={'type':type,'components':components,'title':title, 'kwargs':kwargs }
                if isinstance(gp.window, Floatview):                
                    gp.window.observe(lambda changes : GlueManager.removeViewIfDisposed(self,gp.window),'uid')           
                    self.parent.updateHistory()
        return gp

    def delView(self, key):
        if isinstance(self.active_views[key].window, Floatview):
            GlueManager.removeViewIfDisposed(self,self.active_views[key].window)           
        del self.active_views[key]
        del self.views[key]
        self.parent.container.children = [v.window for k,v in self.active_views.items()]
        self.parent.updateHistory()


    def removeViewIfDisposed(self,window):
        if(window.uid == "disposed"):
            key = id(window)
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

    def disableComponentFromSelection(self, labels, values):
        sset_changed = []
        for sset in self.data.subsets:
            for i, label in enumerate(labels):
                if sset.label == label:
                    if hasattr(sset,"disabled") and sset.disabled == values[i]:
                        pass
                    else:
                        setattr(sset,'disabled',values[i])
                        sset_changed.append(sset)
        return sset_changed

    def changeSubsetColorFromSelection(self, labels, values):
        sset_changed = []
        for sset in self.data.subsets:
            for i, label in enumerate(labels):
                if sset.label == label:
                    if sset.style.color != values[i]:
                        sset.style.color = values[i]
                        sset_changed.append(sset)
        return sset_changed    

    def changeComponentColorFromSelection(self, labels, values):
        sset_changed = []
        for i, label in enumerate(labels):
            component = self.data.get_component(label)
            if component.color != values[i]:
                component.color = values[i]
                return True
        return False   

        
class GlueManagerWidget(widgets.Tab):
    gluemanager = None
    subsets = None
    debug = None
    plots = None
    subsetsui = None
    modal = False
    
    r = r"rgb\((\d+),\s*(\d+),\s*(\d+)\)"

    def __init__(self, gluemanager, modal=False, label=None, display_console=True):
        widgets.Tab.__init__(self);
        if isinstance(gluemanager, GlueManager):
            self.gluemanager = gluemanager
        elif isinstance(gluemanager, gcore.Data):
            self.gluemanager = GlueManager(gluemanager)
        else:
            self.gluemanager = GlueManager(gcore.Data(**gluemanager))
        self.display_console = display_console
        if (label is not None):
            self.gluemanager.data.label=label
        self.container = widgets.VBox()        
        self.gluemanager.setParent(self)
        self.subsets = self.createSubsetsPanel()
        self.plots = self.createPlotsPanel()
        self.history = self.createHistoryPanel()
        self.options = self.createOptions()
        self.modal = modal
        self.disable_color_update = False
        self.debug = self.gluemanager.debug
        self.children = [
            widgets.VBox([self.options, self.plots]), 
            widgets.VBox([self.subsets])
        ]        
        self.set_title(0, 'Plots')
        self.set_title(1, 'Subsets')
        if self.display_console:
            if (self.modal):
                modal_window = Floatview(title = "GMW("+str(id(self))+")", mode = "split-top")              
                with modal_window:
                    display(self)
            else:
                display(self)
                display(self.container)

    def setColorSet(self, dimensions='12', type='qual', dataset='Paired'):         
        if (self.gluemanager.setColorSet(dimensions, type, dataset)):
            self.disable_color_update = True
            for cont in self.dimensions.children:
                vc1 = cont.children[2]
                vc2 = cont.children[1]
                vc3 = cont.children[0]
                color = self.gluemanager.data.get_component(vc2.description).color
                color = re.match(GlueManagerWidget.r, color)
                color = (int(color[1]),int(color[2]),int(color[3]))
                color = '#%02x%02x%02x' % color
                vc2.style.button_color = color
                vc3.value = color
            self.disable_color_update = False
            self.gluemanager.updateTraces()
    
    def listColorSets(self):
        type='qual'
        return self.gluemanager.listColorByType(type)

    def createOptions(self):
        colorsets = self.listColorSets()
        list_cs = []
        for k in colorsets:
            list_cs.append(k[0] + "-qual-" + k[1])
        
        dd = widgets.Dropdown(
            options=list_cs,
            value="-".join(list(self.gluemanager.colorset)),
            disabled=False,
            description = "Colorset",
            layout=widgets.Layout(width = 'auto')
        )
        dd.observe(lambda change, this=self : this.setColorSet(*(change['new'].split('-'))), "value")
        vb1 = widgets.VBox([dd], layout=widgets.Layout(width='auto'))
        return vb1 
    
    def createSubsetsPanel(self):
    
        self.subsetsui = widgets.HBox([], layout=widgets.Layout(display='flex', flex_flow='wrap'))
        self.updateSubsets()
        
        cr = widgets.Button(
            description='Create subset from selection',
            disabled=False,
            button_style='',
            tooltip='create a new subset from current selection',
            layout=widgets.Layout(width='100%')
        )

        tx = widgets.Text(
            value='',
            placeholder='New subset name',
            disabled=False, 
            layout = widgets.Layout(width='auto')
        )
        
        cr.on_click(lambda e : GlueManagerWidget.createSubsetFromSelection(self, tx))
        
        hb1 = widgets.HBox([cr], layout=widgets.Layout(width='auto'))
        vb1 = widgets.VBox([self.subsetsui,tx,hb1], layout=widgets.Layout(width='auto'))

        
        return vb1

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
                color = self.gluemanager.data.get_component(k).color
                color = re.match(GlueManagerWidget.r, color)
                color = (int(color[1]),int(color[2]),int(color[3]))
                color = '#%02x%02x%02x' % color
                vc1 = widgets.Checkbox(
                    value=False, 
                    tooltip = kt, 
                    indent = False,
                    layout = widgets.Layout(width='40px')
                )
                vc2 = widgets.Button(
                    description = kt,
                    style = widgets.ButtonStyle(button_color=color),
                    disabled = False,
                    layout = widgets.Layout(min_width='min-content', max_width='min-content')
                )
                vc2.on_click(lambda event,v=vc1 : setattr(v,'value', not v.value))
                vc3 = widgets.ColorPicker(
                    description = "",
                    concise = True, 
                    value = color,
                    layout = widgets.Layout(width='40px', min_width='')
                )
                vc3.observe(lambda change, this=self, value=kt, vc=[vc2]: this.changeComponentColorFromSelection(value,change['new'],vc), "value")

                vv = widgets.HBox([vc3,vc2,vc1], layout=widgets.Layout(width='auto'))
                v.append(vv)

        self.dimensions = widgets.HBox(v, layout=widgets.Layout(display='flex', flex_flow='wrap'))

        cr = widgets.Button(
            description='Create new visualization',
            disabled=False,
            button_style='',
            tooltip='',
            layout=widgets.Layout(width='100%')
        )

        views = self.gluemanager.listPlots()

        dd = widgets.Dropdown(
            options=views,
            value=views[0],
            disabled=False,
            layout = widgets.Layout(width='auto')
        )

        ss = widgets.Checkbox(
            value=False,
            description='Only subsets',
            disabled=False,
            indent = False,
        )

        tx = widgets.Text(
            value='',
            placeholder='New_Visualization',
            disabled=False, 
            layout = widgets.Layout(width='auto')
        )
        
        
        hb1 = widgets.HBox([ss,cr], layout=widgets.Layout(width='auto'))
        vb1 = widgets.VBox([self.dimensions,dd,tx,hb1], layout=widgets.Layout(width='auto'))
        
        from IPython.display import display
        cr.on_click(lambda e, b=self.dimensions, this=self : this.createNewView(e, dd, b, tx, ss))

        return vb1 
        
    def _repr_html_(self):
        return widgets.Tab._repr_html_(self)

    def createNewView(self,e,dd, tb, tx, ss):
        list_comp = []
        for cont in tb.children:
            if (len(cont.children) == 3):
                vc1 = cont.children[2]
                vc2 = cont.children[1]
                if vc1.value == True:
                    list_comp.append(vc2.description) 
        gp = self.gluemanager.newView(dd.value, list_comp, tx.value, only_subsets=ss.value)
        if self.modal is False:
            new_children = list(self.container.children)
            new_children.append(gp.window)
            self.container.children = new_children
            with self.debug:
                display(gp.window)
            
            
    def createSubsetFromSelection(self, tx):        
        self.gluemanager.createSubsetFromSelection(tx.value)

    def deleteSubsetFromSelection(self, labels):
        self.gluemanager.deleteSubsetFromSelection(labels)

    def disableComponentFromSelection(self, label, ui=None):
        disable = [True]
        if ui is not None:
            disable = [ui.icon == "eye"]
        ssets = self.gluemanager.disableComponentFromSelection([label], disable)
        if ui is not None:
            for sset in ssets:
                if sset.label == label:
                    icon = 'eye'
                    if hasattr(sset, 'disabled') and sset.disabled is True:
                        icon = 'eye-slash'
                    ui.icon = icon
        elif len(ssets) > 0:
            self.updateSubsets()
        if len(ssets) > 0:
            self.gluemanager.updateTraces()
            
    def changeSubsetColorFromSelection(self, label, color, ui_list=None):
        ssets = self.gluemanager.changeSubsetColorFromSelection([label], [color])
        if ui_list is not None:
            for sset in ssets:
                if sset.label == label:
                    for ui in ui_list:
                        ui.style.button_color=color
        elif len(ssets) > 0:
            self.updateSubsets()
            
        if len(ssets) > 0:
            self.gluemanager.updateTraces()

    def changeComponentColorFromSelection(self, label, color, ui_list=[]):
        if self.disable_color_update == False:
            if self.gluemanager.changeComponentColorFromSelection([label], [color]):
                for ui in ui_list:
                    ui.style.button_color=color
                    self.gluemanager.updateTraces()

                
    def updateSubsets(self):
        v = []
        for sset in self.gluemanager.data.subsets:
            kt = sset.label
            color = sset.style.color
            vc2 = widgets.Button(
                description = kt,
                style = widgets.ButtonStyle(button_color=color),
                disabled = False,
                layout = widgets.Layout(min_width='min-content', max_width='min-content')
            )
            vc3 = widgets.Button(
                description = "",
                style = widgets.ButtonStyle(button_color=color),                
                icon = 'remove',
                disabled = False,
                layout = widgets.Layout(width='40px')
            )
            vc3.on_click(lambda event, this=self, value=[kt]: this.deleteSubsetFromSelection(value) )
            icon = 'eye'
            if hasattr(sset,'disabled') and sset.disabled is True:
                icon = 'eye-slash'
            vc1 = widgets.Button(
                description = "",
                style = widgets.ButtonStyle(button_color=color),                
                icon = icon,
                disabled = False,
                layout = widgets.Layout(width='40px'),
                value=True
            )
            vc1.on_click(lambda event, this=self, value=kt, vc=vc1: this.disableComponentFromSelection(value, vc) )
            vc4 = widgets.ColorPicker(
                description = "",
                concise = True, 
                value = sset.style.color,
                layout = widgets.Layout(width='40px', min_width='')
            )
            vc4.observe(lambda change, this=self, value=kt, vc=[vc1,vc2,vc3]: this.changeSubsetColorFromSelection(value,change['new'],vc), "value")
            vv = widgets.HBox([vc1,vc2,vc3,vc4], layout=widgets.Layout(width='auto'))
            v.append(vv)
        self.subsetsui.children = v

    def updateHistory(self):        
        self.activeui.options = [s.window.title for s in self.gluemanager.active_views.values() if isinstance(s.window, Floatview)]
        self.historyui.options = [(s['title'] + " - " + s['type']) for s in self.gluemanager.views.values()]
