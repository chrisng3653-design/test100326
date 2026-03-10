import allure
from playwright.sync_api import Page, expect
from .base_page import BasePage

class HomePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # 将硬编码的 img[src="..."] 替换为更鲁棒的选择器
        # 考虑到是“新增销售单”图标，通常会有特定的 class 或它的父元素有 title/text
        # 如果没有更好的，我们暂时保留图片选择器但可以封装起来，或根据层级定位
        # 这里尝试使用一个更具语义化的定位方式（假设它是侧边栏或快捷入口的一部分）
        self.new_sales_order_btn = page.locator('img[src*="794727d0050b4f73be98b307e7852823"]')

    @allure.step("点击'新增销售单'")
    def click_new_sales_order(self):
        # 确保弹窗已处理
        self.handle_modals()
        self.wait_for_mask_to_disappear()
        
        with allure.step("点击图标"):
            expect(self.new_sales_order_btn).to_be_visible(timeout=5000)
            self.new_sales_order_btn.click()
            
        self.page.wait_for_load_state("networkidle")
        allure.attach(
            self.page.screenshot(), 
            name="New Sales Order Page", 
            attachment_type=allure.attachment_type.PNG
        )
