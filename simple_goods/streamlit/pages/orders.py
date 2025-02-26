import streamlit as st
import pandas as pd
import sg_lib
import altair as alt
    
#---------------------------------------------------------------
#------------------- Шапка с меню датасетов --------------------
#---------------------------------------------------------------
sg_lib.header()  

#---------------------------------------------------------------
#------------------------ Загрукза датасетов -------------------
#---------------------------------------------------------------
data = sg_lib.loaddata()
badtr = data.query('status == "Отклонена"').reset_index(drop=False)
data = data.query('status == "Завершена"').reset_index(drop=False)
   
#---------------------------------------------------------------
# ----------------- Основной блок башборда ---------------------          
#---------------------------------------------------------------
mainblok = st.container()
with mainblok:

    st.subheader('Транзакции')

    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min <= tr_date <= @date_max')
    sg_colors = ['#eb606c', '#a1c5c5', '#506788', '#f1e7ce', '#42445a', '#e8f3f4',  '#f2bc62', ]    
    
    tab1, tab2 = st.tabs(["Успешные", "Отклоненные"])
    # ------- Успешные ----------
    with tab1:
        alltr = data['tr_id'].nunique()
        allfinalsum = data['final_sum'].sum()
        mediansum = data['oper_sum'].median()
        meansum = data['oper_sum'].mean()
        commisionsum = data['oper_sum'].sum() - data['final_sum'].sum()
        oper_time = (pd.to_datetime(data['final_date']) - data['date']).mean()
        oper_time = round(oper_time.seconds / 3600, 0)
        # ------- Цифровые показатели ----------
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего транзакций: **{alltr}**") 
            with col2:
                container = st.container(border=True)
                container.write(f"Медианная сумма транзакций: **{mediansum:_.0f} р**".replace('_', ' ')) 
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
                container.write(f"Средняя сумма транзакций: **{meansum:.0f} р**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Потери на комиссии: **{commisionsum:_.0f} р**".replace('_', ' '))                 


        # ------- Диаграммы ----------        
        cols = st.columns(2, border=True)
        with cols[0]:
            dd = data.groupby('type', as_index=False)['tr_id'].count()
            dd['tr_per'] = dd['tr_id'] / dd['tr_id'].sum()
            pie = alt.Chart(dd).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="tr_per", sort='descending', title='Кол-во', type="quantitative"),
                color=alt.Color(field="type", title='Тип', type="nominal"),
                tooltip=alt.Tooltip(field = 'tr_per', format = '.2%')
            ).properties(
                height=400, width=400,
                title="Доли транзакций по типам"
            ).configure_range(
                category=alt.RangeScheme(sg_colors)
            )
            st.write(pie)
            
        with cols[1]:
            dd = data.groupby('purpose', as_index=False)['tr_id'].count()
            dd['tr_per'] = dd['tr_id'] / dd['tr_id'].sum()
            pie = alt.Chart(dd).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="tr_per", sort='descending', title='Кол-во', type="quantitative"),
                color=alt.Color(field="purpose", title='Назначение', type="nominal"),
                tooltip=alt.Tooltip(field = 'tr_per', format = '.2%')
            ).properties(
                height=400, width=400,
                title="Доли транзакций по назначению"
            ).configure_range(
                category=alt.RangeScheme(sg_colors)
            )
            st.write(pie)

        cols = st.columns(2, border=True)
        with cols[0]:

            s99 = data['oper_sum'].quantile(0.99)
            dd = data.query('oper_sum > @s99')['oper_sum'].value_counts().reset_index()
            big_sum = alt.Chart(dd).mark_bar().encode(
                y=alt.Y('count', title='Кол-во'),
                x=alt.X('oper_sum:O', title='Сумма транзакций'),
                color=alt.value('#eb606c'),  
            ).properties(
                width=600, height=400,
                title="Аномально больше суммы (больше 99% транзакций)"
            )

            st.write(big_sum)
        with cols[1]:
            dd = data.groupby('oper_sum', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bar = alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('tr_id', title='Кол-во'),
                    x=alt.X('oper_sum:O', sort='-y', title='Сумма транзакций'),
                    color=alt.value('#a1c5c5'),                
            ).properties(
                height=400, width=400,
                title="Наиболее частые суммы транзакций"
            )
            st.write(bar)
            
    # ------- Отклоненные ----------            
    with tab2:            
        
        #badtr = badtr.query('@date_min <= final_date <= @date_max')
        #не у всех отклоненных транзакций есть даты, так что выводи все без фильтра
        
        allbad =  len(badtr)
        badcom = badtr['final_sum'].sum()
        badusers = badtr['user_id'].nunique()

        # ------- Цифровые показатели ----------
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего отклоненных транзакций: **{allbad}**") 
            with col2:
                container = st.container(border=True)
                container.write(f"Пользователей, получивших отказ: **{badusers:.0f}**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Потери на комиссии: **{badcom:_.0f} р**".replace('_', ' ')) 



        # ------- Диаграммы ----------
        cols = st.columns(2, border=True)
        with cols[0]:
            dd = badtr.groupby('pay_result', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            badresult = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='Кол-во транзакций'),
                y=alt.Y('pay_result:N', sort='-x', title='Причины'),
                color=alt.value('#eb606c'),
            ).properties(
                width=600, height=400,
                title="Наиболее частые причины отказа"                
            )
            st.write(badresult)

        with cols[1]:
            dd = badtr.groupby('pay_system', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bad_pay_system = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='Кол-во транзакций'),
                y=alt.Y('pay_system:N', sort='-x', title='Платежные системы'),
                color=alt.value('#506788'),
            ).properties(
                width=600, height=400,
                title="Отказавшие платежные системы"                    
            )
            st.write(bad_pay_system)



        cols = st.columns(2, border=True)
        with cols[0]:
            dd = badtr.groupby('pay_bank', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bad_bank = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='Кол-во транзакций'),
                y=alt.Y('pay_bank:N', sort='-x', title='Банки'),
                color=alt.value('#f2bc62'),
            ).properties(
                width=600, height=400,
                title="Отказавшие банки"                   
            )
            st.write(bad_bank)

        with cols[1]:
            dd = badtr.groupby('pay_bank_country', as_index=False)['tr_id'].count().sort_values(by='tr_id', ascending=False).head(20)
            bad_country = alt.Chart(dd).mark_bar().encode(
                x=alt.X('tr_id', title='Кол-во транзакций'),
                y=alt.Y('pay_bank_country:N', sort='-x', title='Страны'),
                color=alt.value('#a1c5c5'),
            ).properties(
                width=600, height=400,
                title="Страны отказавших банков"   
            )

            st.write(bad_country)

# ----------------- Подвал дашборда ---------------------              
sg_lib.footer()