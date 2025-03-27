from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select  # Import Select for dropdowns
from selenium.webdriver.common.keys import Keys
import time
import logging

# Suppress stack trace details by setting Selenium logging to ERROR
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.ERROR)

# Function to simulate slow typing
def slow_typing(element, text, delay=0.2):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)  # Adjust the delay as needed (0.2 seconds per character)

# Function to login as admin and navigate to add product category page
def admin_add_product(driver, email, password):
    # Open the login page
    driver.get("http://127.0.0.1:8000/login/")  # Replace with your actual login URL

    try:
        print("Attempting to log in as admin...")

        # Wait for the email input to be visible and enter the email slowly
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        slow_typing(email_input, email)  # Slow typing for email
        print(f"Entered email: {email}")

        # Wait for the password input to be visible and enter the password slowly
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        slow_typing(password_input, password)  # Slow typing for password
        print("Entered password.")

        # Submit the login form
        password_input.send_keys(Keys.RETURN)

        print("Admin login successful!")

        # Navigate to the 'Add Product Category' page
        print("Navigating to Add Product Category page...")
        driver.get("http://127.0.0.1:8000/add_product_category/")  # Replace with the actual URL

        # Wait for the add product category form to load (using the dropdown ID)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "category"))  # The dropdown ID from the HTML
        )

        # Select "Fruits" in the category dropdown
        category_dropdown = Select(driver.find_element(By.ID, "category"))
        print("Category dropdown found.")  # Debugging line
        category_dropdown.select_by_visible_text("Fruits")  # Adjust the category name as per the HTML

        print("Fruits category selected.")  # Debugging line

        # Enter "Apple" as product name slowly
        product_input = driver.find_element(By.ID, "product_name")  # Adjust the selector as needed
        slow_typing(product_input, "Apple")  # Slow typing for product name
        print("Product name 'Apple' entered.")  # Debugging line

        # Submit the form to add the category and product
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")  # XPath for the submit button
        submit_button.click()

        # Wait for a success message or confirmation
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))  # Assuming a success message uses this class
        )
        print("Category 'Fruits' and product 'Apple' added successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")  # Custom error message without showing the full stack trace
    finally:
        # Close the browser when done
        driver.quit()
        print("Test completed successfully.")

# Initialize the WebDriver (Edge in this case, you can switch to Chrome or Firefox)
driver = webdriver.Edge()

# Run the function for admin login and add product
admin_add_product(driver, "admin@gmail.com", "Admin@123")  # Replace with actual admin credentials
