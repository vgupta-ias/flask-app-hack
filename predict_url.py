import pickle
import time
import config
import argparse
import pandas as pd
from csv import writer
from functions import scrape_url
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# add a new row into csv file for getting recommended segments
def add_row(val1, val2):
    values1 = val1.split("_")
    values2 = val2.split("_")
    keywords = values1[0] + " " + values1[2] + " " + values2[0] + " " + values2[2]
    # List
    list1 = [137, 1234567, keywords, keywords, False]

    # Open our existing CSV file in append mode
    # Create a file object for this file
    with open('inputSegments3.csv', 'a') as f_object:
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)

        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(list1)

        # Close the file object
        f_object.close()
    process_recommend(keywords)


# helper functions for recommender. Use them when needed #######
def get_title_from_index(index, df):
    return df[df.index == index]["Name"].values[0]


def get_index_from_title(title, df):
    return df[df.Name == title]["index"].values[0]


def combine_features(row):
    try:
        return row['Name'] + " " + row['Description'] + " " + row["SegmentType"]
    except:
        print("Error:", row)


# Recommender process , to find segments
def process_recommend(keywords):
    time.sleep(5)
    # Step 1: Read CSV File
    df = pd.read_csv("inputSegments3.csv")
    # print(df.columns)

    # Step 2: Select Features
    features = ['Name', 'Description', 'SegmentType']

    # Step 3: Create a column in DF which combines all selected features
    for feature in features:
        df[feature] = df[feature].fillna('')

    df["combined_features"] = df.apply(combine_features, axis=1)
    # print "Combined Features:", df["combined_features"].head()

    # Step 4: Create count matrix from this new combined column
    cv = CountVectorizer()

    count_matrix = cv.fit_transform(df["combined_features"])

    # Step 5: Compute the Cosine Similarity based on the count_matrix
    cosine_sim = cosine_similarity(count_matrix)
    input_seg_name = keywords
    print("Input Segment/Keywords : " + input_seg_name)

    # Step 6: Get index of this segment from its title
    segment_index = get_index_from_title(input_seg_name, df)

    similar_segments = list(enumerate(cosine_sim[segment_index]))

    # Step 7: Get a list of similar segments in descending order of similarity score
    sorted_similar_segments = sorted(similar_segments, key=lambda x: x[1], reverse=True)

    # Step 8: Print titles of first 5 segments
    print("Recommended Segments : ")
    i = 0
    for segment in sorted_similar_segments:
        seg_name = get_title_from_index(segment[0], df)
        print(seg_name)
        i = i + 1
        if i > 10:
            break


# URL predict logic goes here
pickle_in = open(config.WORDS_FREQUENCY_PATH, "rb")
words_frequency = pickle.load(pickle_in)

parser = argparse.ArgumentParser(description='URLs for category predictions')
parser.add_argument('-u', '--url', help='Predict custom website')
parser.add_argument('-t', '--text_file_path', help='Predict websites written in text file')

args = parser.parse_args()

if args.url:
    url = args.url
    print(url)
    results = scrape_url(url, words_frequency)
    if results:
        print('Predicted main category:', results[0])
        print('Predicted sub-main category:', results[2])
        add_row(results[0], results[2])
elif args.text_file_path:
    file_path = args.text_file_path
    with open(file_path) as f:
        for url in f:
            url = url.replace('\n', '')
            print(url)
            results = scrape_url(url.replace('\n', ''), words_frequency)
            if results:
                print('Predicted main category:', results[0])
                print('Predicted sub-main category:', results[2])
else:
    parser.error("Please specify websites input type. More about input types you can find 'python predict_url -h'")
