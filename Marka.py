import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO


bazarlama_region = [
'BAKI 1',
'BAKI 2',
'BAKI 3',
'BAKI 4',
'BAKI 5',
'GENCE1',
'GENCE2',
'GOYCAY',
'QUBA',
'LENKERAN',
'SABIRABAD',
'SEKI'
]

bazarlama_qol = ['Elektrik']

hesabat_aylar = ['Yanvar','Fevral','Mart','Aprel','May','İyun', 'İyul', 'Avqust']
markalar_mallar_sutunlar = ['ANA_QRUP',	'ALT_QRUP',	'MAL_QRUP', 'STOK_AD']
#Sehifenin nastroykasi
st.set_page_config(
    page_title='FAB MARKALAR',
    page_icon='logo.png',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# FAB Bazarlama \n Bu hesabat FAB şirkətlər qrupunun Bazarlama bölməsi üçün hazırlanmışdır."
    }
)

#Excel melumati oxuyuruq
@st.cache_data
def load_data():
    data = pd.read_excel('MarkalarData.xlsx')
    markalar_mallar = pd.read_excel('MarkalarMallar.xlsx')
    return data, markalar_mallar

#Melumat yenilemek ucun knopka
res_button = st.sidebar.button(':red[🗘 Məlumatları Yenilə]')
if res_button:
    st.cache_data.clear()
with st.spinner('Məlumatlar yüklənir...'):
    data, markalar_mallar = load_data()


bazarlama_qol_list = markalar_mallar['QOL'].unique()
ana_qrup_list = markalar_mallar['ANA_QRUP'].unique()
alt_qrup_list = markalar_mallar['ALT_QRUP'].unique()
mal_qrup_list = markalar_mallar['MAL_QRUP'].unique()
marka_qrup_list = markalar_mallar['MARKA'].unique()


#sidebar secimleri
show_region_check = st.sidebar.toggle("Bütün regionlar üzrə")
if show_region_check:
    SELECT_REGION = 'Bütün regionlar üzrə'
else:
    SELECT_REGION = st.sidebar.selectbox('Region', sorted(bazarlama_region),
                                        label_visibility='visible')
    
show_marka_check = st.sidebar.toggle("Bütün markalar")
if show_marka_check:
    SELECT_MARKA = 'Bütün markalar'
else:
    SELECT_MARKA = st.sidebar.selectbox('Marka', sorted(marka_qrup_list),
                                        label_visibility='visible')

hesabat_sutunlar = st.sidebar.multiselect(
    "Məlumatlar",
    markalar_mallar_sutunlar,
    placeholder = 'Əlavə məlumatlar'
)

SELECT_AY_BAS, SELECT_AY_SON  = st.sidebar.select_slider(
    'Aylar',
    options=hesabat_aylar,
    value=(hesabat_aylar[0], hesabat_aylar[-1]),
)


#sidebara gore melumatlari filterletirik
if SELECT_REGION == 'Bütün regionlar üzrə':
    region_group_data = data.drop(['REGION'], axis=1)
    region_select_data = region_group_data.groupby('STOK_KOD').sum().reset_index()
else:
    region_select_data = data[(data['REGION']==SELECT_REGION)]

if SELECT_MARKA == 'Bütün markalar':
    select_marka_mallar = markalar_mallar
else:
    select_marka_mallar = markalar_mallar[(markalar_mallar['MARKA']==SELECT_MARKA)]


#secilmis aylari sutunlamaq
start_index = hesabat_aylar.index(SELECT_AY_BAS)
end_index = hesabat_aylar.index(SELECT_AY_SON)
SELECT_AYLAR = hesabat_aylar[start_index:end_index + 1]

#sidebara gore secilen mallarin excelini yaradiqi
select_marka_data = pd.merge(select_marka_mallar, region_select_data, on='STOK_KOD', how='left')
select_marka_data.fillna(0, inplace=True)

# Gorsenecek sutunlari yaratmaq
final_sutunlar = ['MARKA']+hesabat_sutunlar+SELECT_AYLAR
select_marka_group_data = select_marka_data[['MARKA']+hesabat_sutunlar+SELECT_AYLAR]
hesabat_table = select_marka_group_data.groupby(['MARKA']+hesabat_sutunlar).sum().reset_index()

hesabat_table.index = np.arange(1, len(hesabat_table)+1)

# Cedvelin reqemlerini formatini duzeltmek ucun
def accounting_format(x):
    if x == 0:
        return ' '
    else:
        return f'{x:,.0f}'.replace(',', ' ')

styled_hesabat_table = hesabat_table.style.format({ay: accounting_format for ay in SELECT_AYLAR})

st.table(styled_hesabat_table)

css_page = """
<style>
    .stSlider [data-testid="stTickBar"] {
        display: none;
    }
    .stSlider label {
        display: block;
        text-align: left;
    }
    
    .stSelectbox label {
        text-align: left;
        display: block;
        width: 100%;
    }

    [data-testid="stHeader"] {
        display: none;
    }
    
    [class="viewerBadge_link__qRIco"] {
        display: none;
    }
    
    [data-testid="stElementToolbar"] {
        display: none;
    }
    
    button[title="View fullscreen"] {
        visibility: hidden;
    }
    
</style>
"""

st.markdown(css_page, unsafe_allow_html=True)