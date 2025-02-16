import streamlit as st
import pandas as pd
#import os
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
#from matplotlib import colors
#from matplotlib import colormaps
import calendar
import numpy as np
#from urllib.parse import urlencode 
#import requests


#----- Стандартные цвета ------
#tab:blue : #1f77b4
#tab:orange : #ff7f0e
#tab:green : #2ca02c
#tab:red : #d62728
#tab:purple : #9467bd
#tab:brown : #8c564b
#tab:pink : #e377c2
#tab:gray : #7f7f7f
#tab:olive : #bcbd22
#tab:cyan : #17becf
# -------------------------------


def header():
    st.set_page_config(
    layout='wide',
    page_title='Дашборд АНО «Простые вещи»'
    )

    #pages = {
    #    "Menu1": [
    #        st.Page("sg_main.py", title="Основные показатели"),
    #        st.Page("users.py", title="Пользователи"),
    #        st.Page("rfm.py", title="RFM анализ"),
    #        st.Page("cogort.py", title="Когортный анализ"),
    #    ],  
    #}
    #st.navigation(pages)
    #pg = st.navigation(pages)
    #pg.run()
    
    
    st.header('Дашборд АНОО "Простые вещи"')    
    header = st.container(border=True)
    with header:
        menu1, menu2, menu3, menu4, menu5 = st.columns(5)
        with menu1:
            st.page_link("sg_main.py", label="Основные показатели", use_container_width=True)
        with menu2:
            st.page_link("pages/month.py", label="Средние показатели", use_container_width=True)      
        with menu3:
            st.page_link("pages/users.py", label="Пользователи", use_container_width=True)  
        with menu4:
            st.page_link("pages/rfm.py", label="RFM анализ", use_container_width=True)
        with menu5:
            st.page_link("pages/cogort.py", label="Когортный анализ", use_container_width=True)
    return            
                
def footer():
    footer = st.container(border=True)
    with footer:
        f1, f2 = st.columns(2)
        with f1:
            st.page_link("pages/data_set.py", label="Данные")
        with f2:

            st.text('Создал Суетов Антон =)')
        



    

def loaddata():
    path = 'data/sg_data.csv'
    data = pd.read_csv('data/sg_data.csv')
    return data

def get_client_table(data):

    dd = data.groupby(['user_id']).agg({'oper_sum' : 'sum', 'tr_date' : 'nunique'})
    bigpayers = dd.query('tr_date == 1 & oper_sum > 25000').sort_values(by = 'oper_sum', ascending = False)
    
    client_table = data.query('not user_id.isin(@bigpayers.index)').groupby('user_id').agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'date' : ['min', 'max']})
    client_table.columns = ['oper_count', 'oper_sum', 'first_date', 'last_date']
    client_table['last_date'] = pd.to_datetime(client_table['last_date'])
    client_table['first_date'] = pd.to_datetime(client_table['first_date'])
    
    client_table['day_on'] = client_table['last_date'] - client_table['first_date']
    client_table['day_on'] = client_table['day_on'].dt.days

    client_table['first_month'] = pd.DatetimeIndex(client_table['first_date']).month
    client_table['month_on'] = 1 + client_table['day_on'] / 30
    client_table['oper_frec'] = client_table['oper_count'] / client_table['month_on']

    maxdate = data.query('date.notna()')['date'].max()
    client_table['day_last'] = client_table['last_date'].apply(lambda x: pd.to_datetime(maxdate) - x)
    client_table['day_last'] = client_table['day_last'].dt.days    
    
    client_table['R'] = client_table['day_last'].apply(lambda x: '1' if x < 30 else ('2' if x < 90 else '3'))
    client_table['F'] = client_table['oper_frec'].apply(lambda x: '1' if x > 2 else ('2' if x > 0.99 else '3'))
    client_table['M'] = client_table['oper_sum'].apply(lambda x: '1' if x > 1400 else ('2' if x > 400 else '3'))
    client_table['RFM'] = client_table['R'] + client_table['F'] + client_table['M']
    
    return client_table


def show_rfm_table_sns(rfm_table, col = 'rfm_sum'):
    fig = plt.figure(figsize = (12, 6))
    rfm_pivot = rfm_table.pivot(index = ['R', 'F'], columns = 'M', values = col).fillna(0)
    rfm_pivot.rename(index={'1':'Недавние(1)', '2' : 'Спящие(2)', '3': 'Уходящие(3)'}, level=0, inplace=True)
    rfm_pivot.rename(index={'1':'Частые(1)', '2' : 'Редкие(2)', '3': 'Разовые(3)'}, level=1, inplace=True)
    rfm_pivot.rename(columns={'1':'Большой чек(1)', '2' : 'Средний чек(2)', '3': 'Малый чек(3)'}, inplace=True)
    par = ''
    if col == 'rfm_sum': par = 'Сумма платежей'
    if col == 'rfm_users': par = 'Количеству пользователей' 
    if col == 'rfm_tr': par = 'Количество транзакций' 

    sns.heatmap(rfm_pivot, cmap='RdYlGn', annot = True, fmt='.0f', cbar=False)
    plt.xlabel('')
    plt.ylabel('')
    plt.title(f'Тепловая карта RFM анализа по параметру "{par}"')
    
    return fig




#Функция показа таблицы данамики по когортам
def show_chogort_table_sns(chogort_table, col='user_count', pr=0):
    dd = chogort_table.pivot(index = 'm_live', columns = 'ch', values = col)

    par = ''
    if col == 'oper_sum': par = 'Сумма платежей'
    if col == 'user_count': par = 'Количество пользователей'
    if col == 'tr_count': par = 'Количество транзакций'
    if col == 'ltv': par = 'LTV'
    if col == 'ltv_m': par = 'LTV в месяц'
    if col == 'rr': par = 'Коэф. удержания'
    if col == 'cr': par = 'Коэф. оттока'
        
    fig = plt.figure(figsize = (12, 6))
    dd.columns=calendar.month_abbr[1:len(dd.columns)+1]
    sns.heatmap(dd, cmap='RdYlGn', annot = True, fmt=f'.{pr}f', cbar=False)
    plt.xlabel('')
    plt.ylabel('')
   
    return fig
    
    