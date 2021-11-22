import requests
from dataclasses import dataclass


@dataclass
class Parameters:
    cod_nivel_gobierno = 'E'
    cod_categoria_presupuestal = '0083'
    cod_departamento = None
    mes = None
    año = 2021

    def get_params(self):
        return {
            '_tgt': 'xls',  # File format
            '_uhc': 'yes',  # ?
            '0': '',  # ?
            '1': self.cod_nivel_gobierno,  # Nivel de Gobierno
            '30': self.cod_categoria_presupuestal,  # Categoría Presupuestal
            '21': self.cod_departamento,  # Departamento
            '23': self.mes,  # Mes
            '31': '',  # ?
            'y': self.año,  # Año
            'ap': 'Proyecto',  # ?
            'cpage': '1',  # Página?
            'psize': '1000000'  # Records per page?
        }


class MinecoAPIMensual:
    BASE_URL = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'

    def sample_request(self):
        params = Parameters()
        response = self._basic_request(params)
        return response

    @staticmethod
    def save_response(response, filename):
        with open(filename, 'wb') as f:
            f.write(response.content)

    def _basic_request(self, params: Parameters):
        response = requests.get(self.BASE_URL, params=params.get_params())
        return response

    def get_detail_report(self):
        pass


def main():
    mineco_api_mensual = MinecoAPIMensual()
    response = mineco_api_mensual.sample_request()
    mineco_api_mensual.save_response(response, 'test_export.xls')
    print(response.url)


if __name__ == "__main__":
    main()
