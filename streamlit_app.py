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
