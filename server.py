from flask import Flask, request, jsonify
from flask_cors import CORS
from io import StringIO
import pickle
import config
import pandas as pd
from csv import writer
from functions import scrape_url
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True


# add a new row into csv file for getting recommended segments
def add_row(val1, val2):
    values1 = val1.split("_")
    values2 = val2.split("_")

    keywords = ""
    if len(values1) >= 1:
        keywords = keywords + " " + values1[0]
    if len(values1) >= 3:
        keywords = keywords + " " + values1[2]
    if len(values2) >= 1:
        keywords = keywords + " " + values2[0]
    if len(values2) >= 3:
        keywords = keywords + " " + values2[2]
    
    list1 = [366, 1234567, keywords, keywords, False, "positive"]

    with open('FinalData.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(list1)
        f_object.close()
    return process_recommend(keywords)

def isNaN(num):
    return num != num

# helper functions for recommender. Use them when needed #######
def get_title_from_index(index, df):
    type = df[df.index == index]["Type"].values[0]

    if isNaN(type):
        type = ""
    return {"name": df[df.index == index]["Name"].values[0],
            "id": int(df[df.index == index]["code"].values[0]),
            "type": type,
            "desc": df[df.index == index]["Description"].values[0]}


def get_id_from_index(index, df):
    return df[df.index == index]["code"].values[0]


def get_index_from_title(title, df):
    return df[df.Name == title]["index"].values[0]


def combine_features(row):
    try:
        return row['Name'] + " " + row['Description'] + " " + row["SegmentType"]
    except:
        print("Error:", row)

def delete_last_row():
    f = open('FinalData.csv', "r+")
    lines = f.readlines()
    lines.pop()
    f = open('FinalData.csv', "w+")
    f.writelines(lines)

# Recommender process , to find segments
def process_recommend(keywords):
    # Step 1: Read CSV File
    df = pd.read_csv("FinalData.csv")
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
    result = []
    i = 0
    for segment in sorted_similar_segments:
        seg_json = get_title_from_index(segment[0], df)
        result.append(seg_json)
        i = i + 1
        if i > 10:
            break

    delete_last_row()
    
    return result


# URL predict logic goes here
pickle_in = open(config.WORDS_FREQUENCY_PATH, "rb")
words_frequency = pickle.load(pickle_in)


@app.route('/ping', methods=['GET'])
def home():
    return "Pong"


@app.route('/recommendation', methods=['POST'])
def segment_by_url():
    content = request.get_json()

    if content == "":
        return "Error: No data.sql found in request. Please specify an request data.sql."

    adserver_url = content["advUrl"]
    if adserver_url == "":
        return "Error: No URL found to recommend!!"
    
    results = scrape_url(adserver_url, words_frequency)
    results = scrape_url(adserver_url, words_frequency)
    
    if results:
        print('Predicted main category:', results[0])
        print('Predicted sub-main category:', results[2])
        return jsonify(add_row(results[0], results[2]))

    return ""


app.run('0.0.0.0', 7050)