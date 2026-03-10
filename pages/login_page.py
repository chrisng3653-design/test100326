import allure
from playwright.sync_api import Page, expect
from .base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.phone_input = page.locator('input[name="phone"]')
        self.password_input = page.locator('#custom-validation_password')
        self.login_button = page.get_by_role("button", name="登 录")

    @allure.step("输入用户名和密码登录")
    def login(self, phone, password):
        with allure.step(f"输入手机号: {phone}"):
            self.phone_input.fill(phone)
            expect(self.phone_input).to_have_value(phone)
            
        with allure.step("输入密码"):
            self.password_input.fill(password)
            
        with allure.step("点击登录按钮"):
            expect(self.login_button).to_be_enabled()
            self.login_button.click()
            
        self.page.wait_for_load_state("networkidle")
