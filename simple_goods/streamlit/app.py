import streamlit as st

#---------------------------------------------------------------    
#---- Инициализация приложения, формирование меню --------------    
#---------------------------------------------------------------  

py_pages = {
    "Меню": [
        st.Page("sg_main.py", title="Основные показатели"),
        st.Page("pages/users.py", title="Пользователи"),
        st.Page("pages/orders.py", title="Платежи"),
        st.Page("pages/rfm.py", title="RFM анализ"),
        st.Page("pages/cogort.py", title="Когортный анализ"),
        st.Page("pages/data_set.py", title="Данные"),
        st.Page("pages/about.py", title="О дашборде"),
        ],  
}
st.navigation(py_pages)
pg = st.navigation(py_pages)
pg.run()
