import time
import datetime
import subprocess
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_reservation_script():
    """运行预约脚本"""
    script_path = r'c:\Users\admin\Desktop\新建文件夹 (3)\auto_reservation.py'
    print(f"开始运行预约脚本: {script_path}")
    try:
        # 使用Python解释器运行脚本
        subprocess.run(['python', script_path], check=True)
        print("预约脚本执行完成")
    except subprocess.CalledProcessError as e:
        print(f"预约脚本执行失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

def wait_until_schedule_time():
    """等待到指定时间"""
    while True:
        now = datetime.datetime.now()
        # 从环境变量获取执行时间，默认为05:00
        schedule_time = os.getenv('SCHEDULE_TIME', '05:00')
        hour, minute = map(int, schedule_time.split(':'))
        
        # 获取目标时间
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time <= now:
            # 如果目标时间已经过了，则设为明天的执行时间
            target_time += datetime.timedelta(days=1)
        
        # 计算需要等待的秒数
        wait_seconds = (target_time - now).total_seconds()
        
        # 显示等待信息
        wait_hours = int(wait_seconds // 3600)
        wait_minutes = int((wait_seconds % 3600) // 60)
        wait_seconds_remainder = int(wait_seconds % 60)
        
        print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"目标时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"等待时间: {wait_hours}小时 {wait_minutes}分钟 {wait_seconds_remainder}秒")
        
        # 每10分钟更新一次等待信息
        if wait_seconds > 600:
            time.sleep(600)  # 睡眠10分钟
        else:
            # 如果等待时间少于10分钟，则每分钟更新一次
            if wait_seconds > 60:
                time.sleep(60)  # 睡眠1分钟
            else:
                # 如果等待时间少于1分钟，则每秒更新一次
                time.sleep(1)
            
            # 再次检查时间，如果已经到了5点，则退出循环
            now = datetime.datetime.now()
            schedule_time = os.getenv('SCHEDULE_TIME', '05:00')
            hour, minute = map(int, schedule_time.split(':'))
            if now.hour == hour and now.minute == minute and 0 <= now.second < 10:
                print(f"已到达目标时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                return

def main():
    schedule_time = os.getenv('SCHEDULE_TIME', '05:00')
    print(f"定时程序已启动，等待每天{schedule_time}运行预约脚本...")
    try:
        while True:
            # 等待到指定时间
            wait_until_schedule_time()
            # 运行预约脚本
            run_reservation_script()
            # 等待下一个执行时间
            print(f"等待下一个{schedule_time}...")
    except KeyboardInterrupt:
        print("\n程序已手动停止")
    except Exception as e:
        print(f"程序发生错误: {e}")

if __name__ == "__main__":
    main()