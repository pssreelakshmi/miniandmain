from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Function to simulate slow typing
def slow_typing(element, text, delay=0.2):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

# Function to login and edit delivery boy's address
def edit_deliveryboy_address(driver, email, password, new_address):
    # Open the login page
    driver.get("http://127.0.0.1:8000/login/")  # Replace with your actual login URL

    try:
        # Wait for the email input to be visible and enter the email
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        slow_typing(email_input, email)  # Slow typing for email

        # Wait for the password input to be visible and enter the password
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        slow_typing(password_input, password)  # Slow typing for password

        # Submit the login form
        password_input.send_keys(Keys.RETURN)

        print("Login successful!")

        # Navigate to the delivery boy profile edit page
        driver.get("http://127.0.0.1:8000/deliveryboy/profile/edit/")  # Replace with the actual profile edit URL

        # Wait for the address input to be visible
        address_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "address"))  # Adjust based on your HTML structure
        )

        # Clear the existing address and enter the new address
        address_input.clear()  # Clear the input field
        slow_typing(address_input, new_address)  # Slow typing for the new address
        print(f"New address '{new_address}' entered.")

        # Submit the form to update the address
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")  # XPath for the submit button
        submit_button.click()

        # Wait for a success message or confirmation (assuming a success message will appear)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))  # Adjust based on success message class
        )
        print("Address updated successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser when done

# Initialize the WebDriver (Edge in this case, you can switch to Chrome or Firefox)
driver = webdriver.Edge()

# Run the function for login and edit address
edit_deliveryboy_address(driver, "psreelakshmi1891@gmail.com", "Sree@123", "panakkal")  # Replace with actual credentials
