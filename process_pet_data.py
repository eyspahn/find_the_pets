from pathlib import Path
import polars as pl
from datetime import datetime, timedelta


filename = 'Seattle_Pet_Licenses_20250304.csv'

def read_in_dog_licenses(filename) -> pl.DataFrame:
    filepath = Path.cwd().joinpath(filename)
    return pl.read_csv(filepath).filter(pl.col("Species")=="Dog")

def process_datetime(df) -> pl.DataFrame:
    """Convert datetimes & only include recent info
    Seattle pet licenses have in the past lasted 1 or 2 years
    In 2024, all licenses will now last only 1 year.

    We'll use the most recent two years
    """
    # parse datetimes
    df = df.with_columns(
        license_date = df["License Issue Date"].str.to_date("%B %d %Y")
    )

    ## keep only license dates more recent than 2 years ago
    date_two_years_ago = (datetime.today() - timedelta(days=2*365))  # .strftime('%Y-%m-%d')
    return df.filter(pl.col("license_date")>=date_two_years_ago)


def clean_zips(df: pl.DataFrame) -> pl.DataFrame:

    df = df.filter(pl.col("ZIP Code").is_not_null())
    df = df.filter(pl.col("ZIP Code")>98100)
    return df

def process_breed_cols(df: pl.DataFrame) -> pl.DataFrame:

    ## Primary Breed & Secondary Breed
    # Messy. 
    # out of 27741 total licensed dogs, secondary column has:  null = 9553 & Mix = 9950

    ## shape to a per-zip code situation.
    # Let's just focus on non-mixed breeds (for MVP)
    df_single_breeds = df.filter(pl.col("Secondary Breed").is_null())
    df_single_breeds =  df_single_breeds.filter(pl.col("Primary Breed")!="Mix")

    # results in Zip, breed & len (count) columns
    # zip & breed are NOT unique here
    # Can use set(df_zips["breed"]) to see the deduped set of breed names

    df_single_breeds = df_single_breeds.group_by(("ZIP Code", "Primary Breed")).len()

    # todo separate out renaming
    df = df_single_breeds.rename({"ZIP Code": "zip", "Primary Breed": "breed", "len": "count"})

    return df




# df.group_by(pl.col('License Number')).len().sort(by='len')
# data looks good, a possible TODO: add an assert or filter out any dupes (take the most recent license)



def correct_breednames(df: pl.DataFrame) -> pl.DataFrame:
    """ Correct the breed names in the data & lowercase it all
    for example: "terrier, norfolk" -> "norfolk terrier"
    There are some entries with multiple commas: e.g. "terrier, fox, toy" -> toy fox terrier
    So, reverse each list and join them

    TODO: Use a polars expression as in 
    https://kevinheavey.github.io/modern-polars/method_chaining.html#extract-city-names
    TODO: figure out the right return_dtype to define in map_elements
    """

    return df.with_columns(pl.col("breed").str.to_lowercase()
          ).with_columns(pl.col("breed").str.split(",")
          ).with_columns(pl.col("breed").list.reverse()
          ).with_columns(pl.col("breed").map_elements(lambda x: [word.strip() for word in x]) # todo figure out the return type & define it to suppress that warning
          ).with_columns(pl.col("breed").list.join(" "))

# df_zips = correct_breednames(df_zips)


# def breed_mapping(df: pl.DataFrame, breed_input: str) -> pl.DataFrame:
#     """input a breed string, output a DF of breed counts per zip code
#     But, what if the user inputs "corgi", do we return all types of corgies?
#     --> probably? So we need to output the breed (s) returned as well

#     OR ==> provide the breed list as a dropdown in shiny, which would make more sense to me.
#     """

#     df.filter(pl.col(breed))

#     pass



# def get_top_breeds(df: pl.DataFrame, n: int=5) -> pl.DataFrame:
#     """Get the top n breeds for each zip code.
#     each row should be one zip code
#     return a field like "{doberman: 5, saluki: 1}"
#     """

#     # df.group_by("zip").agg(pl.col('breed'), pl.col('count')) # returns list[breeds] & list[count]

#     # df.group_by("zip", "breed").agg(pl.col('count'))
#     df.group_by("zip", "breed")
#         .agg(pl.len().alias("count"))


#     pass


# def clean_up_json():
#     """just copying in code here"""

# clean_json = zipsjson.copy()

# # iterate through features & add id element to clean_json
# for i, entry in enumerate(zipsjson.get('features')):
#     clean_json['features'][i]['id'] = entry.get('properties').get('zipcode')

#     pass

if __name__=='__main__':

    df = read_in_dog_licenses(filename)
    df = process_datetime(df)
    df_cleaned = clean_zips(df)
    # TODO: add check for dupe license numbers, before dropping
    df_cleaned = df_cleaned.drop(["License Issue Date", "License Number", "Species"])

    df_cleaned = process_breed_cols(df_cleaned)
    df_cleaned = correct_breednames(df_cleaned)


    df_cleaned = df_cleaned.sort(by=['zip', 'breed'])
    out_filename = 'seattle_dogs_single_breed.csv'
    out_filepath = Path.cwd().joinpath(out_filename)

    df_cleaned.write_csv(out_filepath)
