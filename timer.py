import time
import datetime
import os
import subprocess
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def run_reservation_script():
    """运行预约脚本"""
    print("开始运行预约脚本...")
    try:
        # 使用subprocess运行auto_reservation.py，避免异步循环冲突
        script_path = os.path.join(os.path.dirname(__file__), "auto_reservation.py")
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5分钟超时
        
        if result.returncode == 0:
            print("预约脚本执行完成")
            if result.stdout:
                print("输出:", result.stdout)
        else:
            print(f"预约脚本执行失败，返回码: {result.returncode}")
            if result.stderr:
                print("错误信息:", result.stderr)
                
    except subprocess.TimeoutExpired:
        print("预约脚本执行超时")
    except Exception as e:
        print(f"预约脚本执行失败: {e}")

def parse_schedule_times():
    """解析环境变量中的多个时间点"""
    schedule_times_str = os.getenv('SCHEDULE_TIMES', '05:00')
    times = []
    for time_str in schedule_times_str.split(','):
        time_str = time_str.strip()
        try:
            hour, minute = map(int, time_str.split(':'))
            times.append((hour, minute))
        except ValueError:
            print(f"无效的时间格式: {time_str}，跳过")
    return times

def get_next_schedule_time(schedule_times):
    """获取下一个最近的执行时间"""
    now = datetime.datetime.now()
    today_times = []
    tomorrow_times = []
    
    for hour, minute in schedule_times:
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target_time > now:
            today_times.append(target_time)
        else:
            tomorrow_times.append(target_time + datetime.timedelta(days=1))
    
    # 如果今天还有时间点，返回最近的一个
    if today_times:
        return min(today_times)
    # 否则返回明天最早的时间点
    elif tomorrow_times:
        return min(tomorrow_times)
    else:
        # 如果没有有效时间点，默认明天05:00
        return now.replace(hour=5, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

def wait_until_next_schedule_time(schedule_times):
    """等待到下一个指定时间"""
    while True:
        now = datetime.datetime.now()
        target_time = get_next_schedule_time(schedule_times)
        
        # 计算需要等待的秒数
        wait_seconds = (target_time - now).total_seconds()
        
        # 显示等待信息
        wait_hours = int(wait_seconds // 3600)
        wait_minutes = int((wait_seconds % 3600) // 60)
        wait_seconds_remainder = int(wait_seconds % 60)
        
        print(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"下一个执行时间: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
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
            
            # 再次检查时间，如果已经到了时间点，则退出循环
            now = datetime.datetime.now()
            if abs((target_time - now).total_seconds()) < 10:
                print(f"已到达目标时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                return target_time

def main():
    # 解析多个时间点
    schedule_times = parse_schedule_times()
    if not schedule_times:
        print("没有有效的时间配置，程序退出")
        return
    
    # 显示配置的时间点
    times_str = ', '.join([f"{h:02d}:{m:02d}" for h, m in schedule_times])
    print(f"定时程序已启动，配置的执行时间: {times_str}")
    print("注意：请在环境变量SCHEDULE_TIMES中配置多个时间，用逗号分隔，例如: 05:00,07:00,09:00")
    
    try:
        while True:
            # 等待到下一个指定时间
            executed_time = wait_until_next_schedule_time(schedule_times)
            
            # 运行预约脚本两次
            print("开始第一次预约尝试...")
            run_reservation_script()
            print("等待5秒后进行第二次预约尝试...")
            time.sleep(5)
            print("开始第二次预约尝试...")
            run_reservation_script()
            
            # 显示完成信息
            executed_time_str = executed_time.strftime('%H:%M')
            print(f"时间点 {executed_time_str} 的预约尝试完成，等待下一个执行时间...")
            
    except KeyboardInterrupt:
        print("\n程序已手动停止")
    except Exception as e:
        print(f"程序发生错误: {e}")

if __name__ == "__main__":
    main()