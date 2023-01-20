from IPython.display import clear_output
from glue import core as gcore
from floatview import Floatview
from plotly.offline import init_notebook_mode
from matplotlib import colors
from ipywidgets import Output, Tab, ToggleButton, Text, Dropdown, IntText, VBox, HBox, Accordion, FloatSlider, Label, Checkbox, Button


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
    margins = {}
    on_selection_callback = None
    
    def __init__(self, data, dimensions, **kwargs):
        self.data = data
        self.options = {}
        self.margins = {}
        self.dimensions = dimensions
        self.debug = kwargs.get('debug', None)
        self.modal = kwargs.get('modal', True)
        self.only_subsets = kwargs.get('only_subsets', False)
        self.output_cont = Output()
        self.output_cont.layout.width = '100%'
        self.options_cont = Output()
        self.margins_cont = Output()

        self.option_tab = Tab()
        self.option_tab.children = [self.options_cont, self.margins_cont]
        self.option_tab.set_title(0, "Plot")
        self.option_tab.set_title(1, "Layout") 
        self.option_tab.layout.display = 'none'


        self.options_check = ToggleButton(value = False, description="Options", icon='cog')
        self.options_check.observe(lambda v:self.showWidget(v["new"]), names='value')






        self.tab = HBox()
        self.tab.children = [self.option_tab, self.output_cont]
        init_notebook_mode(connected=True)        
        if (self.window == None) :
            if (self.modal == True):
                title = kwargs.get('title', "")
                mode = kwargs.get('mode', "")
                self.window = Floatview(title = title, mode = mode)  
            else:
                self.window = Output()

        self.options_close = Button(value = "Close", description="Close", icon='close')
        self.options_close.on_click(lambda e: self.parent.delView(id(self.window)))

        self.DefaultMargins()
        self.displayWindow()

    def showWidget(self, show):
        if show:
            self.option_tab.layout.display = None
        else:
            self.option_tab.layout.display = "None"
       
        
    def UpdateLayout(self, options):
        for key, value in options.items():
            try:
                self.plotly_fig.layout[key] = value                
            except:
                pass

    def UpdateTraces(self, options):
        for key, value in options.items():
            for i in range(len(self.plotly_fig.data)):
                with self.debug:
                    self.plotly_fig.data[i][key] = value

            
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

    def DefaultMargins(self,l=50,r=0,b=50,t=30):
        self.margins['left'] = IntText( description = 'Left:', value = l )
        self.margins['left'].observe(lambda v:self.UpdateLayout( {'margin.l':v['new']} ), names='value')
        self.margins['right'] = IntText( description = 'Right:', value = r )
        self.margins['right'].observe(lambda v:self.UpdateLayout( {'margin.r':v['new']} ), names='value')
        self.margins['bottom'] = IntText( description = 'Bottom:', value = b )
        self.margins['bottom'].observe(lambda v:self.UpdateLayout( {'margin.b':v['new']} ), names='value')
        self.margins['top'] = IntText( description = 'Top:', value = t )
        self.margins['top'].observe(lambda v:self.UpdateLayout( {'margin.t':v['new']} ), names='value')
        
    def DefaultLegend(self, orientation, xpos, ypos):
        self.margins['legend'] = Label( value = 'Legend' )
        self.margins['showlegend'] = Checkbox(value = True, description="visible:")
        self.margins['showlegend'].observe(lambda v:self.UpdateLayout( {'showlegend':v['new']} ), names='value')
        self.margins['legend_orientation'] = Dropdown( description = 'orientation:', value = orientation, options = ['h','v'])
        self.margins['legend_orientation'].observe(lambda v:self.UpdateLayout( {'legend.orientation':v['new']} ), names='value')
        self.margins['legend_xpos'] = FloatSlider( description = 'x pos:', value = xpos, min=-0.2, max=1.2 )
        self.margins['legend_xpos'].observe(lambda v:self.UpdateLayout( {'legend.x':v['new']} ), names='value')
        self.margins['legend_ypos'] = FloatSlider( description = 'y pos:', value = ypos, min=-0.2, max=1.2 )
        self.margins['legend_ypos'].observe(lambda v:self.UpdateLayout( {'legend.y':v['new']} ), names='value')
        
    
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
            display(HBox([self.options_check, self.options_close]))
            display(self.tab)


    def displayOptions(self): 
        with self.options_cont:
            clear_output()
            
            if len(self.options) > 0:
                for key, option in self.options.items():
                    display(option)
            else:
                display("there are no options enabled for this Visualization")
        with self.margins_cont:
            clear_output()
            for key, option in self.margins.items():
                display(option)

            
    def setParent(self, parent): 
        self.parent = parent

    def updateRender(self):
        pass
        
    def getDeltaFunction(self, size, alpha_min=0.5, alpha_max=0.8):
        if size > 1 :
            alpha_delta = (alpha_max-alpha_min)/(size-1)
        else :
            alpha_delta = (alpha_max-alpha_min)
        return alpha_min, alpha_max, alpha_delta
    
        
    def getDeltaColor (self, color, alpha_val, step=0, angle=25):
        rgb = colors.to_rgba(color)
        if (step > 0):
            hsv = colors.rgb_to_hsv((rgb[0],rgb[1],rgb[2]))
            h = (round((hsv[0]*360+angle*step))%360)/360
            s = (round((hsv[1]*360+(angle/10)*step))%360)/360
            v = hsv[2]
            rgb = colors.hsv_to_rgb((h,s,v))
        color = list(colors.to_rgba(rgb, alpha=alpha_val))
        for i in range(3):
            if color[i] >= 1.0:
                color[i] = color[i]-0.000001
        color = tuple(color)
        return color
            

    def on_selection(self, callback):#append=False                                                                                                                                                      
        self.on_selection_callback = callback #NOTE: each plot implements its own behaviour  


            



 
