import requests


class MinecoAPIMensual:
    BASE_URL = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'

    @staticmethod
    def parameters(
        cod_nivel_gobierno,
        cod_categoria_presupuestal,
        cod_departamento,
        mes,
        año,
    ):
        return {
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
            'cpage': '1',  # Página?
            'psize': '400'  # Records per page?
        }

    def sample_request(self):
        params = self.parameters(
            cod_nivel_gobierno='E',
            cod_categoria_presupuestal='0083',
            cod_departamento=None,
            mes=None,
            año=2021
        )
        response = requests.get(
            self.BASE_URL, params=params)
        return response

    @staticmethod
    def save_response(response, filename):
        with open(filename, 'wb') as f:
            f.write(response.content)

def main():
    mineco_api_mensual = MinecoAPIMensual()
    response = mineco_api_mensual.sample_request()
    mineco_api_mensual.save_response(response, 'test_export.xls')
    print(response.url)


if __name__ == "__main__":
    main()
