import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage

@allure.feature("登录功能")
class TestLogin:
    
    @allure.story("用户使用手机号正常登录并新增销售单")
    @allure.title("智慧记 AI 零售 - POM 重构测试")
    def test_zhihuiji_login_and_new_order(self, page, config):
        # 初始化页面对象
        login_page = LoginPage(page)
        home_page = HomePage(page)

        # 1. 访问登录页面
        login_page.navigate(config["base_url"])

        # 2. 登录
        login_page.login(config["phone"], config["password"])

        # 3. 点击新增销售单
        home_page.click_new_sales_order()

        # 4. 验证是否进入新增销售单页面 (可选，可以根据实际情况添加断言)
        # expect(page).to_contain_url("sales/order/add")


if __name__ == "__main__":
    import os
    import subprocess

    print("开始运行测试...")
    # 默认通过 pytest 运行
    # 可以通过环境变量 KEEP_OPEN=1 保持浏览器打开
    # os.environ["KEEP_OPEN"] = "1"
    pytest.main(["-v", "-s", "test_login.py", "--alluredir=./allure-results"])

    print("正在生成 Allure 报告...")
    try:
        subprocess.run("allure generate ./allure-results -o ./allure-report --clean", shell=True, check=True)
        print("报告已生成！文件夹：allure-report")
    except Exception as e:
        print(f"生成报告失败，请检查 Allure 环境变量是否配置正确。错误信息: {e}")