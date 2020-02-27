#!/usr/bin/env python3
"""
CIJScraper

Herramienta para recolectar datos publicos de sorteos de causas judiciales en el Centro de Informacion Judicial de la Nacion.
"""


import requests
import pyquery as pq
import collections
import json

CIJ_URL = "https://www.cij.gov.ar/sorteos"
CAMPOS_MAP = {'Fecha de Asignación': 'fecha', 'Expediente':'cod', 'Tipo':'tipo', 'Motivo Asignación':'motivo', 'Dependencia Asignada':'dependencia', 'Denunciantes':'denunciante', 'Denunciados':'denunciados', 'Delitos':'delitos', 'Origen':'origen'}
DatosSorteo = dict

class CIJScraper:
    """CIJScraper"""

    def __init__(self, url = CIJ_URL):
        self._base_url = url

    def scrap_to_json(self, filename):
        """Scrapea la URL y almacena la informacion en filename.csv"""

        lista_sorteos = list()
        resp = requests.get(self._base_url)
        d = pq.PyQuery(resp.text)
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



"""Informacion de un sorteo de causa judicial"""



def main():
    scraper = CIJScraper()
    scraper.scrap_to_json("test.json")

if __name__ == "__main__":
    main()