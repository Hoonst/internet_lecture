#!/bin/bash
cd /home/yoonhoonsang/internet_lecture
source scraper/bin/activate
cd qna_crawler

scrapy crawl ETOOS -a teacher=etoos_yhk
scrapy crawl ETOOS -a teacher=etoos_kww
scrapy crawl MEGASTUDY -a teacher=megastudy_jjs
scrapy crawl SKYEDU -a teacher=skyedu_jhc
