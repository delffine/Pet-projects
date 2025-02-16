import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np

#from sg_lib import show_chogort_table_sns, loaddata, get_client_table
import sg_lib



# ----------------- Меню и загрукза датасетов ---------------------          

sg_lib.header()
                
data = sg_lib.loaddata()
client_table = sg_lib.get_client_table(data)

# ----------------- Основной блок ---------------------          
mainblok = st.container()
with mainblok:
    st.subheader('Основные показатели')

    allusers = data['user_id'].nunique()
    alltr = data['tr_id'].nunique()
    allsum = data['oper_sum'].sum()
    #subscibers = data.query('type == "Оплата с созданием подписки"')['user_id'].unique()
    subscibers = data.query('subscr.notna()')['user_id'].unique()
    allsub = len(subscibers)
    allsubsum = data.query('user_id.isin(@subscibers)')['oper_sum'].sum()
        
    row = st.container()
    with row:    
        col1, col2, col3 = st.columns(3)
        with col1:
            container = st.container(border=True)
            container.write(f"Всего пользователей: **{allusers}**")
        with col2:
            container = st.container(border=True)
            container.write(f"Оформивщих подписку: **{allsub}**")            

        with col3:
            container = st.container(border=True)
            container.write(f"Всего доходов: **{allsum:_} р**".replace('_', ' '))

    row = st.container()
    with row:    
        col1, col2, col3 = st.columns(3)
        with col1:
            container = st.container(border=True)
            container.write(f"Всего транзанкий: **{alltr}**")
        with col2:
            container = st.container(border=True)
            container.markdown(f"Доля оформивщих подписку: **{100 * allsub/allusers:.2f}%**")
        with col3:
            container = st.container(border=True)
            container.write(f"Доходов от подписчиков: **{allsubsum:_.0f} р**".replace('_', ' '))

    week_dynamik = data.groupby('tr_week').agg({'oper_sum' : 'sum', 'user_id' : 'nunique'})
    week_dynamik['cumsum'] = week_dynamik['oper_sum'].cumsum()
    week_dynamik['cumclient'] = week_dynamik['user_id'].cumsum()

    day_dynamik = data.groupby('tr_date').agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    day_dynamik['cumsum'] = day_dynamik['oper_sum'].cumsum()
    day_dynamik['cumclient'] = day_dynamik['user_id'].cumsum()
    day_dynamik['sub_count'] = data.query('user_id.isin(@subscibers)').groupby('tr_date')['user_id'].nunique()
    day_dynamik['sub_sum'] = data.query('user_id.isin(@subscibers)').groupby('tr_date')['oper_sum'].sum()

    
    row = st.container()
    with row:    
        col1, col2 = st.columns(2, border=True)
        with col1:
            st.markdown('**График сумма платежей по дням**')
            st.line_chart(day_dynamik['oper_sum'], color='#ffaa00', x_label = 'Дата', y_label = 'Рубли')
        with col2:
            st.markdown('Плательщики по дням')
            st.line_chart(day_dynamik['user_id'], color='#ff2200', x_label = 'Дата', y_label = 'Человек')
            
    row = st.container()
    with row:    
        col1, col2 = st.columns(2, border=True)
        with col1:
            st.text('Сумма платежей нарастанием')
            st.line_chart(day_dynamik['cumsum'], color='#ff7f0e', x_label = 'Дата', y_label = 'Рубли')

        with col2:
            st.text('Плательщики нарастанием')
            st.line_chart(day_dynamik['cumclient'], color='#1f77b4', x_label = 'Дата', y_label = 'Человек')

    #st.markdown('<div style="background-color:#ff0000;">**This is a custom-styled container.</div>', unsafe_allow_html=True)        



sg_lib.footer()
   
 

