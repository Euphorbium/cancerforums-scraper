# -*- coding: utf-8 -*-
import unicodecsv
from lxml import html
from retrying import retry
import re


@retry(wait_random_min=5000, wait_random_max=10000)
def scrape_thread(thread):
    print thread.attrib['href']
    t = html.parse(thread.attrib['href'])
    title = thread.text
    qid = re.findall('index.php/(.*)\.html.*?', thread.attrib["href"])[0]
    for br in t.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
    reply_to = " "
    posters=set()
    for id, post in enumerate(t.xpath('//div[@class="post"]')):
        inferred_replies = set()

        if id > 0:
            reply_to = qid+"_top"
			unique = qid+'_'+str(id-1)
		else:
		    unique = qid+'_top'
        poster = post.xpath('//div[@class="username"]/text()')[0]
        date = post.xpath('//div[@class="date"]/text()')[0]
        content = post.xpath('//div[@class="posttext"]')[0].text_content()
        for p in posters:
            if p in content:
                inferred_replies.add(p)
        posters.add(poster)

        w.writerow([unique, qid, id-1, title, poster, date, reply_to, content, ' | '.join(inferred_replies), subforum])
        f.flush()

start = html.parse("http://www.cancerforums.net/archive/index.php")
f = open('cancerforums.csv', 'w')
w = unicodecsv.writer(f, encoding='utf-8', lineterminator='\n')
w.writerow(['uniqueID', 'qid', 'localID', 'title', 'poster', 'date', 'replyTo', 'content', 'infered_replies', 'subforum'],)

for sub in start.xpath('//*[@id="content"]/ul/li/ul/li/a'):
    first_page = html.parse(sub.attrib['href'])
    thread_xpath = '//*[@id="content"]/ol/li/a'
    subforum = sub.text
    for thread in first_page.xpath(thread_xpath):
        scrape_thread(thread)
    pages = first_page.xpath('//*[@id="pagenumbers"]/a')
    if pages:
        for page in pages:
            for thread in html.parse(page.attrib['href']).xpath(thread_xpath):
                scrape_thread(thread)
