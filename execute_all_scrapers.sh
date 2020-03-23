#!/bin/bash
cd /home/yoonhoonsang/internet_lecture
cd qna_crawler

scrapy crawl SPIDERMAN -a with_range=False -a teacher=etoos_yhk
scrapy crawl SPIDERMAN -a with_range=False -a teacher=etoos_kww
scrapy crawl SPIDERMAN -a with_range=False -a teacher=etoos_swc
scrapy crawl SPIDERMAN -a with_range=False -a teacher=etoos_grace

scrapy crawl SPIDERMAN -a with_range=False -a teacher=megastudy_kkh
scrapy crawl SPIDERMAN -a with_range=False -a teacher=megastudy_jjs
scrapy crawl SPIDERMAN -a with_range=False -a teacher=megastudy_kkc
scrapy crawl SPIDERMAN -a with_range=False -a teacher=megastudy_jjh

scrapy crawl SPIDERMAN -a with_range=False -a teacher=mimac_lmh
scrapy crawl SPIDERMAN -a with_range=False -a teacher=mimac_lys
scrapy crawl SPIDERMAN -a with_range=False -a teacher=mimac_esj
scrapy crawl SPIDERMAN -a with_range=False -a teacher=mimac_kjj

scrapy crawl SPIDERMAN -a with_range=False -a teacher=skyedu_jhc
scrapy crawl SPIDERMAN -a with_range=False -a teacher=skyedu_jej


