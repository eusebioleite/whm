import os
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import sys
import shutil
import warnings

def handle_i(y):
    """
    Handle the specified input 'y' to either create a new configuration or provide a warning.

    Parameters:
    - y (str): Input to determine whether to proceed with the configuration setup.

    Returns:
    None
    """

    if y == "y":
        # Set the configuration path
        config_path = os.path.join(os.path.expanduser("~"), ".whm")

        # Check if the configuration path exists
        if os.path.exists(config_path):
            # Remove existing directory if it exists
            shutil.rmtree(config_path)
            print(f"Existing directory removed: {config_path}")

        # Create the configuration directory
        os.makedirs(config_path)
        print(f"Directory created in the home folder: {config_path}")

        # Establish a connection to the SQLite database
        connection = sqlite3.connect(os.path.join(config_path, 'whm.db'))
        cursor = connection.cursor()

        # Drop the 'whm' table if it exists
        cursor.execute("DROP TABLE IF EXISTS whm;")

        # Create the 'whm' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS whm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description VARCHAR,
                `group` VARCHAR,
                `hour` FLOAT,
                `date` DATETIME,
                date2 DATETIME,
                total_hours FLOAT,
                subtotal FLOAT
            );
        ''')

        # Commit changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()
    else:
        print("Run this command once, it deletes all records and creates everything again, pass the 'y' parameter to confirm.")


def handle_h():
    """
    Display help information for each command.

    Returns:
    None
    """    
    print("""
    Help commands:
    
    i: Initialize
        - Usage: whm i [--y]
        - Description: Initializes the application, creates the necessary directory and SQLite database. Use --y to confirm and delete all records.

    h: Help
        - Usage: whm h
        - Description: Displays help information for each command.

    n: New Entry
        - Usage: whm n <name> [<group>] [<hour>]
        - Description: Adds a new entry to the database with the provided name, group, and hour values. Group and hour are optional.

    e: End Timer
        - Usage: whm e
        - Description: Ends the currently running timer.

    s: Search
        - Usage: whm s [<date> [<date2>] [<group>]]
        - Description: Searches and displays entries based on the specified date, date range, and/or group.

    x: Export
        - Usage: whm x <output_folder>
        - Description: Exports the database to a CSV file in the specified output folder.

    Example:
        - To add a new entry: whm n "Meeting" "ProjectX" 2.5
        - To search for entries: whm s "01-01-2023" "31-12-2023" "ProjectY"
    """)

def handle_n(name, group, hour):
    """
    Handles the insertion of data into the 'whm' SQLite database.

    Parameters:
    - name (str): Description or name associated with the data entry.
    - group (str): Group information (default to 'NA' if not provided).
    - hour (float): Hour value (defaults to the latest hour value if not provided).

    This function connects to the 'whm' database, retrieves the latest hour value,
    and inserts a new row with the specified information into the 'whm' table.

    Note: The 'whm' table schema should have columns 'description', 'group', 'hour',
    'date', 'date2', 'total_hours', and 'subtotal'.
    """
    if name:
        # Get the path to the configuration file
        config_path = os.path.join(os.path.expanduser("~"), ".whm")

        # Connect to the 'whm' database
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()

        # Retrieve the latest row from the 'whm' table
        cursor.execute("SELECT * FROM whm ORDER BY `date` DESC LIMIT 1;")
        rows = cursor.fetchall()
        hour_value = 0.0
        for row in rows:
            hour_value = row[3]

        # Insert a new row into the 'whm' table
        cursor.execute(f'''INSERT INTO whm (description, `group`, `hour`, `date`,
                           date2, total_hours, subtotal)
                           VALUES ('{name}', '{group if group else 'NA'}', 
                                   {hour if hour else hour_value}, 
                                   '{datetime.now()}', null, 0.0, 0.0);''')

        # Commit changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()
    else:
        print( """Usage: whm n <name> [<group>] [<hour>]
    - Adds a new entry to the database with the provided name, group, and hour values. Group and hour are optional.""")

def handle_e():
    """
    Handles the update of the 'whm' database by calculating and updating
    the total hours and subtotal for the latest entry.

    This function connects to the 'whm' database, retrieves the latest entry,
    calculates the time difference, and updates the 'date2', 'total_hours',
    and 'subtotal' columns for that entry.

    Note: The 'whm' table schema should have columns 'id', 'description', 'group',
    'hour', 'date', 'date2', 'total_hours', and 'subtotal'.
    """
    # Get the path to the configuration file
    config_path = os.path.join(os.path.expanduser("~"), ".whm")

    # Connect to the 'whm' database
    connection = sqlite3.connect(config_path + '/whm.db')
    cursor = connection.cursor()

    # Retrieve the latest row from the 'whm' table
    cursor.execute("SELECT * FROM whm ORDER BY `date` DESC LIMIT 1;")
    rows = cursor.fetchall()
    difference = 0.0
    hour_value = 0.0
    id_value = 0

    # Calculate time difference and retrieve relevant values
    for row in rows:
        date1 = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
        date2 = datetime.now()
        difference = round(((date2 - date1).total_seconds() / 3600), 2)
        hour_value = row[3]
        id_value = row[0]

    # Update the 'whm' table with calculated values
    cursor.execute(f'''UPDATE whm
                   SET date2="{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}", 
                   total_hours={difference}, 
                   subtotal={(hour_value * difference)}
                   WHERE id={id_value};''')

    # Commit changes, close the connection, and print a message
    connection.commit()
    cursor.close()
    connection.close()
    print("Timer ended.")

def handle_s(date, date2, group):
    """
    Handles the retrieval and display of data from the 'whm' database based on specified criteria.

    Parameters:
    - date (str): Starting date for filtering data (format: "%d-%m-%Y").
    - date2 (str): Ending date for filtering data (format: "%d-%m-%Y").
    - group (str): Group information for filtering data.

    This function connects to the 'whm' database, constructs and executes SQL queries based on
    the provided parameters, and prints the results in a formatted table.

    Note: The 'whm' table schema should have columns 'date', 'description', 'group', 'total_hours',
    'hour', and 'subtotal'.
    """
    # Get the path to the configuration file
    config_path = os.path.join(os.path.expanduser("~"), ".whm")

    # Connect to the 'whm' database
    connection = sqlite3.connect(config_path + '/whm.db')
    cursor = connection.cursor()

    # Initialize variables
    is_date = False

    # Suppress DeprecationWarning for date parsing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)

        # Check if 'date' is a valid date format
        if date is not None:
            try:
                datetime.strptime(date, "%d-%m-%Y")
                is_date = True
            except ValueError:
                is_date = False

        # Execute appropriate query based on provided parameters
        if date and date2 and group:
            query = '''SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm
                        WHERE whm.date >= ? AND whm.date <= ? AND whm."group" = ?;'''
            cursor.execute(query, (datetime.strptime(date, "%d-%m-%Y"), datetime.strptime(date2, "%d-%m-%Y"), group))
        elif date and date2:
            query = '''SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm
                        WHERE whm.date >= ? AND whm.date <= ?;'''
            cursor.execute(query, (datetime.strptime(date, "%d-%m-%Y"), datetime.strptime(date2, "%d-%m-%Y")))
        elif is_date:
            cursor.execute(f'''SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm
                                WHERE strftime("%d-%m-%Y", whm.date) = "{date}";''')
        elif date is not None:
            cursor.execute(f'''SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm
                                WHERE whm."group" = "{date}";''')
        elif date is None:
            cursor.execute('SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm ORDER BY whm.date DESC LIMIT 1;')

        # Fetch and display results in a formatted table
        rows = cursor.fetchall()
        col_widths = [20, 40, 10, 8, 8, 8]
        print("+" + "+".join("-" * (width + 2) for width in col_widths) + "+")
        print("|  " + "|  ".join(f'{header.ljust(width)}' for header, width in zip(["Date", "Description", "Group", "Hours", "$Hour", "Total"], col_widths)) + "|")
        print("+" + "+".join("-" * (width + 2) for width in col_widths) + "+")

        for row in rows:
            formatted_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M:%S")
            formatted_total = "{:.2f}".format(row[5])
            row_data = [
                formatted_date,
                row[1],
                row[2],
                f'{row[3]:.2f}',
                f'{row[4]:.2f}',
                formatted_total
            ]
            print("| " + " | ".join(data.ljust(width) for data, width in zip(row_data, col_widths)) + " |")

        print("+" + "+".join("-" * (width + 2) for width in col_widths) + "+")

    # Close the cursor, connection, and exit the function
    cursor.close()
    connection.close()
        
def handle_x(output_folder=None):
    """
    Generates a PDF document containing data from the 'whm' table.

    Args:
        output_folder (str, optional): The path to the output folder for the generated PDF file.

    Returns:
        None
    """
    # Database connection setup
    config_path = os.path.join(os.path.expanduser("~"), ".whm")
    connection = sqlite3.connect(os.path.join(config_path, 'whm.db'))
    cursor = connection.cursor()

    # Fetching data from the 'whm' table
    cursor.execute("SELECT description, `group`, `hour`, date, date2, total_hours, subtotal FROM whm")
    rows = cursor.fetchall()

    # PDF document setup
    pdf_file_path = "whm_data.pdf"
    if output_folder:
        pdf_file_path = os.path.join(output_folder, pdf_file_path)
    pdf_document = SimpleDocTemplate(pdf_file_path, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']
    style_heading = styles['Heading1']

    # Table data setup
    table_data = [['Start', 'End', 'Description', 'Group', 'Total Hours', 'Hour $', 'Total $']]

    # Formatting and populating table data
    for row in rows:
        start_date = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M")
        end_date = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M")
        formatted_hour = "{:.2f}".format(row[2])
        formatted_total_hours = "{:.2f}".format(row[5])
        formatted_subtotal = "{:.2f}".format(row[6])
        table_data.append([start_date, end_date, row[0], row[1], formatted_total_hours, formatted_hour, formatted_subtotal])

    # Creating and styling the table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    # Building the PDF document
    pdf_document.build([table])

    # Closing the database connection
    cursor.close()
    connection.close()

    # Displaying the path to the generated PDF
    print(f"PDF generated at: {pdf_file_path}")

def main():

    if len(sys.argv) < 2:
        print("Please provide a command.")
        sys.exit(1)

    command = sys.argv[1]
    if command == 'i':
        """
         i: Initialize
            - Usage: whm i [--y]
            - Description: Initializes the application, creates the necessary directory and SQLite database. Use --y to confirm and delete all records.
        """
        handle_i(sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == 'h':
        """
        h: Help
            - Usage: whm h
            - Description: Displays help information for each command.
        """
        handle_h()
    elif command == 'n':
        """
        n: New Entry
            - Usage: whm n <name> [<group>] [<hour>]
            - Description: Adds a new entry to the database with the provided name, group, and hour values. Group and hour are optional.
        """
        handle_n(sys.argv[2] if len(sys.argv) > 2 else None,
                 sys.argv[3] if len(sys.argv) > 3 else None,
                 sys.argv[4] if len(sys.argv) > 4 else None)
    elif command == 'e':
        """
        e: End Timer
            - Usage: whm e
            - Description: Ends the currently running timer.
        """
        handle_e()
    elif command == 's':
        """
        s: Search
            - Usage: whm s [<date> [<date2>] [<group>]]
            - Description: Searches and displays entries based on the specified date, date range, and/or group.
        """
        handle_s(sys.argv[2] if len(sys.argv) > 2 else None,
                 sys.argv[3] if len(sys.argv) > 3 else None,
                 sys.argv[4] if len(sys.argv) > 4 else None)
    elif command == 'x':
        """
        x: Export
            - Usage: whm x <output_folder>
            - Description: Exports the database to a CSV file in the specified output folder.
        """
        handle_x(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print("Invalid command, type whm h to a list of commands.")
        sys.exit(1)

if __name__ == '__main__':
    main()