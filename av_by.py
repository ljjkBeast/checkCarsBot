import requests
from bs4 import BeautifulSoup as BS


def get_last_auto_from_av(params):
    """Получаем первоначальный список объявлений с av.by"""
    ids = []
    r = requests.get(params)
    html = BS(r.content, 'html.parser')
    for el in html.select('.listing-item '):
        link = el.select('.listing-item-title > h4 > a')[0]['href']
        id = int(link.split('/')[-1])
        ids.append(id)
        if len(ids) >= 5:
            break
    print(ids)
    return ids


class AvBySearch:
    """Парсер по отфильтрованным параметрам, который отслеживает новые объъявления"""
    def __init__(self, last_auto, params):
        self.last_auto_list = last_auto
        self.params = params

    def new_ads(self, params, last_ads):
        """Проверяем изменился ли список объявлений"""
        r = requests.get(params)
        html = BS(r.content, 'html.parser')
        link = html.select('.listing-item-title > h4 > a')[0]['href']
        id_ads = int(link.split('/')[-1])
        return int(id_ads) != int(last_ads)

    # Сравниваем объявления в файле с объявлениями на сайте до первого совпадения. Повторяем через равные промежутки
    # времени. Если нашлось новое объявление, переписываем файл.
    def get_new_ads_av(self, params, last_ads_list):
        """Получаем новые объявления"""
        r = requests.get(params)
        html = BS(r.content, 'html.parser')
        new_ads_list = []
        ads_count = 0
        for el in html.select('.listing-item '):
            if ads_count > 23:
                break
            link = el.select('.listing-item-title > h4 > a')[0]['href']
            id = int(link.split('/')[-1])
            if id in last_ads_list:
                break
            title = el.select('.listing-item-title > h4 > a')[0].text.strip()
            price = el.select('.listing-item-price > small')[0].text.strip()
            city = el.select('.listing-item-other > .listing-item-location')[0].text.strip()
            description = el.select('.listing-item-desc')[0].text.split(',')
            info_av = {
                'id': id,
                'title': title,
                'price': price,
                'link': link,
                'city': city,
                'year': description[0].strip(),
                'transmission': description[1].strip(),
                'engine_capacity': description[2].strip(),
                'engines_type': description[3].strip(),
                'body_type': description[4].strip(),
                'mileage': description[5].strip(),
            }
            new_ads_list.append(info_av)
            ads_count += 1
        return new_ads_list