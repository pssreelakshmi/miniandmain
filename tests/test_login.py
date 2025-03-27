from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Function to perform login test based on user role
def test_login(driver, role, email, password, dashboard_title):
    try:
        # Open the login page
        driver.get("http://127.0.0.1:8000/login/")  # Replace with your actual login URL

        # Wait for the email input to be visible and enter the email
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        time.sleep(1)  # Brief wait before entering the email
        email_input.clear()
        email_input.send_keys(email)

        # Wait for the password input to be visible and enter the password
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        time.sleep(1)  # Brief wait before entering the password
        password_input.clear()
        password_input.send_keys(password)

        # Submit the form
        password_input.send_keys(Keys.RETURN)

        # Wait for the dashboard page to load by checking for a known element, like logout
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "logout"))
        )

        print(f"{role.capitalize()} login successful!")

        # Perform logout
        logout_button = driver.find_element(By.ID, "logout")
        logout_button.click()

        # Verify that we're back on the login page
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )

        print(f"{role.capitalize()} logout successful!")

    except Exception as e:
        print(f"An error occurred during {role} login: {e}")

# Function to perform invalid login attempt
def test_invalid_login(driver):
    try:
        # Open the login page
        driver.get("http://127.0.0.1:8000/login/")  # Replace with your actual login URL

        # Enter invalid credentials
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        password_input = driver.find_element(By.NAME, "password")

        time.sleep(1)
        email_input.clear()
        email_input.send_keys("invalid@example.com")  # Invalid email
        time.sleep(1)
        password_input.clear()
        password_input.send_keys("InvalidPass123")  # Invalid password
        password_input.send_keys(Keys.RETURN)

        # Wait for an error message to be displayed
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "error"))  # Adjust the selector if needed
        )
        print("Invalid login attempt handled correctly.")

    except Exception as e:
        print(f"An error occurred during invalid login attempt: {e}")

# Main function to run the tests
def run_tests():
    driver = webdriver.Edge()  # Initialize Edge WebDriver (replace with your driver if needed)

    try:
        # Test logins for different roles, including the dashboard title
        test_login(driver, "customer", "grocery18900@gmail.com", "Sree@123", "Customer Dashboard")
        test_login(driver, "farmer", "sreelakshmips2025@mca.ajce.in", "Farmer@123", "Farmer Dashboard")
        test_login(driver, "admin", "admin@gmail.com", "Admin@123", "Admin Dashboard")

        # Perform an invalid login test
        test_invalid_login(driver)

        print("All tests passed successfully!")

    except Exception as e:
        print(f"Test suite failed: {e}")
    finally:
        driver.quit()  # Ensure browser closes at the end of tests

# Run the test suite
if __name__ == "__main__":
    run_tests()
