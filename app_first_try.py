from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_widget, reactive_read
import ipyleaflet as ipyl
from ipywidgets import HTML
import json
from branca.colormap import linear

import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Dict, List


geo_filepath = Path.cwd().joinpath('data').joinpath('clean_seattle_zipcodes.geojson')

# load geometry & associated data
# following what's shown in shiny examples
with open(geo_filepath, 'r') as f:
   geodata = json.load(f)

# pull out all zipcodes.
seattle_zipcodes = []
for elem in geodata.get('features'):
   seattle_zipcodes.append(str(elem.get('properties').get('zipcode')))

# Note, geodata['crs']=CRS: {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::4269'}}

# oof, I need to read this in twice because of the way I set up shiny
# I should have used geodata instead
gdf = gpd.read_file(Path.cwd().joinpath('data').joinpath('clean_seattle_zipcodes.geojson'))

# load breed info
df = pd.read_csv(Path.cwd().joinpath('data').joinpath('seattle_dogs_single_breed.csv'))
df.rename({'zip':'zipcode'}, inplace=True)
ui.input_select("breed"
                , "breed"
                , choices=sorted(df.breed.unique().tolist())
                , multiple=False)


def city_wide_top_dogs(df):
   df_citywide = df[['breed', 'count']].groupby('breed').agg('sum').reset_index()

   top_breeds_str = """City-wide Top Breeds (Breed, count):\n\n"""

   for (breedname, count) in df_citywide.sort_values(by='count', ascending=False).values:
      top_breeds_str+=f"{breedname}:\t{count}\n\n"

   return top_breeds_str


def handle_click(**kwargs):
   print(kwargs)

@render_widget
def map():
   map = ipyl.Map(center=(47.6062, -122.33207), zoom=10)

   # html = HTML("""Hover over a zip""")
   # html.layout.margin = "0px 20px 20px 20px"
   # control = ipyl.WidgetControl(widget=html, position="topright")
   # map.add(control)


   # add in marker thing here, make marker the main object?
   # That was not pretty.
   # marker = ipyl.Marker(location = ([47.6062, -122.33207]),
   # #  draggable=False,
   #  opacity=0, visible=False
   # #  rise_on_hover=True,
   # )
   # marker.on_click(handle_click)
   # map.widget.add(marker)
   # return map

   # return ipyl.Map(center=(47.6062, -122.33207), zoom=10)

   return map



@render.text
def text():

   cntr = reactive_read(map.widget, 'center')
   output_str = f"""center: {cntr}\n\n"""

   return output_str+"\n"+f"{city_wide_top_dogs(df)}"


@reactive.effect
def _():
   """ reactive stuff here"""
   # create a dict to map zip code to count

   raw: list[dict] = df[df['breed']==input.breed()][['zip', 'count']].to_dict('records')
   #  to map, need to go from [{'zip': 98101, 'count': 1}] -> {'98101': 1}

   choro_data = {}
   for elem in raw:
      choro_data[str(elem['zip'])] = elem['count']

   # add zeros to zips that are not in the resulting dataset:
   for zip in seattle_zipcodes:
      if str(zip) not in choro_data.keys():
         choro_data[str(zip)] = 0

   # Can use choropleth
   layer = ipyl.Choropleth(
      geo_data = geodata,
      choro_data = choro_data,
      colormap = linear.Greens_08,
      nan_opacity=0,
      border_color='black',
      style = {'fillOpacity':0.3 }
   )

   map.widget.add(layer)


   # def get_callback(map, html):
   #    '''
   #    https://stackoverflow.com/questions/62941777/ipyleaflet-with-on-hover-event-marker-on-mouseover
   #    '''
   #    def callback(*args, **kwargs):
   #       html.value = f"TEST MESSAGE"

   # or: https://medium.com/swlh/how-to-use-mouse-events-on-ipyleaflet-4d002097efc0

   marker = ipyl.Marker(location = ([47.6062, -122.33207]),
   #  draggable=False,
    opacity=0, visible=False
   #  rise_on_hover=True,
   )
   marker.on_click(handle_click)

   map.widget.add(marker)
   
   # map.on_click(handle_click)
   
   # map.widget.on_click(handle_click, remove=False)

   # map.widget.on_hover(callback, remove=False)


   # Include hover-over, with 1. count of breed(s) selected
   # and 2. top breeds in that zip code.
   # I should be able to do something like
   # layer/map.onclick(methodname)?
   # But maybe that's not on all methods?


   message = HTML()
   message.value = f"TEST MESSAGE"
   message.placeholder = "test"
   message.description = "test"

   # popup = ipyl.Popup(
   #    # location=geodata[0],
   #    location=(47.6062, -122.33207),
   #    child=message,
   #    close_button=False,
   #    auto_close=False,
   #    close_on_escape_key=False
   # )
   
   # map.widget.add(popup)


   # click_loc = reactive_read(marker.widget, '')
