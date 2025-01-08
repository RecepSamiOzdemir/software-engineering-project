import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from dateutil import parser
import subprocess
import threading
import csv
from scrape_all_leagues import scrape_league
import os
from scrape_all_TFF import scrape_TFF

# Authenticate user
def authenticate_user(username, password):
    conn = sqlite3.connect("merged.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    if authenticate_user(username, password):
        root.destroy()  # Close login screen
        open_query_screen()  # Open query screen
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

def load_scraped_data_to_ui(csv_file):
    try:
        # Clear previous data in the treeview
        for i in tree.get_children():
            tree.delete(i)

        # Check for the correct path
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} does not exist.")  # Debug
            raise FileNotFoundError(f"CSV file {csv_file} not found.")

        # Read data from the CSV file
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None)  # Skip the header if present
            data_loaded = False  # Flag to check if any data is loaded
            for row in reader:
                if len(row) == len(tree["columns"]):  # Ensure the row has the right number of columns
                    tree.insert("", "end", values=row)
                    data_loaded = True
                else:
                    print(f"Skipping invalid row: {row}")  # Debug output for invalid rows

            if not data_loaded:
                tree.insert("", "end", values=["No data available"] * len(tree["columns"]))

    except FileNotFoundError:
        messagebox.showerror("File Error", "Scraped data file not found!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading the data: {e}")

def get_years_from_file(file_path):
    years = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:  # Ignore empty lines
                    print(f"Processing line: {line}")  # Debug output to track the line being processed
                    try:
                        # Extract the "YYYY-YY" part from the URL
                        year_part = line.split("/")[-1]  # Extract the "YYYY-YY" part
                        first_year = int(year_part.split("-")[0])  # Get the first year (YYYY)
                        second_year = int(year_part.split("-")[1])  # Get the second year (YY)
                        full_second_year = 2000 + second_year  # Convert YY to full year (20YY)

                        # Add both years to the list
                        years.append(first_year)
                        years.append(full_second_year)
                    except ValueError:
                        print(f"Skipping invalid line: {line}")  # Debug invalid lines
                        continue  # Skip lines that don't have the correct format
    except FileNotFoundError:
        messagebox.showerror("File Error", f"File {file_path} not found!")
    return sorted(set(years))  # Return unique years sorted

# Adjust the query_data function to use the years from the file
def query_data():
    global url_file
    selected_league = league_var.get()
    team_name = team_entry.get().strip()
    initial_year = initial_year_var.get().strip()
    end_year = end_year_var.get().strip()

    if not team_name and not initial_year and not end_year:
        messagebox.showerror("Error", "Please enter a team name or specify a year range!")
        return

    # Validate initial and end years
    try:
        initial_year = int(initial_year) if initial_year else None
        end_year = int(end_year) if end_year else None

        if initial_year and end_year and initial_year > end_year:
            initial_year, end_year = end_year, initial_year  # Swap years if in wrong order
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric years!")
        return

    if selected_league in ["Türkiye 1.Lig", "Türkiye Süper Lig"]:
        url_file = f"../URLS/generated_urls_{selected_league.replace('', '_').upper()}.txt"
    else:
        url_file = f"../URLS/urls_{selected_league.replace(' ', '_').upper()}.txt"
    valid_years = get_years_from_file(url_file)
    if not valid_years:
        messagebox.showerror("Error", "Could not load valid years from the file.")
        return

    # Filter user-provided years by valid years
    if initial_year and initial_year not in valid_years:
        messagebox.showerror("Error", f"Initial year {initial_year} is not in the valid range.")
        return
    if end_year and end_year not in valid_years:
        messagebox.showerror("Error", f"End year {end_year} is not in the valid range.")
        return

    conn = sqlite3.connect("merged.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Football")
        results = cursor.fetchall()

        filtered_results = []
        for row in results:
            league, date_str, home_team, away_team, home_score, away_score = row
            year = extract_year(date_str)

            if year:
                if year not in valid_years:
                    continue  # Skip if year is not valid
                if selected_league != "Select a League" and selected_league.lower() not in league.lower():
                    continue
                if team_name and team_name.lower() not in (home_team.lower() + away_team.lower()):
                    continue
                if initial_year and end_year:
                    if not (initial_year <= year <= end_year):
                        continue
                elif initial_year and not end_year:
                    if year < initial_year:
                        continue
                elif end_year and not initial_year:
                    if year > end_year:
                        continue

                filtered_results.append(row)

        # Clear previous results
        for i in tree.get_children():
            tree.delete(i)

        # Display filtered results
        if filtered_results:
            for row in filtered_results:
                tree.insert("", "end", values=row)
        else:
            messagebox.showinfo("No Results", "No data found matching the criteria.")

    except sqlite3.Error as e:
        messagebox.showerror("Query Error", f"An error occurred: {e}")
    finally:
        conn.close()

# Define a function to clear all data in the Treeview
def clear_data():
    for item in tree.get_children():
        tree.delete(item)
    # Optionally, insert a placeholder row to indicate the table is empty
    tree.insert("", "end", values=["No data available"] * len(tree["columns"]))


# Query screen
def open_query_screen():
    query_screen = tk.Tk()
    query_screen.title("FOOTBALL MATCHES")

    # League selection dropdown
    tk.Label(query_screen, text="Select a League:").pack(pady=5)
    global league_var
    league_var = tk.StringVar()
    league_var.set("Select a League")

    league_dropdown = ttk.Combobox(query_screen, textvariable=league_var, state="readonly")
    league_dropdown['values'] = [
        "Championship", "League One", "Premier League", "Ligue 1", "Bundesliga",
        "Serie A", "La Liga", "Trendyol 1. Lig", "Trendyol Süper Lig"
    ]
    league_dropdown.pack(pady=5)

    # Team name input field
    tk.Label(query_screen, text="Enter a Team Name (Optional):").pack(pady=5)
    global team_entry
    team_entry = tk.Entry(query_screen)
    team_entry.pack(pady=5)

    # Year selection (initial year)
    tk.Label(query_screen, text="Enter Initial Year:").pack(pady=5)
    global initial_year_var
    initial_year_var = tk.StringVar()
    initial_year_entry = tk.Entry(query_screen, textvariable=initial_year_var, width=12)
    initial_year_entry.pack(pady=5)

    # Year selection (end year)
    tk.Label(query_screen, text="Enter End Year:").pack(pady=5)
    global end_year_var
    end_year_var = tk.StringVar()
    end_year_entry = tk.Entry(query_screen, textvariable=end_year_var, width=12)
    end_year_entry.pack(pady=5)

    # Query button
    query_button = tk.Button(query_screen, text="GET DATA FROM DB", command=query_data)
    query_button.pack(pady=10)

    # Results table
    global tree
    columns = ["League", "Date", "Home_Team", "Away_Team", "Home_Score", "Away_Score"]
    tree = ttk.Treeview(query_screen, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(pady=10, fill="both", expand=True)

    # Set initial placeholder
    tree.insert("", "end", values=["No data available"] * len(columns))

    # Clear data button
    clear_button = tk.Button(query_screen, text="CLEAR", command=clear_data)
    clear_button.pack(pady=10)

    # New screen for real-time scraping
    scrape_button = tk.Button(query_screen, text="START WEB SCRAPING", command=start_scraping)
    scrape_button.pack(pady=5)

    # New screen for real-time scraping TFF
    scrape_button = tk.Button(query_screen, text="SCRAPE TÜRKİYE MATCHES", command=start_scraping_TFF)
    scrape_button.pack(pady=5)

    query_screen.mainloop()

def extract_year(date_str):
    try:
        # Attempt to parse the date using `dateutil.parser`
        date_obj = parser.parse(date_str, fuzzy=True)
        return date_obj.year
    except (ValueError, TypeError):
        return None  # Return None if parsing fails


def start_scraping():
    # Start the scraping in a separate thread to prevent freezing the UI
    scraping_thread = threading.Thread(target=scrape_data)
    scraping_thread.daemon = True  # Ensure the thread doesn't keep running after the program exits
    scraping_thread.start()


def scrape_data_TFF():
    try:
        # Retrieve the year inputs from the user
        initial_year = int(initial_year_var.get())
        end_year = int(end_year_var.get())

        # Get the selected league name from the dropdown
        league_name = league_var.get()  # This gets the name of the selected league

        # Construct the URL file path based on the selected league
        url_file = f"../basic_codes/URLS/urls_{league_name.replace(' ', '_').upper()}.txt"

        # Construct CSV filename
        csv_file = f"{initial_year}_{end_year}_{league_var.get().replace(' ', '_').lower()}.csv"

        # Call the scraping function
        scrape_TFF(url_file, league_name, initial_year, end_year)

        load_scraped_data_to_ui(csv_file)  # Load data from the new CSV file

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Subprocess error: {e}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric years!")
    except FileNotFoundError:
        messagebox.showerror("Error", "Scraped CSV file not found!")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


def start_scraping_TFF():
    # Start the scraping in a separate thread to prevent freezing the UI
    scraping_thread = threading.Thread(target=scrape_data_TFF)
    scraping_thread.daemon = True  # Ensure the thread doesn't keep running after the program exits
    scraping_thread.start()


def scrape_data():
    try:
        # Retrieve the year inputs from the user
        initial_year = int(initial_year_var.get())
        end_year = int(end_year_var.get())

        # Get the selected league name from the dropdown
        league_name = league_var.get()  # This gets the name of the selected league
        print(league_name)

        # Construct the URL file path based on the selected league
        url_file = f"../URLS/urls_{league_name.replace(' ', '_').upper()}.txt"

        # Construct CSV filename
        csv_file = f"{initial_year}_{end_year}_{league_var.get().replace(' ', '_').lower()}.csv"

        # Call the scraping function
        scrape_league(url_file, league_name, initial_year, end_year)

        load_scraped_data_to_ui(csv_file)  # Load data from the new CSV file

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Subprocess error: {e}")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric years!")
    except FileNotFoundError:
        messagebox.showerror("Error", "Scraped CSV file not found!")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


# Login screen
root = tk.Tk()
root.title("Login Screen")
root.geometry("400x300")
root.configure(bg="lightblue")

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12), background="blue")
style.configure("TCombobox", font=("Helvetica", 12))

# Username label and entry
tk.Label(root, text="Username:").pack(pady=5)
username_entry = tk.Entry(root)
username_entry.pack(pady=5)

# Password label and entry
tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

# Login button
login_button = tk.Button(root, text="Login", command=login)
login_button.pack(pady=20)

root.mainloop()