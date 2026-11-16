import streamlit as st
import pandas as pd
from db_utils import get_leaf_df, set_leaf_df, reset_leaf_df, SPECIES_LIST

st.set_page_config(page_title="1. 데이터 입력 및 DB 구축", page_icon="📥", layout="wide")

if not st.session_state.get('logged_in', False):
    st.warning("🔒 서비스를 이용하려면 먼저 메인 페이지(run)에서 로그인해 주세요.")
    st.stop()

st.title("📥 1. 나뭇잎 데이터 입력 및 웹 DB 구축")
st.markdown("실측한 나뭇잎의 **가로(X), 세로(Y), 잎자루 길이(Z)** 데이터를 웹 데이터베이스에 저장하거나 CSV 파일로 일괄 업로드·다운로드합니다.")

df = get_leaf_df()

col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("➕ 단일 데이터 직접 입력")
    with st.form("add_leaf_form", clear_on_submit=True):
        species = st.selectbox("식물 종 (Label)", SPECIES_LIST)
        item_name = st.text_input("개체명 (선택)", placeholder="예: 은행31")
        width = st.number_input("가로 길이 (X축, cm)", min_value=0.0, max_value=100.0, value=6.0, step=0.1)
        length = st.number_input("세로 길이 (Y축, cm)", min_value=0.0, max_value=100.0, value=8.0, step=0.1)
        petiole = st.number_input("잎자루 길이 (Z축, cm)", min_value=0.0, max_value=100.0, value=2.5, step=0.1)
        submitted = st.form_submit_button("💾 웹 DB에 저장", use_container_width=True)
        if submitted:
            if not item_name.strip():
                count_sp = len(df[df['종'] == species]) + 1
                item_name = f"{species}{count_sp}"
            new_row = pd.DataFrame([{
                '개체명': item_name.strip(),
                '종': species,
                '가로': float(width),
                '세로': float(length),
                '잎자루': float(petiole),
                '가짜여부': False
            }])
            set_leaf_df(pd.concat([df, new_row], ignore_index=True))
            st.success(f"✅ '{item_name}' ({species}) 데이터가 웹 DB에 저장되었습니다!")
            st.rerun()

    st.divider()
    st.subheader("📁 CSV 파일 일괄 업로드")
    uploaded_file = st.file_uploader("CSV 파일 선택 (열: 종, 가로, 세로, 잎자루)", type=["csv"])
    if uploaded_file is not None:
        try:
            up_df = pd.read_csv(uploaded_file)
            col_map = {}
            for c in up_df.columns:
                if '종' in c or 'species' in c.lower():
                    col_map[c] = '종'
                elif '가로' in c or 'width' in c.lower():
                    col_map[c] = '가로'
                elif '세로' in c or 'length' in c.lower():
                    col_map[c] = '세로'
                elif '잎자루' in c or 'petiole' in c.lower():
                    col_map[c] = '잎자루'
                elif '개체' in c or 'name' in c.lower():
                    col_map[c] = '개체명'
                elif '가짜' in c or 'fake' in c.lower():
                    col_map[c] = '가짜여부'
            up_df = up_df.rename(columns=col_map)
            required = ['종', '가로', '세로', '잎자루']
            if all(r in up_df.columns for r in required):
                up_df['종'] = up_df['종'].astype(str).str.replace(r'\d+', '', regex=True).replace({'화살난무': '화살나무'})
                if '개체명' not in up_df.columns:
                    up_df['개체명'] = [f"{s}_업로드{i+1}" for i, s in enumerate(up_df['종'])]
                if '가짜여부' not in up_df.columns:
                    up_df['가짜여부'] = False
                else:
                    up_df['가짜여부'] = up_df['가짜여부'].isin([True, 'True', 'true', 'O', 'o', 1, '1'])
                up_df = up_df[['개체명', '종', '가로', '세로', '잎자루', '가짜여부']]
                if st.button("📥 업로드 데이터 DB에 병합하기", use_container_width=True):
                    set_leaf_df(pd.concat([df, up_df], ignore_index=True))
                    st.success(f"🎉 {len(up_df)}개의 데이터가 추가되었습니다!")
                    st.rerun()
            else:
                st.error(f"필수 열({required})이 CSV 파일에 포함되어 있어야 합니다.")
        except Exception as e:
            st.error(f"CSV 파일 처리 중 오류 발생: {e}")

    st.divider()
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        csv_bytes = df[['개체명', '종', '가로', '세로', '잎자루']].to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("📤 현재 DB CSV 저장", data=csv_bytes, file_name="leaf_db_export.csv", mime="text/csv", use_container_width=True)
    with c_btn2:
        if st.button("🔄 기본 CSV로 초기화", use_container_width=True):
            reset_leaf_df()
            st.info("기본 나뭇잎 데이터셋(180개)으로 초기화되었습니다.")
            st.rerun()

with col2:
    st.subheader(f"📊 현재 웹 데이터베이스 현황 (총 {len(df)}개)")
    st.caption("기본 세팅 데이터셋(은행, 단풍, 벚나무, 감나무, 밤나무, 화살나무 각 30개씩 총 180개)이 로드되어 있습니다.")
    
    counts = df['종'].value_counts()
    m_cols = st.columns(len(SPECIES_LIST))
    for idx, sp in enumerate(SPECIES_LIST):
        m_cols[idx].metric(label=sp, value=f"{counts.get(sp, 0)}개")

    display_df = df[['개체명', '종', '가로', '세로', '잎자루']].copy()
    st.dataframe(display_df, use_container_width=True, height=450)
