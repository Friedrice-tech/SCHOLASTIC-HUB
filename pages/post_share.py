import streamlit as st
from supabase import create_client, Client
import time
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Post/Share", layout="wide", initial_sidebar_state="expanded")
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
user_name = user.user_metadata.get('full_name', 'Student')

user_avatar = st.session_state.get('uploaded_avatar')
if not user_avatar:
    try:
        profile_res = supabase.table('profiles').select('avatar_url').eq('id', user.id).execute()
        if profile_res.data and profile_res.data[0].get('avatar_url'):
            user_avatar = profile_res.data[0]['avatar_url']
            st.session_state['uploaded_avatar'] = user_avatar 
    except Exception:
        user_avatar = None

#SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### Menu")

    if role == 'class_rep':
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
        index_val = 6
    else:
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
        index_val = 5

    selection = st.radio("Navigation", options, index=index_val, key="post_nav", label_visibility="collapsed") 

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
    elif selection == "Notifications":
        st.switch_page("pages/Notification.py")
    elif selection == "To-Do List":                 
        st.switch_page("pages/To_Do.py")
    elif selection != "Post/Share":
        st.info(f"The {selection} module is coming soon!")   

    st.divider()
    
    if st.button("Logout", use_container_width=True, key="post_logout"):
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

    /* Post Card Styling */
    .post-card {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .post-avatar {
        width: 45px;
        height: 45px;
        background-color: #e0e6ed;
        color: #0a2540;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-size: 18px;
        font-weight: 800;
        overflow: hidden; /* Added to keep pictures perfectly circular */
    }
    
    .post-meta-name { font-weight: 700; color: #0a2540; font-size: 16px; margin-bottom: 2px; }
    .post-meta-date { font-size: 12px; color: #7f8c8d; }
    .post-content { font-size: 15px; color: #334155; line-height: 1.6; margin-bottom: 15px; }
    
    .attachment-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    /* Buttons */
    div.stButton > button[kind="primary"] {
        background: #4285F4 !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 5px 25px !important;
    }
    div.stButton > button[kind="primary"]:hover { background: #3367D6 !important; }
    
    .stLinkButton a {
        background: #f1f5f9 !important;
        color: #0a2540 !important;
        border: 1px solid #cbd5e1 !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        text-decoration: none !important;
    }
    .stLinkButton a:hover { background: #e2e8f0 !important; }
</style>
""", unsafe_allow_html=True)

#MAIN LAYOUT HEADER
st.markdown('<div class="sh-title">SCHOLASTIC HUB</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-dashboard">Student Share / Post Section</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-semester">Collaborate, share reviewers, and discuss with your classmates.</div>', unsafe_allow_html=True)
st.markdown('<div class="sh-divider"></div>', unsafe_allow_html=True)


#CREATE NEW POST SECTION
st.markdown("#### Create New Post")
with st.container(border=True):
    with st.form("create_post_form", clear_on_submit=True):
        post_content = st.text_area("Content", placeholder="Share your notes or reviewers here...", label_visibility="collapsed", height=120)
        
        st.write("Optional Attachment")
        uploaded_file = st.file_uploader("Upload Attachment", type=['pdf', 'docx', 'png', 'jpg', 'zip'], label_visibility="collapsed")
        
        col_btn, col_empty = st.columns([1, 5])
        with col_btn:
            submit_post = st.form_submit_button("Post", type="primary", use_container_width=True)
            
        if submit_post:
            if not post_content and not uploaded_file:
                st.warning("Please enter some text or attach a file to post.")
            else:
                with st.spinner("Publishing post..."):
                    try:
                        file_url = None
                        file_name = None
                        
                        # Handle file upload to Supabase Storage if present
                        if uploaded_file:
                            timestamp = int(time.time())
                            safe_name = uploaded_file.name.replace(" ", "_")
                            path = f"shared/{timestamp}_{safe_name}"
                            
                            supabase.storage.from_("posts").upload(
                                path, 
                                uploaded_file.getvalue(),
                                file_options={"content-type": uploaded_file.type}
                            )
                            file_url = supabase.storage.from_("posts").get_public_url(path)
                            file_name = uploaded_file.name
                            
                        # Insert into Database with the avatar!
                        supabase.table("posts").insert({
                            "author_name": user_name,
                            "author_avatar": user_avatar,  
                            "content": post_content,
                            "file_url": file_url,
                            "file_name": file_name,
                            "created_at": datetime.utcnow().isoformat()
                        }).execute()
                        
                        # Trigger notification for the class
                        supabase.table("notifications").insert({
                            "title": "New Post Shared",
                            "desc": f"{user_name} shared a new post in the discussion board."
                        }).execute()
                        
                        st.success("Post published successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not publish post: {e}")

st.write("")
st.write("")


#RECENT POSTS SECTION
st.markdown("#### Recent Posts")

# Fetch posts strictly from database
try:
    response = supabase.table('posts').select('*').order('created_at', desc=True).execute()
    db_posts = response.data

    profiles_response = supabase.table('profiles').select('full_name, avatar_url').execute()
    avatars_map = {p['full_name']: p.get('avatar_url') for p in profiles_response.data if p.get('full_name')}
except Exception as e:
    st.error(f"Database error: {e}")
    db_posts = []
    avatars_map = {}
    
if not db_posts:
    st.info("No posts have been shared yet. Be the first to start a discussion!")
else:
    # Render Dynamic Posts
    for post in db_posts:
        # Safely parse timezone format for display
        try:
            date_str = post['created_at'].replace('Z', '+00:00')
            utc_date = datetime.fromisoformat(date_str)
            local_date = utc_date.astimezone(timezone(timedelta(hours=8)))
            formatted_date = local_date.strftime("%B %d, %Y at %I:%M %p")
        except Exception as e:
            formatted_date = "Recently"
        author_avatar = avatars_map.get(post['author_name'])
        
        if not author_avatar:
            author_avatar = post.get('author_avatar')
        
        if author_avatar:
            avatar_html = f'<img src="{author_avatar}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">'
        else:
            avatar_html = "".join([n[0] for n in post['author_name'].split()[:2]]).upper() if post['author_name'] else "ST"

        # Post Card HTML
        st.markdown(f"""
            <div class="post-card">
                <div class="post-header">
                    <div class="post-avatar">{avatar_html}</div>
                    <div>
                        <div class="post-meta-name">{post['author_name']}</div>
                        <div class="post-meta-date">Posted on {formatted_date}</div>
                    </div>
                </div>
                <div class="post-content">{post['content']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Render Attachment Box underneath the card if a file exists
        if post.get('file_url') and post.get('file_name'):
            st.markdown('<div style="margin-top: -35px; padding: 0 25px 25px 25px; position: relative; z-index: 5;">', unsafe_allow_html=True)
            with st.container(border=True):
                att_col1, att_col2 = st.columns([4, 1], vertical_alignment="center")
                with att_col1:
                    st.markdown(f"📎 **Attachment:** `{post['file_name']}`")
                with att_col2:
                    st.link_button("Download", url=post['file_url'], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)