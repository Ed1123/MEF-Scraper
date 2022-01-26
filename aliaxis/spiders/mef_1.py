import itertools
import os
from datetime import date, datetime, timedelta
from urllib import parse

import scrapy
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))  # To fix path error when eggyfing


def get_pia_pim_urls(cod_niveles_gobierno, cod_categorias_presupuestales, años):
    parameters = itertools.product(
        cod_niveles_gobierno, cod_categorias_presupuestales, años
    )
    return [
        Url(cod_nivel_gobierno=i, cod_cat_presupuestal=j, año=k)
        for i, j, k in parameters
    ]


def get_monthly_report_urls(
    cod_niveles_gobierno, cod_categorias_presupuestales, cod_departamentos, meses, años
):
    parameters = itertools.product(
        cod_niveles_gobierno,
        cod_categorias_presupuestales,
        cod_departamentos,
        meses,
        años,
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
        cod_cat_presupuestal='0082',
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
            '21': f'{self.cod_departamento:02d}'
            if self.cod_departamento
            else None,  # Departamento
            '23': self.mes,  # Mes
            '31': '',  # ?
            'y': self.año,  # Año
            'ap': 'Proyecto',  # ?
            'cpage': '1',  # Página
            'psize': '1000000'
            if os.getenv('TEST_MODE') != 'True'
            else '1',  # Records per page
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
        urls = get_monthly_report_urls(
            self.get_setting('COD_NIVELES_GOBIERNO'),
            self.get_setting('COD_CATEGORÍAS_PRESUPUESTALES'),
            range(1, len(self.get_setting('DEPARTAMENTOS')) + 1),
            # [date.month],
            range(1, 13),  # Temp for getting all historic data
            [date.year],
        ) + get_pia_pim_urls(
            self.get_setting('COD_NIVELES_GOBIERNO'),
            self.get_setting('COD_CATEGORÍAS_PRESUPUESTALES'),
            [date.year],
        )
        # if os.getenv('TEST_MODE') == 'True':
        #     urls = [Url(mes=1)]
        for url in urls:
            yield scrapy.Request(url=url.get(), meta=url.get_meta())

    def get_month_year(self):
        if 'year' not in self.__dict__ and 'month' not in self.__dict__:
            # Taking the month before if no args were provided
            return datetime.now().replace(day=1) - timedelta(days=1)
        else:
            # If one or more args were provided take them
            year = (
                datetime.now().year if 'year' not in self.__dict__ else int(self.year)
            )
            month = (
                datetime.now().month
                if 'month' not in self.__dict__
                else int(self.month)
            )
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

    def get_setting(self, setting_name):
        return self.settings.attributes.get(setting_name).value
