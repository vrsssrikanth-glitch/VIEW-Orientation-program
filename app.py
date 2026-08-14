import streamlit as st
import pandas as pd
import math

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Orientation Program | Vignan's Institute of Engineering for Women",
    page_icon="🎓",
    layout="centered"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.college-name {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 5px;
}

.program-title {
    text-align: center;
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 25px;
}

.subtitle {
    text-align: center;
    font-size: 16px;
    margin-bottom: 25px;
}

.student-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    margin-top: 20px;
    margin-bottom: 20px;
}

.Batch {
    font-size: 30px;
    font-weight: 700;
    text-align: center;
    padding: 12px;
}

.student-name {
    font-size: 23px;
    font-weight: 600;
}

.branch {
    font-size: 18px;
}

.schedule-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 10px;
}

.footer {
    text-align: center;
    font-size: 13px;
    margin-top: 35px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# LOAD CSV FILES
# ---------------------------------------------------------

@st.cache_data
def load_student_data():

    df = pd.read_csv("studentdata.csv")

    # Remove accidental spaces from column names
    df.columns = df.columns.str.strip()

    # Clean student names
    df["Name"] = df["Name"].astype(str).str.strip()

    # Clean branch
    df["Branch"] = df["Branch"].astype(str).str.strip()

    # Convert rank to numeric
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")

    # Remove rows where essential information is missing
    df = df.dropna(subset=["Name", "Rank"])

    return df


@st.cache_data
def load_schedule():

    df = pd.read_csv("schedule.csv")

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # Clean values
    for column in df.columns:
        df[column] = df[column].astype(str).str.strip()

    return df


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

try:

    students = load_student_data()
    schedule = load_schedule()

except FileNotFoundError:

    st.error(
        "CSV files not found. Please keep studentdata.csv and "
        "schedule.csv in the same folder as app.py."
    )

    st.stop()


# ---------------------------------------------------------
# Batch LIST
# ---------------------------------------------------------

# Rooms are taken from the schedule file.
# This automatically keeps the specified Batch order.

rooms = ["A41", "A42", "A45", "A46", "A47", "B43", "B44", "B46"]


# ---------------------------------------------------------
# METHOD B - EQUAL DISTRIBUTION
# ---------------------------------------------------------

def allocate_rooms(student_df, room_list):

    # Sort students according to rank
    sorted_students = student_df.sort_values(
        by="Rank",
        ascending=True
    ).reset_index(drop=True)

    number_of_students = len(sorted_students)
    number_of_rooms = len(room_list)

    # Base number of students per Batch
    base_size = number_of_students // number_of_rooms

    # Remaining students
    remainder = number_of_students % number_of_rooms

    allocations = []

    start = 0

    for i, Batch in enumerate(room_list):

        # First 'remainder' rooms receive one extra student
        room_size = base_size + (1 if i < remainder else 0)

        end = start + room_size

        allocations.extend(
            [Batch] * room_size
        )

        start = end

    sorted_students["Allocated Batch"] = allocations

    return sorted_students


students = allocate_rooms(
    students,
    rooms
)


# ---------------------------------------------------------
# CREATE SEARCH VERSION OF NAME
# ---------------------------------------------------------

students["Search Name"] = (
    students["Name"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="college-name">'
    "Vignan's Institute of Engineering for Women"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    '<div class="program-title">'
    "🎓 Welcome to Orientation Program"
    "</div>",
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    "Find your allocated Batch and Orientation Program schedule"
    "</div>",
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SEARCH BAR
# ---------------------------------------------------------

st.markdown("### 🔎 Search Student Name")

search_name = st.text_input(
    "Enter your full name",
    placeholder="Type your name here...",
    label_visibility="collapsed"
)


# ---------------------------------------------------------
# SEARCH LOGIC
# ---------------------------------------------------------

if search_name.strip():

    search_text = search_name.strip().lower()

    # Exact match first
    exact_matches = students[
        students["Search Name"] == search_text
    ]

    # If exact match exists
    if len(exact_matches) == 1:

        selected_student = exact_matches.iloc[0]

    elif len(exact_matches) > 1:

        st.warning(
            "More than one student has the same name. "
            "Please enter the full name."
        )

        st.stop()

    else:

        # Partial matching
        matches = students[
            students["Search Name"].str.contains(
                search_text,
                na=False,
                regex=False
            )
        ]

        if len(matches) == 0:

            st.error(
                "❌ Student name not found. "
                "Please check the spelling and try again."
            )

            st.stop()

        elif len(matches) == 1:

            selected_student = matches.iloc[0]

        else:

            st.info("Multiple students found. Please select your name.")

            display_names = matches["Name"].tolist()

            selected_name = st.selectbox(
                "Select your name",
                display_names
            )

            selected_student = matches[
                matches["Name"] == selected_name
            ].iloc[0]


    # -----------------------------------------------------
    # STUDENT INFORMATION
    # -----------------------------------------------------

    student_name = selected_student["Name"]
    branch = selected_student["Branch"]
    allocated_room = selected_student["Allocated Batch"]


    # -----------------------------------------------------
    # DISPLAY STUDENT DETAILS
    # -----------------------------------------------------

    st.markdown(
        '<div class="student-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="student-name">👤 {student_name}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="branch">Branch: <b>{branch}</b></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="Batch">
            🏫 Batch: {allocated_room}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # GET SCHEDULE FOR ALLOCATED Batch
    # -----------------------------------------------------

    room_schedule = schedule[
        schedule["Batch number"].str.upper()
        == str(allocated_room).upper()
    ].copy()


    # -----------------------------------------------------
    # DISPLAY SCHEDULE
    # -----------------------------------------------------

    st.markdown(
        '<div class="schedule-title">📅 Your Orientation Schedule</div>',
        unsafe_allow_html=True
    )

    if len(room_schedule) > 0:

        # Do not display Batch number again
        display_schedule = room_schedule[
            ["Day", "9:30 - 12:30", "2:00 - 4:30"]
        ].copy()

        # Capitalize schedule entries
        for column in ["9:30 - 12:30", "2:00 - 4:30"]:

            display_schedule[column] = (
                display_schedule[column]
                .astype(str)
                .str.title()
            )

        st.dataframe(
            display_schedule,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "Schedule information for your Batch is not available."
        )


# ---------------------------------------------------------
# INITIAL MESSAGE
# ---------------------------------------------------------

else:

    st.info(
        "👆 Enter your name in the search box above "
        "to find your allocated Batch and schedule."
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Vignan's Institute of Engineering for Women<br>
        Orientation Program
    </div>
    """,
    unsafe_allow_html=True
)
