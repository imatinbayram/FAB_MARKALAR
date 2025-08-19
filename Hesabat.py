# streamlit_app.py
import streamlit as st
import pandas as pd
import warnings
from datetime import date
import json
import requests

warnings.simplefilter("ignore")

# -----------------------------
# Query helpers
# -----------------------------
def hesabat_satis():
    today = date.today()
    tarix_1 = today.replace(day=1).isoformat()
    tarix_2 = today.isoformat()
    with open("Hesabat - Satis.sql", encoding="utf-8") as f:
        query_text = f.read().lstrip('\ufeff')
    query = f"""
        DECLARE @tarix1 DATE = '{tarix_1}';
        DECLARE @tarix2 DATE = '{tarix_2}';
        {query_text}
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    html_json = {
    "Query": query
    }
    response = requests.get(url, json=html_json, headers=headers, verify=False)

    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            df = api_data["Data"]
        else:
            print("API Error:", api_data["Message"])
    else:
        print("Error:", response.status_code, response.text)
        
    return pd.DataFrame(df)

def hesabat_qirmizi():
    today = date.today()
    tarix_1 = today.replace(day=1).isoformat()
    tarix_2 = today.isoformat()
    with open("Hesabat - Qirmizi.sql", encoding="utf-8") as f:
        query_text = f.read().lstrip('\ufeff')
    query = f"""
        DECLARE @tarix1 DATE = '{tarix_1}';
        DECLARE @tarix2 DATE = '{tarix_2}';
        {query_text}
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    html_json = {
    "Query": query
    }
    response = requests.get(url, json=html_json, headers=headers, verify=False)

    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            df = api_data["Data"]
        else:
            print("API Error:", api_data["Message"])
    else:
        print("Error:", response.status_code, response.text)
        
    return pd.DataFrame(df)

def hesabat_borc():
    today = date.today()
    tarix_1 = today.replace(day=1).isoformat()
    tarix_2 = today.isoformat()
    with open("Hesabat - Borc.sql", encoding="utf-8") as f:
        query_text = f.read().lstrip('\ufeff')
    query = f"""
        DECLARE @tarix1 DATE = '{tarix_1}';
        DECLARE @tarix2 DATE = '{tarix_2}';
        {query_text}
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    html_json = {
    "Query": query
    }
    response = requests.get(url, json=html_json, headers=headers, verify=False)

    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            df = api_data["Data"]
        else:
            print("API Error:", api_data["Message"])
    else:
        print("Error:", response.status_code, response.text)
        
    return pd.DataFrame(df)

def hesabat_sifaris():
    today = date.today()
    tarix_2 = today.isoformat()
    with open("Hesabat - Sifaris.sql", encoding="utf-8") as f:
        query_text = f.read().lstrip('\ufeff')
    query = f"""
        DECLARE @tarix2 DATE = '{tarix_2}';
        {query_text}
    """
    url = "http://81.17.83.210:1999/api/Metin/GetQueryTable"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    html_json = {
    "Query": query
    }
    response = requests.get(url, json=html_json, headers=headers, verify=False)

    if response.status_code == 200:
        api_data = response.json()
        if api_data["Code"] == 0:
            df = api_data["Data"]
        else:
            print("API Error:", api_data["Message"])
    else:
        print("Error:", response.status_code, response.text)
        
    return pd.DataFrame(df)

# -----------------------------
# Formatting helpers
# -----------------------------
BLUE = "#000C7B"

def remove_index_like_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Drop explicit index-like columns if they exist
    cols_to_drop = [c for c in df.columns if str(c).strip().lower() == "index" or str(c).startswith("Unnamed:")]
    return df.drop(columns=cols_to_drop, errors="ignore")

def fmt_space0(x):
    if pd.isna(x):
        return ""
    try:
        return f"{float(x):,.0f}".replace(",", " ")
    except Exception:
        return x

def fmt_icra(x):
    if pd.isna(x):
        return ""
    try:
        return f"{float(x):.2f} %"
    except Exception:
        return x

def style_for_table(df: pd.DataFrame, fmt_map: dict | None = None, total_idx=None):
    # Header style
    header_css = [
        {
            "selector": "thead th",
            "props": [
                ("background-color", BLUE),
                ("color", "white"),
                ("font-weight", "bold"),
                ("text-align", "right"),
            ],
        }
    ]
    styler = df.style.set_table_styles(header_css).hide(axis="index")

    # Per-column formatters (functions or format strings)
    if fmt_map:
        safe_map = {col: fmt for col, fmt in fmt_map.items() if col in df.columns}
        if safe_map:
            styler = styler.format(safe_map, na_rep="")

    # Highlight SUM row like header
    if total_idx is not None and total_idx in df.index:
        def _apply_total(_df):
            styles = pd.DataFrame("", index=_df.index, columns=_df.columns)
            styles.loc[total_idx, :] = f"background-color: {BLUE}; color: white; font-weight: bold;"
            return styles
        styler = styler.apply(_apply_total, axis=None)

    return styler

def coerce_numeric(df: pd.DataFrame, cols: list[str]):
    existing = [c for c in cols if c in df.columns]
    if existing:
        df[existing] = df[existing].apply(pd.to_numeric, errors="coerce")
    return df

def add_sum_row(df: pd.DataFrame, total_label: str = "CƏM",
                sum_cols: list[str] | None = None,
                sales_col: str | None = None,
                plan_col: str | None = None,
                icra_col: str | None = None,
                icra_as_percent: bool = True):
    
    if df.empty:
        return df, None

    out = df.copy()
    totals = {col: "" for col in out.columns}

    # Label in the first column
    first_col = out.columns[0]
    totals[first_col] = total_label

    # Direct sums
    if sum_cols:
        for c in sum_cols:
            if c in out.columns:
                totals[c] = pd.to_numeric(out[c], errors="coerce").sum(skipna=True)

    # ICRA from totals
    if sales_col and plan_col and icra_col and sales_col in out.columns and plan_col in out.columns:
        sales_total = pd.to_numeric(out[sales_col], errors="coerce").sum(skipna=True)
        plan_total = pd.to_numeric(out[plan_col], errors="coerce").sum(skipna=True)
        if plan_total and plan_total != 0:
            ratio = sales_total / plan_total
            totals[icra_col] = ratio * (100 if icra_as_percent else 1)
        else:
            totals[icra_col] = None
        if (sum_cols or []) and sales_col not in sum_cols:
            totals[sales_col] = sales_total
        if (sum_cols or []) and plan_col not in sum_cols:
            totals[plan_col] = plan_total

    out = pd.concat([out, pd.DataFrame([totals], columns=out.columns)], ignore_index=True)
    total_idx = out.index[-1]
    return out, total_idx

# -----------------------------
# Streamlit App
# -----------------------------
st.set_page_config(
    page_title='FAB HESABAT',
    page_icon='logo.png',
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# FAB HESABAT \n Bu hesabat FAB şirkətlər qrupu üçün hazırlanmışdır."
    }
)
st.header("FAB - Hesabat", divider='rainbow')

st.markdown(
    """
    <style>
    /* Hide left index (row headers) in tables rendered by pandas Styler */
    th.row_heading {display: none !important;}
    th.blank {display: none !important;}      /* top-left blank corner */
    tbody th {display: none !important;}      /* extra guard */
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<style>
  table td {
    text-align: right;
  }
  table th {
    text-align: right; /* Optional: Align headers as well */
  }
  table p {
    text-align: right; /* Optional: Align headers as well */
  }
  
[data-testid="stMarkdownContainer"] table {
    width: 100%;
    border-collapse: collapse;
}

[data-testid="stMarkdownContainer"] th,
[data-testid="stMarkdownContainer"] td {
    text-align: right;
    border: 1px solid #ccc;
    padding: 5px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Satış üçün 4 sütun */
[data-testid="stMarkdownContainer"]:has(h2:has-text("Satış")) table td,
[data-testid="stMarkdownContainer"]:has(h2:has-text("Satış")) table th {
    width: 25%;
}

/* Sifariş, Borc, Qırmızı üçün 2 sütun */
[data-testid="stMarkdownContainer"]:has(h2:has-text("Sifariş")) table td,
[data-testid="stMarkdownContainer"]:has(h2:has-text("Sifariş")) table th,
[data-testid="stMarkdownContainer"]:has(h2:has-text("Borc")) table td,
[data-testid="stMarkdownContainer"]:has(h2:has-text("Borc")) table th,
[data-testid="stMarkdownContainer"]:has(h2:has-text("Qırmızı")) table td,
[data-testid="stMarkdownContainer"]:has(h2:has-text("Qırmızı")) table th {
    width: 50%;
}
</style>
""", unsafe_allow_html=True)

css_header = """
<style>

    [data-testid="stHeader"] {
        display: none;
    }
    
    [data-testid="stElementToolbar"] {
        display: none;
    }
    
</style>
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />
"""

st.markdown(css_header, unsafe_allow_html=True)

css_page = """
<style>

    th {
       color: black;
       font-weight: bold;
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
    
    [data-testid="stHeaderActionElements"] {
        display: none;
    }
    
</style>
<title>FAB MARKALAR</title>
<meta name="description" content="FAB Şirkətlər Qrupu" />
"""

st.markdown(css_page, unsafe_allow_html=True)

sections = [
    ("Satış", hesabat_satis),
    ("Sifariş", hesabat_sifaris),
    ("Borc", hesabat_borc),
    ("Qırmızı", hesabat_qirmizi),
]

for title, func in sections:
    block = st.container()
    block.subheader(title)

    with st.spinner("Məlumat yüklənir..."):
        try:
            df = func()
        except Exception as e:
            block.error(f"Xəta: {e}")
            continue

    if df is None or df.empty:
        block.info("Məlumat tapılmadı.")
        continue

    # Remove explicit index-like columns if exist
    df = remove_index_like_columns(df)

    # ----- Per-section numeric coercion, totals, and formats -----
    fmt_map = {}
    total_idx = None

    if title == "Satış":
        df = coerce_numeric(df, ["SATIS", "PLAN", "ICRA"])
        df, total_idx = add_sum_row(
            df,
            total_label="CƏM",
            sum_cols=["SATIS", "PLAN"],
            sales_col="SATIS",
            plan_col="PLAN",
            icra_col="ICRA",
            icra_as_percent=True
        )
        fmt_map = {
            "SATIS": fmt_space0,   # space thousands, 0 decimals
            "PLAN": fmt_space0,    # space thousands, 0 decimals
            "ICRA": fmt_icra,      # two decimals (no % sign)
        }

    elif title == "Sifariş":
        df = coerce_numeric(df, ["SIFARIS"])
        df, total_idx = add_sum_row(df, total_label="CƏM", sum_cols=["SIFARIS"])
        fmt_map = {"SIFARIS": fmt_space0}

    elif title == "Borc":
        df = coerce_numeric(df, ["BORC"])
        df, total_idx = add_sum_row(df, total_label="CƏM", sum_cols=["BORC"])
        fmt_map = {"BORC": fmt_space0}

    elif title == "Qırmızı":
        df = coerce_numeric(df, ["QIRMIZI"])
        df, total_idx = add_sum_row(df, total_label="CƏM", sum_cols=["QIRMIZI"])
        fmt_map = {"QIRMIZI": fmt_space0}

    block.table(style_for_table(df, fmt_map, total_idx=total_idx))