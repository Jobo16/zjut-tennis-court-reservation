import time
import os
# Playwright是微软开发的自动化测试工具，支持Chrome、Firefox、Safari等浏览器
# sync_playwright是同步版本的API，还有async版本用于异步编程
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()

class AutoReservation:
    def __init__(self, auto_close=False):
        self.username = os.getenv('LOGIN_USERNAME')
        self.password = os.getenv('PASSWORD')
        self.url = "http://www.api.zgyy.zjut.edu.cn/h5/main/reservation"
        self.playwright = None  # 保存playwright实例
        self.browser = None
        self.page = None
        # 同行人员信息
        self.companion_name = os.getenv('COMPANION_NAME')
        self.companion_phone = os.getenv('COMPANION_PHONE')
        self.auto_close = auto_close
    
    def start_browser(self):
        """启动浏览器"""
        # sync_playwright().start() - 启动Playwright实例
        self.playwright = sync_playwright().start()
        
        # playwright.chromium.launch() - 启动Chromium浏览器
        # headless=False - 显示浏览器窗口（True则无头模式，不显示窗口）
        # 其他选项：slow_mo=1000（每个操作延迟1秒），devtools=True（打开开发者工具）
        self.browser = self.playwright.chromium.launch(headless=False)
        
        # browser.new_page() - 创建新的浏览器标签页
        # 返回Page对象，用于后续的页面操作
        self.page = self.browser.new_page()
        print("浏览器已启动")
    
    def user_login(self):
        """用户登录"""
        print("正在访问登录页面...")
        self.page.goto(self.url, timeout=5000, wait_until="load")
        
        print("填写用户名...")
        self.page.fill("#username", self.username)
        
        print("填写密码...")
        self.page.fill("#ppassword", self.password)
        
        print("点击登录按钮...")
        self.page.click("#dl")
        
        self.page.wait_for_selector("text=体育场馆", timeout=10000)
        print("登录成功")
    
    def select_venue(self):
        """选择场馆"""
        print("点击体育场馆...")
        self.page.click("text=体育场馆")
        self.page.wait_for_load_state(state="load")
        
        print("选择屏峰校区...")
        self.page.click(".branch_content")
        self.page.wait_for_load_state(state="load")
        self.page.click("text=屏峰校区")
        
        print("确认校区选择...")
        self.page.click("text=确认")
        self.page.wait_for_load_state(state="load")
        
        print("选择室外网球场...")
        self.page.click(".van-radio")
        self.page.click("text=下一步")
        self.page.wait_for_load_state(state="load")
        print("场馆选择完成")
    
    def select_date_and_mode(self):
        """选择日期和模式"""
        print("选择可用日期...")
        self.page.click(".wh_item_date:not(.wh_want_dayhide):not(.wh_other_dayhide):not(.wh_isToday)")
        self.page.click("text=下一步")
        self.page.wait_for_load_state(state="load")
        
        print("选择半场模式...")
        self.page.click(".venue_list .van-radio")
        self.page.click("text=下一步")
        self.page.wait_for_load_state(state="load")
        print("日期和模式选择完成")

    
    def _get_time_slot_element(self, col, row):
        """获取时间段元素
        
        Args:
            col (int): CSV列号（从1开始）
            row (int): 行号（从1开始）
            
        Returns:
            element: 时间段元素，如果不存在返回None
        """
        # 等待页面加载完成，确保.site元素存在
        try:
            self.page.wait_for_selector(".site", timeout=5000)
        except:
            print("等待页面加载超时")
            return None
        
        
        # 使用CSV列号作为DOM中.site的索引
        base_selector = f".site:nth-child({col}) .site_content"
        elements = self.page.query_selector_all(f"{base_selector} .site_item.left_w1")
        
        if elements and len(elements) >= row:
            return elements[row-1]
        
        return None
    
    def select_time_slots(self, col, rows):
        """选择指定列和行的时间段
        
        Args:
            col (int): 列号
            rows (tuple): 行号元组，如 (1, 2, 3)
        """
        print(f"检查第{col}列，第{rows}行的时间段...")
        
        # 先检查目标行是否有已被预约的格子
        for row in rows:
            try:
                element = self._get_time_slot_element(col, row)
                
                if element:
                    # 检查是否已被预约
                    inner_element = element.query_selector(".yyys")
                    if inner_element:
                        print(f"第{col}列第{row}行已被预约，放弃整列")
                        return False
                        
            except Exception as e:
                print(f"检查第{col}列第{row}行时间段失败: {e}")
                return False
        
        print(f"第{col}列目标行均可用，开始选择时间段...")
        
        selected_count = 0
        for row in rows:
            try:
                element = self._get_time_slot_element(col, row)
                
                if element:
                    # 查找可选择的时间段元素
                    kxzs_element = element.query_selector(".kxzs")
                    if kxzs_element:
                        print(f"点击第{col}列第{row}行时间段...")
                        kxzs_element.click()
                        selected_count += 1
                        time.sleep(0.2)
                    else:
                        print(f"第{col}列第{row}行不可选择")
                else:
                    print(f"第{col}列第{row}行元素不存在")
                    
            except Exception as e:
                print(f"选择第{col}列第{row}行时间段失败: {e}")
                continue
        
        print(f"成功选择了{selected_count}个时间段")
        return selected_count > 0
    
    def complete_reservation(self):
        """完成预约"""
        print("点击同意条款...")
        self.page.click("text=已阅读并同意")
        self.page.wait_for_load_state(state="load")

        print("点击立即预约...")
        self.page.click("text=立即预约")
        self.page.wait_for_load_state(state="load")

        print("填写同行人员姓名...")
        self.page.fill("input[placeholder='请输入姓名']", self.companion_name)
        
        print("填写同行人员手机号...")
        self.page.fill("input[placeholder='请输入手机号']", self.companion_phone)
        self.page.wait_for_load_state(state="load")

        print("点击立即支付...")
        self.page.click("button .van-button__text")
        self.page.wait_for_load_state(state="load")

        print("预约完成！")
        return True
    
    def login(self, col=11, rows=(1, 2, 3)):
        """登录系统并完成预约流程
        
        Args:
            col (int): 列号
            rows (tuple): 行号元组
        """
        try:
            self.user_login()
            self.select_venue()
            self.select_date_and_mode()
            
            if self.select_time_slots(col, rows):
                return self.complete_reservation()
            else:
                return False
                
        except Exception as e:
            print(f"操作失败: {e}")
            return False
    

    
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            # browser.close() - 关闭浏览器实例
            # 这会关闭所有标签页和浏览器窗口
            # 如果只想关闭单个页面，使用page.close()
            self.browser.close()
        if self.playwright:
            # playwright.stop() - 正确关闭playwright实例
            # 确保所有后台进程都被清理
            self.playwright.stop()
        print("浏览器已关闭")
    
    def run(self, col=11, rows=(8, 9, 10)):
        """运行自动预约程序
        
        Args:
            col (int): 列号
            rows (tuple): 行号元组
        """
        # 检查环境变量
        if not all([self.username, self.password, self.companion_name, self.companion_phone]):
            print("错误：请检查.env文件中的环境变量配置")
            print("需要配置：LOGIN_USERNAME, PASSWORD, COMPANION_NAME, COMPANION_PHONE")
            return False
            
        try:
            self.start_browser()
            success = self.login(col, rows)
            if success:
                print("预约流程完成！")
            else:
                print("预约失败，请检查网站状态或重试")
            return success
        except Exception as e:
            print(f"程序运行出错: {e}")
            return False
        finally:
            self.close_browser()

def run_reservation(col, rows):
    """模块导出函数：运行预约程序
    
    Args:
        col (int): 列号
        rows (tuple): 行号元组
    
    Returns:
        bool: 预约是否成功
    """
    app = AutoReservation(auto_close=True)
    return app.run(col, rows)

if __name__ == "__main__":
    app = AutoReservation(auto_close=True)
    app.run()