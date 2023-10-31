# forntend-backend-and-data-analysis
# Create a CSV file processing tool that allows users to upload and process CSV files, and store the processed data in a basic database.
# . Visit the web application.
2. Use the "Browse" button to upload your CSV file.
3. Click the "Submit" button to process the file.
4. The data will be stored in a database engine of your choice and into different tables 
depending on the fields used in the CSV file (Use the appropriate data model based on 
the logical relations between the entities in the CSV file).
5. Process the data to answer the following questions:
a. Number of employees per department.
b. Number of employees per manager.
c. Average, min, max salary per department.
d. Average, min, max salary per education level.
e. A histogram showing the Age distribution per nationality.
f. A histogram showing the Age distribution per residence location.
6. Display visuals of the processed data on the web page. 
7. A confirmation message will appear when processing is complete showing the successful
processing and the total processed records. 
8. Users can download the uploaded CSV file, but with the following modifcations:
a. duplicates are dropped 
b. non approved salaries (<300 or >30000 but not approved) are rounded to the 
closest limit.
c. Records with null values are highlighted in the csv with a special color.
