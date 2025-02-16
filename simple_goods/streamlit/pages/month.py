import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np
import sg_lib
    

sg_lib.header()  


data = sg_lib.loaddata()
client_table = sg_lib.get_client_table(data)

     

mainblok = st.container()
with mainblok:

    st.subheader('Среднемесячные показатели')

    month_dynamik = data.groupby('tr_month').agg({'tr_date' : 'first', 'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    month_dynamik['cumsum'] = month_dynamik['oper_sum'].cumsum()
    month_dynamik['cumclient'] = month_dynamik['user_id'].cumsum()
    month_dynamik['cumtr'] = month_dynamik['tr_id'].cumsum()    
    
    users_month = month_dynamik['user_id'].mean()
    tr_month = month_dynamik['tr_id'].mean()
    sum_month = month_dynamik['oper_sum'].mean()
        
    row = st.container()
    with row:    
        col1, col2, col3 = st.columns(3)
        with col1:
            container = st.container(border=True)
            container.write(f"Среднее колво пользователей в месяц: **{users_month:.0f}**")
        with col2:
            container = st.container(border=True)
            container.write(f"Средняя колво платежей в месяц: **{tr_month:.0f}**") 
        with col3:
            container = st.container(border=True)
            container.write(f"Средняя сумма платежей в месяц: **{sum_month:_.0f}** р.".replace('_', ' '))            


            
    
    row = st.container()
    with row:    
        col1, col2 = st.columns(2, border=True)
        with col1:
            st.markdown('**Сумма платежей по месяцам**')
            st.line_chart(month_dynamik, y='oper_sum', x='tr_date', color='#ffaa00', x_label = 'Месяцы', y_label = 'Рубли')
        with col2:
            st.markdown('**Сумма платежей нарастанием**')
            st.line_chart(month_dynamik, y='cumsum', x='tr_date', color='#ff7f0e', x_label = 'Месяцы', y_label = 'Рубли')
            
    row = st.container()
    with row:    
        col1, col2 = st.columns(2, border=True)
        with col1:
            st.markdown('**Плательщики по месяцам**')
            st.line_chart(month_dynamik, y='user_id', x='tr_date', color='#ff2200', x_label = 'Месяцы', y_label = 'Человек')

        with col2:
            st.markdown('**Плательщики нарастанием**')
            st.line_chart(month_dynamik, y='cumclient', x='tr_date', color='#1f77b4', x_label = 'Месяцы', y_label = 'Человек')
    row = st.container()
    with row:    
        col1, col2 = st.columns(2, border=True)
        with col1:
            st.markdown('Транзакции по месяцам')
            st.line_chart(month_dynamik, y='tr_id', x='tr_date', color='#ff2200', x_label = 'Месяцы', y_label = 'Транзакции')

        with col2:
            st.markdown('Транзакции нарастанием')
            st.line_chart(month_dynamik, y='cumtr', x='tr_date', color='#1f77b4', x_label = 'Месяцы', y_label = 'Транзакции')
            
    
    
    
    
sg_lib.footer()