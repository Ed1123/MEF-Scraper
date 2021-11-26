# %%
import itertools
from datetime import date
from urllib import parse

import scrapy


class MinecoAPI:
    cod_niveles_gobierno = ['E', 'M', 'R']
    cod_categorias_presupuestales = {
        '0082': 'PROGRAMA NACIONAL DE SANEAMIENTO URBANO',
        '0083': 'PROGRAMA NACIONAL DE SANEAMIENTO RURAL',
        '0042': 'APROVECHAMIENTO DE LOS RECURSOS HIDRICOS PARA USO AGRARIO',
        '0138': 'REDUCCION DEL COSTO, TIEMPO E INSEGURIDAD EN EL SISTEMA DE TRANSPORTE',
        '0148': 'REDUCCION DEL TIEMPO, INSEGURIDAD Y COSTO AMBIENTAL EN EL TRANSPORTE URBANO'
    }
    cod_departamentos = range(1, 25)
    meses = range(1, 13)

    def get_pia_pim_urls(self):
        parameters = itertools.product(
            self.cod_niveles_gobierno,
            self.cod_categorias_presupuestales
        )

        return [Url(cod_nivel_gobierno=i, cod_cat_presupuestal=j) for i, j in parameters]

    def get_monthly_report_urls(self):
        parameters = itertools.product(
            self.cod_niveles_gobierno,
            self.cod_categorias_presupuestales,
            self.cod_departamentos,
            self.meses
        )

        return [Url(*args) for args in parameters]


class Url:
    base_url = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'

    nivel_gob = {
        'E': 'Gobierno Nacional',
        'M': 'Gobierno Local',
        'R': 'Gobierno Regional'
    }
    departamentos = [
        'Amazonas', 'Áncash', 'Apurímac', 'Arequipa', 'Ayacucho', 'Cajamarca', 'Callao', 'Cusco',
        'Huancavelica', 'Huánuco', 'Ica', 'Junín', 'La Libertad', 'Lambayeque', 'Lima', 'Loreto',
        'Madre de Dios', 'Moquegua', 'Pasco', 'Piura', 'Puno', 'San Martín', 'Tacna', 'Tumbes',
        'Ucayali'
    ]

    def __init__(self, cod_nivel_gobierno='E', cod_cat_presupuestal='0083', cod_departamento=None, mes=None, año=2021):
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
            'psize': '1000000'  # Records per page
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
            'Mes': self.month_date
        }


# %%
class Mef1Spider(scrapy.Spider):
    name = 'mef_1'

    def start_requests(self):
        mineco_api = MinecoAPI()
        urls = mineco_api.get_monthly_report_urls() + mineco_api.get_pia_pim_urls()
        for url in urls:
            yield scrapy.Request(url=url.get(), meta=url.get_meta())

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
            item = {tittle: value for tittle, value in zip(row_headers, data)}
            item = {**item, **response.meta}
            item['CUI'] = item['Producto / Proyecto'][:8]
            yield item
