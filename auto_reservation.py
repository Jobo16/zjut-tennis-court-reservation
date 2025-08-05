import time
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class AutoReservation:
    def __init__(self):
        self.username = os.getenv('LOGIN_USERNAME')
        self.password = os.getenv('PASSWORD')
        self.url = "http://www.api.zgyy.zjut.edu.cn/h5/main/reservation"
        self.browser = None
        self.page = None
        # 同行人员信息
        self.companion_name = os.getenv('COMPANION_NAME')
        self.companion_phone = os.getenv('COMPANION_PHONE')
    
    def start_browser(self):
        """启动浏览器"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        print("浏览器已启动")
    
    def login(self):
        """登录系统"""
        try:
            # 访问登录页面
            print("正在访问登录页面...")
            self.page.goto(self.url)
            time.sleep(2)
            
            # 填写用户名
            print("填写用户名...")
            self.page.fill("#username", self.username)
            
            # 填写密码
            print("填写密码...")
            self.page.fill("#ppassword", self.password)
            
            # 点击登录按钮
            print("点击登录按钮...")
            self.page.click("#dl")
            
            # 等待页面跳转
            time.sleep(3)
            
            # 点击体育场馆
            print("点击体育场馆...")
            self.page.click("text=体育场馆")
            time.sleep(2)
            
            print("登录完成")
            
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def take_screenshot(self, name="screenshot"):
        """截图"""
        try:
            self.page.screenshot(path=f"{name}.png")
            print(f"截图已保存: {name}.png")
        except Exception as e:
            print(f"截图失败: {e}")
    
    def select_venue(self):
        """选择场馆 - 屏峰校区室外网球场"""
        try:
            print("点击选择校区区域...")
            # 点击校区选择区域
            self.page.click(".branch_content")
            time.sleep(1)
            
            print("选择屏峰校区...")
            # 选择屏峰校区
            self.page.click("text=屏峰校区")
            time.sleep(1)
            
            print("确认校区选择...")
            # 点击确认按钮
            self.page.click("text=确认")
            time.sleep(1)
            
            print("选择室外网球场...")
            # 点击室外网球场的radio按钮
            self.page.click(".van-radio")
            time.sleep(1)
            
            print("点击下一步...")
            # 点击下一步按钮
            self.page.click("text=下一步")
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"选择场馆失败: {e}")
            return False
    
    def select_date_and_mode(self):
        """选择日期和模式"""
        try:
            print("选择可用日期...")
            # 选择可用的日期（排除隐藏和今天的日期）
            self.page.click(".wh_item_date:not(.wh_want_dayhide):not(.wh_other_dayhide):not(.wh_isToday)")
            time.sleep(1)
            
            print("点击下一步...")
            self.page.click("text=下一步")
            time.sleep(2)
            
            print("选择半场模式...")
            # 选择半场模式
            self.page.click(".venue_list .van-radio")
            time.sleep(1)
            
            print("点击下一步...")
            self.page.click("text=下一步")
            time.sleep(2)
            
            return True
        except Exception as e:
            print(f"选择日期和模式失败: {e}")
            return False
    
    def select_time_slots(self):
        """选择时间段 - 17:00-21:00"""
        try:
            print("检查并选择可用的时间段...")
            
            # 从第1列开始尝试，必须找到有完整17:00-21:00时间段的列
            for col in range(1, 15):  # 尝试更多列
                print(f"检查第{col}列...")
                
                # 检查该列的第10-13行是否都可用（没有yyys）
                all_available = True
                for row in range(10, 14):
                    try:
                        selector = f".site:nth-child({col}) .site_content .site_item:nth-child({row})"
                        element = self.page.query_selector(selector)
                        
                        if element:
                            # 检查是否包含yyys类
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
                                kxzs_element = element.query_selector(".kxzs")
                                if kxzs_element:
                                    print(f"点击第{col}列第{row}行时间段...")
                                    kxzs_element.click()
                                    selected_count += 1
                                    time.sleep(0.5)
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
            time.sleep(1)
            
            print("点击立即预约...")
            self.page.click("text=立即预约")
            time.sleep(3)
            
            return True
        except Exception as e:
            print(f"同意条款并预约失败: {e}")
            return False
    
    def fill_companion_info(self):
        """填写同行人员信息"""
        try:
            print("填写同行人员姓名...")
            self.page.fill("input[placeholder='请输入姓名']", self.companion_name)
            time.sleep(0.5)
            
            print("填写同行人员手机号...")
            self.page.fill("input[placeholder='请输入手机号']", self.companion_phone)
            time.sleep(0.5)
            
            return True
        except Exception as e:
            print(f"填写同行人员信息失败: {e}")
            return False
    
    def complete_payment(self):
        """完成支付"""
        try:
            print("点击立即支付...")
            self.page.click("button .van-button__text")
            time.sleep(3)
            
            print("预约完成！")
            return True
        except Exception as e:
            print(f"支付失败: {e}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
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
            
            # 保持浏览器打开以便查看结果
            input("\n预约完成！按回车键关闭浏览器...")
                
        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            self.close_browser()

if __name__ == "__main__":
    app = AutoReservation()
    app.run()