import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np
import sg_lib
 

sg_lib.header()
data = sg_lib.loaddata()


mainblok = st.container()

with mainblok:
    prbar = st.progress(0, text='Начинаю вычисления ...')
    
    st.header('FRM анализ')
    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min < tr_date < @date_max')


    rfm_filtr = st.container(border=True)
    with rfm_filtr:
        col = st.columns(3)
        with col[0]:
            lastdate_range = st.slider("Границы рангов дней с последней оплаты", 10, 180, (30, 90))
        with col[1]:
            freq_range = st.slider("Границы рангов частоты платежей", 0.5, 5.0, (0.99, 2.0))
        with col[2]:
            sum_range = st.slider("Границы рангов сумм платежей", 100, 5000, (400, 1400))
    
    client_table = sg_lib.get_client_table(data, 
            r1=lastdate_range[0], r2=lastdate_range[1], 
            f1=freq_range[0], f2=freq_range[1],            
            m1=sum_range[0], m2=sum_range[1])
    
    rfm_table = client_table.groupby(['R', 'F', 'M'], as_index = False).agg({'RFM' : 'first', 'oper_count' : ['count', 'sum'], 'oper_sum' : 'sum'})
    rfm_table.columns = ['R', 'F', 'M', 'RFM', 'rfm_users', 'rfm_tr', 'rfm_sum']    
    rfm_table['R'] = rfm_table['R'].replace({'1':'Недавние', '2' : 'Спящие', '3': 'Уходящие'})
    rfm_table['F'] = rfm_table['F'].replace({'1':'Частые', '2' : 'Редкие', '3': 'Разовые'})
    rfm_table['M'] = rfm_table['M'].replace({'1':'Большой чек', '2' : 'Средний чек', '3': 'Малый чек'})
    rfm_table['RF'] = rfm_table['R'] + '/' + rfm_table['F']
    rfm_table['avg_sum'] = round(rfm_table['rfm_sum'] / rfm_table['rfm_tr'], 2)

    prbar.progress(20, text='')
    st.header('RFM матрицы')

    col1, col2 = st.columns(2, border=True)
    with col1:
        st.text('Количество пользователей')
        sg_lib.rfn_alt(rfm_table, 'rfm_users:Q')
    prbar.progress(40, text='')        
    with col2:
        st.text('Сумма платежей')
        sg_lib.rfn_alt(rfm_table, 'rfm_sum:Q')

    prbar.progress(60, text='')

    col1, col2 = st.columns(2, border=True)
    with col1:
        st.text('Количество платежей')
        sg_lib.rfn_alt(rfm_table, 'rfm_tr:Q')
    prbar.progress(80, text='')        
    with col2:
        st.text('Средний чек')
        sg_lib.rfn_alt(rfm_table, 'avg_sum:Q')
        
    #st.table(rfm_table[['RFM', 'R', 'F', 'M', 'rfm_users', 'rfm_tr', 'rfm_sum']])

    st.header('RFM таблица')
    st.data_editor(rfm_table[['RFM', 'R', 'F', 'M', 'rfm_users', 'rfm_tr', 'rfm_sum', 'avg_sum']],
    #   column_config={
    #       "R": st.column_config.TextColumn("Давность"),
    #       "F": st.column_config.TextColumn("Частота"),
    #       "M": st.column_config.TextColumn("Сумма"),
    #       "rfm_users": st.column_config.ProgressColumn("Пользователей", format="%d", max_value = rfm_table['rfm_users'].max()),
    #       "rfm_tr": st.column_config.ProgressColumn("Платежей", format="%d", max_value = rfm_table['rfm_tr'].max()),
    #       "rfm_sum": st.column_config.ProgressColumn("Общая сумма", format="%d", max_value = rfm_table['rfm_sum'].max()),
    #       "avg_sum": st.column_config.ProgressColumn("Средний чек", format="%d", max_value = rfm_table['avg_sum'].max()),
    #   },
       use_container_width=True,
       hide_index=True,
       )
    prbar.empty()
    
   
    
sg_lib.footer()
