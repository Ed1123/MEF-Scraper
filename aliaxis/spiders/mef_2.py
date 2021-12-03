import scrapy


class Mef2Spider(scrapy.Spider):
    name = 'mef_2'
    allowed_domains = ['https://apps5.mineco.gob.pe/bingos/seguimiento_pi/Navegador/default.aspx']
    start_urls = ['http://https://apps5.mineco.gob.pe/bingos/seguimiento_pi/Navegador/default.aspx/']

    def parse(self, response):
        pass
