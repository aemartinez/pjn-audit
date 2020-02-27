#!/usr/bin/env python3
"""
CIJScraper

Herramienta para recolectar datos publicos de sorteos de causas judiciales en el Centro de Informacion Judicial de la Nacion.
"""


import requests
import pyquery as pq
import collections
import json
import shutil
from PIL import Image

CIJ_URL = "https://www.cij.gov.ar/sorteos"
CIJ_CAPTCHA_URL = " https://www.cij.gov.ar/lib/securimage/securimage_show.php"
CAMPOS_MAP = {'Fecha de Asignación': 'fecha', 'Expediente':'cod', 'Tipo':'tipo', 'Motivo Asignación':'motivo', 'Dependencia Asignada':'dependencia', 'Denunciantes':'denunciante', 'Denunciados':'denunciados', 'Delitos':'delitos', 'Origen':'origen'}
DatosSorteo = dict

class CIJScraper:
    """CIJScraper"""

    def __init__(self, url = CIJ_URL):
        self._base_url = url

    def scrap_to_json(self, filename):
        """Scrapea la URL y almacena la informacion en filename.json"""

        lista_sorteos = list()
        s = requests.Session() 
        resp = s.get(CIJ_CAPTCHA_URL, stream=True)
        cookies = resp.cookies
        with open('captcha.png', 'wb') as out_file:
            shutil.copyfileobj(resp.raw, out_file)
        del resp

        image = Image.open('captcha.png')
        image.show()

        captcha_code = input("Escribir captcha: ")

        # POST REQUEST EXAMPLE
        # Request URL: https://www.cij.gov.ar/sorteos
        # Request Method: POST
        # 
        # fecha_exacta_juzgados: 27/02/2020
        # selector: rango
        # fecha_juzgados_desde: 2019-02-01
        # fecha_juzgados_desde_aux: 01/02/2019
        # fecha_juzgados_hasta: 2020-02-10
        # fecha_juzgados_hasta_aux: 10/02/2020
        # oficina: 
        # nombre[]: 
        # paginaS1: 0
        # paginaS2: 0
        # origenPaginado: S1
        # paginado: 0
        # captcha_code: sC5E
        # btn: Buscar
        post_data = {
            'selector': 'rango',
            'fecha_juzgados_desde': '2019-02-01',
            'fecha_juzgados_desde_aux': '01/02/2019',
            'fecha_juzgados_hasta': '2020-02-10',
            'fecha_juzgados_hasta_aux': '10/02/2020',
            'paginaS1': '0',
            'paginaS2': '0',
            'origenPaginado': 'S1',
            'paginado': '0',
            'captcha_code': captcha_code,
            'btn': 'Buscar',
        }
        resp = s.post(self._base_url, data = post_data, cookies=cookies)
        d = pq.PyQuery(resp.text)
        with open('web.html', 'w') as fp:
            fp.write(d.html())
        results = d('#sorteos-resultado').children(".result")
        for res in results.items():
            datos = res("ul li")
            
            # === Ejemplo de datos de un sorteo: ===
            # 
            # Fecha de Asignación: 11/02/2020
            # Expediente: CFP 619/2020
            # Tipo: OTROS ORGANISMOS
            # Motivo Asignación: SORTEO
            # Dependencia Asignada: JUZGADO CRIMINAL Y CORRECCIONAL FEDERAL 9
            # Denunciantes: IDENTIDAD RESERVADA - IDENTIDAD RESERVADA -
            # Denunciados: CANUT HNOS SRL -
            # Delitos: INFRACCION LEY 23.737 (ART.44) -
            # Origen: MINISTERIO DE SEGURIDAD
            # 
            # ======================================
            sorteo = DatosSorteo()
            for dato in datos.items():
                dato = dato.text().split(":")
                sorteo[CAMPOS_MAP[dato[0]]] = CIJScraper.sanitizar(dato[1])
            lista_sorteos.append(sorteo)

        with open(filename, 'w') as fp:
            json.dump(lista_sorteos, fp)
            # print(sorteo)
            # print("---------------------")
    
    @staticmethod
    def sanitizar(texto):
        texto = texto.replace(' Ver menos', '')
        texto = texto.replace(' Ver todos', '')
        return texto

def main():
    scraper = CIJScraper()
    scraper.scrap_to_json("test.json")

if __name__ == "__main__":
    main()