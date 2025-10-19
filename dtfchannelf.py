from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

output_file = "UpBulk Channels List.txt"

with open(output_file, "w", encoding="utf-8") as file:
    for i in range(1, 30):
        url = f"https://www.dailymotion.com/upbulk{i}"
        try:
            driver.get(url)

            # Wait for body to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Look for the Follow button by data-testid
            follow_button = driver.find_elements(
                By.XPATH,
                "//button[@data-testid='follow-button' and text()='Follow']"
            )

            if follow_button:
                print(f"✅ Channel exists: {url}")
                file.write(url + "\n")
            else:
                print(f"❌ Channel not found: {url}")

        except Exception as e:
            print(f"⚠️ Error checking {url}: {e}")

driver.quit()
print(f"\n✅ Done! Valid channels saved to '{output_file}'")
