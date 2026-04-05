import streamlit as st
import pandas as pd
import datetime

# 1. 設置頁面配置
st.set_page_config(page_title="TNYP DUPR 助手 Pro", page_icon="🏓", layout="wide")

# ==========================================
# 賽程邏輯定義 (嚴格對照 PDF)
# ==========================================
SCHEDULE_8 = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("B", "D", "F", "H"), ("A", "C", "E", "G"), ("A", "D", "E", "H"), ("B", "C", "F", "G"), ("A", "F", "C", "H"), ("B", "E","D", "G"), ("B", "H","D", "F"), ("A", "G", "C", "E"), ("A", "H", "D", "E"), ("B","G","C","F"), ("A", "B", "E", "F"), ("G", "H", "C", "D"), ("E", "G", "B", "D"), ("F", "H", "A", "C"), ("A", "D", "F", "G")]
SCHEDULE_7 = [("A", "B", "C", "D"), ("E", "F", "A", "G"), ("B", "C", "D", "E"), ("A", "C", "F", "G"), ("A", "F", "B", "E"), ("B", "D", "E", "G"), ("C", "F", "D", "G"), ("A", "E", "B", "F"), ("A", "D", "C", "G"), ("B", "G","C", "E"), ("A", "F","E", "G"), ("D", "F", "B", "C"), ("A", "D", "B", "E"), ("E","G","C","F"), ("A", "B", "E", "F"), ("G", "D", "C", "E"), ("E", "G", "B", "D"), ("F", "A", "C", "G"), ("A", "D", "F", "G")]


st.title("🏓 TNYP DUPR 專業錄入系統")

with st.sidebar:
    st.header("⚙️ 設定")
    event_main = st.text_input("活動名稱", value="TNYP Club Match")
    # 確保日期選擇器
    global_date = st.date_input("日期", datetime.date.today())
    court_count = st.number_input("場地數量", min_value=1, max_value=6, value=2)

tab_list = st.tabs([f"🏟️ 場地 {i+1}" for i in range(court_count)])
all_results = []
draw_detected = False # 檢查是否有平手

for i in range(court_count):
    cid = i + 1
    with tab_list[i]:
        mode = st.radio(f"賽制", ["8人制", "7人制"], key=f"m_{cid}", horizontal=True)
        p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7
        
        with st.expander(f"👤 球員名單", expanded=True):
            p_data = {}
            c1, c2 = st.columns(2)
            for idx, l in enumerate(p_labels):
                col = c1 if idx % 2 == 0 else c2
                name = col.text_input(f"姓名 {l}", key=f"n_{cid}_{l}")
                did = col.text_input(f"ID {l}", key=f"id_{cid}_{l}")
                p_data[l] = {"n": name, "id": did}

        st.subheader("🎯 比分錄入")
        for g_idx, (a1, a2, b1, b2) in enumerate(sch, 1):
            cols = st.columns([2, 1, 0.5, 1, 2])
            cols[0].write(f"**{a1}/{a2}**")
            s1_raw = cols[1].text_input("A", key=f"sA_{cid}_{g_idx}", label_visibility="collapsed")
            cols[2].write("-")
            s2_raw = cols[3].text_input("B", key=f"sB_{cid}_{g_idx}", label_visibility="collapsed")
            cols[4].write(f"**{b1}/{b2}**")
            
            if s1_raw.strip() and s2_raw.strip():
                s1 = int(s1_raw)
                s2 = int(s2_raw)
                
                # 檢查平手
                if s1 == s2:
                    st.error(f"⚠️ 場地 {cid} 第 {g_idx} 場出現平分 ({s1}:{s2})，DUPR 不接受平手，請修正。")
                    draw_detected = True
                
                all_results.append({
                    'matchType': 'D', 'scoreType': 'RALLY',
                    'event': f"{event_main}-C{cid}",
                    'date': global_date.strftime("%Y-%m-%d"), # 修正：YYYY-MM-DD
                    'playerA1': p_data[a1]['n'], 'playerA1DuprId': p_data[a1]['id'],
                    'playerA2': p_data[a2]['n'], 'playerA2DuprId': p_data[a2]['id'],
                    'playerB1': p_data[b1]['n'], 'playerB1DuprId': p_data[b1]['id'],
                    'playerB2': p_data[b2]['n'], 'playerB2DuprId': p_data[b2]['id'],
                    'teamAGame1': s1, 'teamBGame1': s2,
                    'teamAGame2': '', 'teamBGame2': '', 'teamAGame3': '', 'teamBGame3': '',
                    'teamAGame4': '', 'teamBGame4': '', 'teamAGame5': '', 'teamBGame5': ''
                })

st.divider()

if all_results:
    if draw_detected:
        st.warning("❌ 偵測到比賽平分，請修正比分後再下載，否則 DUPR 系統將退件。")
    else:
        df = pd.DataFrame(all_results)
        # 清理空白
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        
        # 補齊 22 欄位順序
        columns_order = [
            'matchType','scoreType','event','date',
            'playerA1','playerA1DuprId','playerA2','playerA2DuprId',
            'playerB1','playerB1DuprId','playerB2','playerB2DuprId',
            'teamAGame1','teamBGame1','teamAGame2','teamBGame2',
            'teamAGame3','teamBGame3','teamAGame4','teamBGame4','teamAGame5','teamBGame5'
        ]
        df = df.reindex(columns=columns_order).fillna('')

        # 匯出標準 UTF-8 (無 BOM)
        csv_bytes = df.to_csv(index=False, encoding='utf-8').encode('utf-8')
        
        st.download_button(
            label="🚀 下載 DUPR 匯入檔案 (已修正日期與平手檢查)",
            data=csv_bytes,
            file_name=f"DUPR_IMPORT_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
