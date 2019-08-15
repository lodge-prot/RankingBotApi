#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import datetime
import requests
import collections
import pprint

from bs4 import BeautifulSoup as bs
from flask import Flask
from flask import abort, jsonify, request, render_template

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

def generate_json(url_list: list, title_list: list):

    ret = {}
    ret["Qiita"] = [{}] * 30

    for i, record in enumerate(list(zip(url_list, title_list))):
        ret["Qiita"][i] = {str(i+1) : [ {"title" : record[1]}, {"url" : record[0]} ]}

    return jsonify(ret)


def get_qiita_ranking():
    url = "https://qiita.com/"

    try:
        html = requests.get(url).text
        app.logger.info('http request executed')
        soup = bs(html, "html.parser")
    except:
        app.logger.warn('http request failed')
        abort(404)

    js = soup.find("div" , class_="p-home_main mb-3 mr-0@s").find("div")['data-hyperapp-props']
    di = json.loads(js)

    article_url = ""
    url_list, title_list = [], []
    for val in di['trend']['edges']:
        tn = val['node']
        article_url = '{}{}/items/{}'.format(url, tn['author']['urlName'], tn['uuid'])
        url_list.append(article_url)
        title_list.append(tn['title'])

    return generate_json(url_list, title_list)


def local_get_qiita_ranking():
    path = "tests/test.json"

    with open(path) as f:
        js = json.load(f)

    return js

@app.route("/api/qiita/ranking")
def qiita():
    return get_qiita_ranking()


@app.route("/api/qiita/ranking/local")
def qiita_local():
    return local_get_qiita_ranking()


@app.errorhandler(404)
@app.errorhandler(404)
def error_handler(error):
    return render_template("404.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
