from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3
from datetime import datetime, timedelta
import calendar
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
DATABASE = 'salon.db'

# 데이터베이스 연결 함수
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# 애플리케이션 종료 시 데이터베이스 연결 종료
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 데이터베이스 초기화 함수
def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_name TEXT NOT NULL,
                    client_phone TEXT NOT NULL,
                    date TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    service_type TEXT NOT NULL
                )
            ''')
            db.commit()

# 메인 페이지 - 날짜 선택
@app.route('/')
def index():
    today = datetime.now().date()
    # 일주일치 날짜 생성
    dates = []
    for i in range(7):  # 오늘부터 6일 후까지 (일주일)
        day = today + timedelta(days=i)
        # 일요일(6)은 제외
        if day.weekday() != 6:  # 0=월요일, 6=일요일
            dates.append(day)
    
    # 최근 예약 목록 가져오기
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE date >= ? 
        ORDER BY date, start_time 
        LIMIT 5
    ''', (today.strftime('%Y-%m-%d'),))
    recent_appointments = cursor.fetchall()
    
    return render_template('index.html', dates=dates, recent_appointments=recent_appointments)

# 예약 목록 페이지
@app.route('/appointments')
def list_appointments():
    db = get_db()
    cursor = db.cursor()
    
    # 오늘 이후의 모든 예약 가져오기
    today = datetime.now().date().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE date >= ? 
        ORDER BY date, start_time
    ''', (today,))
    appointments = cursor.fetchall()
    
    return render_template('appointment_list.html', appointments=appointments)

# 특정 날짜의 예약 가능 시간 확인
@app.route('/appointments/<date>')
def show_appointments(date):
    selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # 해당 날짜에 이미 예약된 시간 슬롯들 가져오기
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE date = ?
    ''', (date,))
    appointments = cursor.fetchall()
    
    # 09:00부터 21:00까지 30분 간격의 시간 슬롯 생성
    time_slots = []
    start = datetime.strptime('09:00', '%H:%M').time()
    end = datetime.strptime('21:00', '%H:%M').time()
    current = datetime.combine(datetime.today(), start)
    
    while current.time() <= end:
        time_slots.append(current.time())
        current = current + timedelta(minutes=30)
    
    # 예약된 시간 확인하여 사용 가능한 슬롯 결정
    available_slots = {}
    for slot in time_slots:
        # 컷은 1시간(2개 슬롯), 펌은 2시간(4개 슬롯) 필요
        cut_available = True
        perm_available = True
        
        # 해당 시간부터 필요한 시간 동안 다른 예약이 있는지 확인
        slot_datetime = datetime.combine(selected_date, slot)
        for appointment in appointments:
            appt_start = datetime.strptime(appointment['start_time'], '%H:%M').time()
            appt_end = datetime.strptime(appointment['end_time'], '%H:%M').time()
            
            appt_start_dt = datetime.combine(selected_date, appt_start)
            appt_end_dt = datetime.combine(selected_date, appt_end)
            
            # 컷 가능 여부 확인 (1시간)
            cut_end = slot_datetime + timedelta(hours=1)
            if not (cut_end <= appt_start_dt or slot_datetime >= appt_end_dt):
                cut_available = False
            
            # 펌 가능 여부 확인 (2시간)
            perm_end = slot_datetime + timedelta(hours=2)
            if not (perm_end <= appt_start_dt or slot_datetime >= appt_end_dt):
                perm_available = False
        
        # 21시 이후 종료되는 예약은 불가능
        last_slot = datetime.strptime('21:00', '%H:%M').time()
        if (slot_datetime + timedelta(hours=1)).time() > last_slot:
            cut_available = False
        if (slot_datetime + timedelta(hours=2)).time() > last_slot:
            perm_available = False
            
        available_slots[slot.strftime('%H:%M')] = {
            'cut': cut_available,
            'perm': perm_available
        }
    
    return render_template('appointments.html', 
                          date=selected_date, 
                          available_slots=available_slots,
                          day_name=calendar.day_name[selected_date.weekday()])

# 예약 처리
@app.route('/book', methods=['POST'])
def book_appointment():
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    service_type = request.form.get('service_type')
    
    if not all([client_name, client_phone, date_str, time_str, service_type]):
        flash('모든 정보를 입력해주세요.')
        return redirect(url_for('show_appointments', date=date_str))
    
    # 날짜와 시간 파싱
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    start_time = datetime.strptime(time_str, '%H:%M').time()
    
    # 서비스 타입에 따라 종료 시간 계산
    if service_type == 'cut':
        duration = timedelta(hours=1)
    else:  # perm
        duration = timedelta(hours=2)
    
    end_time = (datetime.combine(date, start_time) + duration).time()
    
    # 해당 시간에 이미 예약이 있는지 확인
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE date = ? AND (
            (start_time <= ? AND end_time > ?) OR
            (start_time < ? AND end_time >= ?) OR
            (start_time >= ? AND end_time <= ?)
        )
    ''', (
        date_str, 
        time_str, time_str, 
        end_time.strftime('%H:%M'), end_time.strftime('%H:%M'),
        time_str, end_time.strftime('%H:%M')
    ))
    overlapping = cursor.fetchone()
    
    if overlapping:
        flash('선택하신 시간은 이미 예약이 있습니다. 다른 시간을 선택해주세요.')
        return redirect(url_for('show_appointments', date=date_str))
    
    # 예약 생성
    cursor.execute('''
        INSERT INTO appointments (client_name, client_phone, date, start_time, end_time, service_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        client_name, 
        client_phone, 
        date_str, 
        time_str, 
        end_time.strftime('%H:%M'), 
        service_type
    ))
    db.commit()
    
    flash('예약이 성공적으로 완료되었습니다!')
    return redirect(url_for('index'))

# 예약 취소
@app.route('/cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    db = get_db()
    cursor = db.cursor()
    
    # 예약 정보 가져오기
    cursor.execute('SELECT * FROM appointments WHERE id = ?', (appointment_id,))
    appointment = cursor.fetchone()
    
    if not appointment:
        flash('존재하지 않는 예약입니다.')
        return redirect(url_for('list_appointments'))
    
    # 예약 삭제
    cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
    db.commit()
    
    flash('예약이 취소되었습니다.')
    return redirect(url_for('list_appointments'))

if __name__ == '__main__':
    init_db()  # 데이터베이스 초기화
    app.run(debug=True) 