import os
import sqlite3
from sqlite3 import Error
import time
import tkinter
from tkinter import ttk, filedialog, messagebox
import pandas as pd
# Global variables
sqlite_connection = None
database_loaded = False

def on_combobox_select(event):
    """This function is triggered when the user selects an item from the combobox."""
    table_name=table_Name_combobox.get()
    cursor = sqlite_connection.cursor()
    cursor.execute(f"SELECT * FROM [{table_name}]")
    column_names = [description[0] for description in cursor.description]
    sql_where_combobox.configure(values=column_names) # add table names to combobox.
    sql_where_combobox.set("None")
    operator_combobox.set("Select Operator")
    entry_where_cond.delete(0, 'end')
# Load a database
def load_database():
    global sqlite_connection, database_loaded
    sql_where_combobox.set("None")
    operator_combobox.set("Select Operator")
    if not database_loaded:
        filename = filedialog.askopenfilename(filetypes=[("SQLite DB files", "*.db"), ("All files", "*.*")])
        if filename:
            try:
                sqlite_connection = sqlite3.connect(filename)
                cursor = sqlite_connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                query = "SELECT name FROM sqlite_master WHERE type='table';"
                loaded_data = pd.read_sql_query(query, sqlite_connection)
                table_names = loaded_data['name']
                table_list=loaded_data['name'].tolist()
                table_Name_combobox.configure(values=table_list) # add table names to combobox.
                messagebox.showinfo("Success", "Connection to Database established successfully")
                database_loaded = True
            except Error as e:
                messagebox.showerror("Error", f"Failed to connect to database. {e}")
                return None
        else:
            messagebox.showwarning("Warning", "No file selected.")
    else:
        if messagebox.askyesno("Load New Database", "Are you sure you want to load a new database?"):
            database_loaded = False
            if sqlite_connection:
                sqlite_connection.close()
            load_database()
    return sqlite_connection
# Display data from a selected table in the Treeview
def display_data_in_treeview():
    global sqlite_connection
    # Check if the database is loaded
    if not database_loaded:
        messagebox.showerror("Error", "Please load a database first.")
        return
    try:
        # Fetch data from the  tables
        table_name=table_Name_combobox.get()
        where_combo=sql_where_combobox.get()
        condition_text=entry_where_cond.get()
        operator=operator_combobox.get()
        cursor = sqlite_connection.cursor()
        if where_combo!="None" or where_combo =="":
            sql_query = f"SELECT * FROM [{table_name}] WHERE [{where_combo}] {operator} ?"
            print("Executing SQL Query:", sql_query)
            cursor.execute(sql_query, (condition_text,))
        else:
            cursor.execute(f"SELECT * FROM [{table_name}]")
        rows = cursor.fetchall()
        cursor.execute(f"SELECT * FROM [{table_name}]")
        column_names = [description[0] for description in cursor.description]
        sql_where_combobox.configure(values=column_names) # add table names to combobox.
        tree.configure(columns=column_names)
        for col in column_names:
            tree.heading(col, text=col)  # Set the heading (title) of the column
            tree.column(col, width=40, anchor='center')  # Set width and alignment
        # Clear the Treeview
        for item in tree.get_children():
            tree.delete(item)
        # Insert data into the Treeview
        for row in rows:
            tree.insert("", tkinter.END, values=row)
        messagebox.showinfo("Success", "Data displayed successfully.")
    except Error as e:
        messagebox.showerror("Error", f"Failed to fetch data from the database. {e}")
    sql_where_combobox.set("None")
    operator_combobox.set("Select Operator")
    entry_where_cond.delete(0, 'end')

# GUI Setup
window = tkinter.Tk()
window.title("Database Connection")
frame = tkinter.Frame(window)
frame.pack(fill="both", expand=True)
style = ttk.Style()
style.configure("TLabelframe.Label", font=("Helvetica", 10, "bold"))
style.configure("TButton", font=("Helvetica", 9, "bold"))

# Main GUI Widgets
label_window = tkinter.Label(frame, text="Python Database Connection with SQL Examples.", font=("Arial", 18))
label_window.grid(row=0, column=0, columnspan=2, pady=10)
loading_frame = ttk.LabelFrame(frame, text="Importing the Data")
loading_frame.grid(row=1, column=0, padx=10, pady=10)
load_button = ttk.Button(loading_frame, text="Load a Database", command=load_database, width=60)
load_button.grid(row=0, column=0,columnspan=2,pady=5)
display_button = ttk.Button(loading_frame, text="Display Data (FROM a Table)", command=display_data_in_treeview, width=60)
display_button.grid(row=2, column=0,columnspan=2, pady=5)
table_Name_label = tkinter.Label(loading_frame, text="Table Name:",font=("Arail",9,"italic bold"), justify="left")
table_Name_label.grid(row=3, column=0, pady=0, padx=0, sticky="e")
table_Name_combobox = ttk.Combobox(loading_frame, width=27,values=["","","", "",""], justify="left")
table_Name_combobox.grid(row=3, column=1, pady=0,padx=0,sticky="w")
table_Name_combobox.set("---")
table_Name_combobox.bind("<<ComboboxSelected>>", on_combobox_select)
sql_where_label = tkinter.Label(loading_frame, text="WHERE:", font=("Arail",9,"italic bold"),justify="left")
sql_where_label.grid(row=4, column=0, pady=0, padx=0, sticky="e")
sql_where_combobox = ttk.Combobox(loading_frame, width=27,values=["","","", "",""], justify="left")
sql_where_combobox.grid(row=4, column=1, pady=0,padx=0,sticky="w")
sql_where_combobox.set("None")
operator_combobox = ttk.Combobox(loading_frame, width=6,values=["=", ">", "<", ">=", "<=", "LIKE"])
operator_combobox.grid(row=6, column=0, pady=0,padx=0,sticky="e")
operator_combobox.set("Select Operator")
entry_where_cond= tkinter.Entry(loading_frame, width=20,font=("Arial", 12))
entry_where_cond.grid(row=6,column=1,pady=0,padx=0,sticky="w")
tree = ttk.Treeview(frame, columns=("", "", "", ""), show="headings")
tree.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
window.mainloop()
