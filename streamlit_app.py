import streamlit as st
import pandas as pd
import datetime

# 設定網頁標題與圖示 (使用表情符號作為臨時圖示)
st.set_page_config(page_title="TNYP DUPR 助手", page_icon="🏓", layout="centered")

# --- 賽程數據 (保持不變) ---
SCHEDULE_8 = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("B", "D", "F", "H"), ("A", "C", "E", "G"), ("E", "H", "A", "D"), ("F", "G", "B", "C"), ("A", "F", "C", "H"), ("B", "E", "D", "G"), ("B", "H", "D", "F"), ("A", "G", "C", "E"), ("A", "H", "D", "E"), ("C", "F", "B", "G"), ("A", "B", "E", "F"), ("G", "H", "C", "D"), ("E", "G", "B", "D"), ("F", "H", "A", "C"), ("A", "D", "F", "G")]
SCHEDULE_7 = [("A", "B", "C", "D"), ("E", "F", "A", "G"), ("B", "C", "D", "E"), ("A", "C", "F", "G"), ("A", "F", "B", "E"), ("B", "D", "E", "G"), ("C", "F", "D", "G"), ("A", "E", "B", "F"), ("A", "D", "C", "G"), ("C", "E", "B", "G"), ("E", "G", "A", "F"), ("B", "C", "D", "F"), ("A", "D", "B", "E"), ("C", "F", "E", "G"), ("A", "B", "E", "F"), ("A", "G", "C", "D"), ("D", "E", "C", "G"), ("A", "C", "D", "F"), ("A", "F", "B", "E")]

# 自定義 CSS 讓介面更像匹克球風格
st.markdown("""
    <style>
    .stApp { background-color: #fdfdfd; }
    .stButton>button { background-color: #99cc00; color: white; border-radius: 10px; border: none; }
    .stDownloadButton>button { background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏓 TNYP DUPR 賽事錄入")
st.caption("專為 7 人/ 8 人循環賽設計的錄入系統")

# 選擇模式
mode = st.segmented_control("選擇比賽人數", ["8人制", "7人制"], default="8人制")
p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7

# --- 1. 基本資訊 ---
with st.container(border=True):
    event_name = st.text_input("🏆 活動名稱", value=f"TNYP {mode} Match")
    match_date = st.date_input("📅 比賽日期", datetime.date.today())

# --- 2. 球員名單 ---
st.subheader("👤 球員名單設定")
player_data = {}
# 手機版建議使用 2 列顯示
cols = st.columns(2)
for i, label in enumerate(p_labels):
    with cols[i % 2]:
        name = st.text_input(f"球員 {label} 姓名", key=f"n_{label}")
        did = st.text_input(f"DUPR ID", key=f"id_{label}", help="請務必輸入正確 ID")
        player_data[label] = {"n": name, "id": did}

st.divider()

# --- 3. 分數錄入 ---
st.subheader("🎯 比分錄入 (19場)")
results = []
for idx, (a1, a2, b1, b2) in enumerate(sch, 1):
    with st.expander(f"第 {idx:02d} 場: {a1}/{a2} vs {b1}/{b2}", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            s1 = st.number_input(f"{a1}/{a2} 分數", min_value=0, max_value=30, step=1, key=f"s1_{idx}", value=0)
        with c2:
            s2 = st.number_input(f"{b1}/{b2} 分數", min_value=0, max_value=30, step=1, key=f"s2_{idx}", value=0)
        
        # 只有當分數不全為 0 時才記錄
        if s1 != 0 or s2 != 0:
            results.append([
                'D', 'RALLY', event_name, match_date.strftime("%Y-%m-%d"),
                player_data[a1]['n'], player_data[a1]['id'], player_data[a2]['n'], player_data[a2]['id'],
                player_data[b1]['n'], player_data[b1]['id'], player_data[b2]['n'], player_data[b2]['id'],
                s1, s2
            ])

# --- 4. 匯出 ---
if results:
    df = pd.DataFrame(results, columns=[
        'matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId',
        'playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1'
    ])
    csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("💾 下載 DUPR 檔案 (CSV)", csv_data, f"TNYP_{mode}.csv", "text/csv")
else:
    st.warning("請填寫至少一場比賽分數以產生檔案。")
