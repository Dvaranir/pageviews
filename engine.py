from playwright.sync_api import sync_playwright
from decorators import try_action 
import random

class PlaywrightController:
    
    def __init__(self):
        self.chrome_args = [
            '--use-angle=vulkan',
            '--enable-gpu',
            '--no-sandbox',
            '--ignore-gpu-blocklist',
            '--ignore-certificate-errors',
        ]
        
        self.urls = []
        self.current_domain = ''
        self.links_walked = 0
        
        self.CHROME_PATH = 'D:\Programs\Development\PlaywrightBrowsers\chromium-1060\chrome-win\chrome.exe'
        self.FILE_NAME = "urls.txt"
        
        self.MAX_ACTIONS_TIMEOUT = 5000
        self.WALK_LIMIT = 3
        self.MIN_WAIT = 500
        self.MAX_WAIT = 1500
        self.DEFAULT_WAIT_BOOSTER = 4000
        self.LONG_WAIT_BOOSTER = 6000
        
        self.read_urls_from_file()
        self.event_loop()
        
    def event_loop(self):
        with sync_playwright() as pw:
            self.start_session(pw)
            self.main_loop()
            
    
    def main_loop(self):
        if(len(self.urls) <= 0): return
        
        random_index = random.randint(0, len(self.urls) - 1)
        self.current_domain = self.urls[random_index]
        
        self.enter_site()
        self.randomize_walk_limit()
        self.go_deeper()
        self.urls.pop(random_index)
        
        self.main_loop()
                
    def start_session(self, pw):
        self.browser = pw.chromium.launch( headless=False,
                                           executable_path=self.CHROME_PATH,
                                           args=self.chrome_args,
                                           timeout=0 )
        self.browser.new_context(
            user_agent='Mozilla/5.0 (Linux; U; Android 4.1.1; en-gb; Build/KLP) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30'
        )
        
        self.page = self.browser.new_page()
        self.page.set_viewport_size({ 'width': 1920, 'height': 1080 })
        self.patch_webdriver()
        
    def patch_webdriver(self):
        self.page.add_init_script("""
            if (navigator.webdriver === false) {
            // Post Chrome 89.0.4339.0 and already good
            } else if (navigator.webdriver === undefined) {
                // Pre Chrome 89.0.4339.0 and already good
            } else {
                // Pre Chrome 88.0.4291.0 and needs patching
                delete Object.getPrototypeOf(navigator).webdriver
            }
        """)

    def go_deeper(self):
        self.pick_random_element_to_click()
        self.emulate_user()
        self.links_walked += 1
        
        if self.links_walked < self.WALK_LIMIT:
            self.go_deeper()
            
        else: self.links_walked = 0
                
    def enter_site(self): self.default_emulation(self.go_to_site)
        
    def emulate_user(self): self.default_emulation(self.click_on_random_element)
        
    def default_emulation(self, method):
        self.patch_webdriver()
        method()
        self.wait_default() 
        self.scroll()
        
    def click_on_random_element(self):
        self.pick_random_element_to_click()
        try:
            self.element_interaction()            
        except Exception as e:
            print(e)
            self.click_on_random_element()
            
    @try_action
    def scroll_to_element(self):
        self.wait_tiny()
        self.click_element.scroll_into_view_if_needed(timeout=self.MAX_ACTIONS_TIMEOUT)
    
    @try_action
    def hover_element(self):
        self.wait_tiny()
        self.click_element.hover(timeout=self.MAX_ACTIONS_TIMEOUT)
        
    def click_on_element(self):
        self.wait_tiny()
        self.click_element.click(timeout=self.MAX_ACTIONS_TIMEOUT)
        
    def element_interaction(self):
        self.scroll_to_element()
        self.hover_element()
        self.click_element()
            
    def pick_random_element_to_click(self):
        links = self.page.query_selector_all(f"a[href*='{self.current_domain}']")
        
        if not links or len(links) <= 0:
            links = self.page.query_selector_all("a:not([href*='http'])")
            
        self.click_element = links[random.randint(0, len(links) - 1)]
        
    def go_to_site(self):
        print(f"Fetching {self.current_domain}")
        self.page.goto(self.current_domain, timeout=0)
        self.page.wait_for_load_state('domcontentloaded', timeout=0)
        print(f"DOM loaded")
        
       
    def get_body_height(self): return self.page.evaluate("() => document.body.scrollHeight")
    
    def randomize_walk_limit(self): self.WALK_LIMIT = random.randint(3, 5)

    def scroll(self):
        print('Start scrolling')
        body_height = int(self.get_body_height())
        
        if (body_height < 100): body_height = 500
        
        def gen_random_scroll_value():
            scroll_min = int(body_height / 5)
            scroll_max = int(body_height / 2)
            
            return random.randint(scroll_min, scroll_max)
        
        def top():
            scroll_y = -gen_random_scroll_value()
            print(f'Scrolling top by {scroll_y}y')
            self.page.mouse.wheel(0, scroll_y)
            self.wait_long()
            
        def bottom():
            scroll_y = gen_random_scroll_value()
            print(f'Scrolling top by {scroll_y}y')
            self.page.mouse.wheel(0, scroll_y)
            self.wait_long()
        
        scrolls = [top, bottom]
        
        def random_scroll(): scrolls[random.randint(0, len(scrolls) - 1)]()
        
        def random_scrolls():
            scrolls_left = random.randint(1, 3)
            bottom()
            while True:
                random_scroll()
                scrolls_left -= 1
                
                if scrolls_left <= 0: break
        
        random_scrolls()
        print('Scrolling done')
        
    def read_urls_from_file(self):
        with open(self.FILE_NAME, "r") as file:
            print('Reading urls from file')
            for line in file:
                stripped_line = line.strip()
                
                if 'http' not in stripped_line:
                    url = f"https://{stripped_line}"
                else:
                    url = stripped_line
                
                if url:
                    self.urls.append(url)
                    
    def wait_tiny(self, booster=0):
        wait_time = random.randint(self.MIN_WAIT + booster / 2, self.MAX_WAIT+booster)
        print(f"Waiting {wait_time}ms")
        self.page.wait_for_timeout(wait_time)
                    
    def wait_default(self): self.wait_tiny(self.DEFAULT_WAIT_BOOSTER)
    def wait_long(self): self.wait_tiny(self.LONG_WAIT_BOOSTER)
        
    