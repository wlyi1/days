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

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="days-877ee")

hari = dt.now().astimezone()


lahir = datetime.datetime(1996,9,1, tzinfo=tzlocal())
rdelta = relativedelta(hari, lahir)

#st.title("Aku Telah Hidup")
#st.success(f'**{rdelta.years} Tahun - {rdelta.months} Bulan - {rdelta.days} Hari - {rdelta.hours + 7} Jam**')

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
    
    col1 = db.collection('daily')
    st.write("Apakah aku puas dengan hari ini?")
    option = st.radio(' ', ('Iya', 'Engga'), horizontal=True)
    cerita = st.text_area(label='Yang aku dapat hari ini', height=300)
    submit_button = st.form_submit_button(label='Kirim')
    if submit_button:
        col1.add({"option": option, "tanggal": hari, "cerita": cerita})
        st.write('Terimakasih 👍')


doc = db.collection('daily')
datas = list(doc.stream())
list_random = list(map(lambda x: x.to_dict(), datas))
data = pd.DataFrame(list_random)
data = data.sort_values(by=['tanggal'], ascending=False)
df = data['option'].value_counts().rename_axis('option').reset_index(name='counts')

fig1, ax1 = plt.subplots(figsize=(3,3))
ax1.pie(df.counts, autopct='%1.1f%%', labels = df.option, colors = ['#FF5E63', '#3CC0FE'], startangle=90)

st.subheader("**Kepuasan**")
st.pyplot(fig1)

st.subheader('Ceritanya')

for j,k,l in zip(data['cerita'], data['option'], data['tanggal']):
    cerita_list = list(j.split(" "))
    if k == 'Iya':
        st.info(f'**{l.date()}: {" ".join(cerita_list[:5]).title()}**')
    else:
        st.error(f'**{l.date()} : {" ".join(cerita_list[:5]).title()}**')
    st.write(j)

