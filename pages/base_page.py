import allure
from playwright.sync_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("访问页面: {url}")
    def navigate(self, url: str):
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")

    @allure.step("处理所有弹窗")
    def handle_modals(self):
        """
        封装通用的弹窗处理逻辑。
        """
        self.page.wait_for_timeout(2000) # 给弹窗一点弹出时间
        
        for attempt in range(5):
            # 查找所有可见的 ant-modal
            modals = self.page.locator(".ant-modal:visible").all()
            if not modals:
                # 额外检查一下是否有遮罩层还在
                masks = self.page.locator(".ant-modal-mask:visible, .ant-modal-wrap:visible").all()
                if not masks:
                    break
            
            closed_one = False
            # 1. 尝试通过预定义的关闭按钮文本点击
            for text in ["知道了", "我知道了", "确定", "关闭"]:
                btn = self.page.get_by_role("button", name=text).first
                try:
                    if btn.is_visible(timeout=500):
                        btn.click(force=True)
                        closed_one = True
                        self.page.wait_for_timeout(1000)
                        break
                except:
                    pass
            
            # 2. 尝试点击 ant-modal 的关闭图标 X
            if not closed_one:
                close_x = self.page.locator(".ant-modal-close").first
                try:
                    if close_x.is_visible(timeout=500):
                        close_x.click(force=True)
                        closed_one = True
                        self.page.wait_for_timeout(1000)
                except:
                    pass
            
            # 3. 如果还是关不掉，尝试处理特殊的 span.close-btn (针对某些活动弹窗)
            if not closed_one:
                spec_close = self.page.locator("span.close-btn").first
                try:
                    if spec_close.is_visible(timeout=500):
                        spec_close.click(force=True)
                        closed_one = True
                        self.page.wait_for_timeout(1000)
                except:
                    pass

            if not closed_one:
                # 实在关不掉，尝试强制隐藏所有遮罩和弹窗 (应急方案)
                self.page.evaluate("""() => {
                    const selectors = ['.ant-modal-root', '.ant-modal-mask', '.ant-modal-wrap', '.version-update', '.activity-modal'];
                    selectors.forEach(s => {
                        document.querySelectorAll(s).forEach(el => el.style.display = 'none');
                    });
                }""")
                break

        # 最终确认遮罩层消失
        self.wait_for_mask_to_disappear()

        allure.attach(
            self.page.screenshot(), 
            name="Handle Modals Final State", 
            attachment_type=allure.attachment_type.PNG
        )

    def wait_for_mask_to_disappear(self):
        """等待所有遮罩层消失"""
        try:
            self.page.wait_for_function("""() => {
                const masks = document.querySelectorAll('.ant-modal-mask, .ant-modal-wrap');
                return Array.from(masks).filter(m => m.offsetParent !== null).length === 0;
            }""", timeout=5000)
        except:
            print("Warning: Masks did not disappear completely, forcing hide.")
            self.page.evaluate("""() => {
                document.querySelectorAll('.ant-modal-mask, .ant-modal-wrap').forEach(el => el.style.display = 'none');
            }""")
