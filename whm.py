import os
import sqlite3
from datetime import datetime
import csv
import sys

def handle_i(y):
    if y:
        # Create config directory
        config_path = os.path.join(os.path.expanduser("~"), ".whm")
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            print(f"Directory created in the home folder: {config_path}")

        # Start SQLite connection
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS whm;")

        cursor.execute('''CREATE TABLE IF NOT EXISTS whm (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description VARCHAR,
            `group` VARCHAR,
            `hour` FLOAT,
            `date` DATETIME,
            date2 DATETIME,
            total_hours FLOAT,
            subtotal FLOAT);''')

        connection.commit()
        cursor.close()
        connection.close()
    else:
        print("Run this command once, it deletes all records and creates everything again, pass the --y parameter to confirm.")

def handle_h():
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
    if name:
        # Start SQLite connection
        config_path = os.path.join(os.path.expanduser("~"), ".whm")
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()

        # Get last hour value
        cursor.execute("SELECT * FROM whm ORDER BY `date` DESC LIMIT 1;")
        rows = cursor.fetchall()
        hour_value = 0.0
        for row in rows:
            hour_value = row[3]

        cursor.execute('INSERT INTO whm (description, `group`, `hour`, `date`, date2, total_hours, subtotal) ' +
                       f"VALUES ('{name}', '{group if group else 'NA'}', {hour if hour else hour_value}, '{datetime.now()}', null, 0.0, 0.0);")

        connection.commit()
        cursor.close()
        connection.close()

def handle_e():
    # Start SQLite connection
    config_path = os.path.join(os.path.expanduser("~"), ".whm")
    connection = sqlite3.connect(config_path + '/whm.db')
    cursor = connection.cursor()

    # Get the last running timer, and calculate the total_hours and subtotal
    cursor.execute("SELECT * FROM whm ORDER BY `date` DESC LIMIT 1;")
    rows = cursor.fetchall()
    difference = 0.0
    hour_value = 0.0
    id_value = 0
    for row in rows:
        date1 = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
        date2 = datetime.now()
        difference = round(((date2 - date1).total_seconds() / 3600), 2)
        hour_value = row[3]
        id_value = row[0]

    # Finish the last running timer
    cursor.execute('UPDATE whm ' +
                   f'SET date2="{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}", total_hours={difference}, subtotal={(hour_value * difference)} ' +
                   f'WHERE id={id_value};')

    connection.commit()
    cursor.close()
    connection.close()
    print("Timer ended.")


def handle_s(date, date2, group):
    # Start SQLite connection
    config_path = os.path.join(os.path.expanduser("~"), ".whm")
    connection = sqlite3.connect(config_path + '/whm.db')
    cursor = connection.cursor()
    is_date = False
    if date is not None:
        try:
            # Attempt to convert the date parameter to a valid date
            datetime.strptime(date, "%d-%m-%Y")
            is_date = True
        except ValueError:
            is_date = False
    if date and date2 and group:
        cursor.execute('SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm ' +
                        f'WHERE strftime("%d-%m-%Y", whm.date) >= "{date}" AND strftime("%d-%m-%Y", whm.date) <= "{date2}" AND whm."group" = "{group}";')
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
    elif date and date2:
        cursor.execute('SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm ' +
                        f'WHERE strftime("%d-%m-%Y", whm.date) >= "{date}" AND strftime("%d-%m-%Y", whm.date) <= "{date2}";')
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
    elif is_date:
        cursor.execute('SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm ' +
                        f'WHERE strftime("%d-%m-%Y", whm.date) = "{date}"')
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
    elif date is not None:
        cursor.execute('SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm ' +
                        f'WHERE whm."group" = "{date}";')
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
    elif date is None:
        cursor.execute('SELECT whm.date, whm.description, whm."group", whm.total_hours, whm."hour", whm.subtotal FROM whm ORDER BY whm.date DESC LIMIT 1;')
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

    cursor.close()
    connection.close()

def handle_x(output_folder):
    if output_folder:
        # Connect to the SQLite database
        config_path = os.path.join(os.path.expanduser("~"), ".whm")
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()

        # Create the output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Execute a query to fetch data from the "whm" table
        cursor.execute("SELECT * FROM whm")

        # Fetch all rows
        rows = cursor.fetchall()

        # Define the CSV file path
        csv_file_path = os.path.join(output_folder, 'whm_data.csv')

        # Write the data to the CSV file
        with open(csv_file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)

            # Write the header row
            header = [description[0] for description in cursor.description]
            csv_writer.writerow(header)

            # Write the data rows
            csv_writer.writerows(rows)

        # Close the cursor and the database connection
        cursor.close()
        connection.close()
    else:
        print("The parameter --output_folder is required")

def main():

    if len(sys.argv) < 2:
        print("Please provide a command.")
        sys.exit(1)

    command = sys.argv[1]
    if command == 'i':
        handle_i(sys.argv[2] if len(sys.argv) > 2 else None)
    elif command == 'h':
        handle_h()
    elif command == 'n':
        handle_n(sys.argv[2] if len(sys.argv) > 2 else None,
                 sys.argv[3] if len(sys.argv) > 3 else None,
                 sys.argv[4] if len(sys.argv) > 4 else None)
    elif command == 'e':
        handle_e()
    elif command == 's':
        handle_s(sys.argv[2] if len(sys.argv) > 2 else None,
                 sys.argv[3] if len(sys.argv) > 3 else None,
                 sys.argv[4] if len(sys.argv) > 4 else None)
    elif command == 'x':
        handle_x(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print("Invalid command.")
        sys.exit(1)

if __name__ == '__main__':
    main()