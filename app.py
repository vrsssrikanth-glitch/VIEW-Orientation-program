import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Orientation Program | Vignan's Institute of Engineering for Women",
    page_icon="🎓",
    layout="centered"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

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
    margin-bottom: 8px;
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

.batch {
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


# =========================================================
# HELPER FUNCTION
# =========================================================

def find_column(df, possible_names):

    """
    Finds a column irrespective of:
    - upper/lower case
    - spaces
    - underscores
    """

    normalized = {}

    for col in df.columns:
        key = (
            str(col)
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
        )
        normalized[key] = col

    for name in possible_names:

        key = (
            name
            .strip()
            .lower()
            .replace(" ", "")
            .replace("_", "")
        )

        if key in normalized:
            return normalized[key]

    return None


# =========================================================
# LOAD STUDENT DATA
# =========================================================

@st.cache_data
def load_student_data():

    df = pd.read_csv("studentdata.csv")

    # Remove spaces from column headers
    df.columns = df.columns.astype(str).str.strip()

    # ---------------------------------------------
    # FIND STUDENT NAME COLUMN
    # ---------------------------------------------

    name_col = find_column(
        df,
        [
            "Name",
            "Student Name",
            "StudentName",
            "Student"
        ]
    )

    # ---------------------------------------------
    # FIND BRANCH COLUMN
    # ---------------------------------------------

    branch_col = find_column(
        df,
        [
            "Branch",
            "Branch Name",
            "Department"
        ]
    )

    # ---------------------------------------------
    # FIND RANK COLUMN
    # ---------------------------------------------

    rank_col = find_column(
        df,
        [
            "Rank",
            "EAPCET Rank",
            "AP EAPCET Rank",
            "EAMCET Rank"
        ]
    )

    # ---------------------------------------------
    # CHECK REQUIRED COLUMNS
    # ---------------------------------------------

    missing = []

    if name_col is None:
        missing.append("Student Name")

    if branch_col is None:
        missing.append("Branch")

    if rank_col is None:
        missing.append("Rank")

    if missing:

        st.error(
            "Required column(s) not found in studentdata.csv: "
            + ", ".join(missing)
        )

        st.info(
            "Available columns in your CSV: "
            + ", ".join(df.columns.astype(str))
        )

        st.stop()

    # ---------------------------------------------
    # STANDARDIZE COLUMN NAMES
    # ---------------------------------------------

    df = df.rename(
        columns={
            name_col: "Name",
            branch_col: "Branch",
            rank_col: "Rank"
        }
    )

    # ---------------------------------------------
    # CLEAN DATA
    # ---------------------------------------------

    df["Name"] = (
        df["Name"]
        .astype(str)
        .str.strip()
    )

    df["Branch"] = (
        df["Branch"]
        .astype(str)
        .str.strip()
    )

    df["Rank"] = pd.to_numeric(
        df["Rank"],
        errors="coerce"
    )

    # Remove students without valid rank
    df = df.dropna(
        subset=["Name", "Rank"]
    )

    return df


# =========================================================
# LOAD SCHEDULE
# =========================================================

@st.cache_data
def load_schedule():

    df = pd.read_csv("schedule.csv")

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # Find Batch column
    batch_col = find_column(
        df,
        [
            "Batch",
            "Batch Name",
            "Batch No",
            "Batch Number"
        ]
    )

    # Find Day column
    day_col = find_column(
        df,
        [
            "Day"
        ]
    )

    # Find morning schedule column
    morning_col = find_column(
        df,
        [
            "9:30 - 12:30",
            "9:30-12:30",
            "9.30 - 12.30",
            "9.30-12.30"
        ]
    )

    # Find afternoon schedule column
    afternoon_col = find_column(
        df,
        [
            "2:00 - 4:30",
            "2:00-4:30",
            "2.00 - 4.30",
            "2.00-4.30"
        ]
    )

    missing = []

    if batch_col is None:
        missing.append("Batch")

    if day_col is None:
        missing.append("Day")

    if morning_col is None:
        missing.append("9:30 - 12:30")

    if afternoon_col is None:
        missing.append("2:00 - 4:30")

    if missing:

        st.error(
            "Required column(s) not found in schedule.csv: "
            + ", ".join(missing)
        )

        st.info(
            "Available columns in schedule.csv: "
            + ", ".join(df.columns.astype(str))
        )

        st.stop()

    # Standardize column names
    df = df.rename(
        columns={
            batch_col: "Batch",
            day_col: "Day",
            morning_col: "9:30 - 12:30",
            afternoon_col: "2:00 - 4:30"
        }
    )

    # Clean values
    for col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    return df


# =========================================================
# LOAD DATA
# =========================================================

try:

    students = load_student_data()
    schedule = load_schedule()

except FileNotFoundError:

    st.error(
        "CSV files not found. Please keep "
        "studentdata.csv and schedule.csv "
        "in the same folder as app.py."
    )

    st.stop()


# =========================================================
# BATCH ORDER
# =========================================================

batches = [
    "A",
    "1",
    "B",
    "2",
    "C",
    "3",
    "D",
    "4"
]


# =========================================================
# METHOD B
# EQUAL DISTRIBUTION BASED ON RANK
# =========================================================

def allocate_batches(student_df, batch_list):

    # ---------------------------------------------
    # Sort by rank
    # ---------------------------------------------

    sorted_students = (
        student_df
        .sort_values(
            by="Rank",
            ascending=True
        )
        .reset_index(drop=True)
    )

    total_students = len(sorted_students)
    total_batches = len(batch_list)

    # ---------------------------------------------
    # Equal distribution
    # ---------------------------------------------

    base_size = total_students // total_batches

    remainder = total_students % total_batches

    allocations = []

    for i, batch in enumerate(batch_list):

        # First batches receive one additional student
        batch_size = (
            base_size
            + (1 if i < remainder else 0)
        )

        allocations.extend(
            [batch] * batch_size
        )

    sorted_students["Allocated Batch"] = allocations

    return sorted_students


students = allocate_batches(
    students,
    batches
)


# =========================================================
# SEARCH NAME
# =========================================================

students["Search Name"] = (
    students["Name"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# =========================================================
# HEADER
# =========================================================

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


# =========================================================
# SEARCH BAR
# =========================================================

st.markdown("### 🔎 Search Student Name")

search_name = st.text_input(
    "Enter your full name",
    placeholder="Type your name here...",
    label_visibility="collapsed"
)


# =========================================================
# SEARCH
# =========================================================

if search_name.strip():

    search_text = (
        search_name
        .strip()
        .lower()
    )

    # ---------------------------------------------
    # EXACT MATCH
    # ---------------------------------------------

    exact_matches = students[
        students["Search Name"] == search_text
    ]

    if len(exact_matches) == 1:

        selected_student = exact_matches.iloc[0]

    elif len(exact_matches) > 1:

        st.warning(
            "More than one student has the same name. "
            "Please enter the complete name."
        )

        st.stop()

    else:

        # -----------------------------------------
        # PARTIAL MATCH
        # -----------------------------------------

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

            st.info(
                "Multiple students found. "
                "Please select your name."
            )

            selected_name = st.selectbox(
                "Select your name",
                matches["Name"].tolist()
            )

            selected_student = matches[
                matches["Name"] == selected_name
            ].iloc[0]


    # =====================================================
    # STUDENT DETAILS
    # =====================================================

    student_name = selected_student["Name"]

    branch = selected_student["Branch"]

    allocated_batch = selected_student[
        "Allocated Batch"
    ]


    # =====================================================
    # DISPLAY STUDENT INFORMATION
    # =====================================================

    st.markdown(
        '<div class="student-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="student-name">'
        f'👤 {student_name}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="branch">'
        f'Branch: <b>{branch}</b>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="batch">
            🎓 Batch: {allocated_batch}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # =====================================================
    # FIND BATCH SCHEDULE
    # =====================================================

    batch_schedule = schedule[
        schedule["Batch"]
        .str.upper()
        ==
        str(allocated_batch).upper()
    ].copy()


    # =====================================================
    # DISPLAY SCHEDULE
    # =====================================================

    st.markdown(
        '<div class="schedule-title">'
        '📅 Your Orientation Schedule'
        '</div>',
        unsafe_allow_html=True
    )

    if len(batch_schedule) > 0:

        display_schedule = batch_schedule[
            [
                "Day",
                "9:30 - 12:30",
                "2:00 - 4:30"
            ]
        ].copy()

        # Make schedule text cleaner
        for column in [
            "9:30 - 12:30",
            "2:00 - 4:30"
        ]:

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
            f"Schedule information for Batch "
            f"{allocated_batch} is not available."
        )


# =========================================================
# INITIAL MESSAGE
# =========================================================

else:

    st.info(
        "👆 Enter your name in the search box above "
        "to find your allocated Batch and schedule."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Vignan's Institute of Engineering for Women<br>
        Orientation Program - Department of BS&H<br>
        Dr. Srikanth Vemuri
    </div>
    """,
    unsafe_allow_html=True
)
