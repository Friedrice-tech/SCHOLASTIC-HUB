import streamlit as st
from supabase import create_client, Client
from datetime import datetime

st.set_page_config(page_title="Notification", layout="wide")

#SESSION STATE
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

#API SUPABASE
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

user = st.session_state.user
role = user.user_metadata.get('role', 'student')

#SIDE BAR NAVIGATION
with st.sidebar:
    st.markdown("### Menu")

    if role == 'class_rep':
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    else:
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]

    selection = st.radio("Navigation", options, index=len(options)-1, key="notif_nav", label_visibility="collapsed") 

    if selection == "Dashboard":
        if role == 'class_rep':
            st.switch_page("pages/class_rep_dashboard.py")
        else:
            st.switch_page("pages/dashboard.py")
    elif selection == "Profile":
        st.switch_page("pages/Profile.py")
    elif selection == "Schedule":
        st.switch_page("pages/schedule.py")
    elif selection == "Courses":
        st.switch_page("pages/LectureFile.py")
    elif selection == "Post/Share":                   
        st.switch_page("pages/post_share.py")
    elif selection == "To-Do List":                 
        st.switch_page("pages/To_Do.py")
    elif selection != "Notifications":
        st.info(f"The {selection} module is coming soon!")   

    st.divider()
    
    if st.button("Logout", use_container_width=True, key="notif_logout"):
        with st.spinner("Logging out..."):
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            st.session_state.logged_in = False
            st.session_state.user = None
            if 'uploaded_avatar' in st.session_state:
                del st.session_state['uploaded_avatar']
            st.switch_page("login.py")  

# 2. HYBRID DESIGN CSS
st.markdown("""
<style>
   /* Standard Scholastic Hub Base */
    .stApp { background-color: #fafbfc; }
    [data-testid="stSidebarNav"] {display: none !important;}
    .block-container { padding-top: 5.5rem !important; padding-bottom: 3rem !important; max-width: 1200px !important; }
    
    .sh-title { color: #f39c12; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: -15px; }
    .sh-dashboard { font-size: 24px; font-weight: 900; color: #0a2540; margin-bottom: -10px; }
    .sh-semester { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }
    .sh-divider { background-color: #f39c12; height: 3px; width: 60px; border-radius: 2px; margin-bottom: 30px; }

    /* Notification Item Styling (Adapted from your design) */
    .notif-item {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        border: 1px solid #e0e6ed;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .notif-item:hover {
        transform: translateY(-2px);
        border-color: #003C8F; /* Changed hover border to RTU Blue */
        box-shadow: 0 6px 12px rgba(0,0,0,0.05);
    }

    .status-dot {
        height: 12px; width: 12px;
        background-color: #10b981; /* Green active dot */
        border-radius: 50%;
        margin-right: 20px;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
    }

    /* Search Bar Styling */
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #e0e6ed !important;
        background-color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 style="text-align: center; margin-bottom: 0;">Notifications</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #64748b; font-size: 14px;">Recent updates from your school portal</p>', unsafe_allow_html=True)


search_query = st.text_input("Search", placeholder="Search notifications...", label_visibility="collapsed")
st.write("")

# Helper to calculate "Time Ago" with safety fallback parsing
def get_time_ago(created_at_str):
    try:
        # Strip timezone indicators to avoid parsing conflicts in older Python versions
        if 'Z' in created_at_str:
            created_at_str = created_at_str.replace('Z', '')
        if '+' in created_at_str:
            created_at_str = created_at_str.split('+')[0]
        if '.' in created_at_str:
            created_at_str = created_at_str.split('.')[0]
            
        created_time = datetime.fromisoformat(created_at_str)
        now = datetime.utcnow()
        diff = now - created_time
        seconds = diff.total_seconds()
        
        if seconds < 0:
            return "Just now"
        if seconds < 60: 
            return "Just now"
        elif seconds < 3600: 
            return f"{int(seconds/60)} mins ago"
        elif seconds < 86400: 
            return f"{int(seconds/3600)} hours ago"
        else: 
            return f"{int(seconds/86400)} days ago"
    except Exception:
        return "Recently"


#FETCH & FILTER NOTIFICATIONS
try:
    response = supabase.table('notifications').select('*').order('created_at', desc=True).execute()
    notifications_api = response.data
except Exception as e:
    st.error(f"⚠️ Supabase Error: Could not connect to the 'notifications' table. Details: {e}")
    notifications_api = []

# Dynamically filter notifications if the search bar is used
if search_query and notifications_api:
    notifications_api = [
        n for n in notifications_api 
        if search_query.lower() in n['title'].lower() or search_query.lower() in n['desc'].lower()
    ]


#RENDER DATA FEED
if not notifications_api:
    st.markdown("""
        <div style="text-align: center; padding: 60px 0;">
            <div style="font-size: 50px; margin-bottom: 20px;">🕊️</div>
            <h4 style="color: #475569;">No notifications match your query</h4>
            <p style="color: #94a3b8; font-size: 14px;">Once updates are published by the Class Representative, they will show up here.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    for n in notifications_api:
        time_ago = get_time_ago(n['created_at'])
        st.markdown(f"""
            <div class="notif-item">
                <div class="status-dot"></div>
                <div style="flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 700; color: #0a2540; font-size: 16px;">{n['title']}</span>
                        <span style="font-size: 12px; color: #94a3b8; font-weight: 500;">{time_ago}</span>
                    </div>
                    <div style="font-size: 14px; color: #64748b; margin-top: 5px;">{n['desc']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)