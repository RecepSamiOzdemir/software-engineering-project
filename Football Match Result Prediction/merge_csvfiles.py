import csv
import os

# List of CSV file names to merge
file_names = [
    '../ENGLAND/2000_24_EN_ChampionshipLeague.csv',
    '../ENGLAND/2000_24_EN_LeagueOne.csv',
    '../ENGLAND/2000_24_EN_PremierLeague.csv',
    '../FRANCE/2000_24_FR_Ligue1.csv',
    '../GERMAN/2000_24_GER_Bundesliga.csv',
    '../ITALY/2000_24_IT_serieA.csv',
    '../SPAIN/2000_24_SP_laliga.csv',
    '../TURKEY/2000_22_TR_birincilig.csv',
    '../TURKEY/2000_24_TR_superlig.csv'
]

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Output file name
output_file = os.path.join(script_dir, 'merged_data.csv')

# Function to merge CSV files
def merge_csv_files(file_list, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
        writer = csv.writer(outfile)
        is_first_file = True  # Flag to write header only once

        for file in file_list:
            # Resolve full path
            full_path = os.path.abspath(os.path.join(script_dir, file))
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8-sig') as infile:
                        reader = csv.reader(infile)
                        # Write header for the first file only
                        if is_first_file:
                            writer.writerow(next(reader))  # Write header row
                            is_first_file = False
                        else:
                            next(reader, None)  # Skip header for subsequent files

                        # Write remaining rows
                        writer.writerows(reader)
                        print(f"Successfully merged: {full_path}")
                except UnicodeDecodeError:
                    print(f"Error decoding file: {full_path}. Check the file encoding.")
            else:
                print(f"File not found: {full_path}")

# Call the function
merge_csv_files(file_names, output_file)
print(f"Merged CSV saved to: {output_file}")
