from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    try:
        driver.maximize_window()
        driver.get("https://www.selenium.dev/selenium/web/web-form.html")

        text_input = wait.until(EC.presence_of_element_located((By.NAME, "my-text")))
        text_input.send_keys("Hello Selenium")

        textarea = wait.until(EC.presence_of_element_located((By.NAME, "my-textarea")))
        textarea.send_keys("This is my first Selenium demo.")

        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button")))
        submit_button.click()

        message = wait.until(EC.presence_of_element_located((By.ID, "message")))

        print("Page title:", driver.title)
        print("Success message:", message.text)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
