# Read base URLs from the provided text file path
def read_base_urls(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines() if line.strip()]


# Generate years in the format YYYY-YY
def generate_years(start_year, num_years):
    years = []
    for year in range(start_year, start_year + num_years):
        next_year = str(year + 1)[-2:]
        years.append(f"{year}-{next_year}")
    return years


# Main execution block
if __name__ == "__main__":
    # Input the path to the text file containing the base URLs
    # base_urls_path = "../basic_codes/URLS/urls_TRENDYOL_SÜPER_LIG.txt"
    base_urls_path = "../basic_codes/URLS/urls_TRENDYOL_1._LIG.txt"

    # Read the base URLs from the file
    base_urls = read_base_urls(base_urls_path)

    # Start year and number of years to generate
    start_year = 2000
    num_years = len(base_urls)  # Ensure we have one year for each URL

    # Generate the years
    years = generate_years(start_year, num_years)

    # Combine URLs with years in the required format
    final_urls = []
    for i, (url, year) in enumerate(zip(base_urls, years), 1):
        # Modify the URL as per your requirement with a slash between #grp and the year
        final_url = f"{url}hafta={i}#grp/{year}"
        final_urls.append(final_url)

    # Save the URLs to a predefined file
    output_file_path = "../basic_codes/URLS/generated_urls_TRENDYOL_1._LIG.txt"
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(final_urls))

    print(f"URLs saved to {output_file_path}.")
