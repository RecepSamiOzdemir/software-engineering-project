from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Uncomment to run in headless mode
driver = webdriver.Chrome(options=options)


def generate_urls(base_url, start_week=1, end_week=34):
    # Generate URLs for weeks 1 to 34
    return [base_url.replace("{i}", str(i)) for i in range(start_week, end_week + 1)]


def get_urls_for_year_range(file_path, start_year, end_year):
    try:
        # Read URLs from the file
        with open(file_path, "r", encoding="utf-8-sig") as file:
            urls = [line.strip() for line in file.readlines() if line.strip()]

        if not urls:
            raise ValueError("The file is empty or no URLs were read.")

        print(f"Total URLs read: {len(urls)}")
        print(f"URLs: {urls}")

        # Calculate indices
        start_index = start_year - 2000
        end_index = end_year - 2000

        print(f"Start index: {start_index}, End index: {end_index}")

        # Select URLs
        if start_year == end_year:
            selected_urls = [urls[start_index]]
        else:
            selected_urls = urls[start_index:end_index]

        if not selected_urls:
            raise ValueError("No URLs selected for the given year range.")

        print(f"Selected URLs: {selected_urls}")
        return selected_urls

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None


def scrape_TFF(file_path, league_name, start_year, end_year):
    try:
        # Get URLs for the specified year range
        filtered_urls = get_urls_for_year_range(file_path, start_year, end_year)

        all_matches = []

        # Loop through each base URL
        for base_url in filtered_urls:
            print(f"Processing base URL: {base_url}")
            # Generate URLs dynamically for each base URL
            urls = generate_urls(base_url)
            for url in urls:
                print(f"Processing URL: {url}")
                driver.get(url)  # Open the URL in the browser
                time.sleep(5)  # Wait for the page to load

                try:
                    # Scrape the page
                    league_element = driver.find_element(By.XPATH,
                                                         "/html/body/form/div[4]/div/section[2]/article[2]/div[1]/b/i/a")
                    league_name = league_element.text.strip()

                    home_teams = driver.find_elements(By.XPATH, "//td[@class='haftaninMaclariEv']/a/span")
                    dates = driver.find_elements(By.XPATH, "//td[@class='haftaninMaclariTarih']")
                    scores = driver.find_elements(By.XPATH, "//td[@class='haftaninMaclariSkor']")
                    away_teams = driver.find_elements(By.XPATH, "//td[@class='haftaninMaclariDeplasman']/a/span")

                    home_team_names = [team.text.strip() for team in home_teams]
                    match_dates = [date.text.strip() for date in dates]
                    score_results = [score.text.strip() for score in scores]
                    away_team_names = [team.text.strip() for team in away_teams]

                    # Collect match data
                    for home_team, match_date, score, away_team in zip(home_team_names, match_dates, score_results,
                                                                       away_team_names):
                        try:
                            home_score, away_score = map(int, score.split('-'))
                            all_matches.append({
                                "League": league_name,
                                "Date": match_date,
                                "Home Team": home_team,
                                "Away Team": away_team,
                                "Home Score": home_score,
                                "Away Score": away_score,
                            })
                        except ValueError:
                            print(f"Skipping invalid score: {score}")

                except Exception as e:
                    print(f"Error scraping data from {url}: {e}")

        # Save all matches to CSV
        df = pd.DataFrame(all_matches)
        output_file = f"{start_year}_{end_year}_{league_name.replace(' ', '_')}.csv"
        df.to_csv(output_file, index=False)
        print(f"Data scraping complete. Results saved to {output_file}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


# Call the function with appropriate arguments
# Example usage
#scrape_TFF("../basic_codes/URLS/urls_TRENDYOL_SÜPER_LIG.txt", "Trendyol Süper Lig", 2002,2003)