<<<<<<< HEAD
cd qna_crawler

scrapy crawl SPIDERMAN -a teacher=etoos_yhk -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=etoos_kww -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=etoos_swc -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=etoos_grace -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=megastudy_jjs -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=megastudy_kkc -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=megastudy_jjh -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=megastudy_kkh -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=mimac_lmh -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=mimac_lys -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=mimac_esj -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=mimac_kjj -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=skyedu_jej -a with_range=True -a start=2020/03/22 -a till=2020/03/18
scrapy crawl SPIDERMAN -a teacher=skyedu_jhc -a with_range=True -a start=2020/03/22 -a till=2020/03/18
=======
#!/bin/bash
source ~/.profile
pyenv activate scraper
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

>>>>>>> 9c6426e22acd89e17c189044bd860f4ed9170a97

