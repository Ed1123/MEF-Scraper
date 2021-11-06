import scrapy


class Mef1Spider(scrapy.Spider):
    name = 'mef_1'
    allowed_domains = ['https://apps5.mineco.gob.pe/transparencia/mensual']
    start_urls = ['http://https://apps5.mineco.gob.pe/transparencia/mensual/']

    def parse(self, response):
        pass
