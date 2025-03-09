from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_upload():
    # Initialize Chrome driver
    driver = webdriver.Chrome()
    
    try:
        # Navigate to the dashboard
        driver.get('http://localhost:5000/dashboard')
        
        # Wait for file input to be present
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "csv_file"))
        )
        
        # Get the absolute path to test_import.csv
        import os
        csv_path = os.path.abspath('test_import.csv')
        
        # Send the file path to the file input
        file_input.send_keys(csv_path)
        
        # Wait for upload to complete
        time.sleep(2)
        
        # Print any success or error messages
        messages = driver.find_elements(By.CLASS_NAME, "flash-message")
        for message in messages:
            print(f"Message: {message.text}")
            
    finally:
        # Close the browser
        driver.quit()

if __name__ == '__main__':
    test_upload() 