import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np
import altair as alt
import sg_lib
    

sg_lib.header()  
data = sg_lib.loaddata()
client_table = sg_lib.get_client_table(data)
     

mainblok = st.container()
with mainblok:
    st.subheader('Пользователи-донаторы')

    allusers = data['user_id'].nunique()
    #subscibers = data.query('type == "Оплата с созданием подписки"')['user_id'].unique()
    subscibers = data.query('subscr.notna()')['user_id'].unique()
    allsub = len(subscibers)
    activ_users = len(client_table.query('day_on < 30'))

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
        col1, col2 = st.columns(2)
        with col1:
            st.text('Пользователи с наибольщими платежами')
            dd = data.groupby('user_id', as_index=False).agg({'oper_sum': 'sum', 'tr_id': 'count'}).sort_values(by='oper_sum', ascending=False).head(10)

            st.write(alt.Chart(dd).mark_bar().encode(
                y=alt.Y('user_id', sort=None),
                x='oper_sum',
            ))

        with col2:
            st.text('Пользователи сделавшие больще всего транзакций')
            st.write(alt.Chart(dd).mark_bar().encode(
                y=alt.Y('user_id', sort='-x'),
                x='tr_id',
            ))      

    row = st.container()
    with row:    
        col1, col2 = st.columns(2)
        with col1:
            st.text('ТОП стран пользователей')
            dd = data.groupby('country', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

            st.write(alt.Chart(dd).mark_bar().encode(
                y=alt.Y('country', sort='-x'),
                x='user_id',
            ))

        with col2:
            st.text('ТОП городов пользователей')
            dd = data.groupby('city', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

            st.write(alt.Chart(dd).mark_bar().encode(
                y=alt.Y('city', sort='-x'),
                x='user_id',
            )) 

    
            

sg_lib.footer()    