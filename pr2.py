import sqlite3
import os

# Database file path
DB_PATH = "database.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def table_exists(table_name):
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """, (table_name,))
        exists = cursor.fetchone() is not None
        return exists
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def create_table():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    columns = []
    
    # Get unique table name
    while True:
        table_name = input("Enter table name: ")
        if not table_exists(table_name):
            break
        else:
            print("Table already exists. Please enter a different name.")
    
    # Get column names and lengths
    print("Enter column name and its length (press Enter with empty input to finish):")
    while True:
        user_input = input("Column (name length): ")
        if not user_input.strip():
            break
        
        parts = user_input.split()
        if len(parts) == 2 and parts[1].isdigit():
            columns.append((parts[0], int(parts[1])))
        else:
            print("Invalid input. Please enter in the format: columnName length")
            continue
    
    if not columns:
        print("No columns specified. Table not created.")
        conn.close()
        return
    
    # Build CREATE TABLE SQL
    try:
        column_defs = []
        for col_name, col_length in columns:
            column_defs.append(f"{col_name} TEXT")
        
        create_sql = f"CREATE TABLE {table_name} (ID INTEGER PRIMARY KEY AUTOINCREMENT, {', '.join(column_defs)})"
        
        cursor.execute(create_sql)
        conn.commit()
        print(f"Table '{table_name}' created successfully!")
    
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
    
    finally:
        conn.close()

def insert():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get table name
    while True:
        table_name = input("Enter table name: ")
        if table_exists(table_name):
            print("Table exists.")
            break
        else:
            print("Table does not exist.")
    
    try:
        # Get column names (excluding ID)
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info if col[1] != 'ID']
        
        if not column_names:
            print("No columns to insert data into.")
            conn.close()
            return
        
        # Get user input for each column and insert
        more_entries = "y"
        while more_entries.lower() == "y":
            values = []
            for col_name in column_names:
                user_input = input(f"{col_name}: ")
                values.append(user_input)
            
            # Build INSERT SQL
            placeholders = ', '.join(['?' for _ in values])
            columns_str = ', '.join(column_names)
            insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            cursor.execute(insert_sql, values)
            conn.commit()
            print("Record inserted successfully!")
            
            more_entries = input("Do you want to add another entry? (y/n): ")
    
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    
    finally:
        conn.close()

def remove():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get table name
    while True:
        table_name = input("Enter table name: ")
        if table_exists(table_name):
            print("Table exists.")
            break
        else:
            print("Table does not exist.")
    
    # Get search term
    search_term = input("Enter search term to remove: ")
    
    try:
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Build WHERE clause to search in all columns
        where_conditions = ' OR '.join([f"{col} LIKE ?" for col in column_names])
        delete_sql = f"DELETE FROM {table_name} WHERE {where_conditions}"
        
        # Execute with search term for each column
        params = [f'%{search_term}%' for _ in column_names]
        cursor.execute(delete_sql, params)
        
        rows_affected = cursor.rowcount
        conn.commit()
        print(f"Removed {rows_affected} record(s) containing '{search_term}'")
    
    except sqlite3.Error as e:
        print(f"Error removing data: {e}")
    
    finally:
        conn.close()

def print_table():
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get table name
    while True:
        table_name = input("Enter table name: ")
        if table_exists(table_name):
            print("Table exists.")
            break
        else:
            print("Table does not exist.")
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        if not rows:
            print("Table is empty.")
            conn.close()
            return
        
        # Calculate max widths
        max_widths = [len(col) for col in columns]
        for row in rows:
            for i, value in enumerate(row):
                max_widths[i] = max(max_widths[i], len(str(value)))
        
        # Print header
        print("\n" + "-" * (sum(max_widths) + len(columns) * 3))
        for i, col in enumerate(columns):
            print(str(col).ljust(max_widths[i] + 2), end='')
        print("\n" + "-" * (sum(max_widths) + len(columns) * 3))
        
        # Print rows
        for row in rows:
            for i, value in enumerate(row):
                print(str(value).ljust(max_widths[i] + 2), end='')
            print()
        print("-" * (sum(max_widths) + len(columns) * 3))
    
    except sqlite3.Error as e:
        print(f"Error reading table: {e}")
    
    finally:
        conn.close()

def addBook():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    
    try:
        more_entries = "y"
        while more_entries.lower() == "y":
            callNo = input("Enter books call number:")
            author = input("enter author name:")
            title = input("Enter title:")

            insert_sql = "INSERT INTO books (callNo, author, title) VALUES (?,?,?)"
            cursor.execute(insert_sql, (callNo, author, title))
            
            conn.commit()
            print("book added.")
            
            more_entries = input("Do you want to add another entry? (y/n): ")
    
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    
    conn.close()
    
def addUser():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    try:
        more_entries = "y"
        while more_entries.lower() == "y":
            ssn = input("enter users ssn:")
            name = input("enter users name:")

            insert_sql = "INSERT INTO people (ssn, name) VALUES (?,?)"
            cursor.execute(insert_sql, (ssn, name))
            
            conn.commit()
            print("User added.")
            
            more_entries = input("Do you want to add another entry? (y/n): ")
    
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    
    conn.close()

def bookLog():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM checkedOutBooks ORDER BY ssn")
    rows = cursor.fetchall()
    callNo = []
    ssn = []
    for row in rows:
        callNo.append(row[0])
        ssn.append(row[1])

    #get titles
    placeholderscallNo = ', '.join(['?' for _ in callNo])
    query = f"SELECT callNo, author, title FROM books WHERE callNo IN ({placeholderscallNo})"
    cursor.execute(query, callNo)
    titles = cursor.fetchall()
    title_dict = {callNo: (author, title) for callNo, author, title in titles}
    placeholdersSSN = ', '.join(['?' for _ in ssn])
    query = f"SELECT ssn, name FROM people WHERE ssn IN ({placeholdersSSN})"
    cursor.execute(query, ssn)
    names = cursor.fetchall()
    name_dict = {ssn: name for ssn, name in names}

    print("Name\tAuthor\tTitle")

    current_ssn = None
    for callNo, ssn in rows:
        if current_ssn != ssn:
            current_ssn = ssn
            name = name_dict.get(ssn, "Unknown")
        else:
            name = ""  # Empty for subsequent books by same user
        
        if callNo in title_dict:
            author, title = title_dict[callNo]
            print(f"{name}\t{author}\t{title}")

    conn.close()

def checkOut():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    ssn = input("Enter user's SSN:")
    callNo = input("Enter book's call number:")

    try:
        insert_sql = "INSERT INTO checkedOutBooks (callNo, ssn) VALUES (?,?)"
        cursor.execute(insert_sql, (callNo, ssn))
        conn.commit()
        print("Book checked out successfully.")
    except sqlite3.Error as e:
        print(f"Error checking out book: {e}")
    
    conn.close()

def returnBook():
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    while True:
        ssn = input("Enter user's SSN:")
        cursor.execute("SELECT * FROM people WHERE ssn=?", (ssn,))
        result = cursor.fetchone()
        if not result:
            print("This ssn does not exist. try again.")
        else: break

    while True:
        callNo = input("Enter book's call number:")
        select_sql = "SELECT * FROM checkedOutBooks WHERE callNo=? AND ssn=?"
        cursor.execute(select_sql, (callNo, ssn))
        result = cursor.fetchone()
        if not result:
            print("This user does not have this book checked out.")
        else:break

    try:
        delete_sql = "DELETE FROM checkedOutBooks WHERE callNo=? AND ssn=?"
        cursor.execute(delete_sql, (callNo, ssn))
        conn.commit()
        print("Book returned successfully.")
    except sqlite3.Error as e:
        print(f"Error returning book: {e}")
    conn.close()

def main():  
    print(f"Using SQLite database: {os.path.abspath(DB_PATH)}")
    
    while True:
        print("\nSelect an option:")
        print("A. Create Table")
        print("B. Insert")
        print("C. Remove")
        print("D. Print Table")
        print("1. Include a new book in the collection")
        print("2. Include a new user")
        print("3. List library users with books they have checked out")
        print("4. Check out a book")
        print("5. Return a book")
        print("6. Exit")
        
        user_input = input()
        try:
            choice = int(user_input)
        except ValueError:
             choice = user_input.upper()

        if choice == 'A':
            create_table()
        elif choice == 'B':
            insert()
        elif choice == 'C':
            remove()
        elif choice == 'D':
            print_table()
        elif choice == 1:
            addBook()
        elif choice == 2:
            addUser()
        elif choice == 3:
            bookLog()
        elif choice == 4:
            checkOut()
        elif choice == 5:
            returnBook()
        elif choice == 6:
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()