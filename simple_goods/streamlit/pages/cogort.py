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
    
    
    st.header('Когортный анализ')
    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min < tr_date < @date_max')
    client_table = client_table.query('@date_min < first_date < @date_max')
    
    #data['maxdate'] = data['tr_date'].max() - data['tr_date']
    #data['maxdate'] = pd.to_timedelta(data['maxdate']).dt.days
    #data['horizon_month'] = data['maxdate'] // 30
    #hormax = data['horizon_month'].max()

    dd = data.groupby(['user_id']).agg({'oper_sum' : 'sum', 'tr_date' : 'nunique'})
    bigpayers = dd.query('tr_date == 1 & oper_sum > 25000').sort_values(by = 'oper_sum', ascending = False)

    
    col = st.columns(4)
    with col[0]:
        cogort_gorizont = st.number_input('Горизонт анализа', value=7, min_value=3, max_value=7)
        max_month = int(data['tr_month'].max())
    

    ch_dynamika = pd.DataFrame([])
    for c in range(max_month - cogort_gorizont+1, max_month+1):
        ch = set(client_table.query('first_month == @c and not user_id.isin(@bigpayers)').index)
        dd = data.query('user_id.isin(@ch)').groupby('tr_month', as_index = False)\
                    .agg({'tr_id' : 'count', 'user_id' : 'nunique', 'oper_sum' : 'sum'})
        dd = dd.rename(columns = {'tr_id' : 'tr_count', 'user_id' : 'user_count'})
        dd['ch'] = c
        dd['ch_name'] = f'{calendar.month_abbr[c]}'
        dd['avg_sum'] = dd['oper_sum'] / dd['tr_count']    
        dd['m_live'] = dd['tr_month'] - c + 1
        dd['ltv'] = dd['oper_sum'].cumsum() / len(ch)
        dd['ltv_m'] = dd['oper_sum'].cumsum() / (len(ch) * dd['m_live'])
        dd['rr'] = dd['user_count'] / len(ch)
        dd['cr'] = dd['user_count'] / dd['user_count'].shift(1)
        ch_dynamika = pd.concat([ch_dynamika, dd])

    ch_dynamika = ch_dynamika.reset_index(drop=True)
    
    par_name = ["Количество платежей", "Количество пользователей", "Средний чек",
            "LTV", "LTV в месяц", "Коэффициент удержания","Коэффициент оттока" ]
    par_col = ['tr_count', 'user_count', 'avg_sum', 'ltv', 'ltv_m', 'rr', 'cr']
    par_len = len(par_col)
 
    tab = st.tabs(par_name)
    
    for i in range(par_len):
        prbar.progress( (i / par_len), text='Вычисляю ' + par_name[i])   
        with tab[i]:
            st.header(par_name[i])
            col1, col2 = st.columns(2, border=True)
            with col1: 
                st.text('Табличный вид')
                sg_lib.corogt_alt(ch_dynamika, 'ch_name:O', 'm_live:O', par_col[i]+':Q', pr=2)
               
            with col2: 
                st.text('Динамика когорт')
                dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values=par_col[i])
                st.line_chart(dd, x_label = 'Месяц жизни', y_label = par_name[i])            
        

prbar.empty()
            
st.warning('* В когортном анализе не учитываются плательщики, которые сделали разовые платежи >25 тысяч рублей')
            
sg_lib.footer()
        
        