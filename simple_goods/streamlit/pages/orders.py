import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np
import sg_lib
import altair as alt
    

sg_lib.header()  


data = sg_lib.loaddata()
badtr = data.query('status == "Отклонена"').reset_index(drop=False)
data = data.query('status == "Завершена"').reset_index(drop=False)

     

mainblok = st.container()
with mainblok:

    st.subheader('Платежи')

    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min < tr_date < @date_max')
    #badtr = data.query('@date_min < final_date < @date_max')

    
    
    tab1, tab2 = st.tabs(["Успешные", "Отклоненные"])
    with tab1:
        alltr = data['tr_id'].nunique()
        allfinalsum = data['final_sum'].sum()
        mediansum = data['oper_sum'].median()
        meansum = data['oper_sum'].mean()
        commisionsum = data['oper_sum'].sum() - data['final_sum'].sum()
        oper_time = (pd.to_datetime(data['final_date']) - data['date']).mean()
        oper_time = round(oper_time.seconds / 3600, 0)
     # ------- Сумарные значения ----------
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего транзанкий: **{alltr}**") 
            with col2:
                container = st.container(border=True)
                container.write(f"Медианная сумма платежа: **{mediansum:_.0f} р**".replace('_', ' ')) 
            with col3:
                container = st.container(border=True)
                container.write(f"Сумма зачислений: **{allfinalsum:_.0f} р**".replace('_', ' '))   

        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Среднее время зачисления средств: **{oper_time:.0f} ч**") 

            with col2:
                container = st.container(border=True)
                container.write(f"Средняя сумма платежа: **{meansum:.0f} р**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Потери на комиссии: **{commisionsum:_.0f} р**".replace('_', ' '))                 
                
        cols = st.columns(2, border=True)
        with cols[0]:
            dd = data.groupby('type', as_index=False)['tr_id'].count()
            pie = alt.Chart(dd).mark_arc(innerRadius=70).encode(
                theta=alt.Theta(field="tr_id", type="quantitative"),
                color=alt.Color(field="type", type="nominal"),
                tooltip=["type:N", "tr_id:Q"] 
            ).properties(
                height=400, width=400,
                title="Количество транзакций по типам платежа"
            )
            st.write(pie)
        with cols[1]:
            dd = data.groupby('purpose', as_index=False)['tr_id'].count()
            pie = alt.Chart(dd).mark_arc(innerRadius=70).encode(
                theta=alt.Theta(field="tr_id", type="quantitative"),
                color=alt.Color(field="purpose", type="nominal"),
                tooltip=["purpose:N", "tr_id:Q"] 
            ).properties(
                height=400, width=400,
                title="Количество транзакций по назначению платежа"
            )
            st.write(pie)

        cols = st.columns(2, border=True)
        with cols[0]:

            s99 = data['oper_sum'].quantile(0.99)
            dd = data.query('oper_sum > @s99')['oper_sum'].value_counts().reset_index()
            big_sum = alt.Chart(dd).mark_bar().encode(
                y=alt.Y('count', title='Колво'),
                x=alt.X('oper_sum:O', title='Сумма платежа'),
                tooltip=('count', 'oper_sum'),
                color=alt.value('tomato'),  
            ).properties(
                width=600, height=400,
                title="Аномально больше суммы (больше 99% платежей)"
            )

            st.write(big_sum)
        with cols[1]:
            dd = data.groupby('oper_sum', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bar = alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('tr_id', title='Колво'),
                    x=alt.X('oper_sum:O', sort='-y', title='Сумма платежа'),
                    color=alt.value('#2ca02c'),                
            ).properties(
                height=400, width=400,
                title="Наиболее частые суммы платежей"
            )
            st.write(bar)
            
            
    with tab2:            
        allbad =  len(badtr)
        badcom = badtr['final_sum'].sum()
        badusers = badtr['user_id'].nunique()

     # ------- Сумарные значения ----------
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего отклоненных транзанкий: **{allbad}**") 
            with col2:
                container = st.container(border=True)
                container.write(f"Пользователей, получивших отказ: **{badusers:.0f}**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Потери на коммиссии: **{badcom:_.0f} р**".replace('_', ' ')) 


        cols = st.columns(2, border=True)
        with cols[0]:
            dd = badtr.groupby('pay_result', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            badresult = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='колво транзакций'),
                y=alt.Y('pay_result:N', sort='-x', title='Причина отказа'),
                tooltip=('pay_result', 'tr_id'),
                color=alt.value('red'),
            ).properties(
                width=600, height=400,
                title="Наиболее частые причины отказа"                
            )
            st.write(badresult)

        with cols[1]:
            dd = badtr.groupby('pay_system', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bad_pay_system = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='колво транзакций'),
                y=alt.Y('pay_system:N', sort='-x', title='Платежная система'),
                tooltip=('pay_system', 'tr_id'),
                color=alt.value('orange'),
            ).properties(
                width=600, height=400,
                title="Отказавшщие платежные системы"                    
            )
            st.write(bad_pay_system)



        cols = st.columns(2, border=True)
        with cols[0]:
            dd = badtr.groupby('pay_bank', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bad_bank = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='колво транзакций'),
                y=alt.Y('pay_bank:N', sort='-x', title='Причина отказа'),
                tooltip=('pay_bank', 'tr_id'),
                color=alt.value('green'),
            ).properties(
                width=600, height=400,
                title="Отказавшие банки"                   
            )
            st.write(bad_bank)

        with cols[1]:
            dd = badtr.groupby('pay_bank_country', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bad_country = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='колво транзакций'),
                y=alt.Y('pay_bank_country:N', sort='-x', title='Платежная система'),
                tooltip=('pay_bank_country', 'tr_id'),
                color=alt.value('DodgerBlue'),
            ).properties(
                width=600, height=400,
                title="Страны отказавших банков"   
            )

            st.write(bad_country)

            
sg_lib.footer()