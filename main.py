import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud.firestore import Client
import datetime
from datetime import datetime as dt
import pandas as pd
import streamlit.components.v1 as components
from streamlit.components.v1 import html
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import matplotlib.pyplot as plt
import json
from dateutil.relativedelta import relativedelta
from dateutil.tz import *
from zoneinfo import ZoneInfo
from streamlit_login_auth_ui.widgets import __login__

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="days-877ee")
db_lahir = db.collection('lahirs')

hari = dt.now().astimezone()

#lahir = datetime.datetime(1996,9,1, tzinfo=tzlocal())
#rdeltas = relativedelta(hari, lahir)

__login__obj = __login__(auth_token = "courier_auth_token",
                    company_name = "Shims",
                    width = 200, height = 250,
                    logout_button_name = 'Logout', hide_menu_bool = False,
                    hide_footer_bool = False,
                    lottie_url = 'https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json')

LOGGED_IN= __login__obj.build_login_ui()

stream_lahir = list(db_lahir.stream())
list_lahir = list(map(lambda x: x.to_dict(), stream_lahir))
data_lahir = pd.DataFrame(list_lahir)
data_lahir['lahir'] = pd.to_datetime(data_lahir['lahir'])
user_lahir = data_lahir.sort_values(by=['lahir'], ascending=False)

if st.session_state['LOGGED_IN'] == True:
    user_name = __login__obj.cookies['__streamlit_login_signup_ui_username__']
    
    if user_name not in data_lahir['username'].values:     
        #define tanggal user
        st.header(f'Hallo {user_name}, isi tanggal lahir dulu ya 😃')
        with st.form(key='form1', clear_on_submit=True):
            db_lahir = db.collection('lahirs')
            st.write("Kapan kamu lahir? 👶")
            tgl_user = st.date_input('Tanggal Lahir', value=datetime.date(1995,1,1), min_value=datetime.date(1975,1,1), max_value=datetime.date(2010,1,1))
            tgl_user = pd.Timestamp(tgl_user)
            submit_button = st.form_submit_button(label='Kirim')
            if submit_button:
                db_lahir.add({"username": user_name, "lahir": tgl_user})
                st.write('Terimakasih 👍')
                st.write('Logout & Silahkan Login Kembali 🤳🏻')
    
    else:

        # data lahir users
        user_born = data_lahir['lahir'].loc[user_lahir['username'] == user_name]
        lahir = datetime.datetime(1996,9,1, tzinfo=tzlocal())
        uss = pd.to_datetime(user_born)
        dt_tgl = list(uss)[0]
        rdelta = relativedelta(hari, dt_tgl)
        
        #Place Tet into Image
        image = Image.open('frames.png')
        path_font = "Inter-Regular.ttf"

        font = ImageFont.truetype(path_font, 200)
        font1 = ImageFont.truetype(path_font, 65)

        img= ImageDraw.Draw(image)
        img.text((170,314), str(rdelta.years), font=font, fill=(91,112,143))
        img.text((573,304), str(rdelta.months), font=font1, fill=(91,112,143))
        img.text((573,420), str(rdelta.days), font=font1, fill=(91,112,143))
        img.text((573,539), str(rdelta.hours + 7), font=font1, fill=(91,112,143))

        st.image(image)

        with st.form(key='form1', clear_on_submit=True):
            
            col1 = db.collection(f'{user_name}')
            st.write("Apakah aku puas dengan hari ini 👀?")
            option = st.radio(' ', ('Iya', 'Engga'), horizontal=True)
            cerita = st.text_area(label='Yang aku dapat hari ini 👇', height=300)
            submit_button = st.form_submit_button(label='Kirim')
            if submit_button:
                col1.add({"option": option, "tanggal": hari, "cerita": cerita})
                st.write('Terimakasih 👍')

        try:
            doc = db.collection(f'{user_name}')
            datas = list(doc.stream())
            list_random = list(map(lambda x: x.to_dict(), datas))
            data = pd.DataFrame(list_random)
            data = data.sort_values(by=['tanggal'], ascending=False)
            df = data['option'].value_counts().rename_axis('option').reset_index(name='counts')

            fig1, ax1 = plt.subplots(figsize=(3,3))
            ax1.pie(df.counts, autopct='%1.1f%%', labels = df.option, colors = ['#FF5E63', '#3CC0FE'], startangle=90)

            st.subheader("**Persentase Kepuasan Hidup 😊 😟**")
            st.pyplot(fig1)

            st.subheader('Cerita Harian ✍️')

            for j,k,l in zip(data['cerita'], data['option'], data['tanggal']):
                cerita_list = list(j.split(" "))
                if k == 'Iya':
                    st.info(f'**{l.date()}: {" ".join(cerita_list[:5]).title()}**')
                else:
                    st.error(f'**{l.date()} : {" ".join(cerita_list[:5]).title()}**')
                st.write(j)
        except KeyError:
            print('Isi dulu cerita hari ini')
