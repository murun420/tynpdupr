import streamlit as st
import pandas as pd
import datetime

# 1. 設置頁面配置
st.set_page_config(page_title="TNYP DUPR 專業驗證錄入", page_icon="🏓", layout="wide")

# ==========================================
# 賽程邏輯定義
# ==========================================
SCHEDULE_8 = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "C", "E", "G"), ("B", "D", "F", "H"), ("A", "D", "B", "C"), ("E", "H", "F", "G"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("A", "F", "D", "G"), ("B", "E", "C", "H"), ("A", "G", "B", "H"), ("C", "E", "D", "F"), ("A", "H", "C", "F"), ("B", "G", "D", "E"), ("A", "C", "B", "D"), ("E", "G", "F", "H"), ("A", "F", "B", "E"), ("C", "H", "D", "E"), ("A", "H", "B", "G"), ("C", "F", "D", "E")]
SCHEDULE_7 = [("G", "D", "F", "E"), ("B", "G", "C", "A"), ("D", "F", "E", "C"), ("A", "B", "G", "F"), ("E", "A", "C", "D"), ("B", "F", "G", "C"), ("A", "D", "E", "B"), ("G", "A", "F", "C"), ("B", "D", "E", "G"), ("F", "A", "C", "E"), ("D", "F", "B", "G"), ("E", "A", "C", "B"), ("D", "E", "F", "G"), ("A", "B", "C", "D"), ("D", "F", "E", "G"), ("A", "G", "B", "C"), ("C", "F", "D", "E"), ("A", "F", "B", "G"), ("A", "C", "D", "E"), ("B", "C", "F", "G"), ("A", "E", "B", "D")]
# SCHEDULE_8_DBL = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("B", "D", "F", "H"), ("A", "C", "E", "G"), ("E", "H", "A", "D"), ("F", "G", "B", "C"), ("A", "F", "C", "H"), ("B", "E", "D", "G"), ("B", "H", "D", "F"), ("A", "G", "C", "E"), ("A", "H", "D", "E"), ("C", "F", "B", "G"), ("A", "B", "E", "F"), ("G", "H", "C", "D"), ("E", "G", "B", "D"), ("F", "H", "A", "C"), ("A", "D", "F", "G")]
# SCHEDULE_7_DBL = [("A", "B", "C", "D"), ("E", "F", "A", "G"), ("B", "C", "D", "E"), ("A", "C", "F", "G"), ("A", "F", "B", "E"), ("B", "D", "E", "G"), ("C", "F", "D", "G"), ("A", "E", "B", "F"), ("A", "D", "C", "G"), ("C", "E", "B", "G"), ("E", "G", "A", "F"), ("B", "C", "D", "F"), ("A", "D", "B", "E"), ("C", "F", "B", "G"), ("A", "B", "E", "F"), ("G", "D", "C", "E"), ("E", "G", "B", "D"), ("F", "A", "C", "G"), ("A", "D", "F", "G")]
SCHEDULE_6_DBL = [("A", "B", "C", "D"), ("E", "F", "A", "C"), ("B", "E", "D", "F"), ("A", "D", "B", "F"), ("C", "E", "A", "B"), ("D", "F", "C", "E"), ("A", "F", "B", "D"), ("C", "D", "A", "E"), ("B", "C", "E", "F"), ("A", "D", "B", "E"), ("C", "F", "A", "B"), ("B", "D", "E", "F"), ("A", "F", "C", "D"), ("B", "E", "A", "D"), ("C", "E", "B", "F")]
SCHEDULE_5_SGL = [
    ("A", None, "B", None), ("C", None, "D", None), ("E", None, "A", None), ("B", None, "C", None), ("D", None, "E", None),
    ("A", None, "C", None), ("B", None, "D", None), ("C", None, "E", None), ("A", None, "D", None), ("B", None, "E", None),
    ("B", None, "A", None), ("D", None, "C", None), ("A", None, "E", None), ("C", None, "B", None), ("E", None, "D", None),
    ("C", None, "A", None), ("D", None, "B", None), ("E", None, "C", None), ("D", None, "A", None), ("E", None, "B", None)
]

# DUPR 標準標題列
DUPR_COLS = ['matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId','playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1','teamAGame2','teamBGame2','teamAGame3','teamBGame3','teamAGame4','teamBGame4','teamAGame5','teamBGame5']

st.title("🏓 TNYP DUPR 專業驗證錄入系統")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 全域設定")
    event_main = st.text_input("活動名稱", value="TNYP Match")
    global_date = st.date_input("日期", datetime.date.today())
    global_score_type = st.selectbox("計分方式", ["RALLY (落地得分)", "SIDEOUT (發球得分)"])
    score_type_val = "RALLY" if "RALLY" in global_score_type else "SIDEOUT"
    court_count = st.number_input("場地數量", min_value=1, max_value=6, value=2)
    st.divider()
    st.info("💡 您可以選擇下載「單一場地」或「所有場地合併」的成績。")

tab_list = st.tabs([f"🏟️ 場地 {i+1}" for i in range(court_count)])

all_matches_combined = []

for i in range(court_count):
    cid = i + 1
    with tab_list[i]:
        # 1. 賽制選擇
        mode = st.selectbox(f"場地 {cid} 賽制", 
                            ["雙打 - 8人制", "雙打 - 7人制", "雙打 - 6人制", "單打 - 5人制 (20場)"], 
                            key=f"mode_{cid}")
        
        if "8人制" in mode:
            p_labels, sch, m_type = ['A','B','C','D','E','F','G','H'], SCHEDULE_8_DBL, "D"
        elif "7人制" in mode:
            p_labels, sch, m_type = ['A','B','C','D','E','F','G'], SCHEDULE_7_DBL, "D"
        elif "6人制" in mode:
            p_labels, sch, m_type = ['A','B','C','D','E','F'], SCHEDULE_6_DBL, "D"
        else:
            p_labels, sch, m_type = ['A','B','C','D','E'], SCHEDULE_5_SGL, "S"

        # 2. 球員名單驗證
        with st.expander(f"👤 球員名單驗證 (場地 {cid})", expanded=True):
            p_map = {}
            col1, col2 = st.columns(2)
            temp_ids = set()
            for idx, l in enumerate(p_labels):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    n = st.text_input(f"球員 {l} 姓名", key=f"n_{cid}_{l}")
                    did = st.text_input(f"ID {l}", key=f"id_{cid}_{l}").strip().upper()
                    if did:
                        if did in temp_ids: st.error(f"❌ ID 重複: {did}")
                        temp_ids.add(did)
                    p_map[l] = {"n": n, "id": did}

        # 3. 比分錄入
        st.subheader(f"🎯 比分錄入 (場地 {cid})")
        court_matches = []
        court_error = False

        for g_idx, (a1, a2, b1, b2) in enumerate(sch, 1):
            with st.container(border=True):
                idx_col, c1, c2, mid, c3, c4 = st.columns([0.6, 2, 1, 0.5, 1, 2])
                with idx_col: st.markdown(f"### {g_idx:02d}")
                with c1:
                    st.markdown(f"**{a1}:** {p_map[a1]['n'] or '?'}")
                    if a2: st.markdown(f"**{a2}:** {p_map[a2]['n'] or '?'}")
                with c2: sa = st.text_input("A", key=f"sA_{cid}_{g_idx}", label_visibility="collapsed")
                with mid: st.write("-")
                with c3: sb = st.text_input("B", key=f"sB_{cid}_{g_idx}", label_visibility="collapsed")
                with c4:
                    st.markdown(f"**{b1}:** {p_map[b1]['n'] or '?'}")
                    if b2: st.markdown(f"**{b2}:** {p_map[b2]['n'] or '?'}")

                if sa.strip() and sb.strip():
                    try:
                        s1, s2 = int(sa), int(sb)
                        if s1 == s2:
                            st.error(f"❌ 第 {g_idx} 場平分")
                            court_error = True
                        
                        match_entry = {
                            'matchType': m_type, 'scoreType': score_type_val,
                            'event': f"{event_main}-C{cid}", 'date': global_date.strftime("%Y-%m-%d"),
                            'playerA1': p_map[a1]['n'], 'playerA1DuprId': p_map[a1]['id'],
                            'playerA2': p_map[a2]['n'] if a2 else '', 'playerA2DuprId': p_map[a2]['id'] if a2 else '',
                            'playerB1': p_map[b1]['n'], 'playerB1DuprId': p_map[b1]['id'],
                            'playerB2': p_map[b2]['n'] if b2 else '', 'playerB2DuprId': p_map[b2]['id'] if b2 else '',
                            'teamAGame1': s1, 'teamBGame1': s2,
                            'teamAGame2': '', 'teamBGame2': '', 'teamAGame3': '', 'teamBGame3': '',
                            'teamAGame4': '', 'teamBGame4': '', 'teamAGame5': '', 'teamBGame5': ''
                        }
                        court_matches.append(match_entry)
                        all_matches_combined.append(match_entry)
                    except: st.error("數字格式錯誤")

        # --- 單場地下載按鈕 ---
        if court_matches:
            st.divider()
            if court_error:
                st.warning(f"⚠️ 場地 {cid} 存在比分錯誤，無法下載。")
            else:
                df_court = pd.DataFrame(court_matches).reindex(columns=DUPR_COLS).fillna('')
                st.download_button(
                    label=f"📥 下載場地 {cid} 專屬 CSV",
                    data=df_court.to_csv(index=False).encode('utf-8'),
                    file_name=f"Court_{cid}_{datetime.datetime.now().strftime('%m%d')}.csv",
                    mime="text/csv",
                    key=f"dl_btn_{cid}"
                )

# --- 總結算匯出 ---
if all_matches_combined:
    st.divider()
    st.subheader("📦 全場地成績總匯出")
    df_all = pd.DataFrame(all_matches_combined).reindex(columns=DUPR_COLS).fillna('')
    st.download_button(
        label="🚀 下載所有場地合併 CSV (一次上傳 DUPR)",
        data=df_all.to_csv(index=False).encode('utf-8'),
        file_name=f"TNYP_Total_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True
    )
