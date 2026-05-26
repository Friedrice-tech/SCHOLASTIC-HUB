import streamlit as st
import base64
from supabase import create_client, Client



st.set_page_config(page_title="Scholastic Hub", layout="centered")

if 'page' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'login'

#SUPABASE API
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

#BACKGROUND IMAGE
@st.cache_data
def get_base64_of_bin_file(bin_file):
    """Reads a local image file and converts it to a base64 string."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    bg_base64 = get_base64_of_bin_file('background.jpg')

    bg_image_css = f'background-image: url("data:image/jpeg;base64,{bg_base64}");'
except FileNotFoundError:
    bg_image_css = 'background-color: #f4f4f4;'
col1, col2, col3 = st.columns([1, 2, 1])

#CSS
st.markdown(f"""
    <style>
    
    [data-testid="stSidebarNav"] {{display: none !important;}}
    
    [data-testid="stAppViewContainer"] {{
        {bg_image_css}
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    /* SOLID WHITE LOGIN CARD (No Blur) */
    div[data-testid="stColumn"]:nth-of-type(2) > div,
    div[data-testid="column"]:nth-of-type(2) > div {{
        background-color: #ffffff !important; /* 100% Solid White */
        backdrop-filter: none !important; /* Removes any blur */
        -webkit-backdrop-filter: none !important; 
        padding: 2.5rem !important;
        border-radius: 10px !important; 
        border: 1px solid #eaeaea !important; 
        box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.15) !important; 
    }}

    .card-title {{ text-align: center; font-family: 'Arial', sans-serif; font-weight: bold; color: #333; margin-bottom: 20px; padding-top: 10px; }}
    div.stButton > button[kind="primary"] {{ background-color: #4A90E2; color: white; border-radius: 5px; height: 45px; width: 100%; border: none; font-weight: bold; margin-top: 10px; }}
    div.stButton > button[kind="primary"]:hover {{ background-color: #357ABD; color: white; }}
    div.stButton > button[kind="secondary"] {{ background-color: transparent; color: #4A90E2; border: none; box-shadow: none; padding: 0; margin-top: 5px; }}
    div.stButton > button[kind="secondary"]:hover {{ text-decoration: underline; color: #357ABD; background-color: transparent; }}
    div[data-baseweb="input"] {{ border-radius: 5px !important; border: 1px solid #cccccc !important; background-color: white !important; }}
    </style>
""", unsafe_allow_html=True)

with col2:
   
    if st.session_state.page == 'login':
        with st.container(border=True):
            st.markdown('<h2 class="card-title">Scholastic Hub Login</h2>', unsafe_allow_html=True)
            
            email = st.text_input("Email", placeholder="Institutional Email", label_visibility="collapsed")
            password = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
            
            if st.button("Login", type="primary", use_container_width=True):
                if email.endswith("@rtu.edu.ph"):
                    with st.spinner("Logging in......."):
                        #API CALL FOR THE LOG IN
                        try:
                            #API CALL: WILL VERIFY THE STUDENTS CREDENTIALS
                            response = supabase.auth.sign_in_with_password({"email": email, "password": password})

                            #WILL EXTRACT TGE STUDENTS DATA
                            student_user = response.user
                            st.session_state.user = student_user
                            st.session_state.logged_in = True

                            # API ROUTING LOGIC FOR THE STUDENT DASHBOARD AND CLASS REP DASH BOARD
                            student_role =  student_user.user_metadata.get('role', 'student') # Defaults to student if no class reps account found

                            if student_role == 'class_rep':
                                st.switch_page("pages/class_rep_dashboard.py")
                            else:
                                st.switch_page("pages/dashboard.py")
                        
                        except Exception as e:
                            st.error(f"Invalid Email or Password")
                else:
                    st.error("Invalid Email")
           
            st.markdown('<div class="link-container">', unsafe_allow_html=True)
        if st.button("Forgot Password?", type="secondary", use_container_width=True):
            st.info("Password reset link would be sent to your email.")
        
        if st.button("Create an Account", type="secondary", use_container_width=True):
            st.switch_page("pages/registration.py")
        st.markdown('</div>', unsafe_allow_html=True)