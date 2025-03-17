from shiny import reactive
from shiny.express import input, ui
from shinywidgets import render_widget
import ipyleaflet as ipyl
from ipywidgets import HTML
import json
from branca.colormap import linear

import pandas as pd
from pathlib import Path


geo_filepath = Path.cwd().joinpath(['data','clean_seattle_zipcodes.geojson'])
# load geometry & associated data
with open(geo_filepath, 'r') as f:
   geodata = json.load(f)

# pull out all zipcodes.
seattle_zipcodes = []
for elem in geodata.get('features'):
   seattle_zipcodes.append(str(elem.get('properties').get('zipcode')))

# Note, geodata['crs']=CRS: {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::4269'}}

# load breed info
df = pd.read_csv(Path.cwd().joinpath(['data','seattle_dogs_single_breed.csv']))
df.rename({'zip':'zipcode'}, inplace=True)
ui.input_select("breed"
                , "breed"
                , choices=sorted(df.breed.unique().tolist())
                , multiple=False)


@render_widget
def map():
   return ipyl.Map(center=(47.6062, -122.33207), zoom=10)

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

   # geodata.get('features')[0]

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

   def get_callback(map, html):
      '''
      https://stackoverflow.com/questions/62941777/ipyleaflet-with-on-hover-event-marker-on-mouseover
      '''
      def callback(*args, **kwargs):
         html.value = f"TEST MESSAGE"


   # map.widget.on_hover(callback, remove=False)


   # Include hover-over, with 1. count of breed(s) selected
   # and 2. 
   # I should be able to do something like
   # layer/map.onclick(methodname).

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