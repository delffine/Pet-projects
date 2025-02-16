import streamlit as st
import pandas as pd
import datetime
import pytz
import calendar
import os
import numpy as np
import sg_lib


def load_rawdata():
    rawdt = pd.DataFrame([])
#   path = 'd:/newwork/-=simple_goods=-/data/'
    path = 'data/'
    all = 0
    l = 0

    #data_load_state = st.text('') 
    st.text('Начинаю загрузку данны...')

    for ff in os.listdir(path):
        if ff.split('.')[1] == 'xls':
            dd = pd.read_excel(path + ff)
            dd['file'] = ff
            l = len(dd)
            all = all + l
            rawdt = pd.concat([rawdt, dd])
            st.text(f'Загрузка {l} строк данных из файла {ff}')
    st.text(f'Всего загружено {all} строк данных') 
        
    #удаляем колонки, в которых нет значений
    na_col = []
    for i in range(0, len(rawdt.count())):
        if rawdt.count()[i] == 0: na_col.append(rawdt.count().index[i])
    rawdt = rawdt.drop(na_col, axis = 1)
    st.text('удаляем колонки, в которых нет значений')

    #Удаляем колонки с одним уникальным значением
    na_col = []
    for col in rawdt.columns:
        if rawdt[col].nunique() == 1: na_col.append(col)
    rawdt = rawdt.drop(na_col, axis = 1)
    st.text('Удаляем колонки с одним уникальным значением')

    #Наложений нет - можно их объединить
    rawdt['Статус'] = rawdt['Статус'].fillna('')
    rawdt['Статус операции'] = rawdt['Статус операции'].fillna('')
    rawdt['Статус операции'] = rawdt['Статус операции'] + rawdt['Статус']

    #Наложений нет - можно их объединить
    rawdt['ID плательщика'] = rawdt['ID плательщика'].fillna('')
    rawdt['Плательщик'] = rawdt['Плательщик'].fillna('')
    rawdt['user_mail'] = rawdt['Плательщик'] + rawdt['ID плательщика']
    st.text('Объединяем одинаковые по смыслу колонки')
    


    #Создаем словарь псевдоним / почта
    user_dic = {}
    i = 0
    for u in rawdt['user_mail'].unique():
        if str(u) == u :
            i +=1
            user_dic[u] = f'user_{i:04.0f}'
    #замена индификатора пользователей по словарю
    rawdt['user_id'] = rawdt['user_mail'].replace(user_dic)
    st.text('замена индификатора пользователей по словарю')

    #Создаем новые результирующие / преобразованные колонки
    rawdt['status'] = rawdt['Статус операции'].replace({'Completed' : 'Завершена', 'Declined' : 'Отклонена'} )
    rawdt['purpose'] = rawdt['Назначение платежа'].str.lower().str.replace('&quot;' , '"')
    rawdt['date'] = pd.to_datetime(rawdt['Дата и время'], format = '%Y-%m-%d %H:%M:$S', errors = 'coerce')
    
    #колонки с днем, неделью и месяцем транзакции
    rawdt['tr_date'] = rawdt['date'].dt.date
    rawdt['tr_week'] = rawdt['date'].dt.isocalendar().week
    rawdt['tr_month'] = rawdt['date'].dt.month

    st.text('Создаем новые результирующие / преобразованные колонки')
    
    #Удаляем бесполезные колонки
    na_col = ['Срок действия' , 'Эмитент' , 'Карта' , 'Страна эмитента карты',
              'Public ID' , 'Код' ,'RRN', 'Код авторизации', 'Способ оплаты',
              'Платежная система', 'Валюта операции', 'Примечание',
              'Статус', 'Статус операции',
              'ID плательщика', 'Плательщик', 'user_mail',
              'Назначение платежа',
              'Дата и время', 'Дата возмещения', 'Дата/время создания']
    rawdt = rawdt.drop(na_col, axis = 1)
    st.text('Удаляем бесполезные колонки')

    #Для дальнейшего анализа берем только данные с завершенными операциями
    data = rawdt.query('status == "Завершена"').copy()
    data = data.reset_index(drop = True)

    st.text('Переименование колонок к python виду')              
    data = data.rename(columns = {'Номер' : 'tr_id',
                      'Тип' : 'type',
                      'Сумма операции' : 'oper_sum',
                      'Сумма комиссии' : 'oper_com',
                      'Сумма возмещения' : 'final_sum',
                      '% комиссии' : 'com_perc',
                      'Номер заказа' : 'order_id',
                      'Подписка' : 'subscr',
                      'Страна' : 'country',
                      'Город' : 'city',

                      }
           )
           
           
    st.text(f'Загрузка данных завершена!\n Всего загружено {all} строк данных.\n После обработки для дальнейшего анализа отобрано {len(data)} строк данных.')
    

    
    st.text(f'Сохраняю в CSV! по адресу data/sg_data.csv')
    data[['tr_id', 'date', 'user_id', 'oper_sum', 
            'order_id', 'type',  'purpose', 'status', 
            'subscr', 'city', 'country', 
            'tr_date', 'tr_week', 'tr_month', 'file']].to_csv('data/sg_data.csv', index=False)

    return data
    
    
sg_lib.header()
data = sg_lib.loaddata()

st.header('Загруженные данные')
modification_time = os.path.getmtime('data/sg_data.csv')
last_modified = (pd.to_datetime(modification_time, unit='s') + datetime.timedelta(hours=4)).strftime('%Y.%m.%d %H:%M:%S')

#last_modified = t0.strftime('%Y.%m.%d %H:%M:%S')
st.markdown(f'Всего **{len(data)}** строк, aктуальность файла данных **{last_modified}**')

st.text('Пример данных')
st.dataframe(data.sample(10))

if st.button('Перезагрузить данные', type="primary"):
    load_rawdata()

st.text(f' \n \n \n ')

sg_lib.footer()