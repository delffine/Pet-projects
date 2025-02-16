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

    dd = data.groupby(['user_id']).agg({'oper_sum' : 'sum', 'tr_date' : 'nunique'})
    bigpayers = dd.query('tr_date == 1 & oper_sum > 25000').sort_values(by = 'oper_sum', ascending = False)

    ch_dynamika = pd.DataFrame([])
    for c in range(1, 8):
        ch = set(client_table.query('first_month == @c and not user_id.isin(@bigpayers)').index)
        dd = data.query('user_id.isin(@ch)').groupby('tr_month', as_index = False)\
                    .agg({'tr_id' : 'count', 'user_id' : 'nunique', 'oper_sum' : 'sum'})
        dd = dd.rename(columns = {'tr_id' : 'tr_count', 'user_id' : 'user_count'})
        dd['ch'] = c
        dd['ch_name'] = f'{calendar.month_abbr[c]}'
        dd['m_live'] = dd['tr_month'] - c + 1
        dd['ltv'] = dd['oper_sum'].cumsum() / len(ch)
        dd['ltv_m'] = dd['oper_sum'].cumsum() / (len(ch) * dd['m_live'])
        dd['rr'] = dd['user_count'] / len(ch)
        dd['cr'] = dd['user_count'] / dd['user_count'].shift(1)
        ch_dynamika = pd.concat([ch_dynamika, dd])

    ch_dynamika = ch_dynamika.reset_index(drop=True)
    
    
    #row = st.container()
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Количество платежей", "Количество донаторов", "LTV", "LTV в месяц", "Коэффициент удержания","Коэффициент оттока" ])
    with tab1:
        st.header('Количество платежей')
        col1, col2 = st.columns(2)
        with col1: 
            st.text('Табличный вид')
            st.pyplot(sg_lib.show_chogort_table_sns(ch_dynamika, col='tr_count'))
        with col2: 
            st.text('Динамика когорт')
            dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values='tr_count')
            st.line_chart(dd, x_label = 'Месяц жизни', y_label = 'Количество платежей')

    #row = st.container()
    with tab2:
        st.header('Количество донаторов')
        col1, col2 = st.columns(2)
        with col1: 
            st.text('Табличный вид')
            st.pyplot(sg_lib.show_chogort_table_sns(ch_dynamika, col='user_count'))
        with col2: 
            st.text('Динамика когорт')
            dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values='user_count')
            st.line_chart(dd, x_label = 'Месяц жизни', y_label = 'Количество платежей')

    #row = st.container()
    with tab3:
        st.header('LTV')
        col1, col2 = st.columns(2)
        with col1: 
            st.text('Табличный вид')
            st.pyplot(sg_lib.show_chogort_table_sns(ch_dynamika, col='ltv'))
        with col2: 
            st.text('Динамика когорт')
            dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values='ltv')
            st.line_chart(dd, x_label = 'Месяц жизни', y_label = 'Количество платежей')

    #row = st.container()
    with tab4:
        st.header('LTV в  месяц')
        col1, col2 = st.columns(2)
        with col1: 
            st.text('Табличный вид')
            st.pyplot(sg_lib.show_chogort_table_sns(ch_dynamika, col='ltv_m'))
        with col2: 
            st.text('Динамика когорт')
            dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values='ltv_m')
            st.line_chart(dd, x_label = 'Месяц жизни', y_label = 'Количество платежей')

    #row = st.container()
    with tab5:
        st.header('Коэффициент удержания')
        col1, col2 = st.columns(2)
        with col1: 
            st.text('Табличный вид')
            st.pyplot(sg_lib.show_chogort_table_sns(ch_dynamika, col='rr', pr=2))
        with col2: 
            st.text('Динамика когорт')
            dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values='rr')
            st.line_chart(dd, x_label = 'Месяц жизни', y_label = 'Количество платежей')

    #row = st.container()
    with tab6:
        st.header('Коэффициент оттока')
        col1, col2 = st.columns(2)
        with col1: 
            st.text('Табличный вид')
            st.pyplot(sg_lib.show_chogort_table_sns(ch_dynamika, col='cr', pr=2))
        with col2: 
            st.text('Динамика когорт')
            dd = ch_dynamika.pivot(index='m_live', columns='ch_name', values='cr')
            st.line_chart(dd, x_label = 'Месяц жизни', y_label = 'Количество платежей')

            
    st.text('* В когортном анализе не учитываются плательщики, которые сделали разовые платежи >25 тысяч рублей')
            
sg_lib.footer()
        
        