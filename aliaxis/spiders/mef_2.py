import scrapy


class Mef2Spider(scrapy.Spider):
    name = 'mef_2'
    allowed_domains = [
        'https://apps5.mineco.gob.pe/bingos/seguimiento_pi/Navegador/default.aspx']
    start_urls = [
        'https://apps5.mineco.gob.pe/bingos/seguimiento_pi/Navegador/Navegar_2.aspx?'
        '_tgt=xls&_uhc=yes&0=&31=&y=2021&cpage=1&psize=1000000'
    ]

    def parse(self, response):
        row_headers = [
            'Proyecto', 'Costo', 'Ejecución al año 2019', 'Ejecución año 2020', '2021 PIA',
            '2021 PIM', '2021 Devengado', '2021 Avance %', 'Ejecución Total', 'Avan % Total'
        ]
        for row in response.xpath('//table[3]//tr'):
            data = row.xpath('./td/text()').getall()
            data = [d.strip() for d in data]
            item = {tittle: value for tittle, value in zip(row_headers, data)}
            item['CUI'] = item['Proyecto'][:7]
            yield item
