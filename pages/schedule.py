import streamlit as st
import pandas as pd
import time
from datetime import datetime
from supabase import create_client, Client

st.set_page_config(page_title="Class Schedule", layout="wide")

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

# Session state for toggling the editor
if 'show_schedule_editor' not in st.session_state:
    st.session_state.show_schedule_editor = False

def toggle_schedule_editor():
    st.session_state.show_schedule_editor = not st.session_state.show_schedule_editor

# DYNAMIC DATABASE FETCHING
try:
    sched_response = supabase.table('schedules').select('*').execute()
    db_schedules = sched_response.data
except Exception as e:
    st.error(f"Failed to fetch schedule: {e}")
    db_schedules = []

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

schedule_data = {day: [] for day in days}
for row in db_schedules:
    if row['day'] in schedule_data:
        schedule_data[row['day']].append({
            "time": row['time_slot'],
            "subject": row['subject'],
            "room": row['room'],
            "code": row['code'],
            "color": row['color']
        })

# SMART TIME SORTING: Ensures morning classes are always at the top of the grid!
def sort_time_slots(slots):
    def parse_time(slot_str):
        try:
            start_str = slot_str.split('–')[0].split('-')[0].strip()
            return datetime.strptime(start_str, "%I:%M %p").time()
        except Exception:
            return datetime.strptime("11:59 PM", "%I:%M %p").time()
            
    return sorted(list(set(slots)), key=parse_time)

raw_slots = [row['time_slot'] for row in db_schedules]
schedule_slots = sort_time_slots(raw_slots)

#SIDEBAR NAVIGATION
with st.sidebar:
    st.markdown("### Menu")

    if role == 'class_rep':
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    else:
        options = ["Dashboard", "Profile", "Schedule", "To-Do List", "Courses", "Post/Share", "Notifications"]
    
    selection = st.radio("Navigation", options, index=2, key="schedule_nav", label_visibility="collapsed")
    
    if selection == "Dashboard":
        if role == 'class_rep':
            st.switch_page("pages/class_rep_dashboard.py")
        else:
            st.switch_page("pages/dashboard.py")
    elif selection == "Profile":
        st.switch_page("pages/Profile.py")
    elif selection == "Courses":
        st.switch_page("pages/LectureFile.py")
    elif selection == "Notifications":
        st.switch_page("pages/Notification.py")
    elif selection == "Post/Share":                   
        st.switch_page("pages/post_share.py")
    elif selection == "To-Do List":                 
        st.switch_page("pages/To_Do.py")
    elif selection != "Schedule":
        st.info(f"The {selection} module is coming soon!")
    
    st.divider()
    
    if st.button("Logout", use_container_width=True, key="schedule_logout"):
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

#CSS STYLING
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    :root {
        --rtu-blue: #003C8F;
        --rtu-gold: #F4B400;
        --rtu-bg: #F5F7FB;
        --rtu-surface: #FFFFFF;
        --rtu-text: #111827;
        --rtu-muted: #475569;
        --rtu-border: #E2E8F0;
        --rtu-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    }
    body { background: var(--rtu-bg); color: var(--rtu-text); }
    .content-wrapper { max-width: 1400px; margin: 0 auto; padding: 1.5rem 1.5rem 3rem; }
    .page-header-card { background: var(--rtu-surface); border-radius: 24px; padding: 2rem; box-shadow: var(--rtu-shadow); margin-bottom: 1.75rem; border: 1px solid rgba(226, 232, 240, 0.8); }
    .header-grid { display: grid; grid-template-columns: 1fr auto; gap: 2rem; align-items: center; }
    .title-group { display: grid; gap: 0.65rem; }
    .eyebrow { color: var(--rtu-gold); font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; font-size: 0.82rem; margin: 0; }
    .page-header-card h1 { margin: 0; font-size: clamp(2rem, 2.5vw, 2.7rem); color: var(--rtu-text); }
    .page-header-card p { margin: 0; color: var(--rtu-muted); font-size: 1rem; line-height: 1.6; }
    .header-accent { width: 90px; height: 6px; border-radius: 999px; background: linear-gradient(90deg, var(--rtu-blue) 0%, var(--rtu-gold) 100%); margin-top: 0.85rem; }
    .student-info { background: #F8FAFF; border-radius: 18px; padding: 1.25rem; border: 1px solid rgba(226, 232, 240, 0.9); display: grid; gap: 0.85rem; }
    .student-info-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0.35rem 0; }
    .student-info-row .label { color: var(--rtu-muted); font-size: 0.88rem; }
    .student-info-row .value { color: var(--rtu-text); font-weight: 700; font-size: 0.95rem; }
    .stats-card { background: var(--rtu-surface); border-radius: 20px; padding: 1.4rem 1.35rem; box-shadow: var(--rtu-shadow); border-top: 4px solid var(--rtu-blue); min-height: 150px; }
    .card-title { margin: 0; color: var(--rtu-muted); font-size: 0.95rem; font-weight: 700; }
    .card-value { margin: 0.85rem 0 0; font-size: 2rem; color: var(--rtu-text); font-weight: 700; }
    .schedule-section { background: var(--rtu-surface); border-radius: 24px; padding: 1.6rem; box-shadow: var(--rtu-shadow); border: 1px solid rgba(226, 232, 240, 0.9); margin-top: 2.5rem; }
    .section-title { font-size: 1.35rem; font-weight: 700; margin-bottom: 1rem; }
    .schedule-grid { width: 100%; border-collapse: separate; border-spacing: 0 10px; }
    .schedule-grid th, .schedule-grid td { padding: 0.8rem 0.9rem; vertical-align: top; }
    .schedule-grid thead th { font-weight: 700; color: var(--rtu-text); text-transform: uppercase; letter-spacing: 0.06em; font-size: 0.9rem; border-bottom: 1px solid rgba(226, 232, 240, 0.9); padding-bottom: 1.15rem; }
    .schedule-grid tbody tr td:first-child { font-weight: 700; color: var(--rtu-muted); width: 130px; white-space: nowrap; }
    .day-cell { min-width: 160px; padding: 0; }
    .schedule-card { background: #F8FAFF; border-radius: 18px; border: 1px solid rgba(226, 232, 240, 0.9); padding: 1rem; box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06); transition: transform 0.2s ease, box-shadow 0.2s ease; }
    .schedule-card:hover { transform: translateY(-3px); box-shadow: 0 18px 30px rgba(15, 23, 42, 0.12); }
    .schedule-badge { display: inline-block; padding: 0.35rem 0.75rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700; color: white; margin-bottom: 0.9rem; }
    .schedule-card h4 { margin: 0 0 0.55rem; font-size: 1rem; line-height: 1.35; color: var(--rtu-text); }
    .schedule-card p { margin: 0.18rem 0; color: var(--rtu-muted); font-size: 0.92rem; }
    .day-card-empty { min-height: 138px; display: flex; align-items: center; justify-content: center; border-radius: 18px; border: 1px dashed rgba(226, 232, 240, 0.9); background: #FBFCFE; color: var(--rtu-muted); font-size: 0.95rem; }
    @media (max-width: 1100px) { .header-grid, .student-info { grid-template-columns: 1fr; } }
    @media (max-width: 760px) { .schedule-grid thead { display: none; } .schedule-grid, .schedule-grid tbody, .schedule-grid tr, .schedule-grid td { display: block; width: 100%; } .schedule-grid tr { margin-bottom: 1rem; } .schedule-grid td { padding-left: 0; } .schedule-grid td:first-child { font-size: 0.95rem; margin-bottom: 0.75rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)


#MAIN CONTENT
st.markdown("<div class='content-wrapper'>", unsafe_allow_html=True)

# Generate Dynamic Statistics
total_subjects = len(db_schedules)
lab_classes = sum(1 for row in db_schedules if 'Lab' in row['subject'])
class_days = len(set(row['day'] for row in db_schedules))

schedule_header = {
    "title": "Class Schedule",
    "subtitle": "Second Semester AY 2025–2026",
    "student_info": [
        {"label": "Program", "value": "BSIT"},
        {"label": "Block Section", "value": "401A"},
        {"label": "Year Level", "value": "2nd Year"},
        {"label": "Semester Status", "value": "Enrolled"},
    ],
}

student_info_html = ""
for item in schedule_header["student_info"]:
    student_info_html += (
        f"<div class='student-info-row'>"
        f"<span class='label'>{item['label']}</span>"
        f"<span class='value'>{item['value']}</span>"
        f"</div>"
    )

st.markdown(
    f"""
    <div class='page-header-card'>
        <div class='header-grid'>
            <div class='title-group'>
                <div class='eyebrow'>Scholastic Hub</div>
                <h1>{schedule_header['title']}</h1>
                <p>{schedule_header['subtitle']}</p>
                <div class='header-accent'></div>
            </div>
            <div class='student-info'>
                {student_info_html}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

card_cols = st.columns(4, gap="large")
summary_cards = [
    {"label": "Total Subjects", "value": str(total_subjects)},
    {"label": "Total Units", "value": "23"}, 
    {"label": "Laboratory Classes", "value": str(lab_classes)},
    {"label": "Class Days", "value": str(class_days)},
]
for index, card in enumerate(summary_cards):
    card_cols[index].markdown(f"<div class='stats-card'><p class='card-title'>{card['label']}</p><p class='card-value'>{card['value']}</p></div>", unsafe_allow_html=True)

st.markdown("<div class='schedule-section'>", unsafe_allow_html=True)


# CLASS REP SCHEDULE EDITOR
head_col, btn_col = st.columns([4, 1])
with head_col:
    st.markdown("<div class='section-title'>Weekly Class Schedule</div>", unsafe_allow_html=True)
with btn_col:
    if role == 'class_rep':
        st.button("Edit Schedule", type="primary", use_container_width=True, on_click=toggle_schedule_editor)

if st.session_state.show_schedule_editor:
    with st.container(border=True):
        st.markdown("#### 🛠️ Manage Classes")
        st.info("Add new classes by typing in the empty bottom row. To delete a class, click the far-left gray edge of a row and press Delete.")
        
        df = pd.DataFrame(db_schedules)
        if df.empty:
            df = pd.DataFrame(columns=['id', 'day', 'time_slot', 'subject', 'room', 'code', 'color'])
            
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": None, 
                "day": st.column_config.SelectboxColumn("Day", options=days, required=True),
                "time_slot": st.column_config.TextColumn("Time Slot (e.g. 7:00 AM - 9:00 AM)", required=True),
                "subject": st.column_config.TextColumn("Subject Name", required=True),
                "room": st.column_config.TextColumn("Room", required=True),
                "code": st.column_config.TextColumn("Course Code", required=True),
                "color": st.column_config.SelectboxColumn("Card Color", options=["#003C8F", "#1D4ED8", "#2563EB", "#0F766E", "#F4B400", "#E11D48"], required=True)
            }
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.button("Cancel", use_container_width=True, on_click=toggle_schedule_editor)
        with col2:
            if st.button("Save Changes to Database", type="primary", use_container_width=True):
                with st.spinner("Syncing schedule..."):
                    try:
                        # 1. Safely delete all current records
                        current_ids = [row['id'] for row in db_schedules]
                        if current_ids:
                            supabase.table('schedules').delete().in_('id', current_ids).execute()
                            
                        # 2. Insert the newly edited records
                        new_records = edited_df.drop(columns=['id'], errors='ignore').to_dict('records')
                        if new_records:
                            supabase.table('schedules').insert(new_records).execute()
                        

                        #NOTIFICATION TRIGGER
                        supabase.table("notifications").insert({
                            "title": "Schedule Updated",
                            "desc": "The Class Representative has updated the weekly class schedule."
                        }).execute()
                            
                        st.success("Schedule updated successfully!")
                        st.session_state.show_schedule_editor = False
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving schedule: {e}")


#RENDER THE VISUAL GRID
if not schedule_slots:
    st.info("No schedule data found. Click 'Edit Schedule' to start adding classes!")
else:
    schedule_html = """
        <table class='schedule-grid'>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Monday</th>
                    <th>Tuesday</th>
                    <th>Wednesday</th>
                    <th>Thursday</th>
                    <th>Friday</th>
                    <th>Saturday</th>
                </tr>
            </thead>
            <tbody>
    """

    for slot in schedule_slots:
        schedule_html += f"<tr><td class='time-slot'>{slot}</td>"
        for day in days:
            day_entries = schedule_data.get(day, [])
            entry = next((item for item in day_entries if item["time"] == slot), None)
            if entry:
                schedule_html += (
                    f"<td class='day-cell'><div class='schedule-card' style='border-left: 4px solid {entry['color']};'>"
                    f"<div class='schedule-badge' style='background:{entry['color']};'>{entry['code']}</div>"
                    f"<h4>{entry['subject']}</h4>"
                    f"<p style='margin-top:0.85rem; font-weight:700; color: var(--rtu-text);'>{entry['room']}</p>"
                    f"</div></td>"
                )
            else:
                schedule_html += (
                    "<td class='day-cell'><div class='day-card-empty'>No scheduled class</div></td>"
                )
        schedule_html += "</tr>"

    schedule_html += "</tbody></table>"

    st.markdown(schedule_html, unsafe_allow_html=True)
st.markdown("</div></div>", unsafe_allow_html=True)