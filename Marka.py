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

hesabat_aylar = ['Yanvar','Fevral','Mart','Aprel','May','İyun', 'İyul', 'Avqust']
markalar_mallar_sutunlar = ['ANA_QRUP',	'ALT_QRUP',	'MAL_QRUP', 'STOK_AD']
#Sehifenin nastroykasi
st.set_page_config(
    page_title='FAB MARKALAR',
    page_icon='logo.png',
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# FAB Markalar \n Bu hesabat FAB şirkətlər qrupu üçün hazırlanmışdır."
    }
)

#Excel melumati oxuyuruq
@st.cache_data
def load_data():
    data = pd.read_excel('BazarlamaData.xlsx')
    markalar_mallar = pd.read_excel('MarkalarMallar.xlsx')
    return data, markalar_mallar

#Melumat yenilemek ucun knopka
res_button = st.sidebar.button(':red[🗘 Məlumatları Yenilə]')
if res_button:
    st.cache_data.clear()
with st.spinner('Məlumatlar yüklənir...'):
    data, markalar_mallar = load_data()

#Musteri adi ve stok adi drop edirik
data = data.drop(['C_AD','S_AD'], axis=1)

#sidebarda istifade etmek ucun listler yaradiriq
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
    hesabat_sutunlar = []
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
    value=(hesabat_aylar[len(hesabat_aylar)//2], hesabat_aylar[-1]),
)


#sidebara gore melumatlari filterletirik
if SELECT_REGION == 'Bütün regionlar üzrə':
    region_select_data = data.drop(['GROUP'], axis=1).groupby(['C_KOD','S_KOD'], as_index=False).sum().reset_index()
else:
    region_select_data = data[(data['GROUP']==SELECT_REGION)]
    region_select_data = region_select_data.drop(['GROUP'], axis=1)

if SELECT_MARKA == 'Bütün markalar':
    select_marka_mallar = markalar_mallar
else:
    select_marka_mallar = markalar_mallar[(markalar_mallar['MARKA']==SELECT_MARKA)]


#secilmis aylari sutunlamaq
start_index = hesabat_aylar.index(SELECT_AY_BAS)
end_index = hesabat_aylar.index(SELECT_AY_SON)
SELECT_AYLAR = hesabat_aylar[start_index:end_index + 1]


#sidebara gore secilen mallarin excelini yaradiqi
region_marka_merge_data = pd.merge(select_marka_mallar, region_select_data,
                                   left_on='STOK_KOD', right_on='S_KOD', how='left')
select_marka_data = region_marka_merge_data[['MARKA','C_KOD']+hesabat_sutunlar+SELECT_AYLAR]
select_marka_data[SELECT_AYLAR] = select_marka_data[SELECT_AYLAR].applymap(lambda x: np.nan if pd.isna(x) or x <= 0 else x)
select_marka_data_sum = select_marka_data.groupby(['MARKA','C_KOD']+hesabat_sutunlar, as_index=False)[SELECT_AYLAR].count()
select_marka_data_sum[SELECT_AYLAR] = select_marka_data_sum[SELECT_AYLAR].applymap(lambda x: np.nan if pd.isna(x) or x <= 0 else x)
select_marka_data_count = select_marka_data_sum.groupby(['MARKA']+hesabat_sutunlar, as_index=False)[SELECT_AYLAR].count()

#son hesabat cedveli yaranir
hesabat_table = select_marka_data_count
#indexi 1den basladiriq
hesabat_table.index = np.arange(1, len(hesabat_table)+1)

#cedvelde numeric columlar heatmap ucun
numeric_columns = hesabat_table.select_dtypes(include=[float, int]).columns

# Cedvelin reqemlerini formatini duzeltmek ucun
def accounting_format(x):
    if x == 0:
        return '0'
    else:
        return f'{x:,.0f}'.replace(',', ' ')
styled_hesabat_table = hesabat_table.style.format({ay: accounting_format for ay in SELECT_AYLAR})

# Heatmap yaratmaq
def color_cells(val):
    if not isinstance(val, (int, float)):
        return ''
    
    # Get the min and max values for the entire DataFrame
    min_val = hesabat_table[numeric_columns].min().min()
    max_val = hesabat_table[numeric_columns].max().max()
    
    # Normalize value between 0 and 1
    norm_val = (val - min_val) / (max_val - min_val) if max_val != min_val else 0
    
    # Choose color based on the normalized value
    if norm_val < 0.33:  # Lower third
        return f'background-color: rgba(255,165,0, {norm_val + 0.33})'  # Light red
    elif 0.33 <= norm_val <= 0.66:  # Middle third
        return f'background-color: rgba(255,140,0, {norm_val})'  # Yellow
    else:  # Upper third
        return f'background-color: rgba(255,69,0, {norm_val})'  # Green

styled_hesabat_table = styled_hesabat_table.applymap(color_cells, subset=numeric_columns)

#Sehifenin adini tablari duzeldirik
st.header(f'{SELECT_REGION} - {SELECT_MARKA}', divider='rainbow', anchor=False)

st.table(styled_hesabat_table)

css_page = """
<style>

    th {
       color: black;
       font-weight: bold;
    }
        
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