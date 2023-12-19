from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


driver.get("https://www.oddschecker.com/us/football/college-football")


driver.maximize_window()


data = driver.find_element("xpath", 
                            "/html/body/div[5]/div[3]/div[1]/div[1]")

text_data = data.text

# Split the text into lines
lines = text_data.strip().split('\n')

# Remove empty lines
lines = [line for line in lines if line.strip()]

# Create an empty DataFrame with the desired column names
#df = pd.DataFrame(columns=["Date", "Time", "Game", "Moneyline", "Spread", "Total"])
df = pd.DataFrame(columns=["Date", "Time", "Game", "Moneyline"])

# Create a list to store the new rows
new_rows = []

# Iterate over the data list, adding each item to the DataFrame
for i in range(len(lines)):
  if lines[i] == 'MONEYLINE':
    #print(lines[i+1], lines[i+2], lines[i+3], lines[i+4])
    date = lines[i-1]
    game = lines[i+4] + " " + lines[i+5]
    moneyline = lines[i+6] + " : " + lines[i+7]
    #spread = lines[i+8:i+12]
    #total = lines[i+12:i+16]
    time = lines[i+3]
    #new_rows.append({"Date": date, "Time": time, "Game": game, "Moneyline": moneyline, "Spread": spread, "Total": total})
    new_rows.append({"Date": date, "Time": time, "Game": game, "Moneyline": moneyline})
      


df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
# Print the DataFrame
print(df)


# Extract relevant information

'''data = []
current_match = None

for line in lines:
    if line in ["MONEYLINE", "SPREAD", "TOTAL"]:
        continue  # Skip section headers

    if line.endswith("EST"):
        match_date = lines[lines.index(line) - 1]
        match_time = line
        current_match = {"Date": match_date, "Time": match_time}
    elif current_match:
        parts = line.split()
        if len(parts) == 2:
            current_match[parts[0]] = parts[1]
        elif len(parts) == 3:
            current_match[parts[0] + "_Odds"] = parts[1]
            current_match[parts[0]] = parts[2]

        if line.startswith("U "):
            data.append(current_match)
            current_match = None

# Create a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df)
'''


'''
links = driver.find_elements("xpath", "//a[@href]")

for link in links:
    if "Books" in link.get_attribute("innerHTML"):
        link.click()
        break

book_links = driver.find_elements("xpath", 
                                  "//div[contains(@class, 'elementor-column-wrap')][.//h2[text()[contains(.,'7 IN 1')]]][count(.//a)=2]//a")

book_links[0].click()

driver.switch_to.window(driver.window_handles[1])

time.sleep(3)

buttons = driver.find_elements("xpath", "//a[.//span[text()[contains(., 'Paperback')]]]//span[text()[contains(., '$')]]")

for button in buttons:
    print(button.get_attribute("innerHTML"))


driver.quit()

'''


