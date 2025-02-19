import streamlit as st
import pandas as pd
import datetime
import calendar
import numpy as np
import altair as alt
import sg_lib
    
#---------------------------------------------------------------
#------------------- Шапка с меню датасетов --------------------
#---------------------------------------------------------------    
sg_lib.header()  

#---------------------------------------------------------------
#------------------------ Загрукза датасетов -------------------
#---------------------------------------------------------------  
data = sg_lib.loaddata()
data = data.query('status == "Завершена"').reset_index(drop=False)
client_table = sg_lib.get_client_table(data)
     
#---------------------------------------------------------------
# ----------------- Основной блок башборда ---------------------          
#---------------------------------------------------------------
mainblok = st.container()
with mainblok:
    prbar = st.progress(0, text='Начинаю вычисления ...')    
    st.header('Донаторы')

    # ----------------- Фильтр по дате  ------------------------ 
    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min < tr_date < @date_max')
    
    # --------------------- Вычисления ------------------------- 
    allusers = data['user_id'].nunique()
    activ_users = len(client_table.query('day_on < 30'))

    subscibers = data.query('subscr.notna()')['user_id'].unique()
    allsub = len(subscibers)

    procsub = 100 * allsub / allusers
    allsubsum = data.query('user_id.isin(@subscibers)')['oper_sum'].sum()

    sub_dynamik = data.query('user_id.isin(@subscibers)').groupby('tr_date').agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    sub_dynamik['cumsum'] = sub_dynamik['oper_sum'].cumsum()
    sub_dynamik['cumuser'] = data.query('user_id.isin(@subscibers)')[['tr_date','user_id']].drop_duplicates(['user_id']).groupby('tr_date').count().cumsum()
    sub_dynamik['cumuser'] = sub_dynamik['cumuser'].ffill()
    
    tab1, tab2 = st.tabs(["Все донаторов", "Подписчики"])
    # ----------------- Все донаторы -------------------------            
    with tab1:
        prbar.progress(30, text='Донаторы...')   

        # ----------------- Все донаторы показатели ------------------  
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего донаторов: **{allusers}**")
            with col2:
                container = st.container(border=True)
                container.write(f"Оформивщих подписку: **{allsub}**")            
            with col3:
                container = st.container(border=True)
                container.write(f"Активные в последние 30 дней: **{activ_users}**")            

        # ----------------- Все донаторы графики ------------------  
        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Донаторы с наибольщими транзакциями**')
                dd = data.groupby('user_id', as_index=False).agg({'oper_sum': 'sum', 'tr_id': 'count'}).sort_values(by='oper_sum', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('user_id', sort=None, title='Донаторы'),
                    x=alt.X('oper_sum', title='Сумма транзакций'),
                    color=alt.value('#506788'),                
                ))

            with col2:
                st.markdown('**Донаторы сделавшие больще всего транзакций**')
                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('user_id', sort='-x', title='Донаторы'),
                    x=alt.X('tr_id', title='Колво транзакций'),
                    color=alt.value('#eb606c'),
                ))      

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**ТОП стран донаторов**')
                dd = data.groupby('country', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('country', sort='-x', title='Страна'),
                    x=alt.X('user_id', title='Колво донаторов'),
                    color=alt.value('#f2bc62'),                
                ))

            with col2:
                st.markdown('**ТОП городов донаторов**')
                dd = data.groupby('city', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('city', sort='-x', title='Город'),
                    x=alt.X('user_id', title='Колво донаторов'),
                    color=alt.value('#a1c5c5'),
                )) 

    # ----------------- Подписчики -------------------------            
    with tab2:
        prbar.progress(60, text='Подписчики')
        # ----------------- Подписчики показатели ------------------         
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
                container.write(f"Сумма транзакций: **{allsubsum:_.0f} р**".replace('_', ' '))            

        # ----------------- Подписчики графики ------------------ 
        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Подписчики нарастанием**')
                st.line_chart(sub_dynamik['cumuser'], color='#506788', x_label = '', y_label = '')         
                
            with col2:
                st.markdown('**Сумма транзакций нарастанием**')
                st.line_chart(sub_dynamik['cumsum'], color='#eb606c', x_label = '', y_label = '')       
    prbar.empty()

    
# ----------------- Подвал дашборда ---------------------  
sg_lib.footer()    