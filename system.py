# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from PIL import Image
import xlsxwriter

# create and connect db
con = sqlite3.connect("web20.db")
cr = con.cursor()
# create table and fields
cr.execute("""
CREATE TABLE if not exists Manager (
ManagerID serial PRIMARY KEY, 
ManagerName character varying(255) NOT NULL)""")

cr.execute("""
CREATE TABLE if not exists Department (
        DepartmentID serial PRIMARY KEY, 
        DepartmentName character varying(255) NOT NULL, 
        ManagerID integer, 
        FOREIGN KEY (ManagerID) REFERENCES Manager (ManagerID) ON DELETE CASCADE)""")

cr.execute("""
    CREATE TABLE if not exists Employee (
        EmployeeID serial PRIMARY KEY,
        Name character varying(255) NOT NULL,
        Department integer REFERENCES Department (DepartmentName) ON DELETE CASCADE,
        Age integer CHECK (Age > 18),
        Gender character varying(10) CHECK (Gender IN ('M', 'F')),
        Salary numeric(10, 2),
        Manager integer,
        Education_level character varying(50) CHECK (Education_level IN ('High School', 'Undergraduate', 'Graduate', 'phD')),
        Nationality character varying(255),
        Residence character varying(255) CHECK (Residence IN ('Amman', 'Irbid', 'Aqaba', 'Zarqa', 'Madaba', 'Karak', 'Maan', 'Tafilah', 'Balqa', 'Mafraq', 'Jerash', 'Ajloun')),
       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")

 # Insert managers into the Manager table

# Check if the Manager table is empty
cr.execute("SELECT * FROM Manager")
existing_managers = cr.fetchall()

if not existing_managers:
    # If the table is empty, insert managers
    managers = [
        (1, "Tariq"),
        (2, "Loay"),
        (3, "Ahmad"),
        (4, "Hatem"),
        (5, "Asmma")
    ]

    cr.executemany("INSERT INTO Manager (ManagerID, ManagerName) VALUES (?, ?)", managers)
    con.commit()

# Check if the Department table is empty
cr.execute("SELECT * FROM Department")
existing_departments = cr.fetchall()

if not existing_departments:
    # If the table is empty, insert departments
    departments = [
        (1, "HR", 5),
        (2, "DS", 1),
        (3, "SE", 2),
        (4, "MA", 3),
        (5, "FIN", 4)
    ]

    cr.executemany("INSERT INTO Department (DepartmentID, DepartmentName, ManagerID) VALUES (?, ?, ?)", departments)
con.commit()
st.title("CSV Processing Tool")
st.sidebar.title("Upload CSV File")

uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

# Placeholder for Snackbar
processing_snackbar = st.empty()
def round_salary(salary):
    if salary < 300:
        return 300
    elif salary > 30000:
        return 30000
    return salary
def validate_manager_department(df):
    for index, row in df.iterrows():
        department_name = row['Department']
        manager_name = row['Manager']

        # Check if the manager's name matches the department's stored manager
        manager_query = cr.execute(
            "SELECT Manager.ManagerName FROM Department "
            "JOIN Manager ON Department.ManagerID = Manager.ManagerID "
            "WHERE Department.DepartmentName = ?",
            (department_name,)
        )
        stored_manager = manager_query.fetchone()[0] if manager_query else None

        if manager_name != stored_manager:
            return f"Error: Manager '{manager_name}' doesn't match the department's stored manager '{stored_manager}'."
    return None

if uploaded_file is not None:
    st.sidebar.write("Choose data processing options:")
    round_salaries = st.sidebar.selectbox("Do you want to approve or round out of range salaries?", ["Round", "Approve"])
    if st.sidebar.button("Submit"):
        df = pd.read_csv(uploaded_file)
        # Check for existing records in the database
        existing_records_query = "SELECT DISTINCT Name FROM Employee"
        existing_records = pd.read_sql(existing_records_query, con)

        # Identify new records that don't exist in the database
        new_records = df[~df['Name'].isin(existing_records['Name'])]

        if not new_records.empty:
            # Round salaries for the new records
            if round_salaries == "Round":
                new_records['Salary'] = new_records['Salary'].apply(round_salary)

            # Validate manager names against department's stored manager for new records
            validation_error = validate_manager_department(new_records)

            if validation_error:
                st.error(validation_error)
            else:
                # Append the new data to the "Employee" table
                new_records.to_sql("Employee", con, if_exists="append", index=False)
                con.commit()
        con.commit()

        # Display the uploaded data
        # Styler to highlight null values
        st.subheader("Processed File")
        st.dataframe(df.style.highlight_null())

        # Calculate the number of employees per department
        employee_count_by_department = df['Department'].value_counts()
        st.subheader("Number of Employees per Department")
        st.bar_chart(employee_count_by_department)

        # Calculate the number of employees per manager
        employee_count_by_manager = df['Manager'].value_counts()
        st.subheader("Number of Employees per Manager")
        st.bar_chart(employee_count_by_manager)

        # Calculate average, min, and max salary per department
        department_stats = df.groupby('Department')['Salary'].agg(['mean', 'min', 'max'])
        st.subheader("Salary Statistics per Department")
        st.write(department_stats)

        # Calculate average, min, and max salary per education level
        education_stats = df.groupby('Education_level')['Salary'].agg(['mean', 'min', 'max'])
        st.subheader("Salary Statistics per Education Level")
        st.write(education_stats)

        # Age Distribution per Nationality
        st.subheader("Age Distribution per Nationality")
        # Get a list of unique nationalities and assign colors using seaborn color palettes
        nationalities = df['Nationality'].unique()
        colors = sns.color_palette("husl", len(nationalities))

        # Create a single histogram with different colors for each nationality
        fig, ax = plt.subplots()
        for i, nationality in enumerate(nationalities):
            nationality_data = df[df['Nationality'] == nationality]
            ax.hist(nationality_data['Age'], bins=10, label=nationality, color=colors[i], alpha=0.7)

        ax.set_xlabel("Age")
        ax.set_ylabel("Frequency")
        ax.legend()
        st.pyplot(fig)

        # Age Distribution per Residence Location
        st.subheader("Age Distribution per Residence Location")
        # Get a list of unique residence locations and assign colors using seaborn color palettes
        locations = df['Residence'].unique()
        colors = sns.color_palette("husl", len(locations))

        # Create a single histogram with different colors for each location
        fig, ax = plt.subplots()
        for i, location in enumerate(locations):
            location_data = df[df['Residence'] == location]
            ax.hist(location_data['Age'], bins=10, label=location, color=colors[i], alpha=0.7)

        ax.set_xlabel("Age")
        ax.set_ylabel("Frequency")
        ax.legend()
        st.pyplot(fig)


        # Create a Pandas Styler to highlight null values
        def highlight_nulls(val):
            if pd.isnull(val):
                return 'background-color: yellow'
            return ''


        st.subheader("To Download the processed CSV:")
        processed_data = pd.read_sql("SELECT * FROM Employee", con)
        processed_data_styled = processed_data.style.applymap(highlight_nulls)

        # Provide a download link for the processed CSV
        csv = processed_data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="processed_data.csv">Click here!</a>'
        st.markdown(href, unsafe_allow_html=True)


        # Apply the Styler to the DataFrame
        styled_df = df.style.applymap(highlight_nulls)

        st.subheader("To Download the Excel file:")
        # Write the styled DataFrame to an Excel file
        with pd.ExcelWriter('processed_data.xlsx', engine='xlsxwriter') as writer:
            styled_df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Provide a download link for the Excel file
        excel_b64 = base64.b64encode(open('processed_data.xlsx', 'rb').read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="processed_data.xlsx">Download Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

        # Display a Snackbar when processing is complete
        processing_snackbar.info("Processing is complete. Total records processed: " + str(len(df)))
        con.close()
else:
    st.subheader("Welcome!")
    st.write("This tool was created to simplify the process of analyzing CSV files.")
    st.subheader(" ")

    # Create two columns
    col1, col2 = st.columns(2)

    # Column 1: Key Features
    with col1:
        st.subheader("Key Features")
        st.write("✅ Analyze data from CSV files.")
        st.write("📊 Generate visualizations for data insights.")
        st.write("💾 Download processed data for further use")

    # Column 2: How to Use
    with col2:
        st.subheader("How to Use")
        st.write("1. Upload your CSV file.")
        st.write("2. Click the 'Submit' button to process the file.")
        st.write("3. Explore your data and download the results")
    st.subheader(" ")

    image = Image.open("img.jpg")
    st.image(image, width=400)










