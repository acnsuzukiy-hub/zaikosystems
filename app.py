import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="在庫管理システム", layout="wide")
st.title("📦 シリアル在庫管理システム")

# --- Google Sheets 接続設定 ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- データの読み込み ---
# inventoryシートを読み込みます
try:
    df_inv = conn.read(worksheet="inventory", ttl=0).dropna(how="all")
except Exception as e:
    st.error("スプレッドシートの 'inventory' シートが読み込めません。タブ名が半角小文字の 'inventory' になっているか確認してください。")
    st.stop()

# locationsシートを読み込みます（失敗しても基本の選択肢を出します）
try:
    df_loc = conn.read(worksheet="locations", ttl=0).dropna(how="all")
    location_options = df_loc["location_name"].tolist()
except:
    location_options = ["本社", "倉庫"]

# --- メニュー ---
menu = ["🏠 在庫一覧", "➕ 1件登録", "⚙️ 各種管理"]
choice = st.sidebar.selectbox("機能メニュー", menu)

# --- 1. 在庫一覧 ---
if choice == "🏠 在庫一覧":
    st.subheader("📊 現在の在庫状況")
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True, hide_index=True)
    else:
        st.info("現在、登録されているデータはありません。")

# --- 2. 1件登録 ---
elif choice == "➕ 1件登録":
    st.subheader("📝 新規登録")
    with st.form("add_form", clear_on_submit=True):
        sn = st.text_input("シリアル番号（必須）")
        p_name = st.text_input("商品名")
        loc = st.selectbox("保管場所", location_options)
        user = st.text_input("担当者名（必須）")
        
        if st.form_submit_button("スプレッドシートに保存"):
            if sn and user:
                new_row = pd.DataFrame([{
                    "シリアル番号": sn,
                    "商品名": p_name,
                    "現在保管場所": loc,
                    "入庫元": "",
                    "出庫先": "",
                    "ステータス": "在庫中",
                    "最終更新日時": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "登録・更新者": user
                }])
                # スプレッドシートを更新
                updated_df = pd.concat([df_inv, new_row], ignore_index=True)
                conn.update(worksheet="inventory", data=updated_df)
                st.success(f"保存完了: {sn}")
                st.rerun()
            else:
                st.error("シリアル番号と担当者名は必ず入力してください。")

# --- 3. 各種管理 ---
elif choice == "⚙️ 各種管理":
    st.subheader("🏘️ 保管場所の追加")
    new_loc = st.text_input("追加したい場所の名前")
    if st.button("場所を登録"):
        if new_loc:
            new_row_loc = pd.DataFrame([{"location_name": new_loc}])
            updated_loc = pd.concat([df_loc, new_row_loc], ignore_index=True)
            conn.update(worksheet="locations", data=updated_loc)
            st.success(f"追加しました: {new_loc}")
            st.rerun()
