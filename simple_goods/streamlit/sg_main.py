import streamlit as st
import pandas as pd
import sg_lib


#---------------------------------------------------------------
#------------------- Шапка с меню датасетов -------------------
#---------------------------------------------------------------          
sg_lib.header()

#---------------------------------------------------------------
#------------------------ Загрукза датасетов -------------------
#---------------------------------------------------------------          
data = sg_lib.loaddata()
#берем только завершенный транзакции
data = data.query('status == "Завершена"').reset_index(drop=False)

#---------------------------------------------------------------
# ----------------- Основной блок башборда ---------------------          
#---------------------------------------------------------------
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

    data = data.query('@date_min <= tr_date <= @date_max')

    # ------- Сумарные значения ----------    
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

        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Всего пользователей: **{allusers}**")
            with col2:
                container = st.container(border=True)
                container.write(f"Всего транзакций: **{alltr}**")        
            with col3:
                container = st.container(border=True)
                container.write(f"Общая сумма транзакций: **{allsum:_} р**".replace('_', ' '))

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи нарастанием**')
                st.line_chart(day_dynamik['cumuser'], color='#506788', x_label = '', y_label = '')         
                
            with col2:
                st.markdown('**Сумма транзакций нарастанием**')
                st.line_chart(day_dynamik['cumsum'], color='#eb606c', x_label = '', y_label = '')


    # ------- Среднемесячные значения ----------
    month_dynamik = data.groupby('tr_month').agg({'tr_date' : 'first', 'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
    month_dynamik['cumsum'] = month_dynamik['oper_sum'].cumsum()
    month_dynamik['cumclient'] = month_dynamik['user_id'].cumsum()
    month_dynamik['cumtr'] = month_dynamik['tr_id'].cumsum()    
    
    users_month = month_dynamik['user_id'].mean()
    tr_month = month_dynamik['tr_id'].mean()
    sum_month = month_dynamik['oper_sum'].mean()

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
                container.write(f"Среднее колво транзакций в месяц: **{tr_month:.0f}**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Средняя сумма транзакций в месяц: **{sum_month:_.0f}** р.".replace('_', ' '))  

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи по месяцам**')
                st.line_chart(month_dynamik, y='user_id', x='tr_date', color='#506788', x_label = '', y_label = '')

            with col2:
                st.markdown('**Суммы транзакции по месяцам**')
                st.line_chart(month_dynamik, y='oper_sum', x='tr_date', color='#eb606c', x_label = '', y_label = '')

    # ------- Среднедневные значения ----------                 
    daysum = day_dynamik['oper_sum'].mean()
    daytr = day_dynamik['tr_id'].mean()
    dayuser = day_dynamik['user_id'].mean()
        
    with tab3:
        prbar.progress(90, text='Ежедневные значения')        
        row = st.container()
        with row:    
            col1, col2, col3 = st.columns(3)
            with col1:
                container = st.container(border=True)
                container.write(f"Среднее колво пользователей в день: **{dayuser:.0f}**")
            with col2:
                container = st.container(border=True)
                container.write(f"Среднее колво транзакций в день: **{daytr:.0f}**") 
            with col3:
                container = st.container(border=True)
                container.write(f"Средняя сумма транзакций в день: **{daysum:_.0f}** р.".replace('_', ' '))              

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи по дням**')
                st.line_chart(day_dynamik['user_id'], color='#506788', x_label = '', y_label = '')      

            with col2:
                st.markdown('**Суммы транзакции по дням**')
                st.line_chart(day_dynamik['oper_sum'], color='#eb606c', x_label = '', y_label = '')      
                
    prbar.empty()


# ----------------- Подвал дашборда ---------------------          
sg_lib.footer()