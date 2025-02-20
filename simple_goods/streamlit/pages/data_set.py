import streamlit as st
import pandas as pd
import datetime
import os
import sg_lib


def load_rawdata():
    rawdt = pd.DataFrame([])
    
    app_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
    path = os.path.dirname(app_dir.rstrip('/')) + '/data/'
    
    pv = 0
    all = 0
    l = 0
    prbar = st.progress(0, text=f'Начинаю загрузку данны из {path}')

    for ff in os.listdir(path):
        if ff.split('.')[1] == 'xls':
            prbar.progress(pv, f'Загрузка из файла {ff}')
            dd = pd.read_excel(path + ff)
            dd['file'] = ff
            l = len(dd)
            all = all + l
            rawdt = pd.concat([rawdt, dd])
            pv +=5
            prbar.progress(pv, f'Загрузка {l} строк данных из файла {ff}')
    
    #Проверяем дубликаты в колючевых колонках - номер транзакции
    dub_tr_id = rawdt['Номер'].duplicated().sum()
    #если есть дубликаты (скорее всего экспортировались одинаковые файлы) - удаляем дублирвоанные строчки
    if dub_tr_id > 0: rawdt = rawdt.drop_duplicates(subset='Номер').reset_index(drop=True)
    
    #удаляем колонки, в которых нет значений
    na_col = []
    for i in range(0, len(rawdt.count())):
        if rawdt.count()[i] == 0: na_col.append(rawdt.count().index[i])
    rawdt = rawdt.drop(na_col, axis = 1)
    pv +=10
    prbar.progress(pv, 'Удаляем колонки, в которых нет значений либо одно')

    #Удаляем колонки с одним уникальным значением
    na_col = []
    for col in rawdt.columns:
        if rawdt[col].nunique() == 1: na_col.append(col)
    rawdt = rawdt.drop(na_col, axis = 1)

    #Наложений нет - можно их объединить
    rawdt['Статус'] = rawdt['Статус'].fillna('')
    rawdt['Статус операции'] = rawdt['Статус операции'].fillna('')
    rawdt['Статус операции'] = rawdt['Статус операции'] + rawdt['Статус']

    #Наложений нет - можно их объединить
    rawdt['ID плательщика'] = rawdt['ID плательщика'].fillna('')
    rawdt['Плательщик'] = rawdt['Плательщик'].fillna('')
    rawdt['user_mail'] = rawdt['Плательщик'] + rawdt['ID плательщика']
    pv +=10
    prbar.progress(pv, 'Объединяем одинаковые по смыслу колонки')
 
    #Создаем словарь псевдоним / почта
    user_dic = {}
    i = 0
    for u in rawdt['user_mail'].unique():
        if str(u) == u :
            i +=1
            user_dic[u] = f'user_{i:04.0f}'
    #замена индификатора пользователей по словарю
    rawdt['user_id'] = rawdt['user_mail'].replace(user_dic)
    pv +=10
    prbar.progress(pv, 'Замена индификатора пользователей по словарю')

    #Создаем новые результирующие / преобразованные колонки
    rawdt['status'] = rawdt['Статус операции'].replace({'Completed' : 'Завершена', 'Declined' : 'Отклонена'} )
    rawdt['purpose'] = rawdt['Назначение платежа'].str.lower().str.replace('&quot;' , '"')
    rawdt['Тип'] = rawdt['Тип'].replace('Оплата', 'Покупка')
    rawdt['date'] = pd.to_datetime(rawdt['Дата и время'], format = '%Y-%m-%d %H:%M:$S', errors = 'coerce')

    #заменяем пропуски в назначении и типе платежа
    rawdt['purpose'] = rawdt['purpose'].fillna('Не указано')
    
    #колонки с днем, неделью и месяцем транзакции
    rawdt['tr_date'] = rawdt['date'].dt.date
    rawdt['tr_week'] = rawdt['date'].dt.isocalendar().week
    rawdt['tr_month'] = rawdt['date'].dt.month
    
    maxdate = rawdt['date'].max()
    rawdt['days_ago'] = maxdate - rawdt['date']
    rawdt['days_ago'] = rawdt['days_ago'].dt.days
    rawdt['month_ago'] = rawdt['days_ago'] // 30 + 1


    pv +=10
    prbar.progress(pv, 'Создаем новые результирующие / преобразованные колонки')
    
    #Удаляем бесполезные колонки
    #na_col = ['Срок действия' , 'Эмитент' , 'Карта' , 'Страна эмитента карты',
    #          'Public ID' , 'Код' ,'RRN', 'Код авторизации', 'Способ оплаты',
    #          'Платежная система', 'Валюта операции', 'Примечание',
    #          'Статус', 'Статус операции',
    #          'ID плательщика', 'Плательщик', 'user_mail',
    #          'Назначение платежа',
    #          'Дата и время', 'Дата возмещения', 'Дата/время создания']
    #rawdt = rawdt.drop(na_col, axis = 1)
    pv +=10
    prbar.progress(pv, 'Удаляем бесполезные колонки')

    #Для дальнейшего анализа берем только данные с завершенными операциями
    #data = rawdt.query('status == "Завершена"').copy()
    data = rawdt.copy()
    data = data.reset_index(drop = True)

    pv +=10
    prbar.progress(pv, 'Переименование колонок к python виду')              
    data = data.rename(columns = {'Номер' : 'tr_id',
                      'Тип' : 'type',
                      'Сумма операции' : 'oper_sum',
                      'Сумма комиссии' : 'oper_com',
                      'Сумма возмещения' : 'final_sum',
                      'Дата возмещения' : 'final_date',
                      '% комиссии' : 'com_perc',
                      'Платежная система' : 'pay_system', 
                      'Эмитент' : 'pay_bank',
                      'Страна эмитента карты' : 'pay_bank_country',
                      'Примечание' : 'pay_result',                       
                      'Номер заказа' : 'order_id',
                      'Подписка' : 'subscr',
                      'Страна' : 'country',
                      'Город' : 'city',

                      }
           )
           
    prbar.progress(100, 'Загрузка данных завершена')      
    st.success(f'Всего загружено **{all}** строк данных.\nПосле обработки для дальнейшего анализа отобрано **{len(data)}** строк данных.')
    
   
    st.text(f'Сохраняю в CSV формате')
    data[['tr_id', 'date', 'user_id', 'user_mail', 'oper_sum', 'final_sum', 'final_date',
            'order_id', 'type',  'purpose', 'status', 
            'subscr', 'city', 'country', 
            'pay_system', 'pay_bank', 'pay_bank_country', 'pay_result', 
            'tr_date', 'tr_month', 'tr_week', 'days_ago', 'month_ago', 'file']].to_csv(path+'sg_data.csv', index=False)
    prbar.empty()
    return data


    
#---------------------------------------------------------------
#------------------- Шапка с меню датасетов --------------------
#---------------------------------------------------------------      
sg_lib.header()

#---------------------------------------------------------------
#------------------------ Загрукза датасетов -------------------
#--------------------------------------------------------------- 
data = sg_lib.loaddata()

#---------------------------------------------------------------
# ----------------- Основной блок башборда ---------------------          
#---------------------------------------------------------------
mainblok = st.container()
with mainblok:
    st.header('Загруженные данные')
    try:
        app_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
        path = os.path.dirname(app_dir.rstrip('/')) + '/data/'
        modification_time = os.path.getmtime(path+'sg_data.csv')
        last_modified = (pd.to_datetime(modification_time, unit='s') + datetime.timedelta(hours=4)).strftime('%Y.%m.%d %H:%M:%S')
        st.info(f'Всего **{len(data)}** строк, aктуальность локального датасета **{last_modified}**')
    except:
        st.error(f'Нет локального файла CSV с данными!')
            
    st.text('Пример данных')
    st.dataframe(data.sample(10))

    col1, col2, col3 = st.columns(3)
    with col1:
        uploaded_files = st.file_uploader("Загрузить исходные данные", type='xls', accept_multiple_files = True)
        fc = len(uploaded_files)
        i = 0    
        if fc > 0:
            prbar = st.progress(0, '')
            app_dir = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
            data_dir = os.path.dirname(app_dir.rstrip('/')) + '/data/'

            for uploaded_file in uploaded_files:
                if not os.path.isdir(data_dir):
                    os.mkdir(data_dir)
                    
                file_path = data_dir+uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                if os.path.exists(file_path): 
                    prbar.progress((i / fc), f'Файл {uploaded_file.name} загружен!')
                else:
                    st.text(f'Файл {uploaded_file.name} НЕ загружен!')
                i +=1
            prbar.empty()
            if i == fc: 
                st.success(f'{i} файлов загружено!\nМожно пересоздавать локальный датасет')
            else:  
                st.error(f'НЕ все файлы загружены')  
    with col3:        
        if st.button('Пересоздать локальный датасет', type="primary"):
            load_rawdata()
            
# ----------------- Подвал дашборда ---------------------  
sg_lib.footer()