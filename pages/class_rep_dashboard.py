import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")

#AUTHENTICATION CHECK & SUPABASE API
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("app.py")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase: Client = init_connection()

user = st.session_state.user
role = user.user_metadata.get('role', 'student')
user_name = user.user_metadata.get('full_name', 'Class Rep')

if role != 'class_rep':
    st.switch_page("pages/dashboard.py")

# --- REAL-TIME PRESENCE UPDATE ---
try:
    supabase.table('profiles').update({
        'last_active': datetime.now(timezone.utc).isoformat()
    }).eq('id', user.id).execute()
except Exception:
    pass

#SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### Menu")
    options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    selection = st.radio("Navigation", options, index=0, key="global_nav", label_visibility="collapsed") 

    if selection == "Dashboard":
        pass 
    elif selection == "Profile":
        st.switch_page("pages/Profile.py")
    elif selection == "Schedule":
        st.switch_page("pages/schedule.py")
    elif selection == "To-Do List":
        st.switch_page("pages/To_Do.py")
    elif selection == "Courses":
        st.switch_page("pages/LectureFile.py")
    elif selection == "Post/Share":
        st.switch_page("pages/post_share.py")
    elif selection == "Notifications":
        st.switch_page("pages/Notification.py")
    else:
        st.info(f"The {selection} module is coming soon!")   

    st.divider()
    
    if st.button("Logout", use_container_width=True, key="global_logout"):
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

#CSS
st.markdown("""
<style>
    .stApp { background-color: #fafbfc; }
    [data-testid="stSidebarNav"] {display: none !important;}
    .block-container { padding-top: 5.5rem !important; padding-bottom: 3rem !important; max-width: 1100px !important; }
    
    .sh-title { color: #f39c12; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: -15px; }
    .sh-dashboard { font-size: 24px; font-weight: 900; color: #0a2540; margin-bottom: -10px; }
    .sh-semester { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }
    .sh-divider { background-color: #f39c12; height: 3px; width: 60px; border-radius: 2px; margin-bottom: 30px; }

    /* Class Rep Banner (Gold Theme) */
    .welcome-banner {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #f39c12;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .welcome-title { font-size: 28px; font-weight: 900; color: #0a2540; margin-bottom: 5px; }
    .welcome-subtitle { font-size: 15px; color: #475569; }

    /* Metric Cards */
    .metric-card {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #e0e6ed;
        border-top: 4px solid #0a2540;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s ease;
        height: 125px;
        display: flex;
        flex-direction: column;
    }
    .metric-card:hover { transform: translateY(-3px); box-shadow: 0 6px 12px rgba(0,0,0,0.05); }
    .metric-label { color: #7f8c8d; font-size: 13px; font-weight: 600; margin-bottom: 10px; }
    .metric-value { font-size: 32px; font-weight: 900; color: #0a2540; line-height: 1; }

    /* Active Users List Styling */
    .active-users-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
        overflow-y: auto;
        padding-right: 5px;
        flex-grow: 1;
    }
    .active-users-container::-webkit-scrollbar { width: 4px; }
    .active-users-container::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
    
    .active-user-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .active-avatar {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        object-fit: cover;
        background-color: #e2e8f0;
        color: #0f172a;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: 800;
        flex-shrink: 0;
    }
    .active-name {
        font-size: 14px;
        color: #334155;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Summary Activity Cards */
    .summary-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e0e6ed;
        margin-top: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        height: 100%;
    }
    .summary-header {
        font-size: 16px;
        font-weight: 800;
        color: #0a2540;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }
    .summary-item { margin-bottom: 12px; }
    .summary-item:last-child { margin-bottom: 0; }
    .summary-title { font-size: 14px; font-weight: 600; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .summary-meta { font-size: 12px; color: #7f8c8d; margin-top: 2px; }

    /* About Section */
    .about-card {
        background-color: white;
        border-radius: 12px;
        padding: 30px;
        border: 1px solid #e0e6ed;
        margin-top: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .about-title { font-size: 18px; font-weight: 800; color: #0a2540; margin-bottom: 15px; }
    .about-text { font-size: 15px; color: #475569; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)


#FETCH DYNAMIC DATA (METRICS + SUMMARIES)
total_students, active_count, pending_tasks, total_courses = 0, 1, 0, 0
active_users_list, upcoming_tasks, recent_posts, recent_courses = [], [], [], []

try:
    # --- Metrics ---
    profiles_res = supabase.table('profiles').select('id', count='exact').execute()
    total_students = profiles_res.count if profiles_res.count else 0
    
    fifteen_mins_ago = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
    active_res = supabase.table('profiles').select('full_name, avatar_url').gte('last_active', fifteen_mins_ago).execute()
    active_users_list = active_res.data if active_res.data else []

    tasks_res = supabase.table('todos').select('id', count='exact').eq('status', 'Pending').execute()
    pending_tasks = tasks_res.count if tasks_res.count else 0

    courses_res = supabase.table('courses').select('id', count='exact').execute()
    total_courses = courses_res.count if courses_res.count else 0

    # --- Summaries ---
    # Top 3 Upcoming Tasks
    t_res = supabase.table('todos').select('title, due_date').eq('status', 'Pending').order('due_date').limit(3).execute()
    upcoming_tasks = t_res.data
    
    # Top 3 Recent Posts
    p_res = supabase.table('posts').select('author_name, content').order('created_at', desc=True).limit(3).execute()
    recent_posts = p_res.data

    # Top 3 Course 
    c_res = supabase.table('courses').select('*').limit(3).execute()
    recent_courses = c_res.data

except Exception as e:
    st.warning("Dashboard data is currently syncing...")

# --- GENERATE ACTIVE USERS HTML ---
if not any(u.get('full_name') == user_name for u in active_users_list):
    local_avatar = st.session_state.get('uploaded_avatar')
    active_users_list.insert(0, {'full_name': user_name, 'avatar_url': local_avatar})

active_count = len(active_users_list)
active_html = ""

for u in active_users_list:
    name = u.get('full_name') or 'Class Rep'
    avatar = u.get('avatar_url')
    
    if avatar:
        avatar_div = f'<img src="{avatar}" class="active-avatar">'
    else:
        initials = "".join([n[0] for n in name.split()[:2]]).upper() if name else "CR"
        avatar_div = f'<div class="active-avatar">{initials}</div>'
        
    active_html += f'<div class="active-user-row">{avatar_div}<div class="active-name" title="{name}">{name}</div></div>'

#RENDER DASHBOARD
st.markdown('<div class="sh-title">SCHOLASTIC HUB</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-dashboard">Class Representative Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-divider"></div>', unsafe_allow_html=True)

# Welcome Banner
st.markdown(f"""
    <div class="welcome-banner">
        <div class="welcome-title">Welcome, {user_name}!</div>
        <div class="welcome-subtitle">You are logged in as the <b>Class Representative</b>. From here, you have elevated privileges to upload files, modify the schedule, and assign tasks to the class.</div>
    </div>
""", unsafe_allow_html=True)

# Dynamic Metric Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Students</div>
            <div class="metric-value" style="margin-top: auto;">{total_students}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card" style="border-top-color: #10b981; padding-bottom: 10px;">
            <div class="metric-label" style="margin-bottom: 8px;">🟢 Active Online ({active_count})</div>
            <div class="active-users-container">
                {active_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card" style="border-top-color: #f39c12;">
            <div class="metric-label">Pending Class Tasks</div>
            <div class="metric-value" style="margin-top: auto;">{pending_tasks}</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card" style="border-top-color: #4285F4;">
            <div class="metric-label">Courses</div>
            <div class="metric-value" style="margin-top: auto;">{total_courses}</div>
        </div>
    """, unsafe_allow_html=True)

# --- CLASSROOM ACTIVITY SUMMARIES ---
sum_col1, sum_col2, sum_col3 = st.columns(3)

with sum_col1:
    tasks_html = ""
    if not upcoming_tasks:
        tasks_html = "<div class='summary-meta'>No pending deadlines.</div>"
    else:
        for t in upcoming_tasks:
            tasks_html += f"<div class='summary-item'><div class='summary-title'>{t['title']}</div><div class='summary-meta'>📅 Due: {t['due_date']}</div></div>"
            
    st.markdown(f"""
        <div class="summary-card">
            <div class="summary-header">Upcoming Deadlines</div>
            {tasks_html}
        </div>
    """, unsafe_allow_html=True)

with sum_col2:
    posts_html = ""
    if not recent_posts:
        posts_html = "<div class='summary-meta'>No recent discussions.</div>"
    else:
        for p in recent_posts:
            # Truncate content slightly for the summary view
            snippet = p['content'][:45] + "..." if len(p['content']) > 45 else p['content']
            posts_html += f"<div class='summary-item'><div class='summary-title'>🗣️ {p['author_name']}</div><div class='summary-meta'>{snippet}</div></div>"
            
    st.markdown(f"""
        <div class="summary-card">
            <div class="summary-header">Recent Discussions</div>
            {posts_html}
        </div>
    """, unsafe_allow_html=True)

with sum_col3:
    courses_html = ""
    if not recent_courses:
        courses_html = "<div class='summary-meta'>No course folders found.</div>"
    else:
        for c in recent_courses:
            c_name = c.get('course_name', c.get('title', c.get('name', 'Course Folder')))
            c_code = c.get('course_code', c.get('code', '📁'))
            courses_html += f"<div class='summary-item'><div class='summary-title'>{c_code} - {c_name}</div><div class='summary-meta'>Active Repository</div></div>"
            
    st.markdown(f"""
        <div class="summary-card">
            <div class="summary-header">Active Courses</div>
            {courses_html}
        </div>
    """, unsafe_allow_html=True)

# About Section
st.markdown("""
    <div class="about-card">
        <div class="about-title">About Scholastic Hub</div>
        <div class="about-text">
            <b>Scholastic Hub</b> is your centralized digital classroom portal designed exclusively to streamline academic communication, resource sharing, and task management. 
            <br><br>
            As the <b>Class Representative</b>, you are the bridge between the faculty and the students. Use the <b>Schedule</b> page to update the class calendar, create global deadlines in the <b>To-Do List</b>, and securely upload official study materials to the <b>Courses</b> repository. Any updates you make are broadcast instantly to the entire student body in their <b>Notifications</b> feed.
        </div>
    </div>
""", unsafe_allow_html=True)