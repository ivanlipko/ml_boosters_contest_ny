#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 13:36:53 2019

@author: ivan
"""

import random
import time


def get_near_info_strict(dr, address, fp):
#     Осуществляет загрузку страницы
#     dr - selenium chromedriver
#     address - адресс поиска (часть поискового запроса)
#     fp - handle -файла для записи в лог
#     Возвращает dict с описанием

    point_info = []
    
    url = 'https://yandex.ru/maps/?mode=search&text='
    url = url + address.replace(' ', '%20')

    try:
        dr.get(url)
    except Exception as e: 
        #print(e)
        fp.write(e)
        return
    time.sleep(.25)       # ждём загрузку

    point_info = find_onpage(dr,fp)
    return point_info


def find_onpage(dr, fp):
#     Ищет инфу на страницу
#     dr - selenium chromedriver
#     fp - handle -файла для записи в лог
#     Возвращает dict с описанием

    point_info = []
    
    try:
        element = dr.find_element_by_xpath("//div[@class='card-title-view']")
    except:
        #print('Нет заголовка-описания точки')
        fp.write('Нет заголовка-описания точки')

        # Пытаемся понять что происходит
        try:
            # Может быть нам предлагают варианты выбрать? Берём первый попавшийся
            element = dr.find_element_by_xpath("//li[@class='search-snippet-view']")
            element.click()
            time.sleep(.21)

            # Что в этом доме
#            inplace = []
#            try:
#                element = dr.find_elements_by_xpath("//div[@class='business-card-title-view__categories']")
#                for i in range(len(element)):
#                    el = element[i]
#                    inplace.append(el.text.upper())
#            except:
#                print('Нет поля "В этом доме"')

            # Нам предлагают исправление? берём первый
            #try:
            #    element_1 = dr.find_element_by_xpath("//span[@class='search-command-view__show-results-button']")
            #    element_1.click()
            #    time.sleep(1)
            #except:
            #    print('Нет поля "Показать результаты по запросу"')
            return find_onpage(dr,fp)
            
        except:
            # print('Нет списка поиска')
            fp.write('Нет списка поиска')
            return
        
    descr = element.text.split('\n')        # описание того, что нашли с координатами
    
    element = dr.find_element_by_xpath("//div[@class='card-actions-view__item']")
    element.click()
    element = dr.find_element_by_xpath("//div[@class='card-share-view__text']")
    #with open('temp.png', 'wb') as fppng:
    #    fppng.write(element.screenshot_as_png)
    
    pos = [ float(element.text.split(',')[0]), float(element.text.split(',')[1]) ]
    
    
    stop_dist = -1
    stops = -1
    try:
        element = dr.find_element_by_xpath("//div[@class='masstransit-stops-view']")
        stop_dist = element.text.split('\n')
        if len(stop_dist)<3:     # одна остановка
            stops = 1    
        else:                    # много остановок
            stops = element.text.split('\n')[2]
        stop_dist = stop_dist[1]
        if stop_dist.find(",")>-1:     # километры ---> метры
            stop_dist = int(stop_dist.split(' ')[0].replace(',',''))*100
        else:
            stop_dist = int(stop_dist.split(' ')[0])
    except:
        #print('Нет поля "Остановки"')
        #print(fp.name)
        fp.write('Нет поля "Остановки"')
#        return
    
    # Что в этом доме
    inplace = []
    try:
        element = dr.find_elements_by_xpath("//div[@class='search-snippet-categories-view__category']")
        for i in range(len(element)):
            el = element[i]
            inplace.append(el.text.upper())
    except:
#        print('Нет поля "В этом доме"')
         fp.write('Нет поля "В этом доме"')
    
    point_info.append(descr[0])
    point_info.append(descr[1])
    #point_info.append(descr[2].split(','))
    point_info.append([pos[0], pos[1]])
    point_info.append(stops)
    point_info.append(stop_dist)
    point_info.append(inplace)

#     [type][numb][categories][category]
#     point_near[0][3][2][1]
    return point_info



'''
Загатовочка на будущее
    # Каталог "Искать рядом:"
    near = []
    
#     temp = None
#     try:
#         temp = dr.find_element_by_xpath("//div[@class='additional-results-view__hint']")
#     except Exception as e: 
#         print(e)
    catalog = dr.find_elements_by_xpath("//div[@class='catalog-small-item-view__icon']")
    length = len(catalog)    
#     print('if = ', length, catalog)
    if length > 0:
#         length = 8
        for i in range(length):
            catalog = dr.find_elements_by_xpath("//div[@class='catalog-small-item-view__icon']")
#             print('for = ',length, catalog)
            catalog[i].click()  # переход в каталог
            time.sleep(1)       # ждём загрузку
            # Достаём описание объектов
            element = dr.find_elements_by_xpath("//li[@class='search-snippet-view']")
            near_info = []
            for i in range(len(element)):
                el = element[i]
                # название
                el_title = el.find_element_by_xpath(".//div//div[starts-with(@class,'search-business-snippet-view__title')]")
        #         print(el_title.text )
                # категории
                cats = []
                el_type = el.find_elements_by_xpath(".//div//div//div/div[@class='search-snippet-categories-view']/div")
                for i in range(len(el_type)):
                    cats.append(el_type[i].text )
                # адресс
                el_address = el.find_element_by_xpath(".//div//div//div/div[@class='search-business-snippet-view__address']")
        #         print('address:', el_address.text)
                el_info = []
                el_info.append(el_title.text)
                el_info.append(el_address.text)
                el_info.append(cats)
                near_info.append(el_info)
            near.append(near_info)

            sleep_to = random.random()*2+1
            time.sleep(sleep_to)      # ждём загрузку

            # Возвращаемся на страницу с объектом
            element = dr.find_element_by_xpath("//div[@class='sidebar-panel-header-back-view__label']")
            element.click()
            time.sleep(1)       # ждём загрузку
    else:
        print('Не определил точно место')
        
    point_info.append(near)

#     [type][numb][categories][category]
#     point_near[0][3][2][1]
    return point_info
'''

# Web-element screenshot.
# with open('temp.png', 'wb') as outfile:  
#     outfile.write(el_type[1].screenshot_as_png)

# """
# Чтобы найти другие остановки, а не только ближайшую
# //div[@class='card-dropdown-view__content']
# stop_dist = element.text.split('\n')
# if len(stop_dist)<2:
#     stops = []
#     stops.append( stop_dist[0])
# else:
# #     card-dropdown-view__content
#     stop_dist = stop_dist[2]
#     stops = []
#     for i in range(4,int(stop_dist)*2+2+1,2):  # сколько рядом разных остановок и расстояние до них
#         stops.append( element.text.split('\n')[i].split(' ')[0])
# """
    

def upgrade_cities(X, cities):
#     Исправление городов в транслите
#     Х - исходный DataFrame
#     cities - ранее полученные города
#     Возвращает DataFrame с городами

    # редактируем где у анс неправильно
    cities1 = pd.DataFrame( X[~X.address.isnull()].address.apply(lambda x: x.split()[-2]))
    cities1.address = cities1.address.str.upper()
    cities[cities['city'] == 'G'] = cities1[cities['city'] == 'G']
    cities[cities['city'] == 'S'] = cities1[cities['city'] == 'S']
    cities[cities['city'] == 'P'] = cities1[cities['city'] == 'P']
    cities[cities['city'] == 'D'] = cities1[cities['city'] == 'D']
    cities[cities['city'] == 'R'] = cities1[cities['city'] == 'R']
    cities[cities['city'] == 'M'] = cities1[cities['city'] == 'M']
    cities[cities['city'] == 'N'] = cities1[cities['city'] == 'N']
    cities[cities['city'] == '20'] = 'VOLOGDA20'                     # город 'VOLOGDA 20'
    cities[cities['city'] == 'RP'] = cities1[cities['city'] == 'RP']
    cities[cities['city'] == 'KL'] = 'GORYACHIYKL'
    # OB - город ОБЬ
    cities[cities['city'] == 'ST'] = cities1[cities['city'] == 'ST']
    cities[cities['city'] == 'PG'] = cities1[cities['city'] == 'PG']
    cities[cities['city'] == 'S.'] = cities1[cities['city'] == 'S.']
    cities[cities['city'] == 'AK'] = cities1[cities['city'] == 'AK']
    cities[cities['city'] == 'PO'] = 'PORIZHSKAYMECHTA'
    # PO - коттеджный поселок По-Рижская Мечта, 2
    cities[cities['city'] == 'CH'] = cities1[cities['city'] == 'CH'] # Набережные Челны
    cities[cities['city'] == 'YA'] = cities1[cities['city'] == 'YA'] # село Красный Яр
    cities[cities['city'] == 'MO'] = cities1[cities['city'] == 'MO'] #  Раменское
    cities[cities['city'] == 'GP'] = cities1[cities['city'] == 'GP'] # посёлок городского типа Дубинино
    cities[cities['city'] == 'PGT'] = cities1[cities['city'] == 'PGT'] 
    del cities1

    cities[cities['city'] == 'R-N'] = 'OBUHOVO'
    cities[cities['city'] == 'OBL'] = 'DOMODEDOVO'
    cities[cities['city'] == 'VEL'] = 'VELIKIYNOVGOROD'
    cities[cities['city'] == 'VNOVGOROD'] = 'VELIKIYNOVGOROD'

    cities[cities['city'] == 'PGT.'] = 'PROGRESS'
    cities[cities['city'] == 'BAGRATIONOVSKIJ,MOSCOW'] = 'MOSCOW'
    cities[cities['city'] == 'BMOSCOW'] = 'MOSCOW'
    cities[cities['city'] == 'KMOSKVA'] = 'MOSCOW'
    cities[cities['city'] == 'ELITA'] = 'MOSCOW'
    cities[cities['city'] == 'MOSKVA'] = 'MOSCOW'
    cities[cities['city'] == 'STRMOSCOW'] = 'MOSCOW'

    cities[cities['city'] == 'GORO'] = 'SAMARA'

    cities[cities['city'] == 'HSPETERBURG'] = 'SPETERBURG'
    cities[cities['city'] == "SANKTPETERBURG"] = "SPETERBURG"
    cities[cities['city'] == "SANKTPETERB"] = "SPETERBURG"
    cities[cities['city'] == "SPETERSBUR"] = "SPETERBURG"
    cities[cities['city'] == "STPETERBURG"] = "SPETERBURG"
    cities[cities['city'] == "STPETERSBURG"] = "SPETERBURG"
    cities[cities['city'] == "SANKTPETERS"] = "SPETERBURG"
    cities[cities['city'] == "SANTKPETERB"] = "SPETERBURG"
                              
    cities[cities['city'] == "NOVGORO"] = "NIZHNIYNOVGOROD"
    cities[cities['city'] == "NOVG"] = "NIZHNIYNOVGOROD"
    cities[cities['city'] == "NIZHNIYNOVGOROD"] = "NIZHNIYNOVGOROD"
    cities[cities['city'] == "NIZHNNOVGOR"] = "NIZHNIYNOVGOROD"
    cities[cities['city'] == "NIZHNOVGORO"] = "NIZHNIYNOVGOROD"
    cities[cities['city'] == "NNOVGOROD"] = "NIZHNIYNOVGOROD"
    cities[cities['city'] == "NOVGOROD"] = "NIZHNIYNOVGOROD"

    cities[cities['city'] == "TOGLIATTI"] = "TOLYATTI"
    cities[cities['city'] == "ALMETEVSK"] = "ALMETYEVSK"
    cities[cities['city'] == "ARCHANGELSK"] = "ARKHANGELSK"
    cities[cities['city'] == "BALASHIKHA"] = "BALASHIHA"
    cities[cities['city'] == "DZERZHINSKOG"] = "BALASHIHA"
    cities[cities['city'] == "ZHELEZNODORO"] = "BALASHIHA"
    cities[cities['city'] == "ZHELEZNODOROZHN"] = "BALASHIHA"

    cities[cities['city'] == "BELOKURIKHA"] = "BELOKURIHA"
    cities[cities['city'] == "BIROBIYAN"] = "BIROBIDZHAN"

    cities[cities['city'] == "BLAGOVESHCHE"] = "BLAGOVESHCHENSK"
    cities[cities['city'] == "BLAGOVECSHEN"] = "BLAGOVESHCHENSK"
    cities[cities['city'] == "BLAGOVESCHNS"] = "BLAGOVESHCHENSK"
    cities[cities['city'] == "BLAGOVESHENS"] = "BLAGOVESHCHENSK"

    cities[cities['city'] == "BRONNICY"] = "BRONNITSY"
    cities[cities['city'] == "CHEBOXARY"] = "CHEBOKSARY"
    cities[cities['city'] == "CHEKHOV"] = "CHEHOV"
    cities[cities['city'] == "CHELIABINSK"] = "CHELYABINSK"
    cities[cities['city'] == "CHELAYBINSK"] = "CHELYABINSK"
    cities[cities['city'] == "DOLGOPRUDNIY"] = "DOLGOPRUDNYY"
    cities[cities['city'] == "DOLGOPRUDNYJ"] = "DOLGOPRUDNYY"
    cities[cities['city'] == "DOBROVOLTSEVKYZYL"] = "KYZYL"
    cities[cities['city'] == "EGOREVSK"] = "EGORIEVSK"
    cities[cities['city'] == "ELETS"] = "ELEC"
    cities[cities['city'] == "ELISTRA"] = "ELISTA"
    cities[cities['city'] == "GURIEVSK"] = "GURYEVSK"
    cities[cities['city'] == "KAME"] = "KAMEN"

    cities[cities['city'] == "KASPIJSK"] = "KASPIYSK"
    cities[cities['city'] == "KHABAROVSK"] = "HABAROVSK"
    cities[cities['city'] == "KHANDIGA"] = "KHANDYGA" #  тут что-то с координатами, надо смотреть адреса
    cities[cities['city'] == "KHMELNITSKOGBELGOROD"] = "BELGOROD"
    cities[cities['city'] == "KIREYEVSK"] = "KIREEVSK"
    cities[cities['city'] == "KISELIOVSK"] = "KISELEVSK"
    cities[cities['city'] == "KIZILMAZALI"] = "KIZIL"
    cities[cities['city'] == "KLINTSI"] = "KLINTSY"
    cities[cities['city'] == "KOMSOMOLSKNAA"] = "KOMSOMOLSKN"
    cities[cities['city'] == "KOPEJSK"] = "KOPEYSK"
    cities[cities['city'] == "KRASNOKAMENS"] = "KRASNOKAMENSK"
    cities[cities['city'] == "KUPA"] = "KUPAVNA"
    cities[cities['city'] == "KYAHTA"] = "KYAHTA"
    cities[cities['city'] == "LENINSKKUZN"] = "LENINSKKUZNETS"
    cities[cities['city'] == "KOMSOMOLSKNAA"] = "KOMSOMOLSKN"

    cities[cities['city'] == "LIKINODULEV"] = "LIKINODULEVO"
    cities[cities['city'] == "LIPETSK"] = "LIPECK"
    cities[cities['city'] == "LIVNI"] = "LIVNY"
    cities[cities['city'] == "LUKHOVITSY"] = "LUHOVICY"
    cities[cities['city'] == "MALOYAROSLAV"] = "MALOYAROSLAVETS"
    cities[cities['city'] == "MIKHAYLOVSK"] = "MIHAJLOVSK"
    cities[cities['city'] == "MYTISHCHI"] = "MYTISHI"
    cities[cities['city'] == "MYTISCHI"] = "MYTISHI"

    cities[cities['city'] == "NAZYVAYEVSK"] = "NAZYVAEVSK"
    cities[cities['city'] == "NEFTEKUMSK"] = "NEFTEKAMSK"
    cities[cities['city'] == "NOVOALTAJSK"] = "NOVOALTAYSK"
    cities[cities['city'] == "NOVOCHEBOXAR"] = "NOVOCHEBOKSA"
    cities[cities['city'] == "NOVOTROITSK"] = "NOVOTROICK"
    cities[cities['city'] == "NABEREZHNYE"] = "NABCHELNY"
    cities[cities['city'] == "Naberezhnyye"] = "NABCHELNY"
    cities[cities['city'] == "NAKHODKA"] = "NAHODKA"

    cities[cities['city'] == "TAGIL"] = "NTAGIL"
    cities[cities['city'] == "TAGI"] = "NTAGIL"
    cities[cities['city'] == "OTRADNYJ"] = "OTRADNYY"
    cities[cities['city'] == "PERVOMAYSKOYE"] = "PERVOMAYSKOE"
    cities[cities['city'] == "PETROPAVLOVK"] = "PETROPAVLOVSKK"
    cities[cities['city'] == "PETROPAVLOVS"] = "PETROPAVLOVSKK"
    cities[cities['city'] == "PETROPAVLOVSK"] = "PETROPAVLOVSKK"
    cities[cities['city'] == "PROKOPEVSK"] = "PROKOPYEVSK"
    cities[cities['city'] == "RAMENSKOYE"] = "RAMENSKOE"
    cities[cities['city'] == "ROSTOVNADO"] = "ROSTOVNADONU"
    cities[cities['city'] == "RTISHCHEVO"] = "RTISHEVO"
    cities[cities['city'] == "RYBNOYE"] = "RYBNOE"
    cities[cities['city'] == "SAKHAL"] = "SAKHALINSK"
    cities[cities['city'] == "USAHALINSK"] = "SAKHALINSK"
    cities[cities['city'] == "USAKHALINS"] = "SAKHALINSK"
    cities[cities['city'] == "UZHNOSAKHAL"] = "SAKHALINSK"
    cities[cities['city'] == "YSAKHALINSK"] = "SAKHALINSK"
    cities[cities['city'] == "YUSAHALINSK"] = "SAKHALINSK"
    cities[cities['city'] == "YUZHNOSAKHA"] = "SAKHALINSK"
    cities[cities['city'] == "YUZHNOSAKHAL"] = "SAKHALINSK"
    cities[cities['city'] == "YUZHNOSAKHALIN"] = "SAKHALINSK"
    cities[cities['city'] == "SERPUHOV"] = "SERPUKHOV"
    cities[cities['city'] == "SHAKHTI"] = "SHAKHTY"
    cities[cities['city'] == "SPASSKDALNI"] = "SPASSKDALNY"
    cities[cities['city'] == "SVOBODNYY"] = "SVOBODNYY"
    cities[cities['city'] == "TOLYATTI"] = "TOLJATTI"
    cities[cities['city'] == "TROITSK"] = "TROICK"
    cities[cities['city'] == "USOLYESIBIR"] = "USOLIESIBIR"
    cities[cities['city'] == "USSURIJSK"] = "USSURIYSK"
    cities[cities['city'] == "VILJUCHINSK"] = "VILYUCHINSK"
    cities[cities['city'] == "VOLNONADEZH"] = "VOLNONADEZHDIN"
    cities[cities['city'] == "VOLZHSKY"] = "VOLZHSKIY"
    cities[cities['city'] == "ZAOZERNYJ"] = "ZAOZERNYY"
    cities[cities['city'] == "ZHUKOVSKIJ"] = "ZHUKOVSKIY"

    cities.loc[[1846, 7076]] = "MOSCOW"
    cities.loc[[3008, 4068, 4072, 4213, 4278, 5368, 5430, 5431, 5517 ]] = "ZHELEZNOGORSK"
    cities.loc[2987] = "PODGORN"

    cities.loc[4695] = "RTISHCHEVODME"
    cities.loc[7184] = "CHAPLYGIN"
    cities.loc[[1703, 7546]] = "NERYUNGRI"
    cities.loc[7465] = "KOMSOMOLSKN"
    cities.loc[[3145, 8436, 4032]] = "KOMSOMOLSK"
    cities.loc[2231] = "BALASHIHA"

    return cities
