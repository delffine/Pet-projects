import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np
import altair as alt
import sg_lib
    

sg_lib.header()  
data = sg_lib.loaddata()
data = data.query('status == "Завершена"').reset_index(drop=False)
client_table = sg_lib.get_client_table(data)
     

mainblok = st.container()
with mainblok:
    prbar = st.progress(0, text='Начинаю вычисления ...')    
    st.header('Пользователи')

    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min < tr_date < @date_max')
    
    
    allusers = data['user_id'].nunique()
    activ_users = len(client_table.query('day_on < 30'))

    #subscibers = data.query('type == "Оплата с созданием подписки"')['user_id'].unique()
    subscibers = data.query('subscr.notna()')['user_id'].unique()
    allsub = len(subscibers)
    procsub = 100 * allsub / allusers

    allsubsum = data.query('user_id.isin(@subscibers)')['oper_sum'].sum()
    #day_dynamik['sub_count'] = data.query('user_id.isin(@subscibers)').groupby('tr_date')['user_id'].nunique()
    #day_dynamik['sub_sum'] = data.query('user_id.isin(@subscibers)').groupby('tr_date')['oper_sum'].sum()
    sub_dynamik = data.query('user_id.isin(@subscibers)').groupby('tr_date').agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    sub_dynamik['cumsum'] = sub_dynamik['oper_sum'].cumsum()
    sub_dynamik['cumuser'] = data.query('user_id.isin(@subscibers)')[['tr_date','user_id']].drop_duplicates(['user_id']).groupby('tr_date').count().cumsum()
    sub_dynamik['cumuser'] = sub_dynamik['cumuser'].ffill()
    
    tab1, tab2 = st.tabs(["Все пользователи", "Подписчики"])
    with tab1:
        prbar.progress(30, text='Пользователи...')   
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
                container.write(f"Активные в последние 30 дней: **{activ_users}**")            


        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи с наибольщими платежами**')
                dd = data.groupby('user_id', as_index=False).agg({'oper_sum': 'sum', 'tr_id': 'count'}).sort_values(by='oper_sum', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('user_id', sort=None, title='Пользователи'),
                    x=alt.X('oper_sum', title='Сумма платежей'),
                    color=alt.value('#2ca02c'),                
                ))

            with col2:
                st.markdown('**Пользователи сделавшие больще всего транзакций**')
                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('user_id', sort='-x', title='Пользователи'),
                    x=alt.X('tr_id', title='Колво транзакций'),
                    color=alt.value('#1f77b4'),
                ))      


        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**ТОП стран пользователей**')
                dd = data.groupby('country', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('country', sort='-x', title='Страна'),
                    x=alt.X('user_id', title='Пользователей'),
                    color=alt.value('#ff7f0e'),                
                ))

            with col2:
                st.markdown('**ТОП городов пользователей**')
                dd = data.groupby('city', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('city', sort='-x', title='Город'),
                    x=alt.X('user_id', title='Пользователей'),
                    color=alt.value('#8c564b'),
                )) 
    with tab2:
        prbar.progress(60, text='Подписчики')           
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего подписчиков: **{allsub}**")
            with col2:
                container = st.container(border=True)
                container.write(f"Процент подписчиков: **{procsub:.2f}%**")            
            with col3:
                container = st.container(border=True)
                container.write(f"Сумма платежей: **{allsubsum:_.0f} р**".replace('_', ' '))            

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Подписчики нарастанием**')
                st.line_chart(sub_dynamik['cumuser'], color='#1f77b4', x_label = '', y_label = '')         
                
            with col2:
                st.markdown('**Сумма платежей нарастанием**')
                st.line_chart(sub_dynamik['cumsum'], color='#2ca02c', x_label = '', y_label = '')       
    prbar.empty()     

sg_lib.footer()    