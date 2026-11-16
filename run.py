import streamlit as st
import sqlite3
import pytz
from datetime import datetime

st.set_page_config(page_title="AI 나뭇잎 분류 & 윤리 시뮬레이터", page_icon="🌱")

# DB 및 테이블 초기화
def init_db():
    conn = sqlite3.connect('myproject.db')
    c = conn.cursor()
    # 사용자 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id_num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username TEXT NOT NULL,
                    userid TEXT UNIQUE NOT NULL,
                    passwd TEXT NOT NULL,
                    created_at TEXT NOT NULL)''')
    # 실태조사 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
                    id_num INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    userid TEXT NOT NULL,
                    q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
                    q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
                    created_at TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# 세션 상태 초기화 (로그인 유지용)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'userid' not in st.session_state:
    st.session_state['userid'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

# 비로그인 상태일 때 랜딩 페이지 노출 (탭 메뉴)
if not st.session_state['logged_in']:
    st.title("🌱 AI 나뭇잎 분류 & 윤리 시뮬레이터")
    st.write("서비스를 이용하려면 로그인이 필요합니다.")
    
    tab1, tab2 = st.tabs(["로그인", "신규등록"])
    
    # --- 로그인 탭 ---
    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            login_id = st.text_input("아이디")
            login_pw = st.text_input("비밀번호", type="password")
            submit_login = st.form_submit_button("로그인")
            
            if submit_login:
                if login_id and login_pw:
                    conn = sqlite3.connect('myproject.db')
                    c = conn.cursor()
                    c.execute("SELECT username FROM users WHERE userid=? AND passwd=?", (login_id, login_pw))
                    result = c.fetchone()
                    conn.close()
                    
                    if result:
                        st.session_state['logged_in'] = True
                        st.session_state['userid'] = login_id
                        st.session_state['username'] = result[0]
                        st.success(f"{result[0]}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("아이디와 비밀번호를 모두 입력해 주세요.")
                    
    # --- 신규등록 탭 ---
    with tab2:
        st.subheader("신규 회원가입")
        with st.form("signup_form"):
            reg_name = st.text_input("이름")
            reg_id = st.text_input("아이디")
            reg_pw = st.text_input("비밀번호", type="password")
            reg_pw2 = st.text_input("비밀번호 확인", type="password")
            submit_signup = st.form_submit_button("가입하기")
            
            if submit_signup:
                if not reg_name or not reg_id or not reg_pw:
                    st.warning("모든 항목을 입력해 주세요.")
                elif reg_pw != reg_pw2:
                    st.warning("비밀번호가 일치하지 않습니다.")
                else:
                    try:
                        conn = sqlite3.connect('myproject.db')
                        c = conn.cursor()
                        # 한국표준시(KST) 적용
                        kst = pytz.timezone('Asia/Seoul')
                        now = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
                        c.execute("INSERT INTO users (username, userid, passwd, created_at) VALUES (?, ?, ?, ?)",
                                  (reg_name, reg_id, reg_pw, now))
                        conn.commit()
                        conn.close()
                        st.success("회원가입이 완료되었습니다. 로그인 탭에서 로그인해 주세요.")
                    except sqlite3.IntegrityError:
                        st.error("이미 존재하는 아이디입니다.")

# 로그인 상태일 때 메인 화면 노출
else:
    st.title("🌱 AI 나뭇잎 분류 & 윤리 시뮬레이터에 오신 것을 환영합니다!")
    st.write(f"**{st.session_state['username']}**님, 환영합니다! 🎉")
    st.write("좌측 사이드바 메뉴를 통해 **1) 데이터 입력 및 DB 구축**, **2) 3D 산점도 시각화 및 이상치 검증**, **3) AI 자동 분류 시뮬레이터**, **4) AI 윤리 실태조사**를 순차적으로 진행해 보세요.")
    
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['userid'] = None
        st.session_state['username'] = None
        st.rerun()
