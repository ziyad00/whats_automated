from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Path to your WebDriver executable
driver_path = '/Users/ziyad/Downloads/chromedriver-mac-arm64/chromedriver'
remote_debugging_port = 9222

# Initialize the WebDriver (this example uses Chrome)
service = Service(executable_path=driver_path)
options = webdriver.ChromeOptions()
options.add_experimental_option(
    "debuggerAddress", f"localhost:{remote_debugging_port}")

driver = webdriver.Chrome(service=service, options=options)

# Open WhatsApp Web
driver.get("https://web.whatsapp.com")

# Wait for the user to scan the QR code, giving enough time for manual scan
time.sleep(5)  # Adjust this based on how quickly you can scan the QR code

# Assuming the user has scanned the QR code, you might proceed as follows for educational purposes:

try:
    # Wait for the search box to become clickable
    search_box = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='_3sHED']"))
    )
    time.sleep(2)  # Brief pause to ensure the search box is ready

    # Click on the search box and type the name of the contact
    search_box.click()
    # Replace 'Contact Name' with the actual name
    search_box.send_keys('انا')
    time.sleep(2)  # Wait for search results to appear

    # Wait for the contact to appear and click on it
    contact = WebDriverWait(driver, 30).until(
        # Replace 'Contact Name' with the actual name
        EC.element_to_be_clickable((By.XPATH, '//span[@title="Contact Name"]'))
    )
    contact.click()
    time.sleep(2)  # Wait for the chat to open

    # Locate the message box and type a message
    # message_box = driver.find_element(By.XPATH, '//div[@title="Type a message"]')
    # message_box.send_keys('Hello, this is a test message!')

    # Sending messages is not demonstrated here to comply with ethical guidelines and WhatsApp's terms.

    print("Contact selected. Remember to close the browser manually.")
finally:
    # Reminder to close the WebDriver session with driver.quit() when done, to close the browser window.
    # driver.quit()
    pass
