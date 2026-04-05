import streamlit as st
import pandas as pd
import datetime

# 1. 設置頁面配置 (必須是第一個 Streamlit 指令)
st.set_page_config(page_title="TNYP DUPR 終極助手", page_icon="🏓", layout="wide")

# ==========================================
# 賽程邏輯定義
# ==========================================
SCHEDULE_8 = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("B", "D", "F", "H"), ("A", "C", "E", "G"), ("A", "D", "E", "H"), ("B", "C", "F", "G"), ("A", "F", "C", "H"), ("B", "E","D", "G"), ("B", "H","D", "F"), ("A", "G", "C", "E"), ("A", "H", "D", "E"), ("B","G","C","F"), ("A", "B", "E", "F"), ("G", "H", "C", "D"), ("E", "G", "B", "D"), ("F", "H", "A", "C"), ("A", "D", "F", "G")]
SCHEDULE_7 = [("A", "B", "C", "D"), ("E", "F", "A", "G"), ("B", "C", "D", "E"), ("A", "C", "F", "G"), ("A", "F", "B", "E"), ("B", "D", "E", "G"), ("C", "F", "D", "G"), ("A", "E", "B", "F"), ("A", "D", "C", "G"), ("B", "G","C", "E"), ("A", "F","E", "G"), ("D", "F", "B", "C"), ("A", "D", "B", "E"), ("E","G","C","F"), ("A", "B", "E", "F"), ("G", "D", "C", "E"), ("E", "G", "B", "D"), ("F", "A", "C", "G"), ("A", "D", "F", "G")]


st.title("🏓 TNYP DUPR 專業錄入系統 (穩定匯出版)")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    event_main = st.text_input("活動名稱", value="TNYP Club Match")
    global_date = st.date_input("日期", datetime.date.today())
    court_count = st.number_input("場地數量", min_value=1, max_value=6, value=2)
    st.divider()
    st.write("🔧 如果遇到無法下載，請重新整理頁面。")

# 建立場地頁籤
tab_list = st.tabs([f"🏟️ 場地 {i+1}" for i in range(court_count)])

# 用於儲存所有有效比賽的清單
all_matches_to_export = []
draw_found = False

for i in range(court_count):
    cid = i + 1
    with tab_list[i]:
        mode = st.radio(f"場地 {cid} 賽制", ["8人制", "7人制"], key=f"m_{cid}", horizontal=True)
        p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7
        
        # 球員名單
        with st.expander(f"👤 場地 {cid} 球員名單", expanded=True):
            p_map = {}
            col1, col2 = st.columns(2)
            for idx, l in enumerate(p_labels):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    n = st.text_input(f"姓名 {l}", key=f"n_{cid}_{l}")
                    did = st.text_input(f"ID {l}", key=f"id_{cid}_{l}")
                    p_map[l] = {"n": n, "id": did}

        # 比分錄入
        st.subheader(f"🎯 場地 {cid} 比分")
        court_matches = []
        for g_idx, (a1, a2, b1, b2) in enumerate(sch, 1):
            c1, c2, mid, c3, c4 = st.columns([2, 1, 0.5, 1, 2])
            with c1: st.write(f"**{a1}/{a2}**")
            with c2: sa_val = st.text_input("A", key=f"sA_{cid}_{g_idx}", label_visibility="collapsed")
            with mid: st.write("-")
            with c3: sb_val = st.text_input("B", key=f"sB_{cid}_{g_idx}", label_visibility="collapsed")
            with c4: st.write(f"**{b1}/{b2}**")
            
            if sa_val.strip() and sb_val.strip():
                try:
                    sA, sB = int(sa_val), int(sb_val)
                    if sA == sB:
                        st.error(f"⚠️ 第 {g_idx} 場平分！DUPR 不收平手。")
                        draw_found = True
                    
                    match_data = {
                        'matchType': 'D', 'scoreType': 'RALLY',
                        'event': f"{event_main}-C{cid}",
                        'date': global_date.strftime("%Y-%m-%d"),
                        'playerA1': p_map[a1]['n'], 'playerA1DuprId': p_map[a1]['id'],
                        'playerA2': p_map[a2]['n'], 'playerA2DuprId': p_map[a2]['id'],
                        'playerB1': p_map[b1]['n'], 'playerB1DuprId': p_map[b1]['id'],
                        'playerB2': p_map[b2]['n'], 'playerB2DuprId': p_map[b2]['id'],
                        'teamAGame1': sA, 'teamBGame1': sB,
                        'teamAGame2': '', 'teamBGame2': '', 'teamAGame3': '', 'teamBGame3': '',
                        'teamAGame4': '', 'teamBGame4': '', 'teamAGame5': '', 'teamBGame5': ''
                    }
                    court_matches.append(match_data)
                    all_matches_to_export.append(match_data)
                except ValueError:
                    st.warning(f"第 {g_idx} 場請輸入數字")

        # 個別場地下載按鈕
        if court_matches:
            df_court = pd.DataFrame(court_matches)
            csv_court = df_court.to_csv(index=False, encoding='utf-8').encode('utf-8')
            st.download_button(f"📥 下載場地 {cid} CSV", csv_court, f"Court_{cid}.csv", "text/csv")

# --- 總結算區 ---
st.divider()
if all_matches_to_export:
    if draw_found:
        st.error("❌ 偵測到平手比分，請修正後才能下載總表。")
    else:
        st.success(f"✅ 已成功錄入 {len(all_matches_to_export)} 場比賽。")
        df_total = pd.DataFrame(all_matches_to_export)
        
        # 確保欄位順序完全正確
        cols_order = ['matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId','playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1','teamAGame2','teamBGame2','teamAGame3','teamBGame3','teamAGame4','teamBGame4','teamAGame5','teamBGame5']
        df_total = df_total.reindex(columns=cols_order).fillna('')
        
        # 下載按鈕
        final_csv = df_total.to_csv(index=False, encoding='utf-8').encode('utf-8')
        st.download_button(
            label="🔥 下載所有場地合併 CSV (上傳 DUPR 專用)",
            data=final_csv,
            file_name=f"DUPR_TOTAL_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
