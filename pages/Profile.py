from supabase import create_client, Client
import streamlit as st
import time

st.set_page_config(page_title="Profile", layout="wide", initial_sidebar_state="expanded")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.switch_page("login.py")

#SUPABASE API FOR LISTING ACCOUNT INFORMATION
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url,key)

supabase: Client = init_connection()

#STATE OF THE EDIT PROFILE BUTTON
if 'show_edit_menu' not in st.session_state:
    st.session_state.show_edit_menu = False

def toggle_edit():
    st.session_state.show_edit_menu = not st.session_state.show_edit_menu

user = st.session_state.user
email = user.email

role = user.user_metadata.get('role', 'student')

avatar_url = st.session_state.get('uploaded_avatar', None) 
full_name = user.user_metadata.get('full_name', 'Unknown User')
student_id = user.user_metadata.get('student_id', 'N/A')
#WILL FETCH THE DATA FROM THE SUPABASE API DATABASE
try:
    profile_response = supabase.table('profiles').select('*').eq('id', user.id).execute()
    
    if profile_response.data:
        db_data = profile_response.data[0]
        full_name = db_data.get('full_name') or full_name
        student_id = db_data.get('student_id') or student_id

        if not avatar_url:
            avatar_url = db_data.get('avatar_url')
except Exception as e:
    pass
#NAVIGATION SIDE BAR
with st.sidebar:
    st.markdown("### Menu")

    if role == 'class_rep':
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    else:
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]

    selection = st.radio("Navigation", options, index=1, label_visibility="collapsed")

    if selection == "Dashboard":
        if role  == 'class_rep':
            st.switch_page("pages/class_rep_dashboard.py")
        else:
            st.switch_page("pages/dashboard.py")
    elif selection == "Schedule":
        st.switch_page("pages/schedule.py")
    elif selection == "Courses":
        st.switch_page("pages/LectureFile.py")
    elif selection == "Notifications":
        st.switch_page("pages/Notification.py")
    elif selection == "Post/Share":                   
        st.switch_page("pages/post_share.py")
    elif selection == "To-Do List":                 
        st.switch_page("pages/To_Do.py")
    elif selection != "Profile":
        st.info(f"The {selection} module is coming soon!")
    
    st.divider()
    if st.button("Logout", use_container_width=True):
        with st.spinner("Logging out..."):
            #API CALL FOR LOGOUT
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            st.session_state.logged_in = False
            st.session_state.user = None
            st.switch_page("login.py") 
st.markdown("""
    <style>
            
    .stApp { background-color: #fafbfc; }
    [data-testid="stSidebarNav"] {display: none !important;}
    .block-container { padding-top: 5.5rem !important; padding-bottom: 3rem !important; max-width: 1200px !important; }
    
    .profile-pic {
        width: 150px;
        height: 150px;
        background-color: #d1d5db;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;
    }
            
    .profile-img {
        width: 150px !important;
        height: 150px !important;
        object-fit: cover !important;
        border-radius: 50% !important; /* Force the image itself to be circular */
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)


head_left, head_right = st.columns([4, 1])
with head_left:
    st.header(full_name)
with head_right:
    badge_text = "Class Representative" if role == 'class_rep' else "Student"
    st.markdown(f"<div style='text-align: right; padding-top: 10px;'>{badge_text}</div>", unsafe_allow_html=True)

with st.container(border=True):
   
    img_col, info_col = st.columns([1, 3])
    
    with img_col:
        # Display image if it exists, otherwise show emoji
        if avatar_url:
            avatar_html = f'<img src="{avatar_url}" class="profile-img">'
        else:
            fallback_emoji = "👔" if role == 'class_rep' else "👨‍🎓"
            avatar_html = f'<div style="font-size: 60px;">{fallback_emoji}</div>'
            
        st.markdown(f'<div class="profile-pic">{avatar_html}</div>', unsafe_allow_html=True)
        st.button("Edit Profile", type="primary", use_container_width=True, on_click=toggle_edit)
        
    with info_col:
        
        st.write(f"{email}")
        st.write(f"**Student Number:** {student_id}")
        st.write("**Status:** Enrolled" if role == 'class_rep' else "**Status:** Enrolled")

if st.session_state.show_edit_menu:
    with st.container(border=True):
        st.markdown("#### Update Profile Picture")
        
        uploaded_file = st.file_uploader("Choose a image (JPG or PNG)", type=["jpg", "jpeg", "png"])

        #Cancel and Save Button
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            st.button("Cancel", use_container_width=True, on_click=toggle_edit)
        
        with btn_col2:
            if st.button("Save Picture", type="primary", use_container_width=True):
                if uploaded_file is not None:
                    with st.spinner("Uploading your new picture..."):
                        try:
                            file_ext = uploaded_file.name.split('.')[-1]
                            file_name = f"{user.id}/avatar_{int(time.time())}.{file_ext}"
                            file_bytes = uploaded_file.getvalue()
                            
                            # Upload to Supabase Storage
                            supabase.storage.from_("avatars").upload(
                                file_name, 
                                file_bytes,
                                file_options={"content-type": uploaded_file.type}
                            )
                            
                            # Get the public URL
                            public_url = supabase.storage.from_("avatars").get_public_url(file_name)
                            
                            # Update Database
                            supabase.table("profiles").upsert({
                                "id": user.id,
                                "full_name": full_name,
                                "student_id": student_id,
                                "role": role,
                                "avatar_url": public_url
                            }).execute()
                            
                            # Close the menu and refresh
                            st.session_state['uploaded_avatar'] = public_url
                            st.session_state.show_edit_menu = False
                            
                            st.success("Avatar successfully saved!")
                            time.sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving picture: {e}")
                else:
                    st.warning("Please select an image file to upload first.")