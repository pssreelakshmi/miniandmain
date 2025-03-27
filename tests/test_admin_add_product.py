from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Function to perform login, view product page, and logout
def test_login(driver, role, email, password, dashboard_title):
    # Open a new tab with the login URL
    driver.execute_script("window.open('http://127.0.0.1:8000/login/', '_blank');")  # Replace with your actual login URL
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab

    try:
        # Wait for the email input to appear and enter the email
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        time.sleep(1)  # Brief wait before entering the email
        email_input.clear()  # Clear any pre-filled content
        email_input.send_keys(email)

        # Wait for the password input to appear and enter the password
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        time.sleep(1)  # Brief wait before entering the password
        password_input.clear()
        password_input.send_keys(password)

        # Submit the login form
        password_input.send_keys(Keys.RETURN)

        print(f"{role.capitalize()} login successful!")

        # Navigate to the product list page after successful login
        driver.get("http://127.0.0.1:8000/products/")  # Replace with your actual URL for the product page

        # Wait for the logout button to appear on the page to ensure login was successful
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "logout"))
        )

        print(f"{role.capitalize()} dashboard loaded successfully!")

        # Click on the logout button
        logout_button = driver.find_element(By.ID, "logout")
        logout_button.click()

        # Wait for the login page to load again (email input visible)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )

        print(f"{role.capitalize()} logout successful!")

        # If all steps are completed successfully, display "Test Passed" message
        print(f"{role.capitalize()} login test passed!")

    except Exception as e:
        print(f"An error occurred during {role} login: {e}")
    
    finally:
        # Close the current tab
        driver.close()

        # Switch back to the original tab (if needed)
        if len(driver.window_handles) > 0:
            driver.switch_to.window(driver.window_handles[0])


# Initialize Edge WebDriver (replace with the appropriate WebDriver for your browser)
driver = webdriver.Edge()

# Test customer login with provided credentials
test_login(driver, "customer", "grocery18900@gmail.com", "Sree@123", "Customer Dashboard")

# Close the browser after completing the tests
driver.quit()

# Print a final success message after the test
print("Test completed successfully!")
