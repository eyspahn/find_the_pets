# find_the_pets
Let's visualize where pets live in Seattle

# Motivating Statement
Use Seattle Pet License data to determine where the most dogs of a certain breed(s) live.
This is a silly project based on public data, done mostly as a way to get experience in a few different technologies and generate a fun lil web map with selectors that I can share.

[Link to CUGOS presentation, March 2025](https://docs.google.com/presentation/d/1RgS39wb7_gjj-4tTx1ZDokhSLoL3V5E2qmdl0wCcTLg/edit?usp=sharing)


# Project Notes
## Data Sources
- Seattle Pet License Data
- King County Zip Code GIS Data
Initially data were downloaded from city & county websites.

### Follow Up Tasks
- Set up a local PostGIS database with the cleaned data.
- Set up an ETL pipeline. I've been wanting to test out prefect.io. Data does not update often, so maybe a manual retrigger?

## Data Processing
Always more data processing needed than you might think to make things work.

Started using Polars because I wanted to learn it a little better, for the non-spatial pets data.
I got curious to see if Polars can support geothings, but saw that there is [an issue](https://github.com/geopolars/geopolars/pull/240) that is putting the project on pause.

### QGIS
Used QGIS to load up the initial zip code data, play around with it.

## Requirements for app
- Input box so user can select one (or more) dog breeds.
- Return: 
  - a choropleth map of the count of those breed(s) in each zip code in Seattle
  - a hover-over or click-on, which shows a count of those breed(s), along with top n breeds in each zip code

### Frontend & Hosting
We also have to consider the hosting/sharing element.
Don't want to have to have people log in to use the map.
Don't want to bother with putting up a whole website (though I suppose github pages makes it easy enough).

- Shiny
Those R users love their shiny apps. I know there's integrated hosting options available. let's try it! ... and it turns out it's a pain in the butt to work with mapping tooling in python.

- Plotly / Dash
My default solution



