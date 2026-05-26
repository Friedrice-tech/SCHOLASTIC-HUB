import streamlit as st
from supabase import create_client, Client
from datetime import date
import time

st.set_page_config(page_title="To-Do List", layout="wide", initial_sidebar_state="expanded")

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

#SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### Menu")

    if role == 'class_rep':
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Announcements", "Post/Share", "Notifications"]
        index_val = 3
    else:
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
        index_val = 3

    selection = st.radio("Navigation", options, index=index_val, key="todo_nav", label_visibility="collapsed") 

    # Routing Logic
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
    elif selection == "Notifications":
        st.switch_page("pages/Notification.py")
    elif selection != "To-Do List":
        st.info(f"The {selection} module is coming soon!")   

    st.divider()
    
    if st.button("Logout", use_container_width=True, key="todo_logout"):
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
    /* Standard Scholastic Hub Base */
    .stApp { background-color: #fafbfc; }
    [data-testid="stSidebarNav"] {display: none !important;}
    .block-container { padding-top: 5.5rem !important; padding-bottom: 3rem !important; max-width: 900px !important; }
    
    .sh-title { color: #f39c12; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: -15px; }
    .sh-dashboard { font-size: 24px; font-weight: 900; color: #0a2540; margin-bottom: -10px; }
    .sh-semester { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }
    .sh-divider { background-color: #f39c12; height: 3px; width: 60px; border-radius: 2px; margin-bottom: 30px; }

    /* Button Styling */
    div.stButton > button[kind="primary"] {
        background: #4285F4 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="primary"]:hover { background: #3367D6 !important; }
    
    /* Secondary Action Buttons (Done / Delete) */
    div[data-testid="column"] div.stButton > button {
        border-radius: 6px !important;
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
    }
    div[data-testid="column"] div.stButton > button:hover {
        border-color: #0a2540 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

#MAIN CONTENT
st.markdown('<div class="sh-title">SCHOLASTIC HUB</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-dashboard">Class To-Do List</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-semester">Track class assignments, projects, and upcoming deadlines.</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-divider"></div>', unsafe_allow_html=True)

#FETCH ALL TASKS FROM DATABASE
try:
    response = supabase.table('todos').select('*').order('due_date', desc=False).execute()
    db_tasks = response.data
except Exception as e:
    st.error(f"Database error: {e}")
    db_tasks = []

pending_tasks = [t for t in db_tasks if t['status'] == 'Pending']
completed_tasks = [t for t in db_tasks if t['status'] == 'Completed']

#ADD NEW TASK SECTION (CLASS REP ONLY)
if role == 'class_rep':
    st.markdown("#### Add New Task")
    with st.container(border=True):
        with st.form("add_task_form", clear_on_submit=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write("Task Title")
                new_title = st.text_input("Title", label_visibility="collapsed", placeholder="e.g. Complete Project Proposal")
            with col_b:
                st.write("Due Date")
                new_date = st.date_input("Date", value=date.today(), label_visibility="collapsed")
            
            # Empty space layout for button
            col_space, col_btn = st.columns([5, 1.2])
            with col_btn:
                submit_task = st.form_submit_button("Add Task", type="primary", use_container_width=True)
                
            if submit_task:
                if new_title:
                    with st.spinner("Saving..."):
                        try:
                            supabase.table("todos").insert({
                                "user_id": user.id,
                                "title": new_title,
                                "due_date": str(new_date),
                                "status": "Pending"
                            }).execute()
                            
                            #Send a notification when a new task is added!
                            supabase.table("notifications").insert({
                                "title": "New Task Added",
                                "desc": f"A new class deadline was added: {new_title}"
                            }).execute()
                            
                            st.success("Task Added!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not save task: {e}")
                else:
                    st.warning("Please enter a task title!")
    st.write("")

#PENDING TASKS
st.markdown("#### Pending Tasks")

if not pending_tasks:
    st.info("The class is all caught up! No pending tasks.")
else:
    for task in pending_tasks:
        with st.container(border=True):
            # Adjust column layout depending on role (students don't need button columns)
            if role == 'class_rep':
                p_col1, p_col2, p_col3, p_col4 = st.columns([4, 1.5, 0.7, 0.7], vertical_alignment="center")
            else:
                p_col1, p_col2 = st.columns([5.5, 1.5], vertical_alignment="center")

            with p_col1:
                st.markdown(f"<span style='color: #0a2540; font-weight: 600; font-size: 16px;'>{task['title']}</span>", unsafe_allow_html=True)
            with p_col2:
                st.markdown(f"<span style='color: #7f8c8d; font-size: 13px;'>📅 Due: {task['due_date']}</span>", unsafe_allow_html=True)
            
            # Action buttons ONLY visible to Class Rep
            if role == 'class_rep':
                with p_col3:
                    if st.button("✔️", key=f"done_{task['id']}", use_container_width=True, help="Mark as Complete"):
                        try:
                            supabase.table('todos').update({'status': 'Completed'}).eq('id', task['id']).execute()
                            st.rerun()
                        except Exception as e:
                            st.error("Error updating task.")
                with p_col4:
                    if st.button("🗑️", key=f"del_{task['id']}", use_container_width=True, help="Delete Task"):
                        try:
                            supabase.table('todos').delete().eq('id', task['id']).execute()
                            st.rerun()
                        except Exception as e:
                            st.error("Error deleting task.")

st.write("---")

#COMPLETED TASKS
with st.expander("Show Completed Tasks"):
    if not completed_tasks:
        st.write("No completed tasks yet.")
    else:
        for task in completed_tasks:
            with st.container(border=True):
                # Adjust column layout depending on role
                if role == 'class_rep':
                    c_col1, c_col2, c_col3 = st.columns([4, 1.5, 0.7], vertical_alignment="center")
                else:
                    c_col1, c_col2 = st.columns([4.7, 1.5], vertical_alignment="center")
                    
                with c_col1:
                    st.markdown(f"<span style='color: #94a3b8; text-decoration: line-through;'>{task['title']}</span>", unsafe_allow_html=True)
                with c_col2:
                    st.markdown(f"<span style='color: #94a3b8; font-size: 13px;'>Completed</span>", unsafe_allow_html=True)
                
                # Action button ONLY visible to Class Rep
                if role == 'class_rep':
                    with c_col3:
                        if st.button("🗑️", key=f"del_comp_{task['id']}", use_container_width=True, help="Delete Permanently"):
                            try:
                                supabase.table('todos').delete().eq('id', task['id']).execute()
                                st.rerun()
                            except Exception as e:
                                st.error("Error deleting task.")