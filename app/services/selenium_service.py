from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
import random
from app.config import Config

class TwitterTrendsScraper:
    def __init__(self,  manual_verify_timeout=300):
        self.manual_verify_timeout = manual_verify_timeout 
        self.setup_driver()
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        # Enabling headless mode 
        # options.add_argument("--headless=new")  

        options.add_argument("--disable-gpu")  
        options.add_argument("--no-sandbox")  
        options.add_argument("--disable-dev-shm-usage")  
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])


        # SEtting up proxymesh things
        PROXY_USERNAME = Config.PROXY_USERNAME
        PROXY_PASSWORD = Config.PROXY_PASSWORD
        PROXY_HOST = Config.PROXY_HOST
        PROXY_PORT = Config.PROXY_PORT
    
        options.add_argument(f'--proxy-server=http://{PROXY_HOST}:{PROXY_PORT}')
        options.add_argument(f'--proxy-auth={PROXY_USERNAME}:{PROXY_PASSWORD}')
        options.add_argument(f'--proxy-bypass-list=<-loopback>')

        self.driver = webdriver.Chrome(options=options)

    # Simulates human like typing to avoid bot detection
    def human_like_typing(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    # this will help us in waiting for manual code injection by the user (If not headless otherwise we will quit here)   
    def wait_for_manual_verification(self):
        print("\n=== MANUAL VERIFICATION REQUIRED ===")
        print("Please complete the verification in the browser.")
        print(f"You have {self.manual_verify_timeout} seconds to complete it.")
        print("The script will continue automatically once verification is completed.")
        print("===================================\n")
        
        # Store the initial verification URL
        initial_url = self.driver.current_url
        start_time = time.time()
        
        while time.time() - start_time < self.manual_verify_timeout:
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Check if we've been redirected away from the verification page
            if current_url != initial_url and not any([
                "verify" in current_url,
                "verification" in current_url,
                "confirm" in current_url,
                "challenge" in current_url,
                "authenticate" in current_url
            ]):
                print("\nVerification completed successfully! Redirected to:", current_url)
                time.sleep(2)  # Give a moment for any redirects to complete
                return True
                
            # List of indicators that we're still on a verification page
            verification_indicators = [
                "verification" in page_source,
                "verify" in page_source,
                "confirmation" in page_source,
                "confirm your identity" in page_source,
                "enter the code" in page_source,
                "verify your phone" in page_source,
                "verify your email" in page_source
            ]
            
            # If none of the verification indicators are present, assume verification is complete
            if not any(verification_indicators):
                print("\nVerification completed successfully!")
                time.sleep(2)
                return True
                
            # Wait a bit before checking again
            time.sleep(1)
            
        print("\nVerification timeout reached. Please try again.")
        return False
    

    # in case Verification code  is required (THEN WE WILL HAVE TO DO THIS MANUALLY FOR WHICH TIME IS ALLOCATED HERE)
    def check_for_verification(self):
        try:
            verification_elements = self.driver.find_elements(By.XPATH, 
                "//*[contains(text(), 'verification') or contains(text(), 'Verify') or \
                contains(text(), 'confirm') or contains(text(), 'Confirm') or \
                contains(text(), 'Enter the code')]"
            )
            
            if verification_elements:
                # Wait for manual verification to complete
                if self.wait_for_manual_verification():
                    return True
                else:
                    raise Exception("Verification timeout - please try again")
                    
        except NoSuchElementException:
            pass
        return True
    
    # Get the input element 
    def wait_for_element(self, by, value, timeout=10):
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None
    
    # Tells whether current page is home page or not
    def is_home_page(self):
        try:
            home_indicators = [
                'home' in self.driver.current_url.lower(),
                'feed' in self.driver.current_url.lower(),
                self.wait_for_element(By.CSS_SELECTOR, '[data-testid="primaryColumn"]', timeout=5) is not None
            ]
            return any(home_indicators)
        except Exception:
            return False
        
    # Function responsible for telling which page are we at.
    def check_for_input_type(self):
        page_source = self.driver.page_source
        
        if 'Enter your password' in page_source:
            return 'password'
        elif 'Enter your phone number or email address' in page_source:
            return 'email_or_phone'
        elif 'Enter your phone number or username' in page_source:
            return 'phone_or_username'
        elif 'Sign in to X' in page_source:
            return 'username'
        elif any(text in page_source.lower() for text in ['verification code', 'confirm your identity']):
            return 'verification'
        return None
    
    # Handling inputing the value in the input field
    def handle_input_step(self, input_type, value):
        input_selectors = {
            'password': 'input[name="password"]',
            'email_or_phone': 'input[data-testid="ocfEnterTextTextInput"]',
            'phone_or_username': 'input[data-testid="ocfEnterTextTextInput"]',
            'username': 'input[autocomplete="username"]'
        }
        
        selector = input_selectors.get(input_type)
        if not selector:
            return False
            
        try:
            input_field = self.wait_for_element(By.CSS_SELECTOR, selector)
            if input_field:
                # For email_or_phone type, prefer email over phone
                if input_type == 'email_or_phone' and '@' in value:
                    self.human_like_typing(input_field, value)  # Use email
                elif input_type == 'phone_or_username' and not value.startswith('+'):
                    self.human_like_typing(input_field, value)  # Use username
                else:
                    self.human_like_typing(input_field, value)
                    
                time.sleep(random.uniform(0.5, 1.5))
                input_field.send_keys(Keys.ENTER)
                time.sleep(3)
                return True
        except Exception as e:
            print(f"Error handling {input_type} input: {e}")
        return False

    # Login Initiates here
    def login(self, username: str, password: str,email:str):
        try:
            self.driver.get("https://x.com/i/flow/login")
        
            max_steps = 5
            step_count = 0
        
            while step_count < max_steps:
                time.sleep(3)
                
                if self.is_home_page():
                    return True
                
                current_input = self.check_for_input_type()
                print('current_input : ', current_input)
                
                if current_input == 'username':
                    self.handle_input_step('username',username)
                elif current_input == 'password':
                    self.handle_input_step('password', password)
                elif current_input == 'email_or_phone':
                    self.handle_input_step('email_or_phone', email)
                elif current_input == 'phone_or_username':
                    self.handle_input_step('phone_or_username', username)
                elif current_input == 'verification':
                    if not self.wait_for_manual_verification():
                        return False
                else:
                    print("Unknown input type or no input detected")
                    return False
                
                step_count += 1
                time.sleep(2)
            
            return self.is_home_page()
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
        
    # To get the current ip
    def get_ip_address(self):
        try:
            time.sleep(5)
            self.driver.get("http://httpbin.org/ip")
            response = self.driver.find_element(By.TAG_NAME, "body").text
            data = json.loads(response)
            return data['origin']
        except Exception as e:
            print(f"Error fetching IP address: {e}")
            return None
    
    # Fetch the trending topics function
    def get_trending_topics(self):
        try:
            self.driver.get("https://x.com/explore/tabs/trending")
            time.sleep(random.uniform(3, 5))  # Random delay
            
            page_html = self.driver.page_source
            soup = BeautifulSoup(page_html, "html.parser")
            # finding the divs that holds the trend
            trends = soup.find_all("div", {"data-testid": "trend"}, limit=5)
            
            trending_data = []
            for trend in trends:
                try:
                    topic_name = trend.find('div', class_='css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-b88u0q r-1bymd8e')
                    if topic_name:
                        trending_data.append(topic_name.get_text(strip=True))
                except Exception as e:
                    print(f"Error parsing trend: {e}")
                    continue
                    
            return trending_data
            
        except Exception as e:
            print(f"Error fetching trends: {e}")
            return []
            
    #Clean up resources
    def close(self):
        self.driver.quit()


# Example usage
def login_and_fetch_X_trends():
    scraper = TwitterTrendsScraper()
    TWITTER_USERNAME = Config.TWITTER_USERNAME
    TWITTER_PASSWORD = Config.TWITTER_PASSWORD
    TWITTER_EMAIL = Config.TWITTER_EMAIL
    
    try:
        if scraper.login(TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL):
            trends = scraper.get_trending_topics()
            ip_address = scraper.get_ip_address()
            
            return (ip_address, trends) 
    finally:
        scraper.close()
