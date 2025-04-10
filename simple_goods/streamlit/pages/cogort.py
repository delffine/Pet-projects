import streamlit as st
import pandas as pd
import calendar
import altair as alt
import sg_lib
    
#---------------------------------------------------------------    
#----------- Треугольная табилца динамики когорт ---------------    
#---------------------------------------------------------------      
def corogt_alt(dd, xcol, ycol, valcol, pr=0, ch_sort='30d'):
    #-----------------------------------------------    
    #dd - входная таблица когорт
    #xcol - колонка по горизонтали (когорта)
    #ycol - колонка по вертикали (месяц жизни)
    #valcol - колонка целевой переменной
    #pr - колво знаков после запятой
    #ch_sort - для сортировки вывода когорты в хитмапе
    #-----------------------------------------------
    if (pr==0) & (dd[valcol].mean() < 3): pr=2
    sh_sort = '-x'
    if ch_div == '30d': sh_sort ='-x'
    if ch_div == '1mon': sh_sort ='x'
    
    base = alt.Chart(dd).encode(
        x=alt.X(xcol, title='Когорта', sort=sh_sort, axis=alt.Axis(labelAngle=0)),
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
    
    
    
    col = st.columns(3)
    with col[0]:
        st.header('Когортный анализ')
    with col[2]:
        option = st.selectbox("Пользователи", ("Все", "Подписчики", "Покупатели", "Донаторы"))
        gst = 'byer != "ВСЕ"'
        if option == "Все": gst = 'byer != "ВСЕ"'
        if option == "Подписчики": gst = 'subscr =="Подписчик"'
        if option == "Покупатели": gst = 'byer == "Покупатель"'
        if option == "Донаторы": gst = 'byer != "Покупатель" & subscr !="Подписчик"'
        
    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min <= tr_date <= @date_max')
    dd = data.groupby(['user_id']).agg({'oper_sum' : 'sum', 'tr_date' : 'nunique'})
    #bigpayers = dd.query('tr_date == 1 & oper_sum > 25000').sort_values(by = 'oper_sum', ascending = False)
    bigpayers = data.query('oper_sum > 25000')['user_id']

    client_table = sg_lib.get_client_table(data)
    client_table  = client_table.query(gst).reset_index(drop=True)    
    
    col = st.columns(4)
    with col[0]:
        option = st.selectbox("Деление на когорты по", ("Календарный месяц", "30 дней"))
        ch_div = '1mon'
        month_horizont = int(data['tr_month'].max())
        if option == "Календарый месяц": 
            ch_div = '1mon'
            month_horizont = int(data['tr_month'].max())
        if option == "30 дней": 
            ch_div = '30d'
            month_horizont = int(data['month_ago'].max())

    with col[3]:   
        cogort_gorizont = st.number_input('Горизонт анализа', value=month_horizont, min_value=3, max_value=month_horizont)
    
    #--------- рассчеты показателей для когорт по 30 дней -----------    
    if ch_div == '30d': 
        ch30_dynamika = pd.DataFrame([])
        for c in range(1, cogort_gorizont+1):

            ch = set(client_table.query('month_ago == @c and not user_id.isin(@bigpayers)')['user_id'])
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
            ch30_dynamika = pd.concat([ch30_dynamika, dd])
                
        ch_dynamika = ch30_dynamika.sort_values(by=['ch', 'm_live']).reset_index(drop=True)


    #--------- рассчеты показателей для календарных когорт -----------
    if ch_div == '1mon':   
        calendar_ch_dynamika = pd.DataFrame([])
        for c in range(month_horizont - cogort_gorizont+1, month_horizont+1):
            ch = set(client_table.query('first_month == @c and not user_id.isin(@bigpayers)')['user_id'])
            dd = data.query('user_id.isin(@ch)').groupby('tr_month', as_index = False)\
                        .agg({'tr_id' : 'count', 'user_id' : 'nunique', 'oper_sum' : 'sum'})
            dd = dd.rename(columns = {'tr_id' : 'tr_count', 'user_id' : 'user_count'})

            dd['ch'] = f'{c}_{calendar.month_abbr[c]}'
            dd['m_live'] = dd['tr_month'] - c + 1
            dd['ltv'] = dd['oper_sum'].cumsum() / len(ch)
            dd['ltv_m'] = dd['oper_sum'].cumsum() / (len(ch) * dd['m_live'])
            dd['rr'] = dd['user_count'] / len(ch)
            dd['cr'] = dd['user_count'] / dd['user_count'].shift(1)
            dd['avg_sum'] = dd['oper_sum'] / dd['tr_count']
            calendar_ch_dynamika = pd.concat([calendar_ch_dynamika, dd])

        ch_dynamika = calendar_ch_dynamika.reset_index(drop=True)

    
    par_name = ["Количество транзакций", "Активные пользователи", "Сумма транзакций", "Средний чек",
            "LTV", "LTV в месяц", "Коэффициент удержания","Коэффициент оттока" , 'Таблица когорт']
    par_col = ['tr_count', 'user_count', 'oper_sum', 'avg_sum', 'ltv', 'ltv_m', 'rr', 'cr', 'table']
    par_len = len(par_col)
 
    tab = st.tabs(par_name)
    
    for i in range(par_len):
        prbar.progress( (i / par_len), text='Вычисляю ' + par_name[i])   
        with tab[i]:
            st.header(par_name[i])
            if par_col[i] != 'table':
                col1, col2 = st.columns(2, border=True)
                with col1: 
                    st.markdown('**Тепловая карта**')
                    corogt_alt(ch_dynamika, 'ch:O', 'm_live:O', par_col[i], ch_sort=ch_div)
                with col2: 
                    st.markdown('**Динамика когорт**')
                    dd = ch_dynamika.pivot(index='m_live', columns='ch', values=par_col[i])
                    st.line_chart(dd, x_label = 'Месяц жизни', y_label = par_name[i])            
            else:    
                
                if ch_div == '1mon': sorttt = [True, True] 
                else: sorttt = [False, True]
               
                st.data_editor(ch_dynamika[['ch', 'm_live', 'tr_count', 'user_count', 'oper_sum', 'avg_sum', 'ltv', 'ltv_m', 'rr', 'cr']].sort_values(by=['ch', 'm_live'], ascending=sorttt),
                   column_config={
                       "ch": st.column_config.TextColumn("Когорта"),
                       "m_live": st.column_config.NumberColumn("Мес.жизни"),
                       "tr_count": st.column_config.NumberColumn("Транз"),
                       "user_count": st.column_config.NumberColumn("Акт.польз"),
                       "oper_sum": st.column_config.NumberColumn("Сум.транз", format="%.0f руб."),
                       "avg_sum": st.column_config.NumberColumn("Ср.чек", format="%.0f руб."),
                       "ltv": st.column_config.NumberColumn("LTV", format="%.0f руб."),
                       "ltv_m": st.column_config.NumberColumn("LTV/мес", format="%.0f руб."),
                       "rr": st.column_config.NumberColumn("Удержание", format="%.2f"),
                       "cr": st.column_config.NumberColumn("Отток", format="%.2f"),


#                       "ch": st.column_config.TextColumn("Когорта"),
#                       "m_live": st.column_config.NumberColumn("Мес.жизни"),
#                       "tr_count": st.column_config.ProgressColumn("Кол-во транзакций", min_value=0, max_value=ch_dynamika['tr_count'].max(),),
#                       "user_count": st.column_config.ProgressColumn("Акт. пользователей", min_value=0, max_value=ch_dynamika['user_count'].max(), format="%f"),
#                       "oper_sum": st.column_config.ProgressColumn("Сумма транзакций", min_value=0, max_value=ch_dynamika['oper_sum'].max(), format="%f руб."),
#                       "avg_sum": st.column_config.ProgressColumn("Средний чек", min_value=0, max_value=ch_dynamika['avg_sum'].max(), format="%f руб."),
#                       "ltv": st.column_config.ProgressColumn("LTV", min_value=0, max_value=ch_dynamika['ltv'].max(), format="%f руб."),
#                       "ltv_m": st.column_config.ProgressColumn("LTV/мес", min_value=0, max_value=ch_dynamika['ltv_m'].max(), format="%f руб."),
#                       "rr": st.column_config.ProgressColumn("Удержание", min_value=0, max_value=ch_dynamika['rr'].max(), format="%.2f"),
#                       "cr": st.column_config.ProgressColumn("Отток", min_value=0, max_value=ch_dynamika['cr'].max(), format="%.2f"),
#
                       },
                   use_container_width=True,
                   hide_index=True,
                   )
       
           
prbar.empty()

st.warning('* В когортном анализе не учитываются плательщики, которые сделали разовые транзакции >25 тысяч рублей')

# ----------------- Подвал дашборда ---------------------          
sg_lib.footer()