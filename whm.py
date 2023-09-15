import argparse
import os
import sqlite3
from datetime import datetime
import csv

def handle_i(args):
    if args.y:
        # Create config directory
        config_path = os.path.join(os.path.expanduser("~"), ".whm")
        if not os.path.exists(config_path):
            os.makedirs(config_path)
            print(f"Directory created in the home folder: {config_path}")
        else:
            print(f"Directory already exists in the home folder: {config_path}")

        #Start SQLite connection
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()
        
        cursor.execute("DROP TABLE whm;")

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

def handle_h(args):
    print("Help commands")

def handle_n(args):
    if args.name:
        #Start SQLite connection
        config_path = os.path.join(os.path.expanduser("~"), ".whm")
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()

        # Get last hour value
        cursor.execute("SELECT * FROM whm ORDER BY `date` DESC LIMIT 1;")
        rows = cursor.fetchall()
        hour = 0.0
        for row in rows:
            hour = row[3]

        cursor.execute('INSERT INTO whm (description, `group`, `hour`, `date`, date2, total_hours, subtotal) ' +
               f"VALUES ('{args.name}', '{args.group if args.group else 'NA'}', {args.hour if args.hour else hour}, '{datetime.now()}', null, 0.0, 0.0);")

        connection.commit()
        cursor.close()
        connection.close()
    else:
        print("The parameter --name is required")

def handle_e(args):
    #Start SQLite connection
    config_path = os.path.join(os.path.expanduser("~"), ".whm")
    connection = sqlite3.connect(config_path + '/whm.db')
    cursor = connection.cursor()
    
    #Get the last running timer, and calculates the total_hours and subtotal
    cursor.execute("SELECT * FROM whm ORDER BY `date` DESC LIMIT 1;")
    rows = cursor.fetchall()
    difference = 0.0
    hour = 0.0
    id = 0
    for row in rows:

        date1 = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S.%f")
        date2 = datetime.now()
        difference = round(((date2 - date1).total_seconds() / 3600), 2)
        hour = row[3]
        id = row[0]

    # Finish the last running timer x
    cursor.execute('UPDATE whm ' +
               f'SET date2="{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}", total_hours={difference}, subtotal={(hour * difference)} ' +
               f'WHERE id={id};')

    
    connection.commit()
    cursor.close()
    connection.close()

def handle_s(args):
    #Start SQLite connection
    config_path = os.path.join(os.path.expanduser("~"), ".whm")
    connection = sqlite3.connect(config_path + '/whm.db')
    cursor = connection.cursor()
    if args.date and args.date2 and args.sgroup:
        cursor.execute('SELECT `date`, description, `group`, total_hours, `hour`, subtotal FROM whm ' +
                       f'WHERE `date`>={args.date} and date2<={args.date2} and `group`="{args.sgroup}";')
        rows = cursor.fetchall()
        print("Date | Description | Group | Hours | $Hour | Total")
        for row in rows:
            print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
    elif args.date and args.date2:
        cursor.execute('SELECT `date`, description, `group`, total_hours, `hour`, subtotal FROM whm ' +
                       f'WHERE `date`>={args.date} and date2<={args.date2};')
        rows = cursor.fetchall()
        print("Date | Description | Group | Hours | $Hour | Total")
        for row in rows:
            print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
    elif args.date:
        cursor.execute('SELECT `date`, description, `group`, total_hours, `hour`, subtotal FROM whm ' +
                       f'WHERE `date`={args.date};')
        rows = cursor.fetchall()
        print("Date | Description | Group | Hours | $Hour | Total")
        for row in rows:
            print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
    elif args.sgroup:
        cursor.execute('SELECT `date`, description, `group`, total_hours, `hour`, subtotal FROM whm ' +
                       f'WHERE `group`="{args.sgroup}";')
        rows = cursor.fetchall()
        print("Date | Description | Group | Hours | $Hour | Total")
        for row in rows:
            print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]}')
    else:
        cursor.execute("SELECT `date`, description, `group`, total_hours, `hour`, subtotal FROM whm ORDER BY `date` DESC LIMIT 1;")
        rows = cursor.fetchall()
        print("Last timer:")
        print("Date                | Description | Group | Hours | $Hour | Total")
        for row in rows:
            formatted_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f").strftime("%d-%m-%Y %H:%M:%S")
            formatted_total = "{:.2f}".format(row[5])  # Format total to two decimal places
            print(f'{formatted_date} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {formatted_total}')

    
    cursor.close()
    connection.close()
    
def handle_x(args):
    if args.output_folder:
        # Connect to the SQLite database
        config_path = os.path.join(os.path.expanduser("~"), ".whm")
        connection = sqlite3.connect(config_path + '/whm.db')
        cursor = connection.cursor()

        # Create the output folder if it doesn't exist
        if not os.path.exists(args.output_folder):
            os.makedirs(args.output_folder)

        # Execute a query to fetch data from the "whm" table
        cursor.execute("SELECT * FROM whm")

        # Fetch all rows
        rows = cursor.fetchall()

        # Define the CSV file path
        csv_file_path = os.path.join(args.output_folder, 'whm_data.csv')

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
    parser = argparse.ArgumentParser(description='Desc')

    subparsers = parser.add_subparsers(title='Commands', dest='command', required=True)

    # Subparser for the init command
    init_parser = subparsers.add_parser('i', help='Generate config files, only executed once')
    init_parser.add_argument('--y', required=False, help='Confirm drop and create')
    init_parser.set_defaults(func=handle_i)

    # Subparser for the help command
    help_parser = subparsers.add_parser('h', help='Display commands')
    help_parser.set_defaults(func=handle_h)

    # Subparser for the new command
    new_parser = subparsers.add_parser('n', help='Start a timer')
    new_parser.add_argument('--name', required=False, help='Timer name')
    new_parser.add_argument('--group', required=False, help='Timer group')
    new_parser.add_argument('--hour', required=False, help='Set the hour value, if no value is specified, it\'ll get the last value')
    new_parser.set_defaults(func=handle_n)

    # Subparser for the end command
    end_parser = subparsers.add_parser('e', help='Stop the timer')
    end_parser.set_defaults(func=handle_e)

    # Subparser for the show command
    show_parser = subparsers.add_parser('s', help='Display the current timer')
    show_parser.add_argument('--date', required=False, help='Display timers from this date or if date2 is set, after this date')
    show_parser.add_argument('--date2', required=False, help='Display timers from before this date')
    show_parser.add_argument('--sgroup', required=False, help='Display timers from the specified group')
    show_parser.set_defaults(func=handle_s)

    # Subparser for the export command
    export_parser = subparsers.add_parser('x', help='Export the records to csv')
    export_parser.add_argument('--output_folder', required=False, help='Which folder to export')
    export_parser.set_defaults(func=handle_x)

    args = parser.parse_args()

    # Call the appropriate function based on the selected command
    args.func(args)

if __name__ == '__main__':
    main()
    
    
