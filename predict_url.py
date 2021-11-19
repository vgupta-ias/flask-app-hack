import pickle

from nltk.util import pr
import config
import argparse
import json
import random
import requests
import feedparser
import time
import ssl
from functions import scrape_url
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

pickle_in = open(config.WORDS_FREQUENCY_PATH, "rb")
words_frequency = pickle.load(pickle_in)

parser = argparse.ArgumentParser(description='URLs for category predictions')
parser.add_argument('-u', '--url', help='Predict custom website')
parser.add_argument('-t', '--text_file_path', help='Predict websites written in text file')
ssl._create_default_https_context = ssl._create_unverified_context

# args = parser.parse_args()
url = 'https://www.hindustantimes.com/business/cocacola-responds-after-cristiano-ronaldo-gesture-cost-it-4-billion-101623830150314.html'
results = []
if url:
    print(url)
    results = scrape_url(url, words_frequency)
    if results:
        print('category-1:', results[0])
        print('category-2:', results[2])
        # print('category-3:', results[4])
else:
    parser.error("Please specify websites input type. More about input types you can find 'python predict_url -h'")

def getnews(title):
    url = "https://newsapi.org/v2/everything"
    params= {'qinTitle':title,'from':"2021-11-17",'apiKey':"1d1ec61cec55420dbc71cb79d9be7fb0","language":"en"}
    r=requests.get(url,params)
    data=r.json()
    print(data)
    urls=[]
    for url in data['articles']:
        urls.append(url['url'])
    return urls

def trend_data(name):
    
    url="https://trends.google.com/trends/trendingsearches/daily/rss?geo="+name.upper()
    print(url)
    NewsFeed = feedparser.parse(url)
    print('NewsFeed ', NewsFeed)
    output=[]
    for entry in NewsFeed["entries"][:10]:
        topic={
            'title':entry["title"],
            'summary':entry["summary"],
            'traffic':entry["ht_approx_traffic"],
            'news_url':getnews(entry["title"])
        }
        output.append(topic)
    print(output)
    return output


@app.route('/health', methods=['GET'])
def health():
    out = {}
    out['status'] = "OK"
    return jsonify(out)

@app.route('/trending/<string:name>', methods=['GET'])
def translate_string(name):
    print('1')
    trend_urls = trend_data(name)
    print(trend_urls)
    # time.sleep(10)
    top_url = trend_urls[0]['news_url'][0]
    print(request.get_data())
    
    
    dictToSend = {'key':720,
                  'source':top_url,
                  'type':'URL',
                  'sync':'yes'
                  }
    res = requests.post('http://iaseditor.admantx.com/editor/service/descriptor', data=dictToSend)
    print(res.json())
    
    
    lemmas_str = []
    lemmas = res.json()['lemmas']
    print ('lemmas : ',lemmas)
    lem = {}
    for lem in lemmas:
        print(lem)
        lemmas_str.append(lem['name'])
    print(lemmas_str)
    
    
    places_str = []
    places = res.json()['places']
    print ('places : ',places)
    place = {}
    for place in places:
        print(place)
        places_str.append(place['name'])
    print('places_str : ',places_str)
    
    people_str = []
    people = res.json()['people']
    print ('people : ',people)
    person = {}
    for person in people:
        print(person)
        people_str.append(person['name'])
    print('people_str : ',people_str)

    companies_str = []
    companies = res.json()['companies']
    print ('comapanies : ',companies)
    company = {}
    for company in companies:
        print(company)
        companies_str.append(company['name'])
    print('companies_str : ',companies_str)

    feelings_str = []
    feelings = res.json()['feelings']
    print ('feelings : ',feelings)
    feeling = {}
    for feeling in feelings:
        print(feeling)
        feelings_str.append(feeling['name'])
    print('feelings_str :',feelings_str)

    categories_str = []
    categories = res.json()['categories']
    print ('categories : ',categories)
    feeling = {}
    for feeling in categories:
        print(feeling)
        categories_str.append(feeling['name'])
    print('categories_str : ',categories_str)


    segment = {
                'SegmentType': 'Top Trending Today',
                'Name': results[0],
                'Description': {
                    'lemmas':lemmas_str,
                    'places':places_str,
                    'people':people_str,
                    'companies':companies_str,
                    'feelings':feelings_str,
                    'categories':categories_str
                    },
                'code': random.randrange(1000, 10000, 13)
            }
    return jsonify([segment])


app.run('0.0.0.0', 7050)