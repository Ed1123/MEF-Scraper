import scrapy


class Mef2Spider(scrapy.Spider):
    name = 'mef_2'

    def __init__(self, *args, **kwargs):
        super(Mef2Spider, self).__init__(*args, **kwargs)

        if 'urls' in kwargs:
            self.start_urls = kwargs.get('urls').split(',')
        else:
            self.start_urls = [
                'https://apps5.mineco.gob.pe/bingos/seguimiento_pi/Navegador/Navegar_2.aspx?'
                '_tgt=xls&_uhc=yes&0=&33=&y=2022&cpage=1&psize=1000000'
            ]

    def parse(self, response):
        i = self.start_urls[0].find('&y=')
        year = int(self.start_urls[0][i + 3 : i + 7])
        headers = [
            'Proyecto',
            'Costo',
            f'Ejecución al año {year - 2}',
            f'Ejecución año {year - 1}',
            f'{year} PIA',
            f'{year} PIM',
            f'{year} Devengado',
            f'{year} Avance %',
            'Ejecución Total',
            'Avan % Total',
        ]
        for row in response.xpath('//table[3]//tr'):
            data = row.xpath('./td/text()').getall()
            data = [d.strip() for d in data]
            item = {tittle: value for tittle, value in zip(headers, data)}
            item['CUI'] = item['Proyecto'][:7]
            yield item
