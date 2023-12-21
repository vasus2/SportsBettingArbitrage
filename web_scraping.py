from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def get_odds(link):

    driver.get(link)


    driver.maximize_window()


    data = driver.find_element("xpath", 
                                "/html/body/div[5]/div[3]/div[1]/div[1]")

    text_data = data.text

    # Split the text into lines
    lines = text_data.strip().split('\n')

    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    # Create an empty DataFrame with the desired column names
    df = pd.DataFrame(columns=["Date", "Time", "Game", "Moneyline", "Spread", "Total"])
    #df = pd.DataFrame(columns=["Date", "Time", "Game", "Moneyline", "Arb Opp"])
    arb_opp_df =  pd.DataFrame(columns=["Date", "Time", "Game", "Moneyline", "Arb Opp"])

    # Create a list to store the new rows
    new_rows = []
    arb_rows = []

    # Iterate over the data list, adding each item to the DataFrame
    for i in range(len(lines)):
        if lines[i] == 'MONEYLINE':
            date = lines[i-1]
            game = lines[i+4] + " " + lines[i+5]
            moneyline = lines[i+6] + " : " + lines[i+7]
            spread = lines[i+8:i+12]
            total = lines[i+12:i+16]
            time = lines[i+3]
            if int(lines[i+6]) + int(lines[i+7]) > 0:
                arb_opp = "yes"
                arb_rows.append({"Date": date, "Time": time, "Game": game, "Moneyline": moneyline, "Arb Opp": arb_opp})
            else: 
                arb_opp = "no"
                new_rows.append({"Date": date, "Time": time, "Game": game, "Moneyline": moneyline, "Spread": spread, "Total": total})


    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    arb_opp_df = pd.concat([arb_opp_df, pd.DataFrame(arb_rows)], ignore_index=True)
    # Print the DataFrame
    print(df)
    print(arb_opp_df)
    driver.quit()


get_odds("https://www.oddschecker.com/us/football/college-football")






