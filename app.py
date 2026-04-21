import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# ページ設定
st.set_page_config(page_title="在庫管理システム", layout="wide")
st.title("📦 シリアル在庫管理システム")

# スプレッドシート接続
conn = st.connection("gsheets", type=GSheetsConnection)

# データの読み込み（エラーが起きても止まらないように対策）
try:
    # inventoryシートの読み込み
    df_inv = conn.read(worksheet="inventory", ttl=0)
    # 空行を削除
    df_inv = df_inv.dropna(how="all")
except Exception as e:
    st.error(f"スプレッドシートの 'inventory' シートが読み込めません。タブ名を確認してください。")
    st.stop()

try:
    # locationsシートの読み込み
    df_loc = conn.read(worksheet="locations", ttl=0)
    location_options = df_loc["location_name"].dropna().tolist()
except:
    # locationsが読み込めない場合は空のリストにする
    location_options = ["本社", "倉庫"] 

# メニュー
menu = ["🏠 在庫一覧", "➕ 1件登録", "⚙️ 各種管理"]
choice = st.sidebar.selectbox("メニュー", menu)

# --- 在庫一覧 ---
if choice == "🏠 在庫一覧":
    st.subheader("📊 現在の在庫状況")
    if not df_inv.empty:
        st.dataframe(df_inv, use_container_width=True, hide_index=True)
    else:
        st.info("データがまだありません。1件登録から始めてください。")

# --- 1件登録 ---
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
                # 既存データと結合
                updated_df = pd.concat([df_inv, new_row], ignore_index=True)
                # スプレッドシートを更新
                conn.update(worksheet="inventory", data=updated_df)
                st.success(f"保存しました: {sn}")
                st.rerun()
            else:
                st.warning("シリアル番号と担当者名は必須です。")

# --- 各種管理 ---
elif choice == "⚙️ 各種管理":
    st.subheader("🏘️ 保管場所の追加")
    new_loc = st.text_input("新しい場所の名前")
    if st.button("追加"):
        if new_loc:
            # 現在の場所リストに新規追加
            new_loc_df = pd.DataFrame([{"location_name": new_loc}])
            # locationsシートが存在しない場合も考慮して更新
            try:
                updated_loc = pd.concat([df_loc, new_loc_df], ignore_index=True)
            except:
                updated_loc = new_loc_df
            
            conn.update(worksheet="locations", data=updated_loc)
            st.success(f"追加完了: {new_loc}")
            st.rerun()
