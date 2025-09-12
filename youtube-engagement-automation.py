import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class YouTubeBot:
    def search_and_open_video(self, keyword, video_url):
        """Search YouTube for a keyword, then open a specific video URL."""
        try:
            self.driver.get("https://www.youtube.com")
            time.sleep(2)
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "search_query"))
            )
            search_box.clear()
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            print(f"Searched for keyword: {keyword}")
            time.sleep(2)
            self.driver.get(video_url)
            print(f"Opened video URL: {video_url}")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error searching and opening video: {e}")
            return False
    def __init__(self, cookies_file=None):
        # Set up Chrome options
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize the driver
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        
        # Load cookies if provided
        if cookies_file:
            self.load_cookies(cookies_file)
    
    def load_cookies(self, cookies_file):
        """Load cookies from a JSON file"""
        try:
            # First navigate to YouTube to set the domain
            self.driver.get("https://www.youtube.com")
            time.sleep(2)
            
            # Load cookies from file
            with open(cookies_file, 'r') as f:
                cookie_data = json.load(f)
            
            # Handle different cookie formats
            if 'cookies' in cookie_data:
                cookies = cookie_data['cookies']
            else:
                cookies = cookie_data
            
            # Add each cookie to the browser
            for cookie in cookies:
                try:
                    # Ensure required fields are present
                    cookie_dict = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie['domain'],
                        'path': cookie.get('path', '/'),
                        'secure': cookie.get('secure', True)
                    }
                    
                    self.driver.add_cookie(cookie_dict)
                    print(f"Added cookie: {cookie['name']}")
                    
                except Exception as e:
                    print(f"Error adding cookie {cookie.get('name', 'unknown')}: {e}")
            
            # Refresh the page to apply cookies
            self.driver.refresh()
            time.sleep(3)
            print("Cookies loaded successfully")
            
        except Exception as e:
            print(f"Error loading cookies: {e}")
    
    def open_video(self, video_url):
        """Open a YouTube video"""
        try:
            self.driver.get(video_url)
            time.sleep(3)
            
            # Wait for video player to load
            self.wait.until(EC.presence_of_element_located((By.ID, "movie_player")))
            print(f"Video opened: {video_url}")
            return True
            
        except TimeoutException:
            print("Failed to load video")
            return False
    
    def watch_video(self, duration_seconds):
        """Watch video for specified duration"""
        try:
            print(f"Watching video for {duration_seconds} seconds...")
            
            # Click play if video is paused
            try:
                play_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button")
                if play_button.get_attribute("data-title-no-tooltip") == "Play":
                    play_button.click()
                    print("Video started")
            except:
                pass
            
            # Wait for the specified duration
            time.sleep(duration_seconds)
            print("Finished watching video")
            return True
            
        except Exception as e:
            print(f"Error watching video: {e}")
            return False
    
    def like_video(self):
        """Like the video"""
        try:
            # Wait for page to fully load
            time.sleep(1)
            
            # Multiple selectors to find the like button (YouTube changes these frequently)
            like_selectors = [
                "button[aria-label*='like this video']",
                "button[aria-label*='Like this video']", 
                "#segmented-like-button button",
                "ytd-toggle-button-renderer.force-icon-button#like-button-renderer button"
            ]
            
            for selector in like_selectors:
                try:
                    like_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    
                    # Check if already liked (aria-pressed="true")
                    if like_button.get_attribute("aria-pressed") == "true":
                        print("Video is already liked")
                        return True
                    
                    like_button.click()
                    time.sleep(1)
                    print("Video liked successfully")
                    return True
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            print("Could not find like button with any selector")
            return False
            
        except Exception as e:
            print(f"Error liking video: {e}")
            return False
    
    def comment_video(self, comment_text):
        """Add a comment to the video"""
        try:
            # Scroll down to load comments section
            self.driver.execute_script("window.scrollTo(0, 600);")
            time.sleep(3)
            
            # Wait for comments section to load
            try:
                self.wait.until(EC.presence_of_element_located((By.ID, "comments")))
            except:
                print("Comments section not found, scrolling more...")
                self.driver.execute_script("window.scrollTo(0, 1200);")
                time.sleep(3)
            
            # Multiple selectors for comment box
            comment_selectors = [
                "#placeholder-area",
                "#simplebox-placeholder",
                "div#placeholder-area"
            ]
            
            comment_clicked = False
            for selector in comment_selectors:
                try:
                    comment_box = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    comment_box.click()
                    comment_clicked = True
                    break
                except:
                    continue
            
            if not comment_clicked:
                print("Could not click comment box")
                return False
            
            time.sleep(3)
            
            # Multiple selectors for text input
            input_selectors = [
                "#contenteditable-root",
                "div[contenteditable='true']",
                "#textbox"
            ]
            
            text_input = None
            for selector in input_selectors:
                try:
                    text_input = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not text_input:
                print("Could not find text input")
                return False
            
            text_input.click()
            time.sleep(1)
            text_input.clear()
            text_input.send_keys(comment_text)
            time.sleep(1)
            
            # Multiple selectors for submit button
            submit_selectors = [
                "#submit-button button",
                "button[aria-label*='Comment']",
                "#submit-button"
            ]
            
            for selector in submit_selectors:
                try:
                    comment_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    comment_button.click()
                    time.sleep(3)
                    print(f"Comment posted: {comment_text}")
                    return True
                except:
                    continue
            
            print("Could not find submit button")
            return False
            
        except Exception as e:
            print(f"Error posting comment: {e}")
            return False
        

    def subscribe_channel(self):

        """Subscribe to the channel if not already subscribed"""
        try:
            time.sleep(1)  # wait for page load
            # Scroll to the subscribe button area
            self.driver.execute_script("window.scrollTo(0, 400);")
            time.sleep(1)

            subscribe_selectors = [
                "ytd-subscribe-button-renderer tp-yt-paper-button",
                "tp-yt-paper-button[aria-label*='Subscribe']",
                "#subscribe-button ytd-subscribe-button-renderer tp-yt-paper-button",
                "#subscribe-button tp-yt-paper-button",
                "tp-yt-paper-button.style-scope.ytd-subscribe-button-renderer",
                "button[aria-label*='Subscribe']"
            ]

            for selector in subscribe_selectors:
                try:
                    button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    # If already subscribed
                    if "Subscribed" in button.text or button.get_attribute("aria-pressed") == "true":
                        print("Channel is already subscribed")
                        return True
                    button.click()
                    time.sleep(1)
                    print("Channel subscribed successfully")
                    return True
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue

            # Fallback: try to find the button by text
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "tp-yt-paper-button")
                for button in buttons:
                    if button.is_displayed() and ("Subscribe" in button.text or button.get_attribute("aria-label") and "Subscribe" in button.get_attribute("aria-label")):
                        if "Subscribed" in button.text or button.get_attribute("aria-pressed") == "true":
                            print("Channel is already subscribed")
                            return True
                        button.click()
                        time.sleep(1)
                        print("Channel subscribed successfully (fallback)")
                        return True
            except Exception as e:
                print(f"Fallback text search error: {e}")

            print("Could not find subscribe button")
            return False

        except Exception as e:
            print(f"Error subscribing: {e}")
            return False
 
    
    def run_automation(self, video_url, watch_duration, comment_text=None):
        """Run the complete automation process. Accepts a single comment or a list of comments."""
        try:
            # Open the video
            if not self.open_video(video_url):
                return False

            # Watch the video
            if not self.watch_video(watch_duration):
                return False

            # Like the video
            if not self.like_video():
                print("Failed to like video, continuing...")

            # Subscribe to channel
            if not self.subscribe_channel():
                print("Failed to subscribe, continuing...")

            # Post comments (single or multiple)
            if comment_text:
                if isinstance(comment_text, list):
                    for idx, comment in enumerate(comment_text):
                        print(f"Posting comment {idx+1}/{len(comment_text)}: {comment}")
                        if not self.comment_video(comment):
                            print(f"Failed to post comment: {comment}")
                        time.sleep(2)  # Short delay between comments
                else:
                    if not self.comment_video(comment_text):
                        print("Failed to comment, continuing...")

            print("Automation completed successfully")
            return True

        except Exception as e:
            print(f"Error in automation: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

# Example usage
if __name__ == "__main__":
    # Initialize the bot with cookies file
    bot = YouTubeBot(cookies_file="youtube_cookies.json")
    
    try:
        # Example video URLs - replace with actual YouTube video URLs
        keyword = "통영맛집"
        video_url = "https://youtu.be/b-OQQAUfw5Y"
        watch_duration = 10  # Watch for 10 seconds
        comment_text = [
            "곧 갑니다.",
            "여긴 찐맛집이에요ㅎㅎ",
            "❤️"
        ]  # Multiple comments example

        print("Starting YouTube automation...")
        print(f"Searching for keyword: {keyword}")
        print(f"Video URL: {video_url}")
        print(f"Watch duration: {watch_duration} seconds")
        print(f"Comment: {comment_text}")

        # Search and open the video
        bot.search_and_open_video(keyword, video_url)

        success = bot.run_automation(video_url, watch_duration, comment_text)

        if success:
            print("\n✅ Automation completed successfully!")
        else:
            print("\n❌ Automation failed!")

    except KeyboardInterrupt:
        print("\n⏹️ Automation stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    finally:
        # Always close the browser
        print("Closing browser...")
        time.sleep(1)  # Wait a bit before closing
        bot.close()
        print("Browser closed.")