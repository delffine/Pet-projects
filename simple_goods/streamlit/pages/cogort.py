import streamlit as st
import pandas as pd
import calendar
import altair as alt
import sg_lib
    
#---------------------------------------------------------------    
#----------- Треугольная табилца динамики когорт ---------------    
#---------------------------------------------------------------      
def corogt_alt(dd, xcol, ycol, valcol, pr=0):
    #-----------------------------------------------    
    #dd - входная таблица когорт
    #xcol - колонка по горизонтали (когорта)
    #ycol - колонка по вертикали (месяц жизни)
    #valcol - колонка целевой переменной
    #pr - колво знаков после запятой
    #-----------------------------------------------
    base = alt.Chart(dd).encode(
        x=alt.X(xcol, title='Когорта', sort='-x', axis=alt.Axis(labelAngle=0)),
        y=alt.Y(ycol, title='Месяц жизни'),
        tooltip=alt.Text(valcol+':Q', format=f'.{pr}f')
        ).properties(
        width=600, height=400,
        )    
    
    heatmap = base.mark_rect().encode(
    alt.Color(valcol+':Q')
        .scale(scheme="redyellowgreen")
        .legend(None)
    )
    if (pr==0) & (dd[valcol].mean() < 3): pr=2
    text = base.mark_text(baseline="middle").encode(
        text=alt.Text(valcol+':Q', format=f'.{pr}f'),
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
    
    st.header('Когортный анализ')
    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min <= tr_date <= @date_max')
    #client_table = client_table.query('@date_min < first_date < @date_max')
    client_table = sg_lib.get_client_table(data)    
    dd = data.groupby(['user_id']).agg({'oper_sum' : 'sum', 'tr_date' : 'nunique'})
    bigpayers = dd.query('tr_date == 1 & oper_sum > 25000').sort_values(by = 'oper_sum', ascending = False)
   
    col = st.columns(4)
    with col[0]:
        month_horizont = int(data['month_ago'].max())
        
        cogort_gorizont = st.number_input('Горизонт анализа', value=month_horizont, min_value=3, max_value=month_horizont)
        
        
        #max_month = int(data['tr_month'].max())
        #ch_dynamika = pd.DataFrame([])
        #for c in range(max_month - cogort_gorizont+1, max_month+1):
        #    ch = set(client_table.query('first_month == @c and not user_id.isin(@bigpayers)').index)
        #    dd = data.query('user_id.isin(@ch)').groupby('tr_month', as_index = False)\
        #                .agg({'tr_id' : 'count', 'user_id' : 'nunique', 'oper_sum' : 'sum'})
        #    dd = dd.rename(columns = {'tr_id' : 'tr_count', 'user_id' : 'user_count'})
        #   dd['ch'] = c
        #   dd['ch_name'] = f'{calendar.month_abbr[c]}'
        #    dd['avg_sum'] = dd['oper_sum'] / dd['tr_count']    
        #    dd['m_live'] = dd['tr_month'] - c + 1
        #    dd['ltv'] = dd['oper_sum'].cumsum() / len(ch)
        #    dd['ltv_m'] = dd['oper_sum'].cumsum() / (len(ch) * dd['m_live'])
        #    dd['rr'] = dd['user_count'] / len(ch)
        #    dd['cr'] = dd['user_count'] / dd['user_count'].shift(1)
        #    ch_dynamika = pd.concat([ch_dynamika, dd])
        #ch_dynamika = ch_dynamika.reset_index(drop=True)
    
    ch_dynamika = pd.DataFrame([])
    #month_horizont = data['month_ago'].max()
    for c in range(1, cogort_gorizont+1):

        ch = set(client_table.query('month_ago == @c and not user_id.isin(@bigpayers)').index)
        dd = data.query('user_id.isin(@ch)').groupby('month_ago', as_index = False)\
                    .agg({'tr_id' : 'count', 'user_id' : 'nunique', 'oper_sum' : 'sum'})
        dd = dd.rename(columns = {'tr_id' : 'tr_count', 'user_id' : 'user_count'}).sort_values(by='month_ago', ascending=False)
        
        dd['ch'] = f'-{c}мес'
        dd['m_live'] = dd['month_ago'].max() - dd['month_ago'].astype('int') + 1
        dd['m_live'] = dd['m_live'].astype('int')
        dd['ltv'] = round(dd['oper_sum'].cumsum() / len(ch),2)
        dd['ltv_m'] = round(dd['oper_sum'].cumsum() / (len(ch) * dd['m_live']), 2)
        dd['rr'] = round(dd['user_count'] / len(ch), 2)
        dd['cr'] = round(dd['user_count'] / dd['user_count'].shift(1), 2)
        dd['avg_sum'] = round(dd['oper_sum'] / dd['tr_count'], 2)
        ch_dynamika = pd.concat([ch_dynamika, dd])
            
    ch_dynamika = ch_dynamika.sort_values(by=['ch', 'm_live']).reset_index(drop=True)
      
    
    
    par_name = ["Количество транзакций", "Количество донаторов", "Средний чек",
            "LTV", "LTV в месяц", "Коэффициент удержания","Коэффициент оттока" , 'Таблица когорт']
    par_col = ['tr_count', 'user_count', 'avg_sum', 'ltv', 'ltv_m', 'rr', 'cr', 'table']
    par_len = len(par_col)
 
    tab = st.tabs(par_name)
    
    for i in range(par_len):
        prbar.progress( (i / par_len), text='Вычисляю ' + par_name[i])   
        with tab[i]:
            st.header(par_name[i])
            if par_col[i] != 'table':
                col1, col2 = st.columns(2, border=True)
                with col1: 
                    st.text('Тепловая карта')
                    corogt_alt(ch_dynamika, 'ch:O', 'm_live:O', par_col[i])
                with col2: 
                    st.text('Динамика когорт')
                    dd = ch_dynamika.pivot(index='m_live', columns='ch', values=par_col[i])
                    st.line_chart(dd, x_label = 'Месяц жизни', y_label = par_name[i])            
            else:    
              
                st.data_editor(ch_dynamika[['ch', 'm_live', 'tr_count', 'user_count', 'avg_sum', 'ltv', 'ltv_m', 'rr', 'cr']],
                #   column_config={
                #       "ch": st.column_config.TextColumn("Когорта"),
                #       "m_live": st.column_config.NumberColumn("Месяц жизни"),
                #       "tr_count": st.column_config.NumberColumn("Колво транзакции"),
                #       "user_count": st.column_config.NumberColumn("Колво донаторов"),
                #       "avg_sum": st.column_config.NumberColumn("Средний чек"),
                #       "ltv": st.column_config.NumberColumn("LTV"),
                #       "rfm_users": st.column_config.NumberColumn("LTV в месяц"),
                #   },
                   use_container_width=True,
                   hide_index=True,
                   )
       
 
            
prbar.empty()

st.warning('* В когортном анализе не учитываются плательщики, которые сделали разовые транзакции >25 тысяч рублей\n* Месяц = 30 дней, отсчет идет от максимальной даты транзакции')

# ----------------- Подвал дашборда ---------------------          
sg_lib.footer()
