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



def getUrlClassified(top_url):
    url = top_url
    results = []
    if url:
        print(url)
        results = scrape_url(url, words_frequency)
        print('\n getUrlClassified\n')
        if results:
            print('category-1:', results[0])
            print('category-2:', results[2])
        print('\n getUrlClassified\n')
    else:
        parser.error("Please specify websites input type. More about input types you can find 'python predict_url -h'")
    return results    
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
    print('\n trend_data\n')
    print(url)
    NewsFeed = feedparser.parse(url)
    print('\n NewsFeed : \n ', NewsFeed)
    output=[]
    for entry in NewsFeed["entries"][:3]:
        topic={
            'title':entry["title"],
            'summary':entry["summary"],
            'traffic':entry["ht_approx_traffic"],
            'news_url':getnews(entry["title"])
        }
        output.append(topic)
    print("\n Output \n  ",output)
    print('\n trend_data\n')
    return output


@app.route('/health', methods=['GET'])
def health():
    out = {}
    out['status'] = "OK"
    return jsonify(out)

def getContextFromAdmantX(dictToSend):
    response = requests.post('http://iaseditor.admantx.com/editor/service/descriptor', data=dictToSend)
    return response    

def getFormattedLemmasList(res):
    lemmas_str = []
    lemmas = res.json()['lemmas']
    print('\n getFormattedLemmasList\n')
    print ('lemmas : ',lemmas)
    lem = {}
    for lem in lemmas:
        print(lem)
        lemmas_str.append(lem['name'])
    print('\n getFormattedLemmasList\n')
    return lemmas_str

def getFormattedPlacesList(res):
    places_str = []
    print('\n getFormattedPlacesList\n')
    places = res.json()['places']
    print ('places : ',places)
    place = {}
    for place in places:
        print(place)
        places_str.append(place['name'])
    print('places_str : ',places_str)
    print('\n getFormattedPlacesList\n')
    return places_str

def getFormattedPeopleList(res):
    people_str = []
    people = res.json()['people']
    print('\n getFormattedPeopleList\n')
    print ('people : ',people)
    person = {}
    for person in people:
        print(person)
        people_str.append(person['name'])
    print('people_str : ',people_str)
    print('\n getFormattedPeopleList\n')
    return people_str

def getFormattedCompaniesList(res):
    companies_str = []
    companies = res.json()['companies']
    print('\n getFormattedCompaniesList\n')
    print ('comapanies : ',companies)
    company = {}
    for company in companies:
        print(company)
        companies_str.append(company['name'])
    print('companies_str : ',companies_str)
    print('\n getFormattedCompaniesList\n')
    return companies_str

def getFormattedFeelingsList(res):
    feelings_str = []
    feelings = res.json()['feelings']
    print('\n getFormattedFeelingsList\n')
    print ('feelings : ',feelings)
    feeling = {}
    for feeling in feelings:
        print(feeling)
        feelings_str.append(feeling['name'])
    print('feelings_str :',feelings_str)
    print('\n getFormattedFeelingsList\n')
    return feelings_str

def getFormattedCategoriesList(res):
    categories_str = []
    categories = res.json()['categories']
    print('\n getFormattedCategoriesList\n')
    print ('categories : ',categories)
    category = {}
    for category in categories:
        print(category)
        categories_str.append(category['name'])
    print('categories_str : ',categories_str)
    print('\n getFormattedCategoriesList\n')
    return categories_str

def constructSegment(results, lemmas_str, places_str, people_str, companies_str,feelings_str, categories_str):
    return {
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

@app.route('/trending/<string:name>', methods=['GET'])
def getTrendingSegmets(name):
    print('\n getTrendingSegmets\n')
    trend_urls = trend_data(name)
    print('\n',trend_urls)
    trendingSegmets = []
    for i in [0,1,2]:
        url = trend_urls[i]['news_url'][0]
        
        print("\n top_url : ",url,"\n")
        
        results = getUrlClassified(url)
        
        dictToSend = {'key':720,
                    'source':url,
                    'type':'URL',
                    'sync':'yes'
                    }
        res = getContextFromAdmantX(dictToSend)
        print(res.json())
        
        lemmas_str = getFormattedLemmasList(res)    
        places_str = getFormattedPlacesList(res)
        people_str = getFormattedPeopleList(res)
        companies_str = getFormattedCompaniesList(res)
        feelings_str = getFormattedFeelingsList(res)
        categories_str = getFormattedCategoriesList(res)

        segment = constructSegment(results, lemmas_str, places_str, people_str, companies_str,feelings_str, categories_str)
        trendingSegmets.append(segment)
    print('\n getTrendingSegmets\n')
    return jsonify(trendingSegmets)


app.run('0.0.0.0', 7050)