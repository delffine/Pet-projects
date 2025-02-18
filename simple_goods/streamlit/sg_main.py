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
data = data.query('status == "Завершена"').reset_index(drop=False)


# ----------------- Основной блок ---------------------          
mainblok = st.container()
with mainblok:
    prbar = st.progress(0, text='Начинаю вычисления ...')    
    st.header('Основные показатели')

    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min < tr_date < @date_max')
    
    
    allusers = data['user_id'].nunique()
    alltr = data['tr_id'].nunique()
    allsum = data['oper_sum'].sum()

    day_dynamik = data.groupby('tr_date').agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    day_dynamik['cumsum'] = day_dynamik['oper_sum'].cumsum()
    day_dynamik['cumtr'] = day_dynamik['tr_id'].cumsum()
    day_dynamik['cumuser'] = data[['tr_date','user_id']].drop_duplicates(['user_id']).groupby('tr_date').count().cumsum()
    day_dynamik['cumuser'] = day_dynamik['cumuser'].ffill()
    tab1, tab2, tab3 = st.tabs(["Суммарные", "Среднемесячные", "Ежедневные"])
    with tab1:
        prbar.progress(30, text='Сумарные значения')
    # ------- Сумарные значения ----------
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего пользователей: **{allusers}**")
            with col2:
                container = st.container(border=True)
                container.write(f"Всего транзанкий: **{alltr}**")        
            with col3:
                container = st.container(border=True)
                container.write(f"Всего доходов: **{allsum:_} р**".replace('_', ' '))

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи нарастанием**')
                st.line_chart(day_dynamik['cumuser'], color='#1f77b4', x_label = '', y_label = '')         
                
            with col2:
                st.markdown('**Сумма платежей нарастанием**')
                st.line_chart(day_dynamik['cumsum'], color='#2ca02c', x_label = '', y_label = '')



    month_dynamik = data.groupby('tr_month').agg({'tr_date' : 'first', 'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    month_dynamik['cumsum'] = month_dynamik['oper_sum'].cumsum()
    month_dynamik['cumclient'] = month_dynamik['user_id'].cumsum()
    month_dynamik['cumtr'] = month_dynamik['tr_id'].cumsum()    
    
    users_month = month_dynamik['user_id'].mean()
    tr_month = month_dynamik['tr_id'].mean()
    sum_month = month_dynamik['oper_sum'].mean()
    
    # ------- Среднемесячные значения ----------
    with tab2:
        prbar.progress(60, text='Средние значения')
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
                st.markdown('**Плательщики по месяцам**')
                st.line_chart(month_dynamik, y='user_id', x='tr_date', color='#1f77b4', x_label = '', y_label = '')

            with col2:
                st.markdown('**Платежи по месяцам**')
                st.line_chart(month_dynamik, y='oper_sum', x='tr_date', color='#2ca02c', x_label = '', y_label = '')
                
    daysum = day_dynamik['oper_sum'].mean()
    daytr = day_dynamik['tr_id'].mean()
    dayuser = day_dynamik['user_id'].mean()
    
    
    with tab3:
        prbar.progress(90, text='Ежедневные значения')        
    # ------- Ежедневные значения ----------        
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Среднее колво пользователей в день: **{dayuser:.0f}**")
            with col2:
                container = st.container(border=True)
                container.write(f"Средняя колво платежей в день: **{daytr:.0f}**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Средняя сумма платежей в день: **{daysum:_.0f}** р.".replace('_', ' '))              

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Плательщики по дням**')
                st.line_chart(day_dynamik['user_id'], color='#1f77b4', x_label = '', y_label = '')      

            with col2:
                st.markdown('**Платежи по дням**')
                st.line_chart(day_dynamik['oper_sum'], color='#2ca02c', x_label = '', y_label = '')      
                
    prbar.empty()


sg_lib.footer()
   
 

