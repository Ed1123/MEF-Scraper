# %%
import itertools
from urllib import parse

import scrapy


class MinecoAPI:
    base_url = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'

    cod_niveles_gobierno = ['E', 'M', 'R']
    cod_categorias_presupuestales = ['0083']
    cod_departamentos = range(1, 25)
    meses = range(1, 13)

    def _get_url(self, cod_nivel_gobierno='E', cod_cat_presupuestal='0083', cod_departamento=None, mes=None, año=2021):
        params = {
            '_tgt': 'xls',  # File format
            '_uhc': 'yes',  # ?
            '0': '',  # ?
            '1': cod_nivel_gobierno,  # Nivel de Gobierno
            '30': cod_cat_presupuestal,  # Categoría Presupuestal
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
        return f'{self.base_url}?{params}'

    def get_pia_pim_urls(self):
        parameters = itertools.product(
            self.cod_niveles_gobierno,
            self.cod_categorias_presupuestales
        )

        return [self._get_url(cod_nivel_gobierno=i, cod_cat_presupuestal=j) for i, j in parameters]

    def get_monthly_report_urls(self):
        parameters = itertools.product(
            self.cod_niveles_gobierno,
            self.cod_categorias_presupuestales,
            self.cod_departamentos,
            self.meses
        )

        return [self._get_url(*args) for args in parameters]


# %%
class Mef1Spider(scrapy.Spider):
    name = 'mef_1'
    start_urls = [MinecoAPI()._get_url()]

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
