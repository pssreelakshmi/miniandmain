# test_login.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Function to perform login
def login_and_display_dashboard(user_role, username, password):
    # Initialize the WebDriver for Microsoft Edge
    driver = webdriver.Edge()  # Ensure Edge WebDriver is in your PATH

    try:
        # Open the index.html page (update with the correct path to your index.html)
        driver.get("file:///C:/path/to/your/myapp/templates/index.html")  # Update with the correct path

        # Click on the login link/button (update the selector as per your HTML)
        login_button = driver.find_element(By.LINK_TEXT, "Login")  # Adjust the link text as needed
        login_button.click()

        # Wait for the login page to load
        time.sleep(2)

        # Fill in the login form
        username_input = driver.find_element(By.NAME, "email")  # Adjust the selector as needed
        password_input = driver.find_element(By.NAME, "password")  # Adjust the selector as needed

        username_input.send_keys(username)
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)

        # Wait for the dashboard to load
        time.sleep(3)

        # Check if the dashboard is displayed (update the selector as per your HTML)
        if user_role == "farmer":
            assert "Farmer Dashboard" in driver.title  # Adjust as needed
        elif user_role == "customer":
            assert "Customer Dashboard" in driver.title  # Adjust as needed
        elif user_role == "admin":
            assert "Admin Dashboard" in driver.title  # Adjust as needed
        elif user_role == "deliveryboy":
            assert "Delivery Boy Dashboard" in driver.title  # Adjust as needed

        print(f"{user_role.capitalize()} logged in successfully and dashboard displayed.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the browser
        driver.quit()

# User credentials (replace with actual credentials)
users = {
    "farmer": ("farmer_email", "farmer_password"),
    "customer": ("customer_email", "customer_password"),
    "admin": ("admin_email", "admin_password"),
    "deliveryboy": ("deliveryboy_email", "deliveryboy_password"),
}

# Perform login for each user role
for role, (email, password) in users.items():
    login_and_display_dashboard(role, email, password)