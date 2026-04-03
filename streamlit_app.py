import streamlit as st
import pandas as pd
import datetime

# --- 必須是第一個 Streamlit 指令 ---
st.set_page_config(
    page_title="TNYP DUPR 多場地助手", 
    page_icon="🏓", 
    layout="wide"
)

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

# 自定義 CSS (匹克球配色)
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6; border-radius: 8px 8px 0px 0px; padding: 10px 15px;
    }
    .stTabs [aria-selected="true"] { background-color: #99cc00 !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏓 TNYP DUPR 多場地管理系統")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 賽事全域設定")
    event_main = st.text_input("基本活動名稱", value="TNYP Club Match")
    global_date = st.date_input("比賽日期", datetime.date.today())
    court_count = st.number_input("場地數量", min_value=1, max_value=6, value=2)
    st.divider()
    st.info("💡 每個場地可獨立設定 7人或 8人制。")

# 建立場地頁籤
tab_list = st.tabs([f"🏟️ 場地 {i+1}" for i in range(court_count)])

all_data_for_export = []

for i in range(court_count):
    court_id = i + 1
    with tab_list[i]:
        st.subheader(f"場地 {court_id} 配置")
        
        # 1. 模式切換
        mode = st.segmented_control(
            f"場地 {court_id} 賽制", 
            ["8人制", "7人制"], 
            default="8人制", 
            key=f"mode_select_{court_id}"
        )
        
        p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7
        
        # 2. 球員名單輸入
        with st.expander(f"👤 球員名單 (場地 {court_id})", expanded=True):
            p_data = {}
            col1, col2 = st.columns(2)
            for idx, label in enumerate(p_labels):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    n = st.text_input(f"球員 {label} 姓名", key=f"n_{court_id}_{label}", placeholder="姓名")
                    did = st.text_input(f"ID", key=f"id_{court_id}_{label}", placeholder="DUPR ID", label_visibility="collapsed")
                    p_data[label] = {"n": n, "id": did}

        # 3. 比分錄入
        st.subheader(f"🎯 比分錄入 (共 {len(sch)} 場)")
        court_matches = []
        
        for g_idx, (a1, a2, b1, b2) in enumerate(sch, 1):
            with st.container(border=True):
                # 手機版佈局優化
                c1, c2, mid, c3, c4 = st.columns([2, 1, 0.5, 1, 2])
                with c1: st.markdown(f"**{a1}/{a2}**")
                with c2: s1 = st.text_input("A分", key=f"sA_{court_id}_{g_idx}", label_visibility="collapsed")
                with mid: st.write("-")
                with c3: s2 = st.text_input("B分", key=f"sB_{court_id}_{g_idx}", label_visibility="collapsed")
                with c4: st.markdown(f"**{b1}/{b2}**")
                
                # 資料處理
                if s1.strip() and s2.strip():
                    match_row = [
                        'D', 'RALLY', f"{event_main}-C{court_id}", global_date.strftime("%Y-%m-%d"),
                        p_data[a1]['n'], p_data[a1]['id'], p_data[a2]['n'], p_data[a2]['id'],
                        p_data[b1]['n'], p_data[b1]['id'], p_data[b2]['n'], p_data[b2]['id'],
                        s1, s2
                    ]
                    court_matches.append(match_row)
                    all_data_for_export.append(match_row)

        # 單獨場地匯出
        if court_matches:
            df_court = pd.DataFrame(court_matches, columns=['matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId','playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1'])
            st.download_button(
                f"📥 下載場地 {court_id} CSV", 
                df_court.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'),
                f"TNYP_C{court_id}.csv", 
                "text/csv"
            )

# --- 總結算區 ---
st.divider()
if all_data_for_export:
    st.subheader("📦 全場地合併匯出")
    st.write(f"目前累計已錄入 {len(all_data_for_export)} 場比賽資料。")
    df_all = pd.DataFrame(all_data_for_export, columns=['matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId','playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1'])
    st.download_button(
        "🔥 下載所有場地合併 CSV (一次上傳 DUPR)",
        df_all.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'),
        f"TNYP_TOTAL_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
        "text/csv",
        type="primary",
        use_container_width=True
    )
