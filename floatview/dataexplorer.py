import pandas as pd
import qgrid
import os
import floatview
import math
from ipywidgets import Tab, HBox, VBox, Dropdown, Button, Layout, ToggleButton, Checkbox, Output, ButtonStyle, GridBox 


class DataExplorer(VBox):   
    def __init__(self, database_path='./'):            
        VBox.__init__(self, layout=Layout(width="100%", min_height="800px"))        
        self.database_path = database_path
        dbs = Dropdown(description='DB', layout = Layout(width="auto"))
        dbs.observe(lambda event, this=self: this.loadFields(event), "value")
        self.current = "Database"
        layout = {
            "Database":{
                'action': (lambda this=self: this.toDatabase()),
                'click' : (lambda event, this=self: this.clickPanel("Database")),
                'children' : {
                    "list" : dbs,
                    "fields" : VBox(layout = Layout(width="100%", border="1px solid #6666"))
                },
            },
            "Filters":{
                'action': (lambda this=self: this.toFilters()),
                'click' : (lambda event, this=self: this.clickPanel("Filters")),
                'children' : {
                    "grid" : VBox()
                },                
            },
            "Exploration":{
                'action': (lambda this=self: this.toExploration()),
                'click' : (lambda event, this=self: this.clickPanel("Exploration")),
                'children' : {
                    "grid" : HBox()                    
                },                
            },
            "Visualization":{
                'action': (lambda this=self: this.toVisualization()),
                'click' : (lambda event, this=self: this.clickPanel("Visualization")),
                'children' : {
                    "main_view" : Output(),
                    "secondary_view" : Output ()
                },                
            },
        }
        
        self.ui = self.createDefaultLayout(layout);

        content = []
        for i, k in enumerate(self.ui.keys()):
            if 'container' in self.ui[k]:
                content.append(self.ui[k]["container"])

        tabs = []
        for i, k in enumerate(self.ui.keys()):
            if 'container' in self.ui[k]:
                self.ui[k]["tab"] = ToggleButton(value=False, description=k,layout = Layout(width="auto"), disabled=True)
                self.ui[k]["tab"].observe(lambda a, b=k, c=self : self.eventPanel(a,b), "value")
                tabs.append(self.ui[k]["tab"])
                
        self.children = [
            HBox(tabs,layout = Layout(width="auto")),
            VBox(content, layout=Layout(width="auto"))
        ]
        self.clickPanel(self.current)

    def createDefaultLayout(self, layout):
        ui = {}
        lkeys = list(layout.keys())
        tkeys = len(lkeys)
        for i in range(tkeys):
            k = lkeys[i]
            ui[k] = {}
            if i < tkeys-1:
                ui[k]["next"] = Button(description="Go to " + lkeys[i+1], layout = Layout(width="50%"))
                if 'click' in layout[lkeys[i+1]]:
                    ui[k]["next"].on_click(layout[lkeys[i+1]]["click"])                
            else:
                ui[k]["next"] = Button(description="", layout = Layout(width="50%"), disabled=True)
            if i > 0:
                ui[k]["back"] = Button(description="Go to " + lkeys[i-1], layout = Layout(width="50%"))
                if 'click' in layout[lkeys[i-1]]:
                    ui[k]["back"].on_click(layout[lkeys[i-1]]["click"])                
            else:
                ui[k]["back"] = Button(description="", layout = Layout(width="50%"), disabled=True)
            ui[k]["button_container"] = HBox(layout = Layout(width="100%"))
            ui[k]["button_container"].children = [ui[k]["back"], ui[k]["next"]]
            ui[k]["container"] = VBox(layout = Layout(width="100%", border="1px solid #6666"))
            children = []
            children.append(ui[k]["button_container"])            
            if "children" in layout[k]:
                for k2,v in layout[k]["children"].items():
                    ui[k][k2] = v
                    children.append(v)
                children.append(ui[k]["button_container"])

            ui[k]["container"].children = children
            ui[k]["action"] = layout[k]["action"]
        return ui

               
    def showPanel(self, key):
        found = False
        reload = True
        for k,v in self.ui.items():
            self.ui[k]["tab"].disabled = found
            if (k == self.current and found):
                reload = False
            if k == key:
                found = True
                self.ui[k]["container"].layout.display = None
            else:
                self.ui[k]["container"].layout.display = "None"
                
        self.current = key
        return reload

    def clickPanel(self, key):
        self.ui[key]["tab"].disabled = False    
        self.ui[key]["tab"].value=True

    def eventPanel(self, event, key):
        if event["new"] is True:
            self.clickPanel(key)
            for k in self.ui.keys():
                if k != key:                
                    self.ui[k]["tab"].value = False            
            self.ui[key]["action"]()
        else:
            pass;        

    def toDatabase(self, event=None):
        reload = self.showPanel("Database")
        if reload:
            self.ui["Database"]["fields"].children = []
            dbs = []
            for file in os.listdir(self.database_path):
                if file.endswith(".csv"):
                    dbs.append(file)
            self.ui["Database"]["list"].options=dbs
            self.ui["Database"]["list"].value=dbs[0]
            self.loadFields({'new':dbs[0]})

    def toFilters(self, event=None):
        reload = self.showPanel("Filters")
        if reload:        
            columns = []
            for w in self.ui["Database"]["fields"].children:
                if w.value is True:
                    columns.append(w.description)
            df = pd.read_csv(self.ui["Database"]["list"].value, low_memory=False, usecols=columns)
            self.ui["Filters"]["container"].children = [] 
            self.ui["Filters"]["grid"] = qgrid.show_grid(df, show_toolbar=False, grid_options={'editable': False})
            self.ui["Filters"]["container"].children = [
                self.ui["Filters"]["button_container"], 
                self.ui["Filters"]["grid"], 
                self.ui["Filters"]["button_container"]
            ]

    def moveOption(self, pos, up, d, l):
        children = list(d.children)
        lchildren = math.floor(len(children)/3)
        val = children[3*pos]
        vall = self.ui["Exploration"][l][pos]
        if up is False:
            if pos < lchildren-1:
                children[3*pos] = children[3*(pos+1)]
                children[3*(pos+1)]=val
                self.ui["Exploration"][l][pos] = self.ui["Exploration"][l][pos+1]
                self.ui["Exploration"][l][pos+1]=vall

        else:
            if pos > 0:
                children[3*pos] = children[3*(pos-1)]
                children[3*(pos-1)]=val
                self.ui["Exploration"][l][pos] = self.ui["Exploration"][l][pos-1]
                self.ui["Exploration"][l][pos-1]=vall
        d.children = children

    def toExploration(self, event=None):
        reload = self.showPanel("Exploration")    
        if reload:        
            self.ui["Exploration"]["grid"].children = []
            main_dimensions = []
            secondary_dimensions = []
            for k in self.ui["Filters"]["grid"].get_changed_df().columns:
                if "input" in k:
                    main_dimensions.append(Checkbox(value=True, description=k, layout=Layout(width="auto")))
                else:
                    main_dimensions.append(Checkbox(value=False, description=k, layout=Layout(width="auto")))
                secondary_dimensions.append(Checkbox(value=True, description=k, layout=Layout(width="auto")))
            self.ui["Exploration"]["main_dimensions"] = main_dimensions
            self.ui["Exploration"]["main_plot"] = Dropdown(description="Visualization", options=["sankey", "pca", "sankeytree", "sunburst", "parallelscat", "scattermatrix"], value="sankey")
            self.ui["Exploration"]["secondary_dimensions"] = secondary_dimensions
            self.ui["Exploration"]["secondary_plot1"] = Dropdown(description="Visualization", options=["table", "corrcoef", "sankey", "pca", "sankeytree", "sunburst", "parallelscat", "parallels", "scattermatrix"], value="corrcoef")
            self.ui["Exploration"]["secondary_plot2"] = Dropdown(description="Visualization", options=["table", "corrcoef", "sankey", "pca", "sankeytree", "sunburst", "parallelscat", "parallels", "scattermatrix"], value="table")
            vb1 = VBox(main_dimensions, layout = Layout(width="100%", padding="10px"))


            vb1 = GridBox(
                layout=Layout(
                    width='auto',
                    grid_template_columns='auto auto auto',
                    grid_template_rows=" ".join(['auto' for i in self.ui["Exploration"]["main_dimensions"]]),
                    grid_gap='1px 1px'
                )
            )
            children = []
            for i,w in enumerate(self.ui["Exploration"]["main_dimensions"]):
                children.append(w)
                up = Button(icon="angle-up", layout=Layout(width="50px"))
                up.on_click(lambda b, this=self, pos=i, w=vb1, l="main_dimensions": this.moveOption(pos, True, w, l))
                children.append(up)
                down = Button(icon="angle-down", layout=Layout(width="50px"))
                down.on_click(lambda b, this=self, pos=i, w=vb1, l="main_dimensions": this.moveOption(pos, False, w, l))
                children.append(down)
            vb1.children=children        


            vb2 = GridBox(
                layout=Layout(
                    width='auto',
                    grid_template_columns='auto auto auto',
                    grid_template_rows=" ".join(['auto' for i in self.ui["Exploration"]["secondary_dimensions"]]),
                    grid_gap='1px 1px'
                )
            )   
            children = []        
            for i,w in enumerate(self.ui["Exploration"]["secondary_dimensions"]):
                children.append(w)
                up = Button(icon="angle-up", layout=Layout(width="50px"))
                up.on_click(lambda b, this=self, pos=i, w=vb2, l="secondary_dimensions": this.moveOption(pos, True, w, l))
                children.append(up)
                down = Button(icon="angle-down", layout=Layout(width="50px"))
                down.on_click(lambda b, this=self, pos=i, w=vb2, l="secondary_dimensions": this.moveOption(pos, False, w, l))
                children.append(down)
            vb2.children=children  

            self.ui["Exploration"]["grid"].children = [
                VBox([
                    Button(description="Main Dimensions",layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')),
                    self.ui["Exploration"]["main_plot"],
                    vb1,
                ], layout=Layout(width="50%")),
                VBox([
                    Button(description="Secondary Dimensions",layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')),
                    self.ui["Exploration"]["secondary_plot1"],
                    self.ui["Exploration"]["secondary_plot2"],
                    vb2,
                ], layout=Layout(width="50%"))
            ]

    def showPlot( self, a, b, c ):
        secondary_dimensions = []    
        for w in self.ui["Exploration"]["secondary_dimensions"]:
            if hasattr(w, 'value') and w.value is True:
                secondary_dimensions.append(w.description)    
        self.ui["Visualization"]["secondary_view"].clear_output()
        with self.ui["Visualization"]["secondary_view"]: 
            self.ui["Exploration"]["widget"].gluemanager.newView(self.ui["Exploration"]["secondary_plot1"].value, secondary_dimensions, "", only_view=True)
            self.ui["Exploration"]["widget"].gluemanager.newView(self.ui["Exploration"]["secondary_plot2"].value, secondary_dimensions, "", only_view=True)

    def toVisualization(self, event=None):    
        reload = self.showPanel("Visualization")
        if reload:        
            main_dimensions = []
            for w in self.ui["Exploration"]["main_dimensions"]:
                if hasattr(w, 'value') and w.value is True:
                    main_dimensions.append(w.description)
            df = self.ui["Filters"]["grid"].get_changed_df()
            self.ui["Exploration"]["widget"] = floatview.GlueManagerWidget(df, modal=False, label=self.ui["Database"]["list"].value, display_console=False)
            self.ui["Visualization"]["main_view"].clear_output()
            self.ui["Visualization"]["secondary_view"].clear_output()
            with self.ui["Visualization"]["main_view"]:
                a = self.ui["Exploration"]["widget"].gluemanager.newView(self.ui["Exploration"]["main_plot"].value, main_dimensions, "")
                a.on_selection(lambda a, b, c, this=self: this.showPlot(a, b, c))

    def loadFields( self, change ):
        self.ui["Database"]["fields"].children =  []
        df = pd.read_csv(change['new'], low_memory=False, nrows=1)
        columns = []
        for i, c in enumerate(df.columns):
            if i < 15:
                columns.append(Checkbox(value=True, description=c, layout=Layout(width="auto")))
            else:
                columns.append(Checkbox(value=False, description=c, layout=Layout(width="auto")))
        self.ui["Database"]["fields"].children = columns

