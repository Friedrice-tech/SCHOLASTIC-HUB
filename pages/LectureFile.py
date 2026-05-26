from supabase import create_client, Client
import streamlit as st
import time
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Course", layout="wide", initial_sidebar_state="expanded")


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

#STATE MANAGEMENT

if 'selected_course' not in st.session_state:
    st.session_state.selected_course = None
if 'show_add_course' not in st.session_state:
    st.session_state.show_add_course = False

def open_course(course_name):
    st.session_state.selected_course = course_name

def back_to_courses():
    st.session_state.selected_course = None

def toggle_add_course():
    st.session_state.show_add_course = not st.session_state.show_add_course

#SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### Menu")

    if role == 'class_rep':
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    else:
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    
    selection = st.radio("Navigation", options, index=4, key="lecture_nav", label_visibility="collapsed")
    
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
    elif selection == "Notifications":
        st.switch_page("pages/Notification.py")
    elif selection == "Post/Share":                  
        st.switch_page("pages/post_share.py")
    elif selection == "To-Do List":                 
        st.switch_page("pages/To_Do.py")
    elif selection != "Courses":
        st.info(f"The {selection} module is coming soon!")
    
    st.divider()
    
    if st.button(" Logout", use_container_width=True, key="lecture_logout"):
        with st.spinner("Logging out..."):
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            st.session_state.logged_in = False
            st.session_state.user = None
            if 'uploaded_avatar' in st.session_state:
                del st.session_state['uploaded_avatar']
            st.switch_page("app.py")

#CSS
st.markdown("""
    <style>
    /* Base matching themes */
    .stApp { background-color: #fafbfc; }
    [data-testid="stSidebarNav"] {display: none !important;}
    .block-container { padding-top: 5.5rem !important; padding-bottom: 3rem !important; max-width: 1200px !important; }
    
    /* Header Styling */
   .sh-title { color: #f39c12; font-weight: 800; font-size: 13px; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: -15px; }
    .sh-dashboard { font-size: 24px; font-weight: 900; color: #0a2540; margin-bottom: -10px; }
    .sh-semester { color: #7f8c8d; font-size: 14px; margin-bottom: 10px; }
    .sh-divider { background-color: #f39c12; height: 3px; width: 60px; border-radius: 2px; margin-bottom: 30px; }

    /* Universal Button Rules */
    .stDownloadButton button, .stButton button, .stLinkButton a {
        white-space: nowrap !important;
        font-size: 14px !important;
        border-radius: 8px !important;
        height: 40px !important;
        text-decoration: none !important;
        display: flex; justify-content: center; align-items: center;
    }

    /* Primary Buttons */
    div.stButton > button[kind="primary"], .stDownloadButton > button, div[data-testid="column"]:nth-child(3) .stLinkButton > a {
        background: #003C8F !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div.stButton > button[kind="primary"]:hover, .stDownloadButton > button:hover, div[data-testid="column"]:nth-child(3) .stLinkButton > a:hover {
        background: #002b66 !important;
    }

    /* Secondary Buttons */
    div.stButton > button[kind="secondary"], div[data-testid="column"]:nth-child(4) .stLinkButton > a {
        border: 1px solid #e0e6ed !important;
        background-color: white !important;
        color: #0a2540 !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div.stButton > button[kind="secondary"]:hover, div[data-testid="column"]:nth-child(4) .stLinkButton > a:hover {
        border-color: #003C8F !important;
        color: #003C8F !important;
    }
    
    /* Specific styling for the Delete File Button */
    div[data-testid="column"]:nth-child(5) div.stButton > button {
        border: 1px solid #e0e6ed !important;
        background-color: #fff5f5 !important;
        color: #e74c3c !important;
    }
    div[data-testid="column"]:nth-child(5) div.stButton > button:hover {
        background-color: #e74c3c !important;
        color: white !important;
        border-color: #e74c3c !important;
    }

    /* Container Styling */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e0e6ed;
        padding: 5px 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    
    /* Course Folders */
    .course-folder {
        background-color: white;
        border-radius: 12px;
        border: 1px solid #e0e6ed;
        border-top: 4px solid #f39c12;
        padding: 25px 20px 15px 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: -15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .course-folder:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.05);
    }
    .folder-icon { font-size: 50px; margin-bottom: 10px; }
    .folder-title { font-size: 16px; font-weight: 800; color: #0a2540; margin-bottom: 8px; line-height: 1.3; height: 42px; display: flex; align-items: center; justify-content: center; }
    .folder-count { font-size: 13px; color: #7f8c8d; font-weight: 600; margin-bottom: 15px; background: #f8faff; padding: 4px 12px; border-radius: 20px; display: inline-block; }
    
    /* Metric Card Styling */
    .metric-card { background-color: white; border-radius: 8px; border: 1px solid #e0e6ed; border-top: 4px solid #0a2540; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .metric-label { color: #7f8c8d; font-size: 13px; font-weight: 600; margin-bottom: 10px; }
    .metric-value { font-size: 28px; font-weight: 900; color: #0a2540; }
    </style>
""", unsafe_allow_html=True)
#DYNAMIC DATABASE FETCHING
# Fetch Courses
try:
    courses_response = supabase.table('courses').select('*').execute()
    db_courses = [row['course_name'] for row in courses_response.data]
except Exception as e:
    db_courses = []

# Fetch Lectures
try:
    lectures_response = supabase.table('lectures').select('*').order('created_at', desc=True).execute()
    db_lectures = lectures_response.data
except Exception as e:
    db_lectures = []

#FETH ENROLLMENTS
try:
    enrollments_response = supabase.table('enrollments').select('course_name').eq('user_id', user.id).execute()
    enrolled_courses = [row['course_name'] for row in enrollments_response.data]
except Exception as e:
    enrolled_courses = []

# Group lectures by course
course_database = {course: [] for course in db_courses}
for lec in db_lectures:
    c_name = lec.get('course_name')
    if c_name in course_database:
        course_database[c_name].append(lec)

# 6. MAIN CONTENT ROUTING
if st.session_state.selected_course is None:
    
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown('<div class="sh-title">SCHOLASTIC HUB</div>', unsafe_allow_html=True)
        st.markdown('<div class="sh-dashboard">My Courses</div>', unsafe_allow_html=True)
        st.markdown('<div class="sh-semester">Select a course to view its lectures and materials.</div>', unsafe_allow_html=True)
        st.markdown('<div class="sh-divider"></div>', unsafe_allow_html=True)
        
    with col_h2:
        # CLASS REP PRIVILEGE: Create New Folders
        if role == 'class_rep':
            st.button("📁 + New Course", type="primary", use_container_width=True, on_click=toggle_add_course)
            
    # Popup Form for Creating a Course
    if st.session_state.show_add_course:
        with st.container(border=True):
            st.markdown("#### Create New Course")
            with st.form("add_course_form"):
                new_course_name = st.text_input("Course Subject Name", placeholder="e.g. Information Management")
                
                col_btn1, col_btn2 = st.columns([1, 1])
                with col_btn1:
                    cancel_add = st.form_submit_button("Cancel", use_container_width=True)
                with col_btn2:
                    submit_add = st.form_submit_button("Create Folder", use_container_width=True)
                    
                if cancel_add:
                    st.session_state.show_add_course = False
                    st.rerun()
                if submit_add:
                    if new_course_name:
                        try:
                            supabase.table('courses').insert({"course_name": new_course_name}).execute()

                            #NOTIFICATION API
                            supabase.table("notifications").insert({
                                "title": "New Course Created",
                                "desc": f"The Class Representative created a new folder for '{new_course_name}'."
                            }).execute()
                            st.success(f"Folder '{new_course_name}' created!")
                            st.session_state.show_add_course = False
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to create folder: {e}")
                    else:
                        st.warning("Please enter a course name.")

    # Render Dynamic Folders Grid
    if not course_database:
        st.info("No course have been created yet.")
    else:
        cols = st.columns(3, gap="medium")
        
        for index, (course_name, files) in enumerate(course_database.items()):
            col = cols[index % 3] 
            with col:
                file_count = len(files)
                label = f"{file_count} File{'s' if file_count != 1 else ''} Available" if file_count > 0 else "Empty Folder"
                
                st.markdown(f"""
                    <div class="course-folder">
                        <div class="folder-icon">📂</div>
                        <div class="folder-title">{course_name}</div>
                        <div class="folder-count">{label}</div>
                    </div>
                """, unsafe_allow_html=True)

                #ENROLLMENT FUNCTION
                has_access = (role =='class_rep') or  (course_name in enrolled_courses)

                if has_access:
                    st.button(f"Open Course", key=f"open_{course_name}", on_click=open_course, args=(course_name,), use_container_width=True)
                else:
                    if st.button(f"Enroll", key=f"enroll_{course_name}", type="primary", use_container_width=True):
                        with st.spinner("Enrolling..."):
                            #API FOR ENROLLMENT
                            try:
                                supabase.table('enrollments').insert({
                                    "user_id": user.id,
                                    "course_name": course_name,
                                }).execute()
                                st.success(f"Successfully enrolled in {course_name}")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Enrollment failed: {e}")


#SPECIFIC COURSE FILES & UPLOAD
else:
    active_course = st.session_state.selected_course
    files_in_course = course_database.get(active_course, [])

    #ENROLLED STUDENT ON THE SPECIFIC COURSE COUNT
    try:
        count_response = supabase.table('enrollments').select('id', count='exact').eq('course_name', active_course).execute()
        enrolled_count = count_response.count if count_response.count is not None else 0
    except Exception:
        enrolled_count = 0

    col_header, col_metric = st.columns([3, 1])

    with col_header:
        st.markdown(f'<div class="sh-title">Course</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sh-dashboard">📂 {active_course}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sh-semester">Available Lectures and Study Materials</div>', unsafe_allow_html=True)
        st.markdown('<div class="sh-divider"></div>', unsafe_allow_html=True)

    with col_metric:
        if role == 'class_rep':
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Students Enrolled</div>
                    <div class="metric-value">{enrolled_count}</div>
                </div>
            """, unsafe_allow_html=True)
        

    col_back, col_space = st.columns([1, 4])
    with col_back:
        st.button("⬅️ Return to Course Folders", on_click=back_to_courses, use_container_width=True)
    st.write("")
    
    # CLASS REP PRIVILEGE: Upload Files to this specific Course
    if role == 'class_rep':
        with st.expander("📤 Upload New Lecture Material to this Folder"):
            with st.form("upload_lecture_form", clear_on_submit=True):
                lec_title = st.text_input("Lecture Title", placeholder="e.g. Chapter 1 - Intro to Networks")
                uploaded_file = st.file_uploader("Select File", type=['pdf', 'docx', 'pptx', 'zip', 'png', 'jpg'])
                
                if st.form_submit_button("Upload File", type="primary", use_container_width=True):
                    if lec_title and uploaded_file:
                        with st.spinner("Uploading File..."):
                            try:
                                # 1. Upload to Supabase Storage
                                timestamp = int(time.time())
                                file_path = f"{active_course}/{timestamp}_{uploaded_file.name}"
                                file_bytes = uploaded_file.getvalue()
                                
                                supabase.storage.from_("lectures").upload(
                                    file_path, 
                                    file_bytes,
                                    file_options={"content-type": uploaded_file.type}
                                )
                                public_url = supabase.storage.from_("lectures").get_public_url(file_path)
                                
                                # 2. Save metadata to Database
                                supabase.table("lectures").insert({
                                    "course_name": active_course,
                                    "title": lec_title,
                                    "file_name": uploaded_file.name,
                                    "file_url": public_url,
                                    "date": datetime.today().strftime('%Y-%m-%d')
                                }).execute()

                                #NOTIFICATION API TRIGGER

                                supabase.table("notifications").insert({
                                    "title": f"New Material in {active_course}",
                                    "desc": f"Class Representative uploaded '{lec_title}'."
                                }).execute()
                                
                                st.success("File uploaded successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error uploading file: {e}")
                    else:
                        st.warning("Please provide a title and select a file to upload.")
            
            #DELETE COURSE SECTION
            st.markdown("Course Removal")
            st.caption("Deleting this course will permanently remove it and all lecture records associated with it.")

            del_col1, del_col2 = st.columns([1, 2])
            with del_col1:
                if st.button("Delete Course", use_container_width=True):
                    with st.spinner("Deleting Course..."):
                        #API CALL FOR DELETING COURSE
                        try:
                            supabase.table("courses").delete().eq("course_name", active_course).execute()
                            st.session_state.selected_course = None
                            st.success(f"Course '{active_course}' deleted successfully!")
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error Deleting Folder: {e}")

    # Display Files
    if not files_in_course:
        st.info(f"No materials have been uploaded to the {active_course} folder yet.")
    else:
        for lec in files_in_course:
            with st.container(border=True):
                # 2. DYNAMIC COLUMNS (Class Reps get the 5th Delete button column)
                if role == 'class_rep':
                    c_title, c_date, c_dl, c_view, c_del = st.columns([3.5, 2, 1, 1, 1], vertical_alignment="center")
                else:
                    c_title, c_date, c_dl, c_view = st.columns([4, 2, 1.2, 1.2], vertical_alignment="center")
                
                with c_title:
                    st.markdown(f"<span style='color:#0a2540; font-weight:700; font-size:16px;'>📄 {lec['title']}</span>", unsafe_allow_html=True)
                
                with c_date:
                    st.markdown(f"<span style='color:#7f8c8d; font-size:14px;'>📅 {lec['date']}</span>", unsafe_allow_html=True)
                
                with c_dl:
                    st.link_button("Download", url=lec['file_url'], use_container_width=True)
                    
                with c_view:
                    st.link_button("View", url=lec['file_url'], use_container_width=True)
                    
                # The targeted single-file deletion logic
                if role == 'class_rep':
                    with c_del:
                        if st.button("Delete", key=f"del_{lec['id']}", use_container_width=True):
                            with st.spinner("Deleting..."):
                                try:
                                    # We decode the URL string using urllib to get the exact raw storage file path
                                    url_path = lec['file_url'].split('/public/lectures/')[-1]
                                    exact_file_path = urllib.parse.unquote(url_path)
                                    
                                    # Remove from Storage Bucket and Database table
                                    supabase.storage.from_("lectures").remove([exact_file_path])
                                    supabase.table("lectures").delete().eq("id", lec['id']).execute()
                                    
                                    st.success("File deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting file: {e}")