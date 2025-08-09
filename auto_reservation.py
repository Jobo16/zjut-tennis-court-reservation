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
    
    def login(self):
        """登录系统"""
        try:
            # 访问登录页面
            print("正在访问登录页面...")
            # page.goto(url) - 导航到指定URL
            # 等价于在浏览器地址栏输入网址并回车
            # 可选参数：timeout=30000（超时时间30秒），wait_until="load"（等待页面加载完成）
            self.page.goto(self.url, timeout=5000, wait_until="load")

            
            # 填写用户名
            print("填写用户名...")
            # page.fill(selector, value) - 在输入框中填入文本
            # "#username" - CSS选择器，#表示按id查找，等价于document.getElementById("username")
            # 其他选择器示例：
            # ".class" - 按class查找
            # "input[type='text']" - 按属性查找
            # "text=登录" - 按文本内容查找
            self.page.fill("#username", self.username)
            
            # 填写密码
            print("填写密码...")
            # 同样使用fill方法填入密码，#ppassword是密码输入框的id
            self.page.fill("#ppassword", self.password)
            
            # 点击登录按钮
            print("点击登录按钮...")
            # page.click(selector) - 点击元素
            # "#dl" - 按id查找登录按钮并点击
            # 可选参数：button="left"（左键点击），timeout=30000（超时时间）
            self.page.click("#dl")
            
            # 等待页面跳转 - 使用智能等待替代固定延时
            # page.wait_for_selector() - 等待特定元素出现，更可靠
            # timeout=10000 - 最多等待10秒，避免无限等待

            self.page.wait_for_selector("text=体育场馆", timeout=10000)

            
            # 点击体育场馆
            print("点击体育场馆...")
            # "text=体育场馆" - 按文本内容查找元素
            # Playwright会找到包含"体育场馆"文本的可点击元素
            self.page.click("text=体育场馆")
            self.page.wait_for_load_state(state="load")

            print("已点击体育场馆")

            
            return True
        except Exception as e:
            print(f"点击体育场馆前失败: {e}")
            return False
    
    def take_screenshot(self, name="screenshot"):
        """截图"""
        try:
            # page.screenshot() - 对当前页面截图
            # path参数指定保存路径和文件名
            # 其他选项：full_page=True（截取整个页面），clip={"x":0,"y":0,"width":800,"height":600}（截取指定区域）
            screenshot_path = os.path.join("screenshot", f"{name}.png")
            self.page.screenshot(path=screenshot_path)
            print(f"截图已保存: {screenshot_path}") 
        except Exception as e:
            print(f"截图失败: {e}")
    
    def select_venue(self):
        """选择场馆 - 屏峰校区室外网球场"""
        try:
            print("点击选择校区区域...")
            # 点击校区选择区域
            # ".branch_content" - CSS类选择器，.表示按class查找
            self.page.click(".branch_content")
            self.page.wait_for_load_state(state="load")
            
            print("选择屏峰校区...")
            # 选择屏峰校区
            # 按文本内容精确匹配并点击
            self.page.click("text=屏峰校区")
            
            print("确认校区选择...")
            # 点击确认按钮
            # 文本选择器会找到包含"确认"文本的按钮
            self.page.click("text=确认")
            self.page.wait_for_load_state(state="load")

            
            print("选择室外网球场...")
            # 点击室外网球场的radio按钮
            # ".van-radio" - 选择class为van-radio的元素（通常是单选按钮）
            self.page.click(".van-radio")
            
            # 点击下一步按钮
            self.page.click("text=下一步")
            self.page.wait_for_load_state(state="load")
            print("选择室外网球场成功")
            return True
        except Exception as e:
            print(f"选择场馆失败: {e}")
            return False
    
    def select_date_and_mode(self):
        """选择日期和模式"""
        try:
            print("选择可用日期...")
            # 选择可用的日期（排除隐藏和今天的日期）
            # 复杂CSS选择器示例：
            # ".wh_item_date" - 选择class为wh_item_date的元素
            # ":not(.wh_want_dayhide)" - 排除class包含wh_want_dayhide的元素
            # ":not(.wh_other_dayhide)" - 排除class包含wh_other_dayhide的元素
            # ":not(.wh_isToday)" - 排除class包含wh_isToday的元素
            # 多个:not()可以组合使用，表示"且"的关系
            self.page.click(".wh_item_date:not(.wh_want_dayhide):not(.wh_other_dayhide):not(.wh_isToday)")
            
            
            print("选择下一天")
            self.page.click("text=下一步")
            self.page.wait_for_load_state(state="load")
            
            print("选择半场模式...")
            # 选择半场模式
            self.page.click(".venue_list .van-radio")
           
            
            print("点击下一步...")
            self.page.click("text=下一步")
            self.page.wait_for_load_state(state="load")

            
            return True
        except Exception as e:
            print(f"选择日期和模式失败: {e}")
            return False
    
    def select_time_slots(self):
        """选择时间段 - 17:00-21:00"""
        try:
            print("检查并选择可用的时间段...")
            
            # 从第1列开始尝试，必须找到有完整17:00-21:00时间段的列
            for col in range(1, 22):  # 尝试更多列
                print(f"检查第{col}列...")
                
                # 检查该列的第10-13行是否都可用（没有yyys）
                all_available = True
                for row in range(10, 14):
                    try:
                        # 动态构建CSS选择器
                        # ":nth-child(n)" - 选择第n个子元素（从1开始计数）
                        # 空格表示后代选择器，如"A B"表示A元素内部的B元素
                        selector = f".site:nth-child({col}) .site_content .site_item:nth-child({row})"
                        
                        # page.query_selector(selector) - 查找单个元素
                        # 返回ElementHandle对象，如果找不到则返回None
                        # 类似于document.querySelector()
                        element = self.page.query_selector(selector)
                        
                        if element:
                            # 检查是否包含yyys类
                            # element.query_selector() - 在已找到的元素内部继续查找
                            # 这里查找class为yyys的子元素（表示已预约）
                            inner_element = element.query_selector(".yyys")
                            if inner_element:
                                print(f"第{col}列第{row}行已被预约")
                                all_available = False
                                break
                        else:
                            all_available = False
                            break
                    except Exception as e:
                        all_available = False
                        break
                
                # 如果该列的17:00-21:00时间段都可用，选择该列的所有时间段
                if all_available:
                    print(f"第{col}列有完整的17:00-21:00时间段，开始选择...")
                    selected_count = 0
                    for row in range(10, 14):
                        try:
                            selector = f".site:nth-child({col}) .site_content .site_item:nth-child({row})"
                            element = self.page.query_selector(selector)
                            if element:
                                # 查找可选择的时间段元素
                                # ".kxzs" - class为kxzs的元素（表示可选择状态）
                                kxzs_element = element.query_selector(".kxzs")
                                if kxzs_element:
                                    print(f"点击第{col}列第{row}行时间段...")
                                    # 直接在ElementHandle对象上调用click()方法
                                    kxzs_element.click()
                                    selected_count += 1
                                    time.sleep(0.2)
                        except Exception as e:
                            print(f"选择时间段失败: {e}")
                            continue
                    
                    if selected_count == 4:
                        print(f"成功选择了完整的17:00-21:00时间段")
                        return True
                    else:
                        print(f"只选择了{selected_count}个时间段，继续寻找其他列")
                else:
                    print(f"第{col}列没有完整的17:00-21:00时间段，尝试下一列")
            
            print("没有找到有完整17:00-21:00时间段的列")
            return False
        except Exception as e:
            print(f"选择时间段失败: {e}")
            return False
    
    def agree_and_reserve(self):
        """同意条款并预约"""
        try:
            print("点击同意条款...")
            self.page.click("text=已阅读并同意")
            self.page.wait_for_load_state(state="load")

            print("点击立即预约...")
            self.page.click("text=立即预约")
            self.page.wait_for_load_state(state="load")
            
            return True
        except Exception as e:
            print(f"同意条款并预约失败: {e}")
            return False
    
    def fill_companion_info(self):
        """填写同行人员信息"""
        try:
            print("填写同行人员姓名...")
            self.page.fill("input[placeholder='请输入姓名']", self.companion_name)
            
            
            print("填写同行人员手机号...")
            self.page.fill("input[placeholder='请输入手机号']", self.companion_phone)
            self.page.wait_for_load_state(state="load")
            
            return True
        except Exception as e:
            print(f"填写同行人员信息失败: {e}")
            return False
    
    def complete_payment(self):
        """完成支付"""
        try:
            print("点击立即支付...")
            self.page.click("button .van-button__text")
            self.page.wait_for_load_state(state="load")

            
            print("预约完成！")
            return True
        except Exception as e:
            print(f"支付失败: {e}")
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
    
    def run(self):
        """运行自动预约程序"""
        try:
            self.start_browser()
            
            if not self.login():
                print("登录失败")
                return
            
            print("登录成功！")
            self.take_screenshot("login_success")
            
            # 执行预约流程
            if not self.select_venue():
                print("选择场馆失败")
                return
            
            if not self.select_date_and_mode():
                print("选择日期和模式失败")
                return
            
            if not self.select_time_slots():
                print("选择时间段失败")
                return
            
            if not self.agree_and_reserve():
                print("同意条款并预约失败")
                return
            
            if not self.fill_companion_info():
                print("填写同行人员信息失败")
                return
            
            if not self.complete_payment():
                print("支付失败")
                return
            
            print("\n=== 预约成功！===")
            print(f"场馆: 屏峰校区室外网球场")
            print(f"时间: 17:00-21:00")
            print(f"同行人员: {self.companion_name} ({self.companion_phone})")
            
            self.take_screenshot("reservation_completed")
            
            # 根据auto_close参数决定是否等待用户输入
            if self.auto_close:
                print("\n预约完成！程序将自动关闭浏览器...")
                time.sleep(3)  # 等待3秒让用户看到结果
            else:
                input("\n预约完成！按回车键关闭浏览器...")
                
        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            self.close_browser()

if __name__ == "__main__":
    app = AutoReservation(auto_close=True)
    app.run()