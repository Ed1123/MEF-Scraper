import requests


class MinecoAPIMensual:
    BASE_URL = 'https://apps5.mineco.gob.pe/transparencia/mensual/Navegar_6.aspx'
    parameters = {
        '_tgt': 'xls',  # File format
        '_uhc': 'yes',  # ?
        '0': '',  # ?
        '1': 'E',  # Nivel de Gobierno
        '30': '0082',  # Categoría Presupuestal
        '21': '02',  # Departamento
        '23': '1',  # Mes
        '31': '',  # ?
        'y': '2021',  # Año
        'ap': 'Proyecto',  # ?
        'cpage': '1',  # Página?
        'psize': '400'  # Records per page?
    }

    def base_export(self):
        return requests.get(self.BASE_URL, params=self.parameters)


def main():
    mineco_api_mensual = MinecoAPIMensual()
    response = mineco_api_mensual.base_export()
    print(response)


if __name__ == "__main__":
    main()
