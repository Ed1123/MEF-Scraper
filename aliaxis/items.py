# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MinecoItem(scrapy.Item):
    name = scrapy.Field()
    producto_proyecto = scrapy.Field()
    pia = scrapy.Field()
    pim = scrapy.Field()
    certificación = scrapy.Field()
    compromiso_anual = scrapy.Field()
    ejecución_atención_compromiso_mensual = scrapy.Field()
    ejecución_devengado = scrapy.Field()
    ejecución_girado = scrapy.Field()
    avance_porcentual  = scrapy.Field()
