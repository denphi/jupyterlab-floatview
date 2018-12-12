from IPython.display import clear_output
from glue import core as gcore
from floatview import Floatview
from plotly.offline import init_notebook_mode
from matplotlib import colors
from ipywidgets import Output, Tab, Text, Dropdown


class GluePlotly():
    window = None
    plotly_fig = None
    output_cont = None
    options_cont = None
    data = None
    debug = None
    dimensions = None
    parent = None
    tab = None
    modal = True
    only_subsets = False
    options = {}
    
    def __init__(self, data, dimensions, **kwargs):
        self.data = data
        self.debug = kwargs.get('debug', None)
        title = kwargs.get('title', "")
        mode = kwargs.get('mode', "")
        self.only_subsets = kwargs.get('only_subsets', False)
        self.modal = kwargs.get('modal', True)
        self.dimensions = dimensions
        self.output_cont = Output()
        self.options_cont = Output()
        self.tab = Tab()
        self.options = {}
        self.tab.children = [self.output_cont, self.options_cont]
        self.tab.set_title(0, "View")
        self.tab.set_title(1, "View Options")
        init_notebook_mode(connected=True)        
        if (self.window == None) :
            if (self.modal == True):
                self.window = Floatview(title = title, mode = mode)  
            else:
                self.window = Output()
                display(self.window)
        self.displayWindow()

    def UpdateLayout(self, options):
        for key, value in options.items():
            try:
                self.plotly_fig.layout[key] = value                
            except:
                pass

    def UpdateTraces(self, options):
        for key, value in options.items():
            for i in range(len(self.plotly_fig.data)):
                try:
                    self.plotly_fig.data[i][key] = value
                except:
                    pass
            
    def DefaultLayoutTitles(self,title,xaxis,yaxis):
        self.options['title'] = Text( description = 'Title:', value = title )
        self.options['title'].observe(lambda v:self.UpdateLayout( {'title':v['new']} ), names='value')
        self.options['xaxis'] = Text( description = 'Xaxis Title:', value = xaxis )
        self.options['xaxis'].observe(lambda v:self.UpdateLayout( {'xaxis.title':v['new']} ), names='value')
        self.options['yaxis'] = Text( description = 'Yaxis Title:', value = yaxis )
        self.options['yaxis'].observe(lambda v:self.UpdateLayout( {'yaxis.title':v['new']} ), names='value')

    def DefaultLayoutScales(self, xscale, yscale):        
        self.options['xscale'] = Dropdown( description = 'Xaxis Scale:', value = xscale, options = ['linear','log'])
        self.options['xscale'].observe(lambda v:self.UpdateLayout( {'xaxis.type':v['new']} ), names='value')
        self.options['yscale'] = Dropdown( description = 'Yaxis Scale:', value = yscale, options = ['linear','log'])
        self.options['yscale'].observe(lambda v:self.UpdateLayout( {'yaxis.type':v['new']} ), names='value')

    
    def display(self):
        self.displayOutput()
        self.displayOptions()

    def displayOutput(self):   
        with self.output_cont:
            clear_output()
            display(self.plotly_fig)

    def displayWindow(self):   
        with self.window:
            clear_output()
            display(self.tab)


    def displayOptions(self): 
        with self.options_cont:
            clear_output()
            if len(self.options) > 0:
                for key, option in self.options.items():
                    display(option)
            else:
                display("there are no options enabled for this Visualization")

            
    def setParent(self, parent): 
        self.parent = parent

    def updateRender():
        pass
        
    def getDeltaFunction(self, size, alpha_min=0.5, alpha_max=0.8):
        if size > 1 :
            alpha_delta = (alpha_max-alpha_min)/(size-1)
        else :
            alpha_delta = (alpha_max-alpha_min)
        return alpha_min, alpha_max, alpha_delta
    
        
    def getDeltaColor (self, color, alpha_val, step=0, angle=25):
        rgb = colors.to_rgba(color)
        hsv = colors.rgb_to_hsv((rgb[0],rgb[1],rgb[2]))
        h = (round((hsv[0]*360+angle*step))%360)/360
        s = (round((hsv[1]*360+(angle/10)*step))%360)/360
        v = hsv[2]
        rgb = colors.hsv_to_rgb((h,s,v))
        return colors.to_rgba(rgb, alpha=alpha_val)
            

            


            



 
