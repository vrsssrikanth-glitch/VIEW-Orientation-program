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
    font-size: 25px;
    font-weight: 600;
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    font-size: 16px;
    margin-bottom: 28px;
}

.student-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #dddddd;
    margin-top: 20px;
    margin-bottom: 20px;
}

.student-name {
    font-size: 23px;
    font-weight: 600;
    margin-bottom: 8px;
}

.branch {
    font-size: 18px;
    margin-bottom: 12px;
}

.batch {
    font-size: 30px;
    font-weight: 700;
    text-align: center;
    padding: 14px;
}

.schedule-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 25px;
    margin-bottom: 12px;
}

.footer {
    text-align: center;
    font-size: 13px;
    margin-top: 40px;
    padding-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# FUNCTION TO NORMALIZE COLUMN NAMES
# =========================================================

def normalize_column_name(column):

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


# =========================================================
# LOAD STUDENT DATA
# =========================================================

@st.cache_data
def load_student_data():

    # Read CSV
    df = pd.read_csv("studentdata.csv")

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    # -----------------------------------------------------
    # Find columns
    # -----------------------------------------------------

    column_map = {}

    for column in df.columns:
        column_map[normalize_column_name(column)] = column

    name_col = None
    branch_col = None
    rank_col = None

    # Student Name
    for key in [
        "studentname",
        "name",
        "student"
    ]:
        if key in column_map:
            name_col = column_map[key]
            break

    # Branch
    for key in [
        "branch",
        "branchname",
        "department"
    ]:
        if key in column_map:
            branch_col = column_map[key]
            break

    # Rank
    for key in [
        "rank",
        "eapcetrank",
        "apeapcetrank",
        "eamcetrank"
    ]:
        if key in column_map:
            rank_col = column_map[key]
            break

    # -----------------------------------------------------
    # Check columns
    # -----------------------------------------------------

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
            "Columns detected in studentdata.csv: "
            + ", ".join(df.columns.astype(str))
        )

        st.stop()

    # -----------------------------------------------------
    # Rename columns internally
    # -----------------------------------------------------

    df = df.rename(
        columns={
            name_col: "Student Name",
            branch_col: "Branch",
            rank_col: "Rank"
        }
    )

    # -----------------------------------------------------
    # Clean values
    # -----------------------------------------------------

    df["Student Name"] = (
        df["Student Name"]
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

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "Student Name",
            "Rank"
        ]
    )

    # Remove completely empty names
    df = df[
        df["Student Name"].str.strip() != ""
    ]

    return df


# =========================================================
# LOAD SCHEDULE DATA
# =========================================================

@st.cache_data
def load_schedule_data():

    df = pd.read_csv("schedule.csv")

    # Clean column names
    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    # -----------------------------------------------------
    # Detect columns
    # -----------------------------------------------------

    column_map = {}

    for column in df.columns:
        column_map[normalize_column_name(column)] = column

    day_col = None
    batch_col = None
    morning_col = None
    afternoon_col = None

    # Day
    for key in ["day"]:
        if key in column_map:
            day_col = column_map[key]
            break

    # Batch
    for key in [
        "batch",
        "batchname",
        "batchno",
        "batchnumber"
    ]:
        if key in column_map:
            batch_col = column_map[key]
            break

    # Morning
    for key in [
        "9:30-12:00",
        "930-1200",
        "9301200"
    ]:
        if key in column_map:
            morning_col = column_map[key]
            break

    # Afternoon
    for key in [
        "1:30-4:20",
        "130-420",
        "130420"
    ]:
        if key in column_map:
            afternoon_col = column_map[key]
            break

    # -----------------------------------------------------
    # Check columns
    # -----------------------------------------------------

    missing = []

    if day_col is None:
        missing.append("Day")

    if batch_col is None:
        missing.append("Batch")

    if morning_col is None:
        missing.append("9:30 - 12:00")

    if afternoon_col is None:
        missing.append("1:30 - 4:20")

    if missing:

        st.error(
            "Required column(s) not found in schedule.csv: "
            + ", ".join(missing)
        )

        st.info(
            "Columns detected in schedule.csv: "
            + ", ".join(df.columns.astype(str))
        )

        st.stop()

    # -----------------------------------------------------
    # Rename internally
    # -----------------------------------------------------

    df = df.rename(
        columns={
            day_col: "Day",
            batch_col: "Batch",
            morning_col: "9:30 - 12:00",
            afternoon_col: "1:30 - 4:20"
        }
    )

    # -----------------------------------------------------
    # Clean values
    # -----------------------------------------------------

    for column in df.columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )

    return df


# =========================================================
# LOAD BOTH FILES
# =========================================================

try:

    students = load_student_data()
    schedule = load_schedule_data()

except FileNotFoundError as error:

    st.error(
        "CSV file not found."
    )

    st.info(
        "Make sure these files are in the same GitHub repository "
        "and folder as app.py:"
    )

    st.code(
        "studentdata.csv\nschedule.csv"
    )

    st.stop()


# =========================================================
# BATCH ORDER
# =========================================================

# IMPORTANT:
# Students are allocated in exactly this order.

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

def allocate_batches(student_data, batch_list):

    # -----------------------------------------------------
    # Sort students by rank
    # -----------------------------------------------------

    sorted_students = (
        student_data
        .sort_values(
            by="Rank",
            ascending=True
        )
        .reset_index(drop=True)
    )

    total_students = len(sorted_students)

    total_batches = len(batch_list)

    # -----------------------------------------------------
    # Calculate equal distribution
    # -----------------------------------------------------

    base_students = total_students // total_batches

    extra_students = total_students % total_batches

    allocations = []

    # -----------------------------------------------------
    # Assign batches
    # -----------------------------------------------------

    for i, batch in enumerate(batch_list):

        # The first few batches get one extra student
        number_for_this_batch = (
            base_students
            + (1 if i < extra_students else 0)
        )

        allocations.extend(
            [batch] * number_for_this_batch
        )

    # Safety check
    if len(allocations) != total_students:

        raise ValueError(
            "Batch allocation error: "
            "number of allocations does not match "
            "number of students."
        )

    sorted_students["Allocated Batch"] = allocations

    return sorted_students


# =========================================================
# PERFORM BATCH ALLOCATION
# =========================================================

students = allocate_batches(
    students,
    batches
)


# =========================================================
# SEARCH COLUMN
# =========================================================

students["Search Name"] = (
    students["Student Name"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="college-name">
        Vignan's Institute of Engineering for Women
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="program-title">
        🎓 Welcome to Orientation Program
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        Find your allocated Batch and Orientation Program schedule
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SEARCH BOX
# =========================================================

st.markdown("### 🔎 Search Student Name")

search_name = st.text_input(
    "Student Name",
    placeholder="Enter your name...",
    label_visibility="collapsed"
)


# =========================================================
# SEARCH LOGIC
# =========================================================

if search_name.strip():

    search_text = (
        search_name
        .strip()
        .lower()
    )

    # -----------------------------------------------------
    # EXACT MATCH
    # -----------------------------------------------------

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

        # -------------------------------------------------
        # PARTIAL MATCH
        # -------------------------------------------------

        matches = students[
            students["Search Name"].str.contains(
                search_text,
                na=False,
                regex=False
            )
        ]

        if len(matches) == 0:

            st.error(
                "❌ Student name not found."
            )

            st.info(
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
                matches["Student Name"].tolist()
            )

            selected_student = matches[
                matches["Student Name"] == selected_name
            ].iloc[0]


    # =====================================================
    # STUDENT INFORMATION
    # =====================================================

    student_name = selected_student[
        "Student Name"
    ]

    branch = selected_student[
        "Branch"
    ]

    allocated_batch = selected_student[
        "Allocated Batch"
    ]


    # =====================================================
    # DISPLAY STUDENT DETAILS
    # =====================================================

    st.markdown(
        """
        <div class="student-card">
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="student-name">
            👤 {student_name}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="branch">
            Branch: <b>{branch}</b>
        </div>
        """,
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
        "</div>",
        unsafe_allow_html=True
    )


    # =====================================================
    # FIND SCHEDULE FOR THE ALLOCATED BATCH
    # =====================================================

    batch_schedule = schedule[
        schedule["Batch"]
        .str.strip()
        .str.upper()
        ==
        str(allocated_batch)
        .strip()
        .upper()
    ].copy()


    # =====================================================
    # DISPLAY SCHEDULE
    # =====================================================

    st.markdown(
        """
        <div class="schedule-title">
            📅 Your Orientation Schedule
        </div>
        """,
        unsafe_allow_html=True
    )

    if len(batch_schedule) > 0:

        display_schedule = batch_schedule[
            [
                "Day",
                "9:30 - 12:00",
                "1:30 - 4:20"
            ]
        ].copy()

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
