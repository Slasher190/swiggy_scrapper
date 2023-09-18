from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import csv

# Initialize the WebDriver


def initialize_driver():
    driver = webdriver.Chrome()  # You can change this to your preferred browser
    return driver

# Function to scrape restaurant data and append to CSV


def scrape_restaurant_data(driver):
    cnt = 0
    last_processed_link = None
    start = 0
    stop = 10
    while True:
        try:
            # Find and click the "Show more" button
            restaurant_cards = driver.find_elements(
                By.CSS_SELECTOR, ".jXGZuP .kcEtBq")[start:stop]

            # Scrape restaurant data
            with open("swiggy_restaurants.csv", "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Restro Link", "Image Link", "Offer",
                              "Name", "Food Type", "Address"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                for card in restaurant_cards:
                    restro_link = card.get_attribute("href")
                    if restro_link == last_processed_link:
                        # Skip this card, as we've already processed it
                        continue
                    image_link = card.find_element(
                        By.CSS_SELECTOR, ".kvGwZG").get_attribute("src")
                    offer = card.find_element(By.CSS_SELECTOR, ".jgEJgd").text
                    name = card.find_element(By.CSS_SELECTOR, ".cwvucc").text
                    food_type = card.find_element(
                        By.CSS_SELECTOR, ".sw-restaurant-card-descriptions-container > div:nth-child(1)").text
                    address = card.find_element(
                        By.CSS_SELECTOR, ".sw-restaurant-card-descriptions-container > div:nth-child(2)").text

                    restaurant_info = {
                        "Restro Link": restro_link,
                        "Image Link": image_link,
                        "Offer": offer,
                        "Name": name,
                        "Food Type": food_type,
                        "Address": address,
                    }
                    writer.writerow(restaurant_info)
                    last_processed_link = restro_link

            # Adjust the sleep time as needed
            show_more_button = driver.find_element(
                By.CSS_SELECTOR, ".brTFTS > .fBowAU")
            show_more_button.click()
            cnt += 1
            start = stop
            stop = start + 15
            time.sleep(2)

        except Exception as e:
            # When the "Show more" button is no longer available, exit the loop
            print("No more 'Show more' button.")
            break

# Function to get detailed restaurant data


def get_restaurant_details(driver, url):
    try:
        driver.get(url)

        avg_rate = driver.find_element(
            By.CSS_SELECTOR, ".RestaurantRatings_avgRating__1TOWY span:nth-child(2)").text
        total_rate = driver.find_element(
            By.CSS_SELECTOR, ".RestaurantRatings_totalRatings__3d6Zc:nth-child(2)").text

        # Scroll to the bottom of the container to load all the cards
        js_script = "window.scrollTo(0, document.body.scrollHeight);"
        driver.execute_script(js_script)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".styles_item__3_NEA")))

        # Find all individual cards within the parent element
        cards = driver.find_elements(
            By.CSS_SELECTOR, ".styles_item__3_NEA")

        # Iterate through each card and extract information
        for card in cards:
            item_name = card.find_element(
                By.CSS_SELECTOR, ".styles_itemNameText__3ZmZZ").text
            item_price = card.find_element(
                By.CSS_SELECTOR, ".styles_itemPrice__1Nrpd").text
            try:
                item_description = card.find_element(
                    By.CSS_SELECTOR, ".styles_itemDesc__3vhM0").text
            except Exception:
                item_description = "No"
            try:
                item_image_src = card.find_element(
                    By.CSS_SELECTOR, ".styles_itemImage__3CsDL img").get_attribute("src")
            except Exception:
                item_image_src = "No"
            try:
                best_seller = card.find_element(
                    By.CSS_SELECTOR, ".styles_itemRibbon__353Fy ").text
            except Exception:
                best_seller = "No"
            with open("swiggy_restaurants_dishes_detail.csv", "a", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["Restro Link", "Item Name", "Item Price",
                              "Item Description", "Item Image Source", "Bestselling"]
                dishes_detail = csv.DictWriter(csvfile, fieldnames=fieldnames)
                dish_detail = {
                    "Restro Link": url,
                    "Item Name": item_name,
                    "Item Price": item_price,
                    "Item Description": item_description,
                    "Item Image Source": item_image_src,
                    "Bestselling": best_seller,
                }
                dishes_detail.writerow(dish_detail)
        address = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".RestaurantFooterAddress_address__37uUA p"))).text
        license = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".RestaurantLicence_licenceText__2XEQc:nth-child(2)"))).text

        with open("swiggy_restaurants_detail.csv", "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Restro Link", "Average Rate", "Total Ratings",
                          "Address", "License Number"]
            restro_details = csv.DictWriter(csvfile, fieldnames=fieldnames)
            restro_detail = {
                "Restro Link": url,
                "Average Rate": avg_rate,
                "Total Ratings": total_rate,
                "Address": address,
                "License Number": license
            }
            restro_details.writerow(restro_detail)
        print(address, license)
        print("-" * 100)
    except Exception as e:
        print("Error processing the link:", e)
    time.sleep(2)

# Main function


def main():
    # Initialize the WebDriver
    driver = initialize_driver()

    # Scrape restaurant data and append to CSV
    scrape_restaurant_data(driver)

    # Read the restaurant URLs from a CSV file
    df = pd.read_csv('swiggy_restro_indore_data.csv')
    restro_url = df['Restro Link']

    # Get detailed restaurant data for each URL
    for url in restro_url:
        get_restaurant_details(driver, url)

    # Close the WebDriver
    driver.quit()


if __name__ == "__main__":
    main()
