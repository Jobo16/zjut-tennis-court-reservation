import csv
import os
import schedule
import time
from datetime import datetime
from auto_reservation import run_reservation

class ReservationScheduler:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.auto_reservation_path = os.path.join(os.path.dirname(csv_file_path), 'auto_reservation.py')
    
    def read_csv_file(self):
        """读取CSV文件并解析用户意愿"""
        reservations = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                rows = list(reader)
                
                if len(rows) < 2:
                    print("CSV文件格式错误：至少需要标题行和数据行")
                    return reservations
                
                # 获取列标题（第一行）
                headers = rows[0]
                
                # 遍历每一列（跳过第一列时间标题）
                for col_index in range(1, len(headers)):
                    col_name = headers[col_index]
                    rows_with_1 = []
                    
                    # 检查这一列的每一行（跳过标题行）
                    for row_index in range(1, len(rows)):
                        if col_index < len(rows[row_index]) and rows[row_index][col_index] == '1':
                            rows_with_1.append(row_index)  # CSV中的行号，需要转换为网页中的行号
                    
                    # 如果这一列有'1'，添加到预约列表
                    if rows_with_1:
                        reservations.append({
                            'col': col_index,  # 列号（从1开始）
                            'rows': tuple(rows_with_1),  # 行号元组
                            'col_name': col_name
                        })
                        print(f"发现预约需求：{col_name}列（第{col_index}列），行号：{rows_with_1}")
                
                return reservations
                
        except FileNotFoundError:
            print(f"错误：找不到文件 {self.csv_file_path}")
            return []
        except Exception as e:
            print(f"读取CSV文件时出错：{e}")
            return []
    
    def run_auto_reservation(self, col, rows):
        """运行auto_reservation程序"""
        try:
            print(f"\n开始预约第{col}列，行号：{rows}")
            print("="*50)
            
            # 直接调用预约函数
            success = run_reservation(col, rows)
            
            print(f"预约结果：{'成功' if success else '失败'}")
            print("="*50)
            
            return success
            
        except Exception as e:
            print(f"运行预约程序时出错：{e}")
            return False
    

    
    def run_all_reservations(self):
        """运行所有预约任务"""
        print("开始解析预约意愿表...")
        reservations = self.read_csv_file()
        
        if not reservations:
            print("没有找到需要预约的时间段")
            return
        
        print(f"\n共找到 {len(reservations)} 个预约任务")
        
        success_count = 0
        for i, reservation in enumerate(reservations, 1):
            print(f"\n执行第 {i}/{len(reservations)} 个预约任务")
            print(f"列名：{reservation['col_name']}")
            
            success = self.run_auto_reservation(
                reservation['col'], 
                reservation['rows']
            )
            
            if success:
                success_count += 1
            
            # 如果不是最后一个任务，等待一段时间
            if i < len(reservations):
                print("等待5秒后执行下一个预约任务...")
                import time
                time.sleep(1)
        
        print(f"\n所有预约任务完成！")
        print(f"成功：{success_count}/{len(reservations)}")

def scheduled_reservation():
    """定时执行的预约任务"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行定时预约任务")
    csv_file = r"c:\Users\admin\Desktop\2project\自动预约程序\reservation.csv"
    scheduler = ReservationScheduler(csv_file)
    scheduler.run_all_reservations()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 定时预约任务完成\n")

if __name__ == "__main__":
    # 设置定时任务：每天7:00:05执行
    schedule.every().day.at("07:00:05").do(scheduled_reservation)
    
    print("自动预约程序已启动，等待定时执行...")
    print("执行时间：每天 07:00:05")
    print("按 Ctrl+C 退出程序")
    print("-" * 50)
    
    # 检查是否有即将执行的任务
    next_run = schedule.next_run()
    if next_run:
        print(f"下次执行时间：{next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n程序已退出")