PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/go/bin
source scraper/bin/activate
cd qna_crawler

scrapy crawl ETOOS -a teacher=etoos_yhk -o outie.csv
scrapy crawl ETOOS -a teacher=etoos_kww -o cold.csv
