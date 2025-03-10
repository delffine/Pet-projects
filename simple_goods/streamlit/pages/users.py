import streamlit as st
import pandas as pd
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

     
#---------------------------------------------------------------
# ----------------- Основной блок башборда ---------------------          
#---------------------------------------------------------------
mainblok = st.container()
with mainblok:
    prbar = st.progress(0, text='Начинаю вычисления ...')    
    st.header('Пользователи')

    # ----------------- Фильтр по дате  ------------------------ 
    date_filtr = st.container(border=True)
    with date_filtr:
        date_min = pd.to_datetime(data['tr_date']).dt.date.min()
        date_max = pd.to_datetime(data['tr_date']).dt.date.max()
        date_range = st.slider('Фильтр данных по датам', date_min, date_max, (date_min, date_max), key='tr_date_slider')
        date_min = str(date_range[0])
        date_max = str(date_range[1])

    data = data.query('@date_min <= tr_date <= @date_max')
    client_table = sg_lib.get_client_table(data)
    
    
    tab = st.tabs(["Все пользователи", "Подписчики / Покупатели", "Динамика подписок / покупок"])
    # ----------------- Все пользователи -------------------------            
    with tab[0]:
        prbar.progress(20, text='Пользователи...')   

        # --------------------- Вычисления ------------------------- 
        allusers = data['user_id'].nunique()
        activ_users = len(client_table.query('day_last < 30'))
        subscibers = client_table.query('subscr == "Подписчик"')['user_id']
        byers = client_table.query('byer == "Покупатель"')['user_id']
        byers_i_subscr = client_table.query('byer == "Покупатель" & subscr == "Подписчик"')['user_id']
        not_byers_subscr = client_table.query('byer != "Покупатель" & subscr != "Подписчик"')['user_id']
        allsub = len(subscibers)
        allbyers = len(byers)
        all_byers_i_subscr = len(byers_i_subscr)
        all_not_byers_subscr = len(not_byers_subscr)
        
        # ----------------- Все пользователи показатели ------------------  
        row = st.container()
        with row:    
            col = st.columns(4)
            with col[0]:
                container = st.container(border=True)
                container.write(f"Всего пользователей: **{allusers}**")
            with col[1]:
                container = st.container(border=True)
                container.write(f"Оформивших подписку: **{allsub}**")            
            with col[2]:
                container = st.container(border=True)
                container.write(f"Сделавших покупку: **{allbyers}**")            
            with col[3]:
                container = st.container(border=True)
                container.write(f"Активных за 30 дней: **{activ_users}**")   


        # ----------------- Все пользователи графики ------------------  
        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи с наибольшими суммами транзакций**')
                dd = data.groupby('user_id', as_index=False).agg({'oper_sum': 'sum', 'tr_id': 'count'})

                st.write(alt.Chart(dd.sort_values(by='oper_sum', ascending=False).head(10)).mark_bar().encode(
                    y=alt.Y('user_id', sort=None, title='Пользователи'),
                    x=alt.X('oper_sum', title='Сумма транзакций'),
                    color=alt.value('#506788'),                
                ))

            with col2:
                st.markdown('**Пользователи, сделавшие больше всего транзакций**')
                st.write(alt.Chart(dd.sort_values(by='tr_id', ascending=False).head(10)).mark_bar().encode(
                    y=alt.Y('user_id', sort='-x', title='Пользователи'),
                    x=alt.X('tr_id', title='Кол-во транзакций'),
                    color=alt.value('#eb606c'),
                ))


            
        prbar.progress(40, text='Города / страны')
        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**ТОП стран пользователей**')
                dd = data.groupby('country', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('country', sort='-x', title='Страна'),
                    x=alt.X('user_id', title='Кол-во пользователей'),
                    color=alt.value('#f2bc62'),                
                ))

            with col2:
                st.markdown('**ТОП городов пользователей**')
                dd = data.groupby('city', as_index=False)['user_id'].nunique().sort_values(by='user_id', ascending=False).head(10)

                st.write(alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('city', sort='-x', title='Город'),
                    x=alt.X('user_id', title='Кол-во пользователей'),
                    color=alt.value('#a1c5c5'),
                )) 


    
    # ----------------- Подписчики / Покупатели -------------------            
    with tab[1]:
        prbar.progress(60, text='Подписчики / Покупатели')

        # --------------------- Вычисления ------------------------- 
        #procsub = 100 * allsub / allusers
        #allsubsum = data.query('user_id.isin(@subscibers) & type!="Покупка"')['oper_sum'].sum()
    
       
        # ----------------- Подписчики / Покупатели показатели ------------------         
        row = st.container()
        with row:    
            col = st.columns(4)
            with col[0]:
                container = st.container(border=True)
                container.write(f"Подписчиков: **{allsub}**")            
            with col[1]:
                container = st.container(border=True)
                container.write(f"Покупателей: **{allbyers}**")            
            with col[2]:
                container = st.container(border=True)
                container.write(f"Подписчиков & покупателей: **{all_byers_i_subscr}**")            
            with col[3]:
                container = st.container(border=True)
                container.write(f"Донаторы: **{all_not_byers_subscr}**")            


        # ----------------- Подписчики / Покупатели графики ------------------ 

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                sg_colors = ['#eb606c', '#a1c5c5', '#506788', '#f1e7ce', '#42445a', '#e8f3f4',  '#f2bc62', ]
               
                dd = client_table.groupby(['byer', 'subscr'], as_index=False).agg({'user_id' : 'nunique', 'oper_sum' : 'sum', 'oper_count' : 'sum'}).sort_values(by='user_id', ascending=False)
                dd['user'] = dd['byer'] + dd['subscr']
                dd['user'] = dd['user'].replace('--', 'Донатор')
                dd['user'] = dd['user'].str.replace('-', '').str.replace('льПо', 'ль & По')
                dd['user_prec'] = dd['user_id'] / allusers
                
                pie1 = alt.Chart(dd).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field='user_prec', sort='descending', type="quantitative"),
                    color=alt.Color(field="user", type="nominal", title = "Роль"),
                    tooltip=alt.Tooltip(field='user_prec', format = '.2%', title = "Роль")
                ).properties(
                    height=400, width=400,
                    title="Распределение пользователей"
                ).configure_range(
                    category=alt.RangeScheme(sg_colors)
                )
                
                st.write(pie1)

           
            with col2:
                st.markdown('**Пользователи по сумме транзакций**')
                bar = alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('oper_sum',  title='Сумма'),
                    x=alt.X('user', sort='-y', title='', axis=alt.Axis(labelAngle=0)),
                    color=alt.value('#f2bc62'),
                )
                st.write(bar)

            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Пользователи по колву транзакций**')
                bar = alt.Chart(dd).mark_bar().encode(
                    y=alt.Y('oper_count',  title='Кол-во транзакций'),
                    x=alt.X('user', sort='-y', title='', axis=alt.Axis(labelAngle=0)),
                    color=alt.value('#42445a'),
                )
                st.write(bar)
                
            with col2:
                st.markdown('**Баланс**')

                dd = dd[['user', 'user_id', 'oper_sum', 'oper_count']]
                dd.loc[4] = pd.Series(dd.sum(), name='Total')
                dd.loc[4, 'user'] = 'Итого'
                dd.columns =('Роль пользователя', 'Кол-во', 'Сумма', 'Транзакций')
                
                st.data_editor(dd,
                   use_container_width=True,
                   hide_index=True,
                   )

        st.warning('- Подписчики определяются по наличию транзакций с индефикатором подписки\n- Покупатели определяются по наличию транзакций с типом операции "Оплата". (При предобработке переименовывается в "Покупка"')

    #------------------- Динамика подписок / покупок ---------------------- 
    
    with tab[2]:
        prbar.progress(80, text='Данмика подписок / покупок')   

        col = st.columns(4)
        with col[3]:
            option = st.selectbox("Группировка", ("День", "Неделя", "Месяц"))
            grby = 'tr_date'
            if option == "День": grby = 'tr_date'
            if option == "Неделя": grby = 'tr_week'
            if option == "Месяц": grby = 'tr_month'
    

        sub_dynamik = data.query('user_id.isin(@subscibers) & type!="Покупка"').groupby(grby).agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
        sub_dynamik['cumsum'] = sub_dynamik['oper_sum'].cumsum()
        sub_dynamik['cumuser'] = data.query('user_id.isin(@subscibers)')[[grby,'user_id']].drop_duplicates(['user_id']).groupby(grby).count().cumsum()
        sub_dynamik['cumuser'] = sub_dynamik['cumuser'].ffill()

        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Подписчики нарастанием**')
                st.line_chart(sub_dynamik['cumuser'], color='#506788', x_label = '', y_label = '')         
                
            with col2:
                st.markdown('**Сумма транзакций подписок нарастанием**')
                st.line_chart(sub_dynamik['cumsum'], color='#eb606c', x_label = '', y_label = '')                
        
        allbyetr = data.query('type=="Покупка"')['tr_id'].count()
        allbyesum = data.query('type=="Покупка"')['oper_sum'].sum()
        byers_dynamik = data.query('type=="Покупка"').groupby(grby).agg({'tr_id' : 'count', 'oper_sum' : 'sum', 'user_id' : 'nunique'})
        byers_dynamik['cumsum'] = byers_dynamik['oper_sum'].cumsum()
        
        row = st.container()
        with row:    
            col1, col2 = st.columns(2, border=True)
            with col1:
                st.markdown('**Покупки по дням**')
                st.line_chart(byers_dynamik['tr_id'], color='#506788', x_label = '', y_label = '')         
                
            with col2:
                st.markdown('**Сумма транзакций покупок нарастанием**')
                st.line_chart(byers_dynamik['cumsum'], color='#eb606c', x_label = '', y_label = '')  
                
    prbar.empty()

    
# ----------------- Подвал дашборда ---------------------  
sg_lib.footer()    
