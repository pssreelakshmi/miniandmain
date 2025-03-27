from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select  # For dropdowns
from selenium.webdriver.common.keys import Keys
import time

# Function to login and add a subcategory
def add_subcategory(driver, email, password, subcategory_name, category_name, product_category_name):
    # Step 1: Login
    driver.get("http://127.0.0.1:8000/login/")  # Replace with your actual login URL

    try:
        # Wait for the email input to be visible and enter the email
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys(email)
        time.sleep(1)  # Introduce delay after typing email

        # Wait for the password input to be visible and enter the password
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(password)
        time.sleep(1)  # Introduce delay after typing password

        # Submit the login form
        password_input.send_keys(Keys.RETURN)
        time.sleep(2)  # Wait a little before proceeding to the next page

        print("Login successful!")

        # Step 2: Navigate to the subcategory form page
        driver.get("http://127.0.0.1:8000/add_subcategory/")  # Replace with the actual form URL

        # Wait for the form elements to load
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "subcategory_name"))
        )

        # Step 3: Fill in the form
        # Enter the subcategory name
        subcategory_input = driver.find_element(By.ID, "subcategory_name")
        subcategory_input.send_keys(subcategory_name)  # Enter subcategory name directly
        time.sleep(1)  # Delay after typing subcategory
        print(f"Subcategory name '{subcategory_name}' entered.")

        # Select the Category as 'Fruits'
        category_dropdown = Select(driver.find_element(By.ID, "category"))
        category_dropdown.select_by_visible_text(category_name)  # Automatically select 'Fruits'
        time.sleep(1)  # Delay after selecting category
        print(f"Category '{category_name}' selected.")

        # Select the Product Category as 'Apple'
        product_category_dropdown = Select(driver.find_element(By.ID, "product_category"))
        product_category_dropdown.select_by_visible_text(product_category_name)  # Automatically select 'Apple'
        time.sleep(1)  # Delay after selecting product category
        print(f"Product Category '{product_category_name}' selected.")

        # Step 4: Submit the form
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")  # XPath for the submit button
        submit_button.click()
        time.sleep(2)  # Delay after submitting the form

        # Wait for a success message or confirmation (assuming a success message will appear)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "alert-success"))  # Adjust based on success message class
        )
        print(f"Subcategory '{subcategory_name}' added successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Close the browser when done

# Initialize the WebDriver (Edge in this case, you can switch to Chrome or Firefox)
driver = webdriver.Edge()

# Run the function for login and add a subcategory
add_subcategory(driver, "admin@gmail.com", "Admin@123", "Kashmir", "Fruits", "apple")  # Replace with actual credentials and category names
