import streamlit as st
import pandas as pd
import datetime

# 1. 設置頁面配置
st.set_page_config(page_title="TNYP DUPR 專業驗證錄入", page_icon="🏓", layout="wide")

# ==========================================
# 賽程邏輯定義 (嚴格對照 PDF)
# ==========================================
SCHEDULE_8 = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "C", "E", "G"), ("B", "D", "F", "H"), ("A", "D", "B", "C"), ("E", "H", "F", "G"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("A", "F", "D", "G"), ("B", "E", "C", "H"), ("A", "G", "B", "H"), ("C", "E", "D", "F"), ("A", "H", "C", "F"), ("B", "G", "D", "E"), ("A", "C", "B", "D"), ("E", "G", "F", "H"), ("A", "F", "B", "E"), ("C", "H", "D", "E"), ("A", "H", "B", "G"), ("C", "F", "D", "E")]
SCHEDULE_7 = [("G", "D", "F", "E"), ("B", "G", "C", "A"), ("D", "F", "E", "C"), ("A", "B", "G", "F"), ("E", "A", "C", "D"), ("B", "F", "G", "C"), ("A", "D", "E", "B"), ("G", "A", "F", "C"), ("B", "D", "E", "G"), ("F", "A", "C", "E"), ("D", "F", "B", "G"), ("E", "A", "C", "B"), ("D", "E", "F", "G"), ("A", "B", "C", "D"), ("D", "F", "E", "G"), ("A", "G", "B", "C"), ("C", "F", "D", "E"), ("A", "F", "B", "G"), ("A", "C", "D", "E"), ("B", "C", "F", "G"), ("A", "E", "B", "D")]

st.title("🏓 TNYP DUPR 專業驗證錄入系統")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 全域設定")
    event_main = st.text_input("活動名稱", value="TNYP Club Match")
    global_date = st.date_input("日期", datetime.date.today())
    global_score_type = st.selectbox("計分方式 (Score Type)", ["RALLY (落地得分)", "SIDEOUT (發球得分)"])
    score_type_val = "RALLY" if "RALLY" in global_score_type else "SIDEOUT"
    court_count = st.number_input("場地數量", min_value=1, max_value=6, value=2)
    st.divider()
    st.info("💡 比賽序號與 Scoresheet 一致，請依序錄入。")

# 建立場地頁籤
tab_list = st.tabs([f"🏟️ 場地 {i+1}" for i in range(court_count)])

all_matches_to_export = []
draw_found = False
id_error_found = False

for i in range(court_count):
    cid = i + 1
    with tab_list[i]:
        mode = st.radio(f"場地 {cid} 賽制", ["8人制", "7人制"], key=f"mode_radio_{cid}", horizontal=True)
        p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7
        
        # --- 1. 球員名單驗證 ---
        with st.expander(f"👤 場地 {cid} 球員名單驗證", expanded=True):
            p_map = {}
            col1, col2 = st.columns(2)
            temp_ids = set()
            for idx, l in enumerate(p_labels):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    n = st.text_input(f"球員 {l} 姓名", key=f"n_{cid}_{l}", placeholder="輸入姓名")
                    did = st.text_input(f"ID {l}", key=f"id_{cid}_{l}", placeholder="DUPR ID").strip().upper()
                    if did:
                        if did in temp_ids:
                            st.error(f"❌ ID {did} 重複！")
                            id_error_found = True
                        temp_ids.add(did)
                    p_map[l] = {"n": n, "id": did}

        # --- 2. 比分錄入 (加入序號) ---
        st.subheader(f"🎯 比分錄入 (計分制: {score_type_val})")
        for g_idx, (a1, a2, b1, b2) in enumerate(sch, 1):
            if any(label not in p_map for label in [a1, a2, b1, b2]):
                continue

            with st.container(border=True):
                # 佈局：序號 | 隊伍A | 分數A | vs | 分數B | 隊伍B
                idx_col, c1, c2, mid, c3, c4 = st.columns([0.6, 2, 1, 0.5, 1, 2])
                
                with idx_col:
                    st.markdown(f"### {g_idx:02d}") # 顯示序號如 01, 02...
                
                with c1: 
                    st.markdown(f"**{a1}:** {p_map[a1]['n'] or '未填'}")
                    st.markdown(f"**{a2}:** {p_map[a2]['n'] or '未填'}")
                with c2: sa_val = st.text_input("A", key=f"sA_{cid}_{g_idx}", label_visibility="collapsed")
                with mid: st.write("-")
                with c3: sb_val = st.text_input("B", key=f"sB_{cid}_{g_idx}", label_visibility="collapsed")
                with c4: 
                    st.markdown(f"**{b1}:** {p_map[b1]['n'] or '未填'}")
                    st.markdown(f"**{b2}:** {p_map[b2]['n'] or '未填'}")
                
                if sa_val.strip() and sb_val.strip():
                    try:
                        s1, s2 = int(sa_val), int(sb_val)
                        if s1 == s2:
                            st.error(f"❌ 第 {g_idx} 場平分，DUPR 不接受。")
                            draw_found = True
                        
                        curr_ids = [p_map[a1]['id'], p_map[a2]['id'], p_map[b1]['id'], p_map[b2]['id']]
                        if any(not d for d in curr_ids):
                            id_error_found = True

                        all_matches_to_export.append({
                            'matchType': 'D', 'scoreType': score_type_val,
                            'event': f"{event_main}-C{cid}",
                            'date': global_date.strftime("%Y-%m-%d"),
                            'playerA1': p_map[a1]['n'], 'playerA1DuprId': p_map[a1]['id'],
                            'playerA2': p_map[a2]['n'], 'playerA2DuprId': p_map[a2]['id'],
                            'playerB1': p_map[b1]['n'], 'playerB1DuprId': p_map[b1]['id'],
                            'playerB2': p_map[b2]['n'], 'playerB2DuprId': p_map[b2]['id'],
                            'teamAGame1': s1, 'teamBGame1': s2,
                            'teamAGame2': '', 'teamBGame2': '', 'teamAGame3': '', 'teamBGame3': '',
                            'teamAGame4': '', 'teamBGame4': '', 'teamAGame5': '', 'teamBGame5': ''
                        })
                    except ValueError:
                        st.error(f"❌ 第 {g_idx} 場分數格式錯誤。")

# --- 3. 匯出邏輯 ---
st.divider()
if all_matches_to_export:
    if draw_found or id_error_found:
        st.error("🚫 資料有誤（平手或 ID 遺漏/重複），請修正後再下載。")
    else:
        st.success(f"✅ 驗證成功：共 {len(all_matches_to_export)} 場比賽。")
        df_total = pd.DataFrame(all_matches_to_export)
        cols = ['matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId','playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1','teamAGame2','teamBGame2','teamAGame3','teamBGame3','teamAGame4','teamBGame4','teamAGame5','teamBGame5']
        df_total = df_total.reindex(columns=cols).fillna('')
        
        csv_data = df_total.to_csv(index=False, encoding='utf-8').encode('utf-8')
        st.download_button(
            label="🚀 下載驗證合格的 DUPR CSV",
            data=csv_data,
            file_name=f"TNYP_FINAL_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
