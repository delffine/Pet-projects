import streamlit as st
import pandas as pd
import os
import datetime
import calendar
import numpy as np
import altair as alt


#----- Стандартные цвета ------
tab_blue = '#1f77b4'
tab_orange = '#ff7f0e'
tab_green = '#2ca02c'
tab_red = '#d62728'
tab_purple = '#9467bd'
tab_brown = '#8c564b'
tab_pink = '#e377c2'
tab_gray = '#7f7f7f'
tab_olive = '#bcbd22'
tab_cyan = '#17becf'
# -------------------------------


def header():
    st.set_page_config(
    layout='wide',
    page_title='Дашборд АНО «Простые вещи»',
    initial_sidebar_state = 'collapsed',
    menu_items={
        'Основные показатели': 'sg_main.py',
        'Пользователи': "users.py",
        'Платежи': "orders.py"
    }
    )
#    st.cache_resource.clear()

#    py_pages = {
#        "Разделы": [
#            st.Page("sg_main.py", title="Основные показатели"),
#            st.Page("pages/users.py", title="Пользователи"),
#            st.Page("pages/orders.py", title="Платежи"),
#            st.Page("pages/rfm.py", title="RFM анализ"),
#            st.Page("pages/cogort.py", title="Когортный анализ"),
#            st.Page("pages/data_set.py", title="Данные"),
#        ],  
#    }
#    st.navigation(py_pages)
#    pg = st.navigation(py_pages)
#    pg.run()
    
    
    st.header('Аналитическая панель инклюзивных мастерских «Простые вещи»')    
    header = st.container(border=True)
    with header:
        menu = ['Основные показатели', 'Пользователи', 'Платежи', 'RFM анализ', 'Когортный анализ']
        script = ['sg_main.py', 'pages/users.py', 'pages/orders.py', 'pages/rfm.py', 'pages/cogort.py']
        len_menu = len(menu)
        mm = st.columns(len_menu)
        for i in range(0, len_menu):
            with mm[i]:
                #st.page_link(script[i], label=menu[i], use_container_width=True)                
                if st.button(menu[i], type="primary", use_container_width=True):
                    st.switch_page(script[i])


    return            
                
def footer():
    footer = st.container(border=True)
    with footer:
        f1, f2 = st.columns(2)
        with f1:
            st.page_link("pages/data_set.py", label="Данные")
        with f2:

            st.text('Создал Суетов Антон =)')
        



    

def loaddata():
    #path = 'data/sg_data.csv'
    #data = pd.read_csv('data/sg_data.csv')

    app_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
    data_path = app_dir + '/data/sg_data.csv'
    
    try:
        data = pd.read_csv(data_path)
    except:
        #data = pd.read_csv('data/sg_data.csv')
        #st.markdown(f'<p style="background-color:#FF0000;color:#FFFFFF;padding:5px;">Нет локальных данных! Читаю данные с Гугл диска!</p>', unsafe_allow_html=True)
        st.warning('Нет локальных данных! Читаю данные с Гугл диска!')
        url='https://drive.google.com/file/d/19IKilgchEDr-Qk2TJzv-0CRA9Snx3sN6/view?usp=drive_link'
        url='https://drive.google.com/uc?id=' + url.split('/')[-2]
        data = pd.read_csv(url)

    data['date'] = pd.to_datetime(data['date'])

    return data


def get_client_table(data, r1=30, r2=90, f1=0.99, f2=2, m1=400, m2=1400):

    dd = data.groupby(['user_id']).agg({'oper_sum' : 'sum', 'tr_date' : 'nunique'})
    bigpayers = dd.query('tr_date == 1 & oper_sum > 25000').sort_values(by = 'oper_sum', ascending = False)
    
    client_table = data.query('not user_id.isin(@bigpayers.index)').groupby('user_id').agg({'user_mail' : 'first', 'tr_id' : 'count', 'oper_sum' : 'sum', 'date' : ['min', 'max']})
    client_table.columns = ['user_mail', 'oper_count', 'oper_sum', 'first_date', 'last_date']
    client_table['last_date'] = pd.to_datetime(client_table['last_date'])
    client_table['first_date'] = pd.to_datetime(client_table['first_date'])
    
    client_table['day_on'] = client_table['last_date'] - client_table['first_date']
    client_table['day_on'] = client_table['day_on'].dt.days

    client_table['first_month'] = pd.DatetimeIndex(client_table['first_date']).month
    client_table['month_on'] = 1 + client_table['day_on'] / 30
    client_table['oper_frec'] = client_table['oper_count'] / client_table['month_on']

    maxdate = data.query('date.notna()')['date'].max()
    client_table['day_last'] = client_table['last_date'].apply(lambda x: pd.to_datetime(maxdate) - x)
    client_table['day_last'] = client_table['day_last'].dt.days    
    
    client_table['R'] = client_table['day_last'].apply(lambda x: '1' if x < r1 else ('2' if x < r2 else '3'))
    client_table['F'] = client_table['oper_frec'].apply(lambda x: '1' if x > f2 else ('2' if x > f1 else '3'))
    client_table['M'] = client_table['oper_sum'].apply(lambda x: '1' if x > m2 else ('2' if x > m1 else '3'))
    client_table['RFM'] = client_table['R'] + client_table['F'] + client_table['M']
    
    return client_table

    
def corogt_alt(dd, xcol, ycol, valcol, pr=0):
    base = alt.Chart(dd).encode(
        x=alt.Y(xcol, title='Когорта', sort=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y(ycol, sort='y', title='Месяц жизни'),
        tooltip=alt.Text(valcol, format=f'.{pr}f')
        ).properties(
        width=600, height=400,
        )    
    
    heatmap = base.mark_rect().encode(
    alt.Color(valcol)
        .scale(scheme="redyellowgreen")
        .legend(None)
    )

    text = base.mark_text(baseline="middle").encode(
        #text=valcol,
        text=alt.Text(valcol, format=f'.{pr}f'),
        color=alt.value("white"),
    )
    st.write(heatmap + text)
    return      
    
def rfn_alt(dd, valcol):
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
