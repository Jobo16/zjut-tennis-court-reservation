from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import csv
from datetime import datetime

app = Flask(__name__)

# 时间段配置
TIME_SLOTS = [
    "08:00-09:00", "09:00-10:00", "10:00-11:00", "11:00-12:00",
    "12:00-13:00", "13:00-14:00", "14:00-15:00", "15:00-16:00",
    "16:00-17:00", "17:00-18:00", "18:00-19:00", "19:00-20:00",
    "20:00-21:00", "21:00-22:00"
]

# 场地配置（1-1到11-2，共22个场地）
COURTS = []
for i in range(1, 12):
    COURTS.append(f"{i}-1")
    COURTS.append(f"{i}-2")

def load_existing_config():
    """读取现有配置文件"""
    config = {
        'username': '',
        'password': '',
        'companion_name': '',
        'companion_phone': '',
        'selected_slots': []
    }
    
    # 读取.env文件
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key == 'LOGIN_USERNAME':
                            config['username'] = value
                        elif key == 'PASSWORD':
                            config['password'] = value
                        elif key == 'COMPANION_NAME':
                            config['companion_name'] = value
                        elif key == 'COMPANION_PHONE':
                            config['companion_phone'] = value
        except Exception as e:
            print(f"读取.env文件失败: {e}")
    
    # 读取CSV文件
    if os.path.exists('reservation.csv'):
        try:
            with open('reservation.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                if len(rows) > 1:  # 有数据行
                    for i, row in enumerate(rows[1:]):  # 跳过表头
                        if len(row) > 1:
                            for j, value in enumerate(row[1:]):  # 跳过时间段列
                                if value == '1':
                                    config['selected_slots'].append(f"{i}_{j}")
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
    
    return config

@app.route('/')
def index():
    config = load_existing_config()
    return render_template('config.html', time_slots=TIME_SLOTS, courts=COURTS, config=config)

@app.route('/save_config', methods=['POST'])
def save_config():
    try:
        # 获取用户信息
        username = request.form.get('username')
        password = request.form.get('password')
        companion_name = request.form.get('companion_name')
        companion_phone = request.form.get('companion_phone')
        
        # 获取选中的时间段
        selected_slots = request.form.getlist('time_slots')
        
        # 保存.env文件
        env_content = f"""LOGIN_USERNAME={username}
PASSWORD={password}
COMPANION_NAME={companion_name}
COMPANION_PHONE={companion_phone}
TIME=7:00"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # 生成CSV文件
        csv_data = [['时间段'] + COURTS]
        
        for i, time_slot in enumerate(TIME_SLOTS):
            row = [time_slot]
            for j, court in enumerate(COURTS):
                slot_id = f"{i}_{j}"
                if slot_id in selected_slots:
                    row.append('1')
                else:
                    row.append('0')
            csv_data.append(row)
        
        with open('reservation.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
        
        return jsonify({'success': True, 'message': '配置保存成功！'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败：{str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)