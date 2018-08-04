# -*- coding: utf-8 -*-
from requests_html import HTML
import requests
from pyquery import PyQuery as pq
# import psycopg2

def get_metadata_from(url):

    def fetch(url):
        play_load = {'encodeURIComponen': 1,'step': 1,'firstin': 1,'off': 1,'TYPEK': 'sii',}
        response = requests.post(url, data=play_load)
        return response

    def parse_article_entries(doc):
        html = HTML(html=doc)
        post_entries = html.find('table.hasBorder tr')[2:]
        return post_entries

    def entry_groups(post_entries):

        i = 0
        entry_group = []

        for entry in post_entries[:50]:

            if i == 0:
               previous = pq(entry.html).hasClass('lColor')
               entry_group.append([entry])
               i = i +1
               continue

            if previous == pq(entry.html).hasClass('lColor'):
               entry_group[-1].extend([entry])
               i = i +1
               continue

            else:
               previous = pq(entry.html).hasClass('lColor')
               entry_group.append([entry])
               i = i +1
               continue

        return entry_group

    def entry_group_meta(entry_group):

        sequence_number = pq(entry_group[0].html).find('td').eq(0).text()
        stock_symbol = pq(entry_group[0].html).find('td').eq(1).text()
        company_name = pq(entry_group[0].html).find('td').eq(2).text()
        job_title = pq(entry_group[0].html).find('td').eq(3).text()
        naturalperson_name = pq(entry_group[0].html).find('td').eq(4).text()
        Date_of_inauguration = pq(entry_group[0].html).find('td').eq(5).text()

        current_jobs = []
        core_experiences = []
        adjunct_companys = []
        adjunct_job_tiltes = []

        for j in range(len(entry_group)):

            if j==0:

                current_jobs.append(pq(entry_group[j].html).find('td.textleft[rowspan]').eq(0))
                core_experiences.append(pq(entry_group[j].html).find('td.textleft[rowspan]').eq(1))
                adjunct_companys.append(pq(entry_group[j].html).find('td.textleft').eq(2).text())
                adjunct_job_tiltes.append(pq(entry_group[j].html).find('td.textleft').eq(3).text())

            else:
                adjunct_companys.append(pq(entry_group[j].html).find('td').eq(0).text())
                adjunct_job_tiltes.append(pq(entry_group[j].html).find('td').eq(1).text())



        for adjunct_company, adjunct_job_tilte in zip(adjunct_companys,adjunct_job_tiltes):
            result = {}
            result['序號'] = sequence_number
            result['公司代號'] = stock_symbol
            result['公司名稱'] = company_name
            result['職位'] = job_title
            result['姓名'] = naturalperson_name
            result['就任日期'] = Date_of_inauguration
            result['兼任公司'] = adjunct_company
            result['兼任公司職稱'] = adjunct_job_tilte

            print(result)

        for current_job in current_jobs:
            director_current_job = {}
            director_current_job['序號'] = sequence_number
            director_current_job['公司代號'] = stock_symbol
            director_current_job['公司名稱'] = company_name
            director_current_job['職位'] = job_title
            director_current_job['姓名'] = naturalperson_name
            director_current_job['就任日期'] = Date_of_inauguration
            director_current_job['主要現職'] = current_job.text()

            print(director_current_job)

        for core_experience in core_experiences:
            director_core_experience = {}
            director_core_experience['序號'] = sequence_number
            director_core_experience['公司代號'] = stock_symbol
            director_core_experience['公司名稱'] = company_name
            director_core_experience['職位'] = job_title
            director_core_experience['姓名'] = naturalperson_name
            director_core_experience['主要經歷'] = core_experience.text()

            print(director_core_experience)



    resp = fetch(url)
    resp.encoding = "utf-8"
    post_entries = parse_article_entries(resp.text)
    entry_group = entry_groups(post_entries)
    for entry in entry_group:
        entry_group_meta(entry)


if __name__ == '__main__':
   get_metadata_from('http://mops.twse.com.tw/mops/web/t93sc01_1')
