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

    rfm_table = client_table.groupby(['R', 'F', 'M'], as_index = False).agg({'RFM' : 'first', 'oper_count' : ['count', 'sum'], 'oper_sum' : 'sum', 'last_date' : 'max'})
    
    rfm_table.columns = ['R', 'F', 'M', 'RFM', 'rfm_users', 'rfm_tr', 'rfm_sum', 'rfm_last_date']
    #st.write(rfm_table)

    st.header('Количество донаторов')
    st.pyplot(sg_lib.show_rfm_table_sns(rfm_table, 'rfm_users'))

    st.subheader('Рекомендации')
    
    frmtop = rfm_table[['RFM', 'rfm_users']].sort_values(by='rfm_users', ascending=False).head(5)
    for frm_code in frmtop['RFM'].tolist():
        if frm_code == '111': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото1 '
        if frm_code == '112': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото1 '
        if frm_code == '121': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото2 '
        if frm_code == '122': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото3 '
        if frm_code == '211': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото4 '
        if frm_code == '212': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото5 '
        if frm_code == '221': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото6 '
        if frm_code == '222': recomed = f'Велика доля клиентов из сегмента {frm_code} Надо делать тото и тото7 '
        st.subheader(f'Велика доля клиентов из сегмента {frm_code}')    
        st.text (recomed)
    
    
    
sg_lib.footer()