import streamlit as st
import pandas as pd
import datetime

# 1. 設置頁面配置
st.set_page_config(page_title="TNYP DUPR 驗證錄入系統", page_icon="🏓", layout="wide")

# ==========================================
# 賽程邏輯定義
# ==========================================
SCHEDULE_8 = [("A", "B", "C", "D"), ("E", "F", "G", "H"), ("A", "C", "B", "D"), ("E", "G", "F", "H"), ("A", "D", "B", "C"), ("E", "H", "F", "G"), ("A", "E", "B", "F"), ("C", "G", "D", "H"), ("A", "F", "B", "E"), ("C", "H", "D", "G"), ("A", "G", "B", "H"), ("C", "E", "D", "F"), ("A", "H", "B", "G"), ("C", "F", "D", "E"), ("A", "B", "E", "F"), ("G", "H", "C", "D"), ("E", "G", "B", "D"), ("F", "H", "A", "C"), ("A", "D", "F", "G")]
SCHEDULE_7 = [("G", "D", "F", "E"), ("B", "G", "C", "A"), ("D", "F", "E", "C"), ("A", "B", "G", "F"), ("E", "A", "C", "D"), ("B", "F", "G", "C"), ("A", "D", "E", "B"), ("G", "A", "F", "C"), ("B", "D", "E", "G"), ("F", "A", "C", "E"), ("D", "F", "B", "G"), ("E", "A", "C", "B"), ("D", "E", "F", "G"), ("A", "B", "C", "D"), ("G", "D", "F", "E"), ("B", "G", "C", "A"), ("E", "G", "B", "D"), ("F", "A", "C", "G"), ("A", "D", "F", "G")]

st.title("🏓 TNYP DUPR 專業驗證錄入系統")

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 全域設定")
    event_main = st.text_input("活動名稱", value="TNYP Club Match")
    global_date = st.date_input("日期", datetime.date.today())
    # 比賽進行方式修改
    global_score_type = st.selectbox("計分方式 (Score Type)", ["RALLY (落地得分)", "SIDEOUT (發球得分)"])
    score_type_val = "RALLY" if "RALLY" in global_score_type else "SIDEOUT"
    
    court_count = st.number_input("場地數量", min_value=1, max_value=6, value=2)
    st.divider()
    st.warning("⚠️ 注意：DUPR ID 為必填且不可重複")

# 建立場地頁籤
tab_list = st.tabs([f"🏟️ 場地 {i+1}" for i in range(court_count)])

all_matches_to_export = []
draw_found = False
id_error_found = False

for i in range(court_count):
    cid = i + 1
    with tab_list[i]:
        mode = st.radio(f"場地 {cid} 賽制", ["8人制", "7人制"], key=f"m_{cid}", horizontal=True)
        p_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] if mode == "8人制" else ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        sch = SCHEDULE_8 if mode == "8人制" else SCHEDULE_7
        
        # --- 球員名單與 ID 檢查 ---
        with st.expander(f"👤 場地 {cid} 球員名單與 ID 驗證", expanded=True):
            p_map = {}
            col1, col2 = st.columns(2)
            temp_ids = []
            for idx, l in enumerate(p_labels):
                target_col = col1 if idx % 2 == 0 else col2
                with target_col:
                    st.markdown(f"**球員 {l}**")
                    n = st.text_input(f"姓名", key=f"n_{cid}_{l}", placeholder="輸入姓名")
                    did = st.text_input(f"ID", key=f"id_{cid}_{l}", placeholder="輸入 DUPR ID (如: BK5V6D)")
                    
                    # 驗證 ID 格式 (DUPR ID 通常為 6 位大寫英數)
                    if did:
                        if len(did) != 6:
                            st.caption("⚠️ ID 長度建議為 6 位")
                        if did in temp_ids:
                            st.error(f"❌ ID {did} 重複出現！")
                            id_error_found = True
                        temp_ids.append(did)
                    
                    p_map[l] = {"n": n, "id": did}

        # --- 比分錄入 ---
        st.subheader(f"🎯 比分錄入 (計分制: {score_type_val})")
        for g_idx, (a1, a2, b1, b2) in enumerate(sch, 1):
            with st.container(border=True):
                c1, c2, mid, c3, c4 = st.columns([2, 1, 0.5, 1, 2])
                with c1: 
                    st.write(f"**{a1}:** {p_map[a1]['n'] or '未填'}")
                    st.write(f"**{a2}:** {p_map[a2]['n'] or '未填'}")
                with c2: sa_val = st.text_input("A", key=f"sA_{cid}_{g_idx}", label_visibility="collapsed")
                with mid: st.write("-")
                with c3: sb_val = st.text_input("B", key=f"sB_{cid}_{g_idx}", label_visibility="collapsed")
                with c4: 
                    st.write(f"**{b1}:** {p_map[b1]['n'] or '未填'}")
                    st.write(f"**{b2}:** {p_map[b2]['n'] or '未填'}")
                
                if sa_val.strip() and sb_val.strip():
                    try:
                        sA, sB = int(sa_val), int(sb_val)
                        if sA == sB:
                            st.error(f"❌ 場次 {g_idx}: 平分 ({sA}:{sB}) DUPR 不接受。")
                            draw_found = True
                        
                        # 檢查該場比賽球員 ID 是否齊全
                        current_ids = [p_map[a1]['id'], p_map[a2]['id'], p_map[b1]['id'], p_map[b2]['id']]
                        if "" in current_ids:
                            st.warning(f"⚠️ 場次 {g_idx}: 仍有球員 ID 未填寫，無法匯出。")
                            id_error_found = True

                        match_data = {
                            'matchType': 'D', 'scoreType': score_type_val,
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
                        all_matches_to_export.append(match_data)
                    except ValueError:
                        st.error(f"❌ 場次 {g_idx}: 請輸入整數比分")

# --- 匯出控制 ---
st.divider()
if all_matches_to_export:
    if draw_found:
        st.error("🚫 偵測到平手比分，請修正後下載。")
    elif id_error_found:
        st.error("🚫 偵測到 ID 重複或未填，請修正後下載。")
    else:
        st.success(f"✅ 驗證通過：共 {len(all_matches_to_export)} 場比賽準備就緒。")
        df_total = pd.DataFrame(all_matches_to_export)
        
        # 嚴格排序 DUPR 官方欄位
        cols_order = ['matchType','scoreType','event','date','playerA1','playerA1DuprId','playerA2','playerA2DuprId','playerB1','playerB1DuprId','playerB2','playerB2DuprId','teamAGame1','teamBGame1','teamAGame2','teamBGame2','teamAGame3','teamBGame3','teamAGame4','teamBGame4','teamAGame5','teamBGame5']
        df_total = df_total.reindex(columns=cols_order).fillna('')
        
        final_csv = df_total.to_csv(index=False, encoding='utf-8').encode('utf-8')
        st.download_button(
            label="🚀 下載驗證合格的 DUPR CSV",
            data=final_csv,
            file_name=f"TNYP_Verified_{datetime.datetime.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
