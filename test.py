import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_dynamic_html(url):
    options = Options()
    options.add_argument('--headless')  # Run Chrome in headless mode
    service = Service('/usr/local/bin/chromedriver')  # Path to ChromeDriver
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    
    # Wait for the specific element to be present

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#framework7-root > div.sheet-modal.sheet-modal-bottom.main-overlay.modal-in > div > div > div > div > div > div.sheet-modal-swipe-step > div.block.inset.block-strong.box.minheight > div.outlet-list.accordion-list.accordion-opposite")))

    except Exception as e:
        print(f"Error: {e}")
    time.sleep(5)  # Wait for the content to load
    html = driver.page_source
    driver.quit()
    return html

def parse_charger_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    chargers = []
    
    container = soup.select_one("#framework7-root > div.sheet-modal.sheet-modal-bottom.main-overlay.modal-in > div > div > div > div > div > div.sheet-modal-swipe-step > div.block.inset.block-strong.box.minheight > div.outlet-list.accordion-list.accordion-opposite")
    if container:
        for item in container.select('.accordion-item'):
            capacity = item.select_one('.col-50.outlet-spec')
            availability = item.select_one('.col-35.outlet-count span')
            
            if capacity and availability:
                chargers.append({
                    'Capacity': capacity.get_text(strip=True),
                    'Availability': availability.get_text(strip=True)
                })
    
    return chargers

def save_to_csv(data, filename='chargers_data.csv'):
    # Write the parsed charger data to a CSV file
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Capacity', 'Availability'])
        
        # Write header only if the file is empty
        if file.tell() == 0:
            writer.writeheader()
        
        # Write the data to the CSV
        writer.writerows(data)

# List of URLs to parse
urls = [
    "https://chargefinder.com/us/charging-station-columbus-snappy-s-market-columbus-tx/969de5",
    "https://chargefinder.com/us/charging-station-columbus-columbus-tx-supercharger/x8gm5"
]

# Process each URL and save the data to CSV
for url in urls:
    print(f"\nParsing data from: {url}")
    html = get_dynamic_html(url)
    chargers = parse_charger_data(html)

    # Save the results to a CSV file
    save_to_csv(chargers)

    # Optionally print the data to the console
    print("| Capacity | Availability |")
    print("|----------|-------------|")
    for charger in chargers:
        print(f"| {charger['Capacity']} | {charger['Availability']} |")
