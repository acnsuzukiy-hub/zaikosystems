import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="在庫管理システム", layout="wide")
st.title("📦 シリアル在庫管理システム")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_inv = conn.read(worksheet="inventory", ttl=0).dropna(how="all")
    df_loc = conn.read(worksheet="locations", ttl=0).dropna(how="all")
    location_options = df_loc["location_name"].tolist() if not df_loc.empty else []
except:
    st.error("スプレッドシートが読み込めません。Secrets設定とシート名を確認してください。")
    st.stop()

menu = ["🏠 在庫一覧", "➕ 1件登録", "⚙️ 各種管理"]
choice = st.sidebar.selectbox("メニュー", menu)

if choice == "🏠 在庫一覧":
    st.dataframe(df_inv, use_container_width=True, hide_index=True)

elif choice == "➕ 1件登録":
    with st.form("add_form", clear_on_submit=True):
        sn = st.text_input("シリアル番号")
        p_name = st.text_input("商品名")
        loc = st.selectbox("保管場所", location_options) if location_options else st.text_input("保管場所")
        user = st.text_input("担当者名")
        if st.form_submit_button("登録"):
            new_row = pd.DataFrame([{"シリアル番号":sn,"商品名":p_name,"現在保管場所":loc,"入庫元":"","出庫先":"","ステータス":"在庫中","最終更新日時":datetime.now().strftime("%Y-%m-%d %H:%M"),"登録・更新者":user}])
            updated_df = pd.concat([df_inv, new_row], ignore_index=True)
            conn.update(worksheet="inventory", data=updated_df)
            st.success("保存完了！")
            st.rerun()

elif choice == "⚙️ 各種管理":
    new_loc = st.text_input("新しい場所の名前")
    if st.button("場所を追加"):
        new_row = pd.DataFrame([{"location_name": new_loc}])
        updated_loc = pd.concat([df_loc, new_row], ignore_index=True)
        conn.update(worksheet="locations", data=updated_loc)
        st.success("追加完了")
        st.rerun()
