import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# 設定網頁標題與圖示
st.set_page_config(page_title="TNYP DUPR 助手", layout="centered")

# ==========================================
# 賽程邏輯定義 (嚴格對照 PDF)
# ==========================================
SCHEDULE_8 = [
    ("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "E", "B", "F"), ("C", "G", "D", "H"),
    ("B", "D", "F", "H"), ("A", "C", "E", "G"), ("E", "H", "A", "D"), ("F", "G", "B", "C"),
    ("A", "F", "C", "H"), ("B", "E", "D", "G"), ("B", "H", "D", "F"), ("A", "G", "C", "E"),
    ("A", "H", "D", "E"), ("C", "F", "B", "G"), ("A", "B", "E", "F"), ("G", "H", "C", "D"),
    ("E", "G", "B", "D"), ("F", "H", "A", "C"), ("A", "D", "F", "G")
]

SCHEDULE_7 = [
    ("A", "B", "C", "D"), ("E", "F", "A", "G"), ("B", "C", "D", "E"), ("A", "C", "F", "G"),
    ("A", "F", "B", "E"), ("B", "D", "E", "G"), ("C", "F", "D", "G"), ("A", "E", "B", "F"),
    ("A", "D", "C", "G"), ("C", "E", "B", "G"), ("E", "G", "A", "F"), ("B", "C", "D", "F"),
    ("A", "D", "B", "E"), ("C", "F", "B", "G"), ("A", "B", "E", "F"), ("G", "D", "C", "E"),
    ("E", "G", "B", "D"), ("F", "A", "C", "G"), ("A", "D", "F", "G")
]

st.title("🎾 TNYP DUPR 賽事錄入")

# 選擇人數模式
mode = st.radio("選擇比賽人數", ["8人制", "7人制"], horizontal=True)
p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7

# --- 第一部分：基本資訊 ---
with st.expander("📝 第一步：設定活動資訊", expanded=True):
    event_name = st.text_input("活動名稱", value=f"TNYP {mode} Match")
    match_date = st.date_input("比賽日期", datetime.date.today())

# --- 第二部分：球員名單 ---
with st.expander("👤 第二步：輸入球員名單", expanded=True):
    st.write("請輸入每位代號對應的姓名與 DUPR ID")
    player_data = {}
    cols = st.columns(2)
    for i, label in enumerate(p_labels):
        with cols[i % 2]:
            st.markdown(f"**球員 {label}**")
            name = st.text_input(f"姓名", key=f"n_{label}", label_visibility="collapsed", placeholder=f"姓名 {label}")
            did = st.text_input(f"ID", key=f"id_{label}", label_visibility="collapsed", placeholder=f"DUPR ID {label}")
            player_data[label] = {"n": name, "id": did}

# --- 第三部分：比分錄入 ---
st.markdown("### 🏆 第三步：依序錄入比分")
results = []
for idx, (a1, a2, b1, b2) in enumerate(sch, 1):
    with st.container():
        st.markdown(f"**場次 {idx:02d}**")
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 2])
        with c1:
            st.markdown(f"<span style='color:#0056b3'>**{a1}/{a2}**</span>", unsafe_allow_html=True)
        with c2:
            s1 = st.text_input("A分", key=f"s1_{idx}", label_visibility="collapsed")
        with c3:
            st.write("vs")
        with c4:
            s2 = st.text_input("B分", key=f"s2_{idx}", label_visibility="collapsed")
        with c5:
            st.markdown(f"<span style='color:#d32f2f'>**{b1}/{b2}**</span>", unsafe_allow_html=True)
        
        if s1 and s2:
            results.append([
                'D', 'RALLY', event_name, match_date.strftime("%Y-%m-%d"),
                player_data[a1]['n'], player_data[a1]['id'], player_data[a2]['n'], player_data[a2]['id'],
                player_data[b1]['n'], player_data[b1]['id'], player_data[b2]['n'], player_data[b2]['id'],
                s1, s2
            ])
    st.divider()

# --- 第四部分：匯出下載 ---
if results:
    df = pd.DataFrame(results, columns=[
        'matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId',
        'playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1'
    ])
    
    # 轉成 CSV 字串
    csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    
    st.download_button(
        label="📥 下載 DUPR 匯入檔案 (CSV)",
        data=csv_data,
        file_name=f"DUPR_{mode}_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.info("請在上方輸入至少一場比賽的分數，即可產生下載按鈕。")