import itertools
import os
from datetime import date, datetime
from urllib import parse

import scrapy
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))  # To fix path error when eggyfing


class MinecoAPI:
    cod_niveles_gobierno = ['E', 'M', 'R']
    cod_categorias_presupuestales = [
        '0001',
        '0002',
        '0016',
        '0017',
        '0018',
        '0024',
        '0030',
        '0031',
        '0032',
        '0036',
        '0039',
        '0040',
        '0041',
        '0042',
        '0046',
        '0047',
        '0048',
        '0049',
        '0051',
        '0057',
        '0058',
        '0062',
        '0065',
        '0066',
        '0067',
        '0068',
        '0072',
        '0073',
        '0074',
        '0079',
        '0080',
        '0082',
        '0083',
        '0086',
        '0087',
        '0089',
        '0090',
        '0093',
        '0094',
        '0095',
        '0096',
        '0097',
        '0099',
        '0101',
        '0103',
        '0104',
        '0106',
        '0107',
        '0109',
        '0110',
        '0111',
        '0113',
        '0114',
        '0115',
        '0116',
        '0117',
        '0118',
        '0119',
        '0120',
        '0121',
        '0122',
        '0123',
        '0124',
        '0125',
        '0126',
        '0127',
        '0128',
        '0129',
        '0130',
        '0131',
        '0132',
        '0133',
        '0134',
        '0135',
        '0137',
        '0138',
        '0139',
        '0140',
        '0141',
        '0142',
        '0143',
        '0144',
        '0145',
        '0146',
        '0147',
        '0148',
        '0149',
        '0150',
        '1001',
        '1002',
    ]
    cod_departamentos = range(1, 25)
    meses = range(1, 13)

    def get_pia_pim_urls(self):
        parameters = itertools.product(
            self.cod_niveles_gobierno, self.cod_categorias_presupuestales
        )

        return [
            Url(cod_nivel_gobierno=i, cod_cat_presupuestal=j) for i, j in parameters
        ]

    def get_monthly_report_urls(self):
        ### MAKE THIS METHOD A NEW MORE GENERAL ONE THAT GETS LISTS AS ARGUMENTS
        parameters = itertools.product(
            self.cod_niveles_gobierno,
            self.cod_categorias_presupuestales,
            self.cod_departamentos,
            self.meses,
        )

        return [Url(*args) for args in parameters]


class Url:
    base_url = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'

    nivel_gob = {
        'E': 'Gobierno Nacional',
        'M': 'Gobierno Local',
        'R': 'Gobierno Regional',
    }
    departamentos = [
        'Amazonas',
        'Áncash',
        'Apurímac',
        'Arequipa',
        'Ayacucho',
        'Cajamarca',
        'Callao',
        'Cusco',
        'Huancavelica',
        'Huánuco',
        'Ica',
        'Junín',
        'La Libertad',
        'Lambayeque',
        'Lima',
        'Loreto',
        'Madre de Dios',
        'Moquegua',
        'Pasco',
        'Piura',
        'Puno',
        'San Martín',
        'Tacna',
        'Tumbes',
        'Ucayali',
    ]

    def __init__(
        self,
        cod_nivel_gobierno='E',
        cod_cat_presupuestal='0083',
        cod_departamento=None,
        mes=None,
        año=2021,
    ):
        self.cod_nivel_gobierno = cod_nivel_gobierno
        self.cod_cat_presupuestal = cod_cat_presupuestal
        self.cod_departamento = cod_departamento
        self.mes = mes
        self.año = año

    def _get_params_str(self):
        params = {
            '_tgt': 'xls',  # File format
            '_uhc': 'yes',  # ?
            '0': '',  # ?
            '1': self.cod_nivel_gobierno,  # Nivel de Gobierno
            '30': self.cod_cat_presupuestal,  # Categoría Presupuestal
            '21': self.cod_departamento,  # Departamento
            '23': self.mes,  # Mes
            '31': '',  # ?
            'y': self.año,  # Año
            'ap': 'Proyecto',  # ?
            'cpage': '1',  # Página
            'psize': '1000000',  # Records per page
        }
        params = {k: v for k, v in params.items() if v is not None}
        params = parse.urlencode(params)
        return params

    def get(self):
        return f'{self.base_url}?{self._get_params_str()}'

    @property
    def departamento(self):
        if self.cod_departamento is None:
            return
        return self.departamentos[self.cod_departamento - 1]

    @property
    def month_date(self):
        if self.mes is None:
            return
        return date(self.año, self.mes, 1)

    def get_meta(self):
        return {
            'Nivel de Gobierno': self.nivel_gob[self.cod_nivel_gobierno],
            'Categoría Presupuestal': self.cod_cat_presupuestal,
            'Departamento': self.departamento,
            'Mes': self.month_date,
        }


class Mef1Spider(scrapy.Spider):
    name = 'mef_1'

    def start_requests(self):
        date = self.get_month_year()
        mineco_api = MinecoAPI()
        urls = mineco_api.get_monthly_report_urls() + mineco_api.get_pia_pim_urls()
        if os.getenv('TEST_MODE') == 'True':
            urls = [Url(mes=1)]
        for url in urls:
            yield scrapy.Request(url=url.get(), meta=url.get_meta())

    def get_month_year(self):
        if not self.year:
            year = datetime.now().year
        if not self.month:
            month = datetime.now().month
        return datetime(year, month, 1)

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
            'Avance %',
        ]
        rows = response.xpath('//table[3]//tr')
        for row in rows:
            data = row.xpath('./td/text()').getall()
            data = [d.strip() for d in data]
            item = {tittle: value for tittle, value in zip(row_headers, data)}
            meta = {
                k: v
                for k, v in response.meta.items()
                if k
                not in [
                    'download_timeout',
                    'download_slot',
                    'download_latency',
                    'depth',
                ]
            }
            item = {**item, **meta}
            item['CUI'] = item['Producto / Proyecto'][:7]
            yield item
