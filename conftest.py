import pytest
import yaml
import os
from playwright.sync_api import sync_playwright

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def config():
    return load_config()

@pytest.fixture(scope="session")
def browser_context_args(config):
    return {
        "viewport": {"width": 1920, "height": 1080},
    }

@pytest.fixture(scope="function")
def page(config):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=config.get("headless", False))
        context = browser.new_context()
        page = context.new_page()
        yield page
        # 根据用户需求，有时需要保持浏览器打开，这里我们可以根据配置或环境变量来决定
        if os.getenv("KEEP_OPEN") != "1":
            browser.close()
        else:
            print("\nKEEP_OPEN is set. Browser will stay open. Press Enter in terminal to close.")
            input("Press Enter to continue...")
            browser.close()
