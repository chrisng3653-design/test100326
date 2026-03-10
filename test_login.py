import os

import allure
import pytest
import yaml
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect, sync_playwright


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def config() -> dict:
    return load_config()


@pytest.fixture(scope="function")
def page(config):
    mcp_debug = os.getenv("MCP_DEBUG", "0") == "1"
    keep_open = os.getenv("KEEP_OPEN", "0") == "1"
    slow_mo = int(os.getenv("PW_SLOW_MO", "300" if mcp_debug else "0"))
    action_timeout = int(os.getenv("PW_ACTION_TIMEOUT", "10000"))
    final_wait_ms = int(os.getenv("PW_FINAL_WAIT", "0"))

    launch_headless = config.get("headless", False)
    if mcp_debug:
        launch_headless = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=launch_headless, slow_mo=slow_mo)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        test_page = context.new_page()
        test_page.set_default_timeout(action_timeout)

        try:
            yield test_page
        finally:
            if final_wait_ms > 0:
                test_page.wait_for_timeout(final_wait_ms)
            if keep_open:
                print("\nKEEP_OPEN is set. Browser will stay open. Press Enter in terminal to close.")
                input("Press Enter to continue...")
            context.close()
            browser.close()


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("访问页面: {url}")
    def navigate(self, url: str):
        self.page.goto(url, wait_until="domcontentloaded")
        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except PlaywrightTimeoutError:
            pass


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.phone_input = page.locator('input[name="phone"]')
        self.password_input = page.locator('#custom-validation_password')
        self.login_button = page.get_by_role("button", name="登 录")

    @allure.step("输入用户名和密码登录")
    def login(self, phone: str, password: str):
        self.phone_input.fill(phone)
        expect(self.phone_input).to_have_value(phone)
        self.password_input.fill(password)
        expect(self.login_button).to_be_enabled()
        self.login_button.click()
        try:
            self.page.wait_for_load_state("networkidle", timeout=8000)
        except PlaywrightTimeoutError:
            pass


@allure.feature("登录功能")
class TestLogin:
    @allure.story("用户使用手机号正常登录")
    @allure.title("智慧记 AI 零售 - 仅登录测试")
    def test_zhihuiji_login_only(self, page, config):
        login_page = LoginPage(page)
        login_page.navigate(config["base_url"])
        login_page.login(config["phone"], config["password"])
