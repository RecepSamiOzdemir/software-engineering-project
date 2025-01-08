from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time

def filter_urls_by_year(urls, initial_year, end_year):
    filtered_urls = []
    for url in urls:
        url = url.strip()  # Clean up the URL

        # Extract the year part from the URL
        year_part = url.split("/")[-1]  # Adjust this based on your URL structure
        try:
            first_year, second_year = map(int, year_part.split("-"))
            full_second_year = 2000 + second_year
            if initial_year <= first_year < end_year or initial_year <= full_second_year < end_year:
                filtered_urls.append(url)
        except ValueError:
            print(f"Skipping URL with invalid year format: {url}")

    print(f"Filtered URLs: {filtered_urls}")
    return filtered_urls

def scrape_league(url_file, league_name, initial_year, end_year):
    # Initialize Selenium WebDriver
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment to run in headless mode
    driver = webdriver.Chrome(options=options)

    # Initialize empty lists to store the extracted data
    leagues = []
    dates = []
    home_teams = []
    away_teams = []
    home_scores = []
    away_scores = []

    # Read URLs from the file
    with open(url_file, "r") as file:
        urls = file.readlines()

    # Filter the URLs based on the year range
    filtered_urls = filter_urls_by_year(urls, initial_year, end_year)

    # Loop through each URL and scrape the data
    for url in filtered_urls:
        print(f"Processing URL: {url}")

        try:
            driver.get(url)
            driver.implicitly_wait(5)

            # Click "Show More" button until all matches are loaded
            while True:
                try:
                    show_more_span = driver.find_element(By.XPATH, "//span[@class='plus-more__text' and text()='Show More']")
                    show_more_button = show_more_span.find_element(By.XPATH, "./ancestor::button")
                    driver.execute_script("arguments[0].click();", show_more_button)
                    time.sleep(2)
                except Exception:
                    print("No more 'Show More' button or all data loaded.")
                    break

            # Extract league name
            try:
                league_header = driver.find_element(By.CLASS_NAME, 'swap-text__target')
                league = league_header.text.strip()
            except:
                league = 'Unknown'

            # Get all sections containing headers and matches
            sections = driver.find_elements(By.XPATH, "//div[contains(@class, 'fixres__body')]/..")

            for section in sections:
                date_headers = driver.find_elements(By.XPATH, "//h3[contains(@class, 'fixres__header1')]")
                for i, header in enumerate(date_headers):
                    date = driver.execute_script("return arguments[0].textContent;", header).strip() or "Unknown"

                    # Find all matches under this section
                    match_elements = section.find_elements(By.CLASS_NAME, 'fixres__item')

                    for match in match_elements:
                        # Extract teams
                        try:
                            team_elements = match.find_elements(By.CLASS_NAME, 'swap-text__target')
                            home_team = team_elements[0].text if len(team_elements) > 0 else 'Unknown'
                            away_team = team_elements[1].text if len(team_elements) > 1 else 'Unknown'
                        except:
                            home_team, away_team = 'Unknown', 'Unknown'

                        # Extract scores
                        try:
                            score_elements = match.find_elements(By.CLASS_NAME, 'matches__teamscores-side')
                            home_score = score_elements[0].text if len(score_elements) > 0 else 'N/A'
                            away_score = score_elements[1].text if len(score_elements) > 1 else 'N/A'
                        except:
                            home_score, away_score = 'N/A', 'N/A'

                        # Append the data to the lists
                        leagues.append(league)
                        dates.append(date)
                        home_teams.append(home_team)
                        away_teams.append(away_team)
                        home_scores.append(home_score)
                        away_scores.append(away_score)

        except Exception as e:
            print(f"Error loading URL {url}: {e}")

    driver.quit()  # Ensure WebDriver quits after processing

    # Save results to CSV
    data = {
        "League": leagues,
        "Date": dates,
        "Home Team": home_teams,
        "Away Team": away_teams,
        "Home Score": home_scores,
        "Away Score": away_scores,
    }
    df = pd.DataFrame(data)
    output_file = f"{initial_year}_{end_year}_{league_name.replace(' ', '_')}.csv"
    df.to_csv(output_file, index=False)
    print(f"Data scraping complete. Results saved to {output_file}")

# Usage example:
# scrape_league("../basic_codes/URLS/urls_LA_LIGA.txt", "La Liga", 2024, 2025)
