
import re
from pathlib import Path
from browser_automation import BrowserManager

from selenium.webdriver.common.by import By

from browser_automation import Node
from utils import Utility

class Assisterr:
    def __init__(self, node: Node, profile: dict) -> None:
        self.driver = node._driver
        self.node = node
        self.profile_name = profile.get('profile_name')
        self.password = profile.get('password')
        self.wallet_url = 'chrome-extension://bfnaelmomeimhlpmgjnjophhpkkoljpa'
    def unlock_wallet(self):
        actions = [
            (self.node.go_to, f'{self.wallet_url}/popup.html', 'get'),
            (self.node.find_and_input, By.CSS_SELECTOR, 'input[data-testid="unlock-form-password-input"]', self.password, None, 0.1, 10),
            (self.node.find_and_click, By.CSS_SELECTOR, 'button[data-testid="unlock-form-submit-button"]'),
        ]
        
        return self.node.execute_chain(actions=actions, message_error='Unlock Phantom thất bại')
        
    def _run_logic(self):
        self.unlock_wallet()
        
        self.node.go_to('https://build.assisterr.ai/dashboard')
        self.node.find_and_click(By.XPATH, '//button[text()="Grab Daily Tokens"]')
        text = self.node.get_text(By.XPATH, '//div[text()="Come back in "]//div')
        if not text:
            self.node.snapshot('Check-in thất bại')
        else:
            self.node.log(f'Quay lại check-in sau {text}')

class Auto:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
    def _run(self):

        Assisterr(self.node, self.profile)._run_logic()

class Setup:
    def __init__(self, node: Node, profile) -> None:
        self.node = node
        self.profile = profile
        
    def _run(self):
        self.node.go_to('https://build.assisterr.ai/dashboard')
        self.node.new_tab('chrome-extension://bfnaelmomeimhlpmgjnjophhpkkoljpa/popup.html', 'get')

if __name__ == '__main__':
    DATA_DIR = Path(__file__).parent/'data.txt'

    if not DATA_DIR.exists():
        print(f"File {DATA_DIR} không tồn tại. Dừng mã.")
        exit()

    proxy_re = re.compile(r"^(?:\w+:\w+@)?\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}$")
    PROFILES = []
    num_parts = 2 #số dữ liệu, không bao gồm proxy

    with open(DATA_DIR, 'r') as file:
        data = file.readlines()

    for line in data:
        parts = line.strip().split('|')

        proxy_re = re.compile(r"^(?:\w+:\w+@)?\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}$")
        proxy_info = parts[-1] if proxy_re.match(parts[-1]) else None
        if proxy_info:
            parts = parts[:-1]
            
        if len(parts) < num_parts:
            print(f"Warning: Dữ liệu không hợp lệ - {line}")
            continue        
    
        profile_name, password, *_ = (parts + [None] * num_parts)[:num_parts]

        PROFILES.append({
            'profile_name': profile_name,
            # 'username': username,
            'password': password,
            'proxy_info': proxy_info
        })


    browser_manager = BrowserManager(AutoHandlerClass=Auto, SetupHandlerClass=Setup)
    browser_manager.config_extension('Phantom-*.crx')
    # browser_manager.run_browser(PROFILES[1])
    browser_manager.run_terminal(
        profiles=PROFILES,
        auto=False,
        max_concurrent_profiles=4,
        headless=False
    )
