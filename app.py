import streamlit as st
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Orientation Program | Vignan's Institute of Engineering for Women",
    page_icon="🎓",
    layout="centered"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.college-name {
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 6px;
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


# ============================================================
# HELPER: CLEAN COLUMN NAMES
# ============================================================

def clean_column_name(column):

    return (
        str(column)
        .replace("\ufeff", "")      # BOM
        .replace("\u00A0", " ")     # Non-breaking space
        .replace("\u2007", " ")     # Figure space
        .replace("\u202F", " ")     # Narrow no-break space
        .replace("\t", " ")         # Tab
        .strip()
    )


def normalize_column_name(column):

    return (
        clean_column_name(column)
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


# ============================================================
# LOAD STUDENT DATA
# ============================================================

@st.cache_data
def load_student_data():

    df = pd.read_csv("studentdata.csv")

    # Clean column names
    df.columns = [
        clean_column_name(column)
        for column in df.columns
    ]

    # Map normalized names to original names
    column_map = {
        normalize_column_name(column): column
        for column in df.columns
    }

    # --------------------------------------------------------
    # FIND STUDENT NAME
    # --------------------------------------------------------

    name_column = None

    for key in [
        "studentname",
        "name",
        "student"
    ]:
        if key in column_map:
            name_column = column_map[key]
            break

    # --------------------------------------------------------
    # FIND BRANCH
    # --------------------------------------------------------

    branch_column = None

    for key in [
        "branch",
        "branchname",
        "department"
    ]:
        if key in column_map:
            branch_column = column_map[key]
            break

    # --------------------------------------------------------
    # FIND RANK
    # --------------------------------------------------------

    rank_column = None

    for key in [
        "rank",
        "eapcetrank",
        "apeapcetrank",
        "eamcetrank"
    ]:
        if key in column_map:
            rank_column = column_map[key]
            break

    # --------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

    missing = []

    if name_column is None:
        missing.append("Student Name")

    if branch_column is None:
        missing.append("Branch")

    if rank_column is None:
        missing.append("Rank")

    if missing:

        st.error(
            "Required column(s) not found in studentdata.csv: "
            + ", ".join(missing)
        )

        st.info(
            "Columns detected: "
            + ", ".join(df.columns.astype(str))
        )

        st.stop()

    # --------------------------------------------------------
    # STANDARDIZE INTERNAL COLUMN NAMES
    # --------------------------------------------------------

    df = df.rename(
        columns={
            name_column: "Student Name",
            branch_column: "Branch",
            rank_column: "Rank"
        }
    )

    # --------------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------------

    df["Student Name"] = (
        df["Student Name"]
        .astype(str)
        .str.replace("\u00A0", " ", regex=False)
        .str.strip()
    )

    df["Branch"] = (
        df["Branch"]
        .astype(str)
        .str.replace("\u00A0", " ", regex=False)
        .str.strip()
    )

    df["Rank"] = pd.to_numeric(
        df["Rank"],
        errors="coerce"
    )

    # Remove invalid records
    df = df.dropna(
        subset=[
            "Student Name",
            "Rank"
        ]
    )

    # Remove empty names
    df = df[
        df["Student Name"].str.strip() != ""
    ]

    return df


# ============================================================
# LOAD SCHEDULE DATA
# ============================================================

@st.cache_data
def load_schedule_data():

    df = pd.read_csv("schedule.csv")

    # --------------------------------------------------------
    # CLEAN ALL COLUMN NAMES
    # --------------------------------------------------------

    df.columns = [
        clean_column_name(column)
        for column in df.columns
    ]

    # Map normalized names
    column_map = {
        normalize_column_name(column): column
        for column in df.columns
    }

    # --------------------------------------------------------
    # FIND DAY
    # --------------------------------------------------------

    day_column = column_map.get("day")

    # --------------------------------------------------------
    # FIND BATCH
    # --------------------------------------------------------

    batch_column = None

    for key in [
        "batch",
        "batchname",
        "batchno",
        "batchnumber"
    ]:
        if key in column_map:
            batch_column = column_map[key]
            break

    # --------------------------------------------------------
    # FIND MORNING SCHEDULE
    # 9:30 - 12:00
    # --------------------------------------------------------

    morning_column = None

    for key in [
        "9:3012:00",
        "9301200",
        "9.3012.00"
    ]:
        if key in column_map:
            morning_column = column_map[key]
            break

    # --------------------------------------------------------
    # FIND AFTERNOON SCHEDULE
    # 1:30 - 4:20
    # --------------------------------------------------------

    afternoon_column = None

    for key in [
        "1:304:20",
        "130420",
        "1.304.20"
    ]:
        if key in column_map:
            afternoon_column = column_map[key]
            break

    # --------------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # --------------------------------------------------------

    missing = []

    if day_column is None:
        missing.append("Day")

    if batch_column is None:
        missing.append("Batch")

    if morning_column is None:
        missing.append("9:30 - 12:00")

    if afternoon_column is None:
        missing.append("1:30 - 4:20")

    if missing:

        st.error(
            "Required column(s) not found in schedule.csv: "
            + ", ".join(missing)
        )

        st.info(
            "Columns detected: "
            + ", ".join(df.columns.astype(str))
        )

        st.stop()

    # --------------------------------------------------------
    # STANDARDIZE INTERNAL COLUMN NAMES
    # --------------------------------------------------------

    df = df.rename(
        columns={
            day_column: "Day",
            batch_column: "Batch",
            morning_column: "9:30 - 12:00",
            afternoon_column: "1:30 - 4:20"
        }
    )

    # --------------------------------------------------------
    # CLEAN VALUES
    # --------------------------------------------------------

    for column in df.columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.replace("\u00A0", " ", regex=False)
            .str.strip()
        )

    return df


# ============================================================
# LOAD FILES
# ============================================================

try:

    students = load_student_data()
    schedule = load_schedule_data()

except FileNotFoundError:

    st.error("CSV file not found.")

    st.info(
        "Please make sure these files are in the same folder "
        "as app.py:"
    )

    st.code(
        "app.py\n"
        "studentdata.csv\n"
        "schedule.csv"
    )

    st.stop()


# ============================================================
# BATCH ORDER
# ============================================================

# Students will be distributed in this exact order.

BATCHES = [
    "A",
    "1",
    "B",
    "2",
    "C",
    "3",
    "D",
    "4"
]


# ============================================================
# EQUAL BATCH ALLOCATION
# ============================================================

def allocate_batches(student_data):

    # --------------------------------------------------------
    # Sort students by rank
    # --------------------------------------------------------

    sorted_students = (
        student_data
        .sort_values(
            by="Rank",
            ascending=True
        )
        .reset_index(drop=True)
    )

    total_students = len(sorted_students)

    total_batches = len(BATCHES)

    # --------------------------------------------------------
    # Calculate equal distribution
    # --------------------------------------------------------

    students_per_batch = (
        total_students // total_batches
    )

    extra_students = (
        total_students % total_batches
    )

    allocations = []

    # --------------------------------------------------------
    # Allocate batches
    # --------------------------------------------------------

    for index, batch in enumerate(BATCHES):

        batch_size = students_per_batch

        # Give one extra student to the first batches
        if index < extra_students:
            batch_size += 1

        allocations.extend(
            [batch] * batch_size
        )

    # Safety check
    if len(allocations) != total_students:

        raise ValueError(
            "Batch allocation count does not match "
            "student count."
        )

    sorted_students["Allocated Batch"] = allocations

    return sorted_students


# ============================================================
# PERFORM ALLOCATION
# ============================================================

students = allocate_batches(students)


# ============================================================
# CREATE SEARCH FIELD
# ============================================================

students["Search Name"] = (
    students["Student Name"]
    .astype(str)
    .str.replace("\u00A0", " ", regex=False)
    .str.strip()
    .str.lower()
)


# ============================================================
# HEADER
# ============================================================

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


# ============================================================
# SEARCH BOX
# ============================================================

st.markdown("### 🔎 Search Student Name")

search_name = st.text_input(
    "Enter your name",
    placeholder="Type your name here...",
    label_visibility="collapsed"
)


# ============================================================
# SEARCH PROCESS
# ============================================================

if search_name.strip():

    search_text = (
        search_name
        .strip()
        .lower()
    )

    # --------------------------------------------------------
    # EXACT MATCH
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # PARTIAL MATCH
        # ----------------------------------------------------

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


    # ========================================================
    # GET STUDENT INFORMATION
    # ========================================================

    student_name = selected_student[
        "Student Name"
    ]

    branch = selected_student[
        "Branch"
    ]

    allocated_batch = selected_student[
        "Allocated Batch"
    ]


    # ========================================================
    # DISPLAY STUDENT DETAILS
    # ========================================================

    st.markdown(
        '<div class="student-card">',
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
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # FIND BATCH SCHEDULE
    # ========================================================

    batch_schedule = schedule[
        schedule["Batch"]
        .str.strip()
        .str.upper()
        ==
        str(allocated_batch)
        .strip()
        .upper()
    ].copy()


    # ========================================================
    # DISPLAY SCHEDULE
    # ========================================================

    st.markdown(
        """
        <div class="schedule-title">
            📅 Your Orientation Schedule
        </div>
        """,
        unsafe_allow_html=True
    )

    if not batch_schedule.empty:

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


# ============================================================
# INITIAL MESSAGE
# ============================================================

else:

    st.info(
        "👆 Enter your name in the search box above "
        "to find your allocated Batch and schedule."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Vignan's Institute of Engineering for Women<br>
        Orientation Program - Department of BS&H<br>
        Dr. V. Srikanth
    </div>
    """,
    unsafe_allow_html=True
)
