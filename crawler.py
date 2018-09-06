# -*- coding: utf-8 -*-
from requests_html import HTML
from pyquery import PyQuery as pq
import requests
import psycopg2
from multiprocessing import Pool
import configparser
import os

CONFIG_FILE = os.environ.get('CONFIG_FILE', 'config.ini')
CONFIG_FILE_LOCAL = os.environ.get('CONFIG_FILE_LOCAL', 'config.local.ini')
config = configparser.ConfigParser()
config.read(CONFIG_FILE, "utf-8")

def get_config_value(Section, Key):
    return config.get(Section, Key)

def fetch(url,play_load):
    response = requests.post(url, data=play_load)
    return response.text

def get_metadata_from(resp):

    def parse_article_entries(doc):
        html = HTML(html=doc)
        post_entries = html.find('table.hasBorder tr')[2:]
        return post_entries

    def entry_groups(post_entries):
        ##分類邏輯  每個<table class="hasBorder">下有很多個tr 同樣class屬性的為同一個人的資料
        # [l] [cccccccc] [llll] [ccc] [ll ]

        i = 0
        entry_group = []

        for entry in post_entries:

            if i == 0:
                previous = pq(entry.html).hasClass('lColor')
                entry_group.append([entry])
                i = i + 1
                continue

            if previous == pq(entry.html).hasClass('lColor'):
                entry_group[-1].extend([entry])
                i = i + 1
                continue

            else:
                previous = pq(entry.html).hasClass('lColor')
                entry_group.append([entry])
                i = i + 1
                continue

            return entry_group
    def entry_group_meta(entry_group):


        sequence_number = pq(entry_group[0].html).find('td').eq(0).text()
        stock_symbol = pq(entry_group[0].html).find('td').eq(1).text()
        Company_Name = pq(entry_group[0].html).find('td').eq(2).text()
        job_title = pq(entry_group[0].html).find('td').eq(3).text()
        naturalperson_name = pq(entry_group[0].html).find('td').eq(4).text()
        Date_of_inauguration = pq(entry_group[0].html).find('td').eq(5).text()
        adjunct_companys = []
        adjunct_job_tiltes = []


        for j in range(len(entry_group)):
            if j == 0:
                adjunct_companys.append(pq(entry_group[j].html).find('td.textleft').eq(2).text())
                adjunct_job_tiltes.append(pq(entry_group[j].html).find('td.textleft').eq(3).text())

            else:
                adjunct_companys.append(pq(entry_group[j].html).find('td').eq(0).text())
                adjunct_job_tiltes.append(pq(entry_group[j].html).find('td').eq(1).text())

        results = []
        for adjunct_company, adjunct_job_tilte in zip(adjunct_companys, adjunct_job_tiltes):
            result = {}
            result['序號'] = sequence_number
            result['公司代號'] = stock_symbol
            result['公司名稱'] = Company_Name
            result['職位'] = job_title
            result['姓名'] = naturalperson_name
            result['就任日期'] = Date_of_inauguration
            result['兼任公司'] = adjunct_company
            result['兼任公司職稱'] = adjunct_job_tilte
            results.append(result)

        return results

    post_entries = parse_article_entries(resp)
    entry_group = entry_groups(post_entries)
    Result_group = []
    for entry in entry_group:
        Results = entry_group_meta(entry)
        Result_group += Results
    return Result_group

if __name__ == '__main__':
    # 獨立董事 的市場別有上市、上櫃、興櫃、公開發行分別post不同的參數
    categroy_list = ['sii', 'otc', 'rotc', 'pub']
    post_links = []
    Result_group = []
    for i in range(len(categroy_list)):
        play_load = {'encodeURIComponen': 1, 'step': 1, 'firstin': 1, 'off': 1, 'TYPEK': categroy_list[i]}
        Result = fetch('http://mops.twse.com.tw/mops/web/t93sc01_1', play_load)
        Result_group.append(Result)

    with Pool(processes=4) as pool:
        contents = pool.map(get_metadata_from, Result_group)
