# """trying out shiny... and it's not very fun. :(
#    ipyleaflet <-> shiny is not great
#    documentation may be out of date or not the most straightforward way
#  """

from shiny import reactive
from shiny.express import input, ui, render
from shinywidgets import render_widget, reactive_read
import ipyleaflet as ipyl
from ipywidgets import HTML, Label, Layout
import json
from branca.colormap import linear

import geopandas as gpd
import pandas as pd
from pathlib import Path
from typing import Dict, List

geo_filepath = Path.cwd().joinpath('data').joinpath('clean_seattle_zipcodes.geojson')
gdf = gpd.read_file(geo_filepath)
gdf.zipcode = gdf.zipcode.astype('int64') # for merging later

top_breeds_by_zip_df = pd.read_csv(Path.cwd().joinpath('data').joinpath('top_5_breeds_by_zip.csv'))


gdf = gdf.merge(top_breeds_by_zip_df, how='inner', left_on='zipcode', right_on='zip')

# keep only relevant columns
gdf = gdf[['zip', 'geometry', 'top_5_breeds']]

# and for choropleth:
with open(geo_filepath, 'r') as f:
   geodata = json.load(f)


# and we'll need to load up the full breed info by zip
df = pd.read_csv(Path.cwd().joinpath('data').joinpath('seattle_dogs_single_breed.csv'))
df.rename({'zip':'zipcode'}, inplace=True)

# ui.page_opts(title = "")

ui.input_select("breed"
                , "breed"
                , choices=sorted(df.breed.unique().tolist())
                , multiple=False)


# def city_wide_top_dogs(df):
#    df_citywide = df[['breed', 'count']].groupby('breed').agg('sum').reset_index()

#    top_breeds_str = """City-wide Top Breeds (Breed, count):\n\n"""

#    for (breedname, count) in df_citywide.sort_values(by='count', ascending=False).values:
#       top_breeds_str+=f"{breedname}:\t{count}\n\n"

#    return top_breeds_str


@render_widget
def map():
    map = ipyl.Map(center=(47.6062, -122.33207), zoom=10)
    return map

breed_html = HTML("")
breed_html.value = "Click on a zip"

# @render.text
# def breed_text():
#     "want to return count of breed when we click or hover on the map"
#     # # example from docs
#     # cntr = reactive_read(map.widget, 'center')
#     # return f"""center: {cntr}\n\n"""

#     # should get updated reactive values below.
#     return breed_html.value


@render.text
def update_html(value=None, feature={}, **kwargs):

    breed_html.value = f"""{feature.get("properties","N/A")}"""

    return breed_html.value


@render.text
def blank():
    return ""

@render.text
def top_dogs_label():
    return """\nTop single-breed dogs in Seattle:"""

@render.data_frame
def top_dogs_in_seattle():
    return df[['breed', 'count']].groupby('breed').agg('sum').reset_index().sort_values(by='count', ascending=False)



@reactive.effect
def _():
    """reactive things here"""

    # # # label below map
    # label = Label(layout=Layout(width="100%"))

    # create a dict to map zip code to count
    raw: list[dict] = df[df['breed']==input.breed()][['zip', 'count']].to_dict('records')
    #  to map, need to go from [{'zip': 98101, 'count': 1}] -> {'98101': 1}

    choro_data = {}
    for elem in raw:
        choro_data[str(elem['zip'])] = elem['count']

    # add zeros to zips that are not in the resulting dataset:
    for elem in geodata['features']:
        if elem['id'] not in choro_data.keys():
            choro_data[elem['id']] = 0
    
    layer = ipyl.Choropleth(
        geo_data = geodata,
        choro_data = choro_data,
        colormap = linear.PRGn_11,
        nan_opacity=0,
        border_color='black',
        style = {'fillOpacity':0.3 }
    )

    map.widget.add(layer)

    # our click layer
    geo_data = ipyl.GeoData(
        geo_dataframe=gdf,
        style={
            "color": "black",
            "fillColor": "#366370",
            "opacity": 0.0, # 0.05,
            "weight": 1.9,
            "dashArray": "2",
            "fillOpacity": 0.0, # 0.3,
        },
        hover_style={"fillColor": "#b08a3e", "fillOpacity": 0.1},
    )

    # from https://gist.github.com/justinm0rgan/281c2d92a479ecaf83dbb1e239596953

    # click callback function
    def click_handler(event=None, feature=None, id=None):
        breed_html.value = f'Details: {feature["properties"]}'

    # geo_data.on_hover(update_html)

    # alternate: on click
    geo_data.on_click(click_handler)

    map.widget.add(geo_data)

    # import ipdb; ipdb.set_trace()

    
