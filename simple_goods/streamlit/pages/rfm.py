import streamlit as st
import pandas as pd
import io
import altair as alt
import sg_lib


#---------------------------------------------------------------    
#------------------- Матрица RFM анализа -----------------------    
#---------------------------------------------------------------     
def rfm_alt(dd, valcol):
    #-----------------------------------------------    
    #dd - входная RFM таблица
    #valcol - колонка целевой переменной
    #-----------------------------------------------
    
    base = alt.Chart(dd).encode(
    x=alt.X('M:O', title='M', sort=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y('RF:O', title='R-F', sort=None),
    tooltip=alt.Text(valcol, format=f'.0f')
    ).properties(
        width=600, height=400,
    )

    heatmap = base.mark_rect(color='red').encode(
        alt.Color(valcol)
            .scale(scheme="redyellowgreen")
            .legend(None)
    )

    text = base.mark_text(baseline="middle").encode(
        text=valcol,
        color=alt.value("white"),
    )

    st.write(heatmap + text)
    return   
    

#---------------------------------------------------------------
#------------------- Шапка с меню датасетов --------------------
#--------------------------------------------------------------- 
sg_lib.header()

#---------------------------------------------------------------
#------------------------ Загрукза датасетов -------------------
#---------------------------------------------------------------
data = sg_lib.loaddata()
data = data.query('status == "Завершена"').reset_index(drop=False)


#---------------------------------------------------------------
# ----------------- Основной блок башборда ---------------------          
#---------------------------------------------------------------
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

    data = data.query('@date_min <= tr_date <= @date_max')


    rfm_filtr = st.container(border=True)
    with rfm_filtr:
        col = st.columns(3)
        with col[0]:
            lastdate_range = st.slider("Границы рангов дней с последнего действия", 10, 180, (30, 90))
        with col[1]:
            freq_range = st.slider("Границы рангов частоты транзакций", 0.5, 5.0, (0.99, 2.0))
        with col[2]:
            sum_range = st.slider("Границы рангов сумм транзакций", 100, 5000, (400, 1400))
    
    client_table = sg_lib.get_client_table(data, 
            r1=lastdate_range[0], r2=lastdate_range[1], 
            f1=freq_range[0], f2=freq_range[1],            
            m1=sum_range[0], m2=sum_range[1])

    #--------------------------------------------------------
    #Построение RFM таблицы по заданным границам рангов
    #Ранги 1 - отлично, 2 - хорошо, 3 - плохо
    #--------------------------------------------------------
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
        st.text('Количество донаторов')
        rfm_alt(rfm_table, 'rfm_users:Q')
    prbar.progress(40, text='')        
    with col2:
        st.text('Сумма транзакций')
        rfm_alt(rfm_table, 'rfm_sum:Q')

    prbar.progress(60, text='')

    col1, col2 = st.columns(2, border=True)
    with col1:
        st.text('Количество транзакций')
        rfm_alt(rfm_table, 'rfm_tr:Q')
    prbar.progress(80, text='')        
    with col2:
        st.text('Средний чек')
        rfm_alt(rfm_table, 'avg_sum:Q')
        
    st.header('RFM таблица')
    st.data_editor(rfm_table[['RFM', 'R', 'F', 'M', 'rfm_users', 'rfm_tr', 'rfm_sum', 'avg_sum']],
       column_config={
           "R": st.column_config.TextColumn("Давность"),
           "F": st.column_config.TextColumn("Частота"),
           "M": st.column_config.TextColumn("Сумма"),
           "rfm_users": st.column_config.NumberColumn("Колво донаторов"),
           "rfm_tr": st.column_config.NumberColumn("Колво транзакций"),
           "rfm_sum": st.column_config.NumberColumn("Общая сумма"),
           "avg_sum": st.column_config.NumberColumn("Средний донат"),
       },
       use_container_width=True,
       hide_index=True,
       )
       
    prbar.progress(100, text='')   

    st.warning('* Ранги RFM: 1 - отлично, 2 - хорошо, 3 - плохо')

    download_rfm = client_table.reset_index()[['RFM', 'user_id', 'user_mail', 'first_date', 'last_date', 'oper_count', 'oper_sum']].copy()
    download_rfm['first_date'] = download_rfm['first_date'].dt.date
    download_rfm['last_date'] = download_rfm['last_date'].dt.date
    download_rfm.columns = ['RFM', 'id пользователя', 'mail пользователя', 'Первая дата', 'Последняя датa', 'Колво транзакций', 'Сумма донатов']
    buffer = io.BytesIO()
    download_rfm.to_excel(buffer, index=False)
    st.download_button('Скачать RFM таблицу донаторов', buffer, file_name='sg_users_rfm.xlsx', type="primary")
   
    prbar.empty()   

    
# ----------------- Подвал дашборда ---------------------  
sg_lib.footer()