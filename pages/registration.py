import streamlit as st
import base64
from supabase import create_client, Client

st.set_page_config(
    page_title="Scholastic Hub",
    layout="centered"
)

#SUPABASE API
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

@st.cache_data
def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

img_base64 = get_base64_image("background.jpg")
bg_img_css = f'background-image: url("data:image/jpg;base64,{img_base64}");' if img_base64 else ""

st.markdown(f"""
<style>
            
    header, [data-testid="stHeader"] {{
        display: none !important;
    }}

    html, body, [data-testid="stAppViewContainer"] {{
        overflow: hidden !important; 
        height: 100vh !important;  
    }}

    .stApp {{
        {bg_img_css}
        background-size: 100% 100%;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
        height: 100vh !important;
    }}

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        height: 100vh !important;
        display: flex !important;
        align-items: center !important; 
        justify-content: center !important;
    }}

    [data-testid="stVerticalBlock"] {{
        background-color: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(12px);
        padding: 40px 60px !important; /* Slightly less vertical padding */
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.6);
        box-shadow: 0px 20px 40px rgba(0,0,0,0.2);
        max-width: 650px;
        margin: auto !important;
    }}

    .title {{
        text-align: center;
        font-size: 38px; 
        font-weight: 900;
        color: #222;
        margin-bottom: 20px;
    }}

    .title {{
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        color: #222;
        margin-top: 0px !important;
        margin-bottom: 30px;
    }}

    .stButton > button {{
        width: 1000px !important;        
        background-color: #4285F4 !important;
        color: white !important;
        height: 55px !important;
        font-size: 20px !important;
        border-radius: 12px !important;
        border: none !important;
        transition: 0.3s;
    }}

    .stButton {{
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }}
    
    .login-text {{
        text-align: center;
        margin-top: 20px;
        font-size: 16px;
    }}

    .login-blue-text {{
        color: #4285F4;
        text-decoration: underline;
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

# REGISTER CARD
st.markdown('<div class="register-container">', unsafe_allow_html=True)

st.markdown(
    '<div class="title">Scholastic Hub Register</div>',
    unsafe_allow_html=True
)

# INPUT FIELDS
fullname = st.text_input("Full Name", placeholder="Enter your full name")
email = st.text_input("Institutional Email", placeholder="e.g. 202X-XXXXX@rtu.edu.ph")
student_number = st.text_input("Student Number", placeholder="202X-XXXXX")
password = st.text_input("Password", type="password" , placeholder="Password")
confirm_password = st.text_input("Confirm Password", type="password" , placeholder="Password")

# REGISTER BUTTON
if st.button("Register", type="primary"):
    # VALIDATION
    if not fullname or not email or not student_number or not password or not confirm_password:
        st.error("Please fill in all fields.")
    elif not email.endswith("@rtu.edu.ph"):
        st.error("Please use your institutional email.")
    elif password != confirm_password:
        st.error("Passwords do not match.")
    elif len(password) < 8:
        st.error("Password must be at least 8 characters.")
    else:
        with st.spinner("Creating your account..."):
            try:
                #API creates account
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": {
                            "full_name": fullname,
                            "student_id": student_number,
                            "role": "student"
                        }
                    }
                })
                st.success("Registration Successful! You can now log in.")
            except Exception as e:
                st.error(f"Registration Error: {str(e)}")

# LOGIN FOOTER
if st.button("Already have an account? Login", type="secondary", use_container_width=True):
    st.switch_page("login.py")

st.markdown('</div>', unsafe_allow_html=True)