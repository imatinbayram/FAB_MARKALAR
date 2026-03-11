import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import requests

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

css_header = """
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />
"""

st.markdown(css_header, unsafe_allow_html=True)

bazarlama_login = {
'Admin' : 'fab',
'BAKI 1' : 'FAB10',
'BAKI 2' : 'FAB90',
'BAKI 3' : 'FAB99',
'BAKI 4' : 'FAB77',
'BAKI 5' : 'FAB01',
'GENCE1' : 'FAB20',
'GENCE2' : 'FAB22',
'GOYCAY' : 'FAB23',
'QUBA' : 'FAB40',
'LENKERAN' : 'FAB42',
'SABIRABAD' : 'FAB54',
'SEKI' : 'FAB55'
}


if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['login_region'] = ''


def check_password():
    with st.form(key='login_form'):
        username_region = st.selectbox('Region', sorted(bazarlama_login.keys()), label_visibility='visible')
        password = st.text_input('Şifrə', type="password")
        submit_button = st.form_submit_button('Daxil ol')
        
        if submit_button:
            if username_region in bazarlama_login.keys() and password == bazarlama_login[username_region]:
                st.session_state['logged_in'] = True
                st.session_state['login_region'] = username_region
                st.success("Giriş edilir...")
                st.rerun()
            else:
                st.error("Şifrə düzgün deyil!")           

if not st.session_state['logged_in']:
    check_password()
    st.stop()

# =============================================================================
# if st.sidebar.button(':blue[:arrow_left: ÇIXIŞ]'):
#     st.session_state['logged_in'] = False
#     st.session_state['login_region'] = ''
#     st.rerun()
# =============================================================================

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

hesabat_aylar = ['2024_01',	'2024_02',	'2024_03',	'2024_04',	'2024_05',	'2024_06',
                 '2024_07',	'2024_08',	'2024_09',	'2024_10',	'2024_11',	'2024_12',
                 '2025_01', '2025_02', '2025_03', '2025_04', '2025_05', '2025_06',
                 '2025_07','2025_08','2025_09','2025_10', '2025_11', '2025_12',
                 '2026_01', '2026_02']
markalar_mallar_sutunlar = ['ANA_QRUP',	'ALT_QRUP',	'MAL_QRUP', 'STOK_AD']

SELECT_ANA_QRUP = list()
SELECT_ALT_QRUP = list()
SELECT_MAL_QRUP = list()
SELECT_STOK_QRUP = list()

def sql_segment():
    query = f"""
    SELECT [ContragentCode] [C_KOD] ,[ContragentMainContragentSegment] [C_SEGMENT] FROM [BazarlamaHesabatDB].[dbo].[ContragentSegmentView]
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    html_json = {"Query": query, "Kod": st.secrets["Kod"]}

    response = requests.get(url, json=html_json, headers=headers, verify=False)
    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            return pd.DataFrame(api_data["Data"])
        else:
            st.warning(f"API Error (): {api_data['Message']}")
            return pd.DataFrame()
    else:
        st.error(f"HTTP Error (): {response.status_code} {response.text}")
        return pd.DataFrame()
        
sql_segment = sql_segment()

#Excel melumati oxuyuruq
@st.cache_data
def load_data():
    data = pd.read_excel('BazarlamaData.xlsx')
    markalar_mallar = pd.read_excel('MarkalarMallar.xlsx')
    cariler = pd.read_excel('Cariler.xlsx')
    segment = pd.read_excel('Segment.xlsx')
    return data, markalar_mallar, cariler, segment

#Melumat yenilemek ucun knopka
st.sidebar.text('Son yenilənmə: 28.02.2026')
res_button = st.sidebar.button(':red[🗘 Məlumatları Yenilə]')
if res_button:
    st.cache_data.clear()
with st.spinner('Məlumatlar yüklənir...'):
    data, markalar_mallar, cariler, segment = load_data()

#Musteri adi ve stok adi drop edirik
data = data.drop(['C_AD','S_AD'], axis=1)

#sidebarda istifade etmek ucun listler yaradiriq
bazarlama_qol_list = markalar_mallar['QOL'].unique()
marka_qrup_list = markalar_mallar['MARKA'].unique()

#sidebar secimleri
SELECT_AY_BAS, SELECT_AY_SON  = st.sidebar.select_slider(
    'Tarix',
    options=hesabat_aylar,
    #value=(hesabat_aylar[len(hesabat_aylar)//2], hesabat_aylar[-1]),
    value=(hesabat_aylar[-3], hesabat_aylar[-1]),
    label_visibility='collapsed'
)

if st.session_state['login_region'] == 'Admin':
    
    #Bildiriş göndəririk
    #st.info('SAFVIDA, ANDELI markası əlavə olundu. Sol tərəfdən :red[🗘 Məlumatları Yenilə] klik edib yeniləyə bilərsiz.', icon="ℹ️")
    
    SELECT_REGION = st.sidebar.selectbox('Region',['Bütün regionlar üzrə'] + sorted(bazarlama_region),
                                        index=0,
                                        placeholder = 'Region',
                                        label_visibility='collapsed')
else:
    SELECT_REGION = st.sidebar.selectbox('Region',[st.session_state['login_region']],
                                        disabled=True,
                                        placeholder = 'Region',
                                        index=0,
                                        label_visibility='collapsed')

SELECT_SEGMENT = st.sidebar.checkbox("Seqmentləri göstər")

SELECT_MARKA = st.sidebar.selectbox('Marka', ['Bütün markalar'] + sorted(marka_qrup_list),
                                    placeholder = 'Marka',
                                    index=0,
                                    label_visibility='collapsed', )

#sidebara gore melumatlari filterletirik
if SELECT_REGION == 'Bütün regionlar üzrə':
    region_select_data = data.drop(['GROUP'], axis=1).groupby(['C_KOD','S_KOD'], as_index=False).sum().reset_index()
    region_select_cariler = cariler
else:
    region_select_data = data[(data['GROUP']==SELECT_REGION)]
    region_select_data = region_select_data.drop(['GROUP'], axis=1)
    region_select_cariler = cariler[(cariler['GROUP']==SELECT_REGION)]

if SELECT_SEGMENT:
    hesabat_sutunlar = ['C_SEGMENT']
else:
    hesabat_sutunlar = []
    
if SELECT_MARKA == 'Bütün markalar':
    select_marka_mallar_marka = markalar_mallar
else:
    select_marka_mallar_marka = markalar_mallar[(markalar_mallar['MARKA']==SELECT_MARKA)]
    #elave melumatin gosterilmesi ucun
    hesabat_sutunlar_melumat = st.sidebar.multiselect(
        "Məlumatlar",
        markalar_mallar_sutunlar,
        placeholder = 'Əlavə məlumatlar',
        label_visibility='collapsed'
    )
    hesabat_sutunlar.extend(hesabat_sutunlar_melumat)
    
    if 'ANA_QRUP' in hesabat_sutunlar:
        ana_qrup_list = select_marka_mallar_marka['ANA_QRUP'].unique()
        SELECT_ANA_QRUP = st.sidebar.multiselect(
            "Ana qrup",
            sorted(ana_qrup_list),
            placeholder = 'Ana qrup',
            label_visibility='collapsed'
        )
    else:
        SELECT_ANA_QRUP = list()
    
    if 'ALT_QRUP' in hesabat_sutunlar:
        alt_qrup_list = select_marka_mallar_marka[
            select_marka_mallar_marka['ANA_QRUP'].isin(SELECT_ANA_QRUP if SELECT_ANA_QRUP else select_marka_mallar_marka['ANA_QRUP'])
            ]['ALT_QRUP'].unique()
        SELECT_ALT_QRUP = st.sidebar.multiselect(
            "Alt qrup",
            sorted(alt_qrup_list),
            placeholder = 'Alt qrup',
            label_visibility='collapsed'
        )
    else:
        SELECT_ALT_QRUP = list()
        
    if 'MAL_QRUP' in hesabat_sutunlar:
        mal_qrup_list = select_marka_mallar_marka[
            select_marka_mallar_marka['ANA_QRUP'].isin(SELECT_ANA_QRUP if SELECT_ANA_QRUP else select_marka_mallar_marka['ANA_QRUP'])
            &
            select_marka_mallar_marka['ALT_QRUP'].isin(SELECT_ALT_QRUP if SELECT_ALT_QRUP else select_marka_mallar_marka['ALT_QRUP'])
            ]['MAL_QRUP'].unique()
        SELECT_MAL_QRUP = st.sidebar.multiselect(
            "Mal qrup",
            sorted(mal_qrup_list),
            placeholder = 'Mal qrup',
            label_visibility='collapsed'
        )
    else:
        SELECT_MAL_QRUP = list()

    if 'STOK_AD' in hesabat_sutunlar:
        stok_qrup_list = select_marka_mallar_marka[
            select_marka_mallar_marka['ANA_QRUP'].isin(SELECT_ANA_QRUP if SELECT_ANA_QRUP else select_marka_mallar_marka['ANA_QRUP'])
            &
            select_marka_mallar_marka['ALT_QRUP'].isin(SELECT_ALT_QRUP if SELECT_ALT_QRUP else select_marka_mallar_marka['ALT_QRUP'])
            &
            select_marka_mallar_marka['MAL_QRUP'].isin(SELECT_MAL_QRUP if SELECT_MAL_QRUP else select_marka_mallar_marka['MAL_QRUP'])
            ]['STOK_AD'].unique()
        SELECT_STOK_QRUP = st.sidebar.multiselect(
            "Stok",
            sorted(stok_qrup_list),
            placeholder = 'Stok',
            label_visibility='collapsed'
        )
    else:
        SELECT_STOK_QRUP = list()

select_marka_mallar_filter = select_marka_mallar_marka[
    select_marka_mallar_marka['ANA_QRUP'].isin(SELECT_ANA_QRUP if SELECT_ANA_QRUP else select_marka_mallar_marka['ANA_QRUP'])
    &
    select_marka_mallar_marka['ALT_QRUP'].isin(SELECT_ALT_QRUP if SELECT_ALT_QRUP else select_marka_mallar_marka['ALT_QRUP'])
    &
    select_marka_mallar_marka['MAL_QRUP'].isin(SELECT_MAL_QRUP if SELECT_MAL_QRUP else select_marka_mallar_marka['MAL_QRUP'])
    &
    select_marka_mallar_marka['STOK_AD'].isin(SELECT_STOK_QRUP if SELECT_STOK_QRUP else select_marka_mallar_marka['STOK_AD'])
    ]

select_marka_mallar = select_marka_mallar_filter

#secilmis aylari sutunlamaq
start_index = hesabat_aylar.index(SELECT_AY_BAS)
end_index = hesabat_aylar.index(SELECT_AY_SON)
SELECT_AYLAR = hesabat_aylar[start_index:end_index + 1]

#sidebara gore secilen mallarin excelini yaradiqi
region_marka_merge_data_segment = pd.merge(select_marka_mallar, region_select_data,
                                   left_on='STOK_KOD', right_on='S_KOD', how='left')
region_marka_merge_data = pd.merge(region_marka_merge_data_segment, sql_segment,
                                   left_on='C_KOD', right_on='C_KOD', how='left').fillna({'C_SEGMENT': 'D Asagi'})

select_marka_data = region_marka_merge_data[['MARKA','C_KOD']+hesabat_sutunlar+SELECT_AYLAR]
select_marka_data['CƏMİ'] = select_marka_data[SELECT_AYLAR].sum(axis=1)
SELECT_AYLAR = SELECT_AYLAR + ['CƏMİ']
select_marka_data[SELECT_AYLAR] = select_marka_data[SELECT_AYLAR].applymap(lambda x: np.nan if pd.isna(x) or x <= 0 else x)
select_marka_data_sum = select_marka_data.groupby(['MARKA','C_KOD']+hesabat_sutunlar, as_index=False, dropna=False)[SELECT_AYLAR].count()
select_marka_data_sum_mebleg = select_marka_data.groupby(['MARKA','C_KOD']+hesabat_sutunlar, as_index=False, dropna=False)[SELECT_AYLAR].sum()
select_marka_data_sum[SELECT_AYLAR] = select_marka_data_sum[SELECT_AYLAR].applymap(lambda x: np.nan if pd.isna(x) or x <= 0 else x)
select_marka_data_count = select_marka_data_sum.groupby(['MARKA']+hesabat_sutunlar, as_index=False, dropna=False)[SELECT_AYLAR].count()
select_marka_data_count_mebleg = select_marka_data_sum_mebleg.groupby(['MARKA']+hesabat_sutunlar, as_index=False, dropna=False)[SELECT_AYLAR].sum()

#cariler uzre cixaris
select_marka_data_count_mebleg_cari = select_marka_data_sum_mebleg.groupby(['MARKA','C_KOD']+hesabat_sutunlar, as_index=False)[SELECT_AYLAR].sum()
select_marka_data_count_mebleg_cari = select_marka_data_count_mebleg_cari[select_marka_data_count_mebleg_cari['CƏMİ']!=0]
#cari adini getirmer
select_marka_data_final_cari_ad = pd.merge(select_marka_data_count_mebleg_cari, region_select_cariler[['C_KOD','C_AD']], 
                                   on='C_KOD', how='left')
select_marka_data_final_cari = select_marka_data_final_cari_ad

#son cari cedvelinin yaranması
hesabat_table_cari = select_marka_data_final_cari
reordered_columns_cariler = ['MARKA','C_KOD','C_AD']+hesabat_sutunlar+SELECT_AYLAR
hesabat_table_cari = hesabat_table_cari[reordered_columns_cariler]
hesabat_table_cari.index = np.arange(1, len(hesabat_table_cari)+1)
satis_cemi = hesabat_table_cari['CƏMİ'].sum()
satis_sayi = hesabat_table_cari['C_KOD'].nunique()

#satilmiyan carileri secmek
satilan_cariler = hesabat_table_cari['C_KOD'].unique().tolist()
satilmayan_cariler = region_select_cariler[~region_select_cariler['C_KOD'].isin(satilan_cariler)]
satilmayan_cariler.index = np.arange(1, len(satilmayan_cariler)+1)
satilamayan_sayi = satilmayan_cariler['C_KOD'].nunique()
    
if 'STOK_AD' in select_marka_data_count.columns:
    select_marka_data_count_qiymet = pd.merge(select_marka_data_count, markalar_mallar[['STOK_AD','QİYMƏT']], 
                                       on='STOK_AD', how='left')
    select_marka_data_count_qiymet = select_marka_data_count_qiymet[['MARKA']+hesabat_sutunlar+['QİYMƏT']+SELECT_AYLAR]
    select_marka_data_count_qiymet['QİYMƏT'] = select_marka_data_count_qiymet['QİYMƏT'].astype(str)+' ₼'
    select_marka_data_final = pd.merge(select_marka_data_count_qiymet, select_marka_data_count_mebleg,
                                      on=['MARKA']+hesabat_sutunlar, how='left', suffixes=('', '_₼')) 
    hesabat_sutunlar = hesabat_sutunlar + ['QİYMƏT']
else:
    select_marka_data_count_qiymet = select_marka_data_count
    
    select_marka_data_final = pd.merge(select_marka_data_count_qiymet, select_marka_data_count_mebleg,
                                      on=['MARKA']+hesabat_sutunlar, how='left', suffixes=('', '_₼'))  

#select_marka_data_final = select_marka_data_count_qiymet

#son hesabat cedveli yaranir
hesabat_table = select_marka_data_final
#indexi 1den basladiriq
hesabat_table.index = np.arange(1, len(hesabat_table)+1)

#cedvelde numeric columlar heatmap ucun
numeric_columns = SELECT_AYLAR.copy()
numeric_columns.remove('CƏMİ')
SELECT_AYLAR_FORMAT = []
for ay in [ay+'_₼' for ay in SELECT_AYLAR]:
    SELECT_AYLAR_FORMAT.append(ay)

aylar_order = merged_list = [item for pair in zip(SELECT_AYLAR, SELECT_AYLAR_FORMAT) for item in pair]

reordered_columns = ['MARKA']+hesabat_sutunlar+aylar_order
hesabat_table = hesabat_table[reordered_columns]

# Cedvelin reqemlerini formatini duzeltmek ucun
def accounting_format(x):
    if x == 0:
        return ' '
    else:
        return f'{x:,.0f} ₼'.replace(',', ' ')
    
styled_hesabat_table = hesabat_table.style.format({ay: accounting_format for ay in SELECT_AYLAR_FORMAT})

styled_hesabat_table_cari = hesabat_table_cari.style.format({ay: accounting_format for ay in SELECT_AYLAR})

# Heatmap yaratmaq
def color_cells(val):
    if not isinstance(val, (int, float)):
        return ''
    
    # aylar uzre min max musteri sayi
    min_val = hesabat_table[numeric_columns].min().min()
    max_val = hesabat_table[numeric_columns].max().max()
    
    # rengin alpha deyerini hesabla
    norm_val = (val - min_val) / (max_val - min_val) if max_val != min_val else 0
    
    # setire ve aylara gore renglendir
    if norm_val < 0.33:  # Asagi
        return f'background-color: rgba(165,42,42, {norm_val + 0.11})'  # Asagi
    elif 0.33 <= norm_val <= 0.66:  # Orta
        return f'background-color: rgba(178,34,34, {norm_val})'  # Orta
    else:  # Yuksek
        return f'background-color: rgba(128,0,0, {norm_val})'  # Yuksek

styled_hesabat_table = styled_hesabat_table.applymap(color_cells, subset=numeric_columns)

# CEMİ sutununu qirmizi reng elemek
def highlight_sum_col(val, col_name):
    if col_name == 'CƏMİ':
        return 'background-color: #990000'
    return ''
styled_hesabat_table = styled_hesabat_table.applymap(lambda x: highlight_sum_col(x, 'CƏMİ'), subset=['CƏMİ'])

#Error mesajin qarsisini aliriq
try:
    
    #Sehifenin adini tablari duzeldirik
    st.header(f'{SELECT_REGION} - {SELECT_MARKA}', divider='rainbow', anchor=False)
    
    #Fayli excele yuklemek
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        hesabat_table.to_excel(writer, index=False, sheet_name='Ümumi')
        hesabat_table_cari.to_excel(writer, index=False, sheet_name='Satılan carilər')
        satilmayan_cariler.to_excel(writer, index=False, sheet_name='Satılmayan carilər')
    excel_data = output.getvalue()
    st.download_button(
        label=":green[Cədvəli Excel'ə yüklə] :floppy_disk:",
        data=excel_data,
        file_name=f'{SELECT_REGION} - {SELECT_MARKA}.xlsx',
    )
    
    st.write(f':red[{satis_sayi}] müştəriyə ümumilikdə qaytarma nəzərə alınmadan', f':red[{satis_cemi:,.0f}]'.replace(',', ' '),' :red[AZN] satış olmuşdur.')
    st.table(styled_hesabat_table)
# =============================================================================
#    if show_satilan:
#        with st.expander('Satılan müştərilərin siyahısı'):
#            st.write(f':red[{satis_sayi}] müştəriyə ümumilikdə ', f':red[{satis_cemi:,.0f}]'.replace(',', ' '),' :red[AZN] satış olmuşdur.')
#            st.table(styled_hesabat_table_cari)
# =============================================================================
    with st.expander('Satılmayan müştərilərin siyahısı'):
        st.write(f':red[{satilamayan_sayi}] müştəriyə satış olmamışdır.')
        st.table(satilmayan_cariler)

except:
    st.error('Məlumatlar yenilənmişdir. Zəhmət olmasa sol üstə yerləşən "Məlumatları Yenilə" düyməsinə basın.')
    
    
css_page = """
<style>
    th {
       color: black;
       font-weight: bold;
    }
    
    [data-testid="stToolbarActionButton"] { display: none; }
    [data-testid="stMainMenu"] { display: none; }
    
    [class="viewerBadge_link__qRIco"] { display: none; }

    [data-testid="stElementToolbar"] { display: none; }

    button[title="View fullscreen"] { visibility: hidden; }
</style>
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />
"""


st.markdown(css_page, unsafe_allow_html=True)











