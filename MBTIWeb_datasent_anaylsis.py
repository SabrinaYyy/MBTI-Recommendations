import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm


mbtis = ['INTP_df.csv','ISTP_df.csv','ENTP_df.csv','ESTP_df.csv','ENFP_df.csv','INFP_df.csv','ESFP_df.csv','ISFP_df.csv',
        'INTJ_df.csv','ISTJ_df.csv','INFJ_df.csv','ISFJ_df.csv','ENTJ_df.csv','ENFJ_df.csv','ESTJ_df.csv','ESFJ_df.csv']

    
data_genres = pd.read_csv('data_by_genres.csv')

useless_genres_col = ['mode','popularity','key','duration_ms']

non_numeric_column_genres = 'genres'

data_genres = data_genres.rename(columns={'liveness': 'liveness_mean',
                                          'danceability':'danceability_mean',
                                          'energy':'energy_mean',
                                          'loudness':'loudness_mean',
                                          'speechiness':'speechiness_mean',
                                          'acousticness':'acousticness_mean',
                                          'valence':'valence_mean',
                                          'tempo':'tempo_mean',
                                          'instrumentalness':'instrumentalness_mean'
                                          })

for column in data_genres.columns:
        # Drop useless columns
        if column in useless_genres_col:
            data_genres = data_genres.drop(columns=column, errors='ignore')
        elif column == non_numeric_column_genres:
            # Handle 'mbti' column separately
            data_genres[non_numeric_column_genres] = data_genres[non_numeric_column_genres].apply(
                lambda x: x if pd.notna(pd.to_numeric(x, errors='coerce')) else x)
        else:
            # General cleaning for numeric columns
            data_genres = data_genres.dropna(subset=[column])
            data_genres[column] = data_genres[column].apply(lambda x: int(x) if isinstance(x, str) else x)
            useless_values = [0, 1]
            data_genres = data_genres[~data_genres[column].isin(useless_values)]
            #print(f"DataFrame after cleaning {column}:")
            #print(data_genres.head())
data_genres = data_genres.dropna(subset=[non_numeric_column_genres])
#print("Final Cleaned DataFrame:")
#print(data_genres.head())
data_genres.to_csv("data_by_genres.csv", index=False)


useless_columns = ['G#/Abminor_count', 'G#/AbMajor_count','Aminor_count','AMajor_count','A#/Bbminor_count','A#/BbMajor_count','Bminor_count',
'BMajor_count','Dminor_count','D#_Ebminor_count','D#_EbMajor_count','Gminor_count','Cminor_count','CMajor_count','C#/Dbminor_count',
'C#/DbMajor_count','DMajor_count','Eminor_count','EMajor_count','Fminor_count','FMajor_count','F#/Gbminor_count','F#/GbMajor_count',
'GMajor_count','function_pair','playlist_name','playlist_id','track_count','danceability_stdev','energy_stdev','loudness_stdev',
'mode_stdev','speechiness_stdev','mode_mean','acousticness_stdev','liveness_stdev','valence_stdev','tempo_stdev',
'instrumentalness_stdev']

non_numeric_column = 'mbti'



def findrange(data_mbti, mbti_type):
        mbti_ranges = {}
        genre_matches = []
        for column in data_mbti.columns:
            # Drop useless columns
            if column in useless_columns:
                data_mbti = data_mbti.drop(columns=column, errors='ignore')
            elif column == non_numeric_column:
                # Handle 'mbti' column separately
                data_mbti[non_numeric_column] = data_mbti[non_numeric_column].apply(lambda x: x if pd.notna(pd.to_numeric(x, errors='coerce')) else x)
            else:
                # General cleaning for numeric columns
                data_mbti = data_mbti.dropna(subset=[column])
                data_mbti[column] = data_mbti[column].apply(lambda x: int(x) if isinstance(x, str) else x)
                useless_values = [0, 1]
                data_mbti = data_mbti[~data_mbti[column].isin(useless_values)]
                #print(f"DataFrame after cleaning {column}:")
                #print(data_mbti.head())
                # Calculate mean for the current column
                mean_value = np.mean(data_mbti[column])
                #print(f"Mean for column '{column}': {mean_value}")

                # Calculate standard deviation for the current column
                std_dev = np.std(data_mbti[column], ddof=1)
                #print(f"Standard Deviation for column '{column}': {std_dev}")

                # Calculate range for the current column
                lower_bound = mean_value - std_dev*1.5
                upper_bound = mean_value + std_dev*1.5
                RANGE = [lower_bound, upper_bound]
                #print(f"Range for column '{column}': {RANGE}")
                mbti_ranges[column] = RANGE
        pd.DataFrame([mbti_ranges], columns=mbti_ranges.keys()).to_csv(f"{mbti_type}_ranges.csv", index=False)
        #print(f"Ranges saved to {mbti_type}_ranges.csv")

              

        data_mbti = data_mbti.dropna(subset=[non_numeric_column])

        data_mbti.to_csv(f"{mbti_type}_cleaned_data.csv", index=False)

import json
import ast

def load_mbti_ranges(mbti_type):
    # Load MBTI ranges from the CSV file
    mbti_ranges_file = f"{mbti_type}_ranges.csv"
    mbti_ranges_df = pd.read_csv(mbti_ranges_file)

    if len(mbti_ranges_df) < 1:
        raise ValueError(f"Insufficient data in {mbti_ranges_file}. Expected at least 2 rows.")

    # Extract the range values from the second row
    range_values = mbti_ranges_df.iloc[0].to_dict()

    #print(f"Loaded ranges for {mbti_type}: {range_values}")

    return range_values

def match_genres_with_ranges(data_genres, mbti_type):
    # Load MBTI ranges for the given type
    mbti_ranges = load_mbti_ranges(mbti_type)

    matched_genres = []

    for index, row in data_genres.iterrows():
        is_match = True
        for column in mbti_ranges:
            # Convert string representation to list
            str_representation = mbti_ranges[column]
            ranges = ast.literal_eval(str_representation)
            #print(ranges, row[column], ranges[1])

            # Check if the value falls within the range for the corresponding MBTI column
            o, l, r = float(ranges[0]), float(ranges[1]), float(row[column])

            columns_match = all((o <= r <= l) for column in row.index[1:])

            # If any column doesn't match, break out of the inner loop
            if not columns_match:
                is_match = False
                break

        # If all MBTI columns match, add the row to matched genres
        if is_match:
            matched_genres.append(row['genres'])

    return matched_genres


def save_matched_genres_to_json(matched_genres, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(matched_genres, json_file)


for mbti in mbtis:
    mbti_type = mbti.split('_')[0]
    data_mbti = pd.read_csv(mbti)
    findrange(data_mbti, mbti_type)
    matched_genres = match_genres_with_ranges(data_genres, mbti_type)
    print(f"Matched genres for {mbti_type}: {matched_genres}")
    save_matched_genres_to_json(matched_genres, f"{mbti_type} matched_genres.json")



