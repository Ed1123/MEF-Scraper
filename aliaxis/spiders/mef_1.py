from urllib import parse

import scrapy


def get_url(cod_nivel_gobierno='E', cod_categoria_presupuestal='0083', cod_departamento=None, mes=None, año=2021):
    url = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'
    params = {
        '_tgt': 'xls',  # File format
        '_uhc': 'yes',  # ?
        '0': '',  # ?
        '1': cod_nivel_gobierno,  # Nivel de Gobierno
        '30': cod_categoria_presupuestal,  # Categoría Presupuestal
        '21': cod_departamento,  # Departamento
        '23': mes,  # Mes
        '31': '',  # ?
        'y': año,  # Año
        'ap': 'Proyecto',  # ?
        'cpage': '1',  # Página
        'psize': '1000000'  # Records per page
    }
    params = {k: v for k, v in params.items() if v is not None}
    params = parse.urlencode(params)
    return f'{url}?{params}'


class Mef1Spider(scrapy.Spider):
    name = 'mef_1'
    start_urls = [get_url()]

    def parse(self, response):
        row_headers = [
            'Producto / Proyecto',
            'PIA',
            'PIM',
            'Certificación',
            'Compromiso Anual',
            'Ejecución - Atención de Compromiso Mensual',
            'Ejecución - Devengado',
            'Ejecución - Girado',
            'Avance %'
        ]
        rows = response.xpath('//table[3]//tr')
        for row in rows:
            data = row.xpath('./td/text()').getall()
            data = [d.strip() for d in data]
            yield {tittle: value for tittle, value in zip(row_headers, data)}
