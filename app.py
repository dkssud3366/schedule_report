from flask import Flask
import requests,time
from datetime import datetime,timedelta
from model import *
import schedule


app = Flask(__name__)


url = f"https://api.telegram.org/bot{os.getenv('bot_token')}/sendMessage"


def od_status(emp_orders,od,emp_name,status):

    if status in ['입고완료']:
       od_type = '입고건'
    elif status in ['출고완료', '현장완료', '미입금'] :
       od_type = '출고건'
    elif status == '입고취소':
       od_type = '입고취소건'
    elif status == '환불':
       od_type = '환불건'
    elif status == '예약':
       od_type = '예약건'
    elif status == '메이드완료':
       od_type = '메이드건'
    elif status == '외주입고':
       od_type = '외주입고건'
    else:
       od_type = '기타'
    emp_orders[emp_name][od_type].append({
            'buyer_name': od['buyer_name'],
            'hp': od['hp'],
            'count': 0,
            'sales': od['sales'],
        })
    count = int(len(emp_orders[emp_name][od_type]) - 1)
    emp_orders[emp_name][od_type][count]['count'] += 1

def send_telegram_message(chat_id):
    weekday = datetime.now().weekday()
    weekday_match = {
        0: '월요일',
        1: '화요일',
        2: '수요일',
        3: '목요일',
        4: '금요일',
        5: '토요일',
        6: '일요일'
    }
    weekd = weekday_match.get(weekday,'Null')
    today = datetime.now().strftime('%m-%d').split('-')
    sql_today = datetime.now().date()
    line = 'ㅡ' * 12
    emp_orders = {}
    sql = f'''
    select 
    e.FullName,
    o.*
    from `order` o 
    inner join employees e on o.fk_emp_id = e.id
    where o.start_date = '{sql_today}' or o.end_date = '{sql_today}'
    '''
    result = query_db(sql)

    for od in result:
        emp_name = od['FullName']
        if emp_name not in emp_orders:
           emp_orders[emp_name] = {
               'total_count': 0,
               '입고건': [],
               '출고건': [],
               '입고취소건': [],
               '환불건': [],
               '예약건': [],
               '메이드건': [],
               '외주입고건': [],
               '기타': [],
           }
        emp_orders[emp_name]['total_count'] += 1 if od['start_date'] == sql_today else 0
        od_status(emp_orders, od, emp_name, od['status'])
        
    for key,order in emp_orders.items():     
        total_count = order['total_count'] 
        #입고건 与其他状态的for循环的方法一样
        count = len(order.get('입고건'))
        buyer_name_ = [var['buyer_name'] for var in order.get('입고건', []) + order.get('메이드건', [])]
        hp_ = list([var['hp'][-4:] for var in order.get('입고건', []) + order.get('메이드건', [])])
        sales_ = list([var['sales'] for var in order['입고건'] + order['메이드건']])
        # 출고건
        finish_count = 0
        f_buyer_name_ = []
        f_hp_ = []
        f_sales_ = []
        # 입고취소건
        cancel_count = 0
        c_buyer_name_ = []
        c_hp_ = []
        # 수리불가
        cancel_count = 0
        c_buyer_name_ = []
        c_hp_ = []
        # 환불건
        _count = 0
        _buyer_name_ = []
        _hp_ = []
        _sales_ = []
        # 예약
        reservation_count = 0
        reservation_buyer_name_ = []
        reservation_hp_ = []              
        # 외주입고건
        subcontractor_count = 0
        subcontractor_buyer_name_ = []
        subcontractor_hp_ = []            
        # for od in order.get('입고건', []) + order.get('메이드건', []):
        #     # count += od.get('count', 0)
        #     buyer_name_.append(od['buyer_name'])
        #     hp_.append(od['hp'][-4:])
        #     sales_.append(od['sales'])

        for od in order['출고건']:
            finish_count += 1
            f_buyer_name_.append(od['buyer_name'])
            f_hp_.append(od['hp'][-4:])
            f_sales_.append(od['sales'])      

        for od in order['입고취소건']:
            cancel_count += 1
            c_buyer_name_.append(od['buyer_name'])
            c_hp_.append(od['hp'][-4:])  

        for od in order['환불건']:
            _count += 1
            _buyer_name_.append(od['buyer_name'])
            _hp_.append(od['hp'][-4:])
            _sales_.append(od['sales'])   

        for od in order['예약건']:
            reservation_count += 1
            reservation_buyer_name_.append(od['buyer_name'])
            reservation_hp_.append(od['hp'][-4:])            
        for od in order['외주입고건']:
            subcontractor_count += 1
            subcontractor_buyer_name_.append(od['buyer_name'])
            subcontractor_hp_.append(od['hp'][-4:])        
        text = """ 
        {today[0]}월 {today[1]}일 {weekd} - [{key}]\
        \n{line}\
        \n금일 접수건 : {total_count}건\
        \n{line}\
        \n금일 입고건 : {count} 건\
        \n - {buyers}\
        \n{line}\
        \n금일 출고건 : {finish_count}건\
        \n - {f_buyers}\
        \n{line}\
        \n입고 후(메이드)취소건 : {cancel_count}건\
        \n - {c_buyers}\
        \n{line}\
        \n수리불가(환불)건 : {_count}건\
        \n - {_buyers}\
        \n{line}\
        \n방문대기(예약)건 : {reservation_count}건\
        \n - {reservation_buyers} {majoy}\
        \n{line}\
        """.format(today=today, weekd=weekd, key=key, line=line, total_count=total_count, count=count,
                   finish_count=finish_count , cancel_count=cancel_count, _count=_count,reservation_count=reservation_count,
                   majoy='택배진행' if key == '마재원' else "",
                   buyers='\n - '.join(f"{a.ljust(2)} {b} {'{:,}'.format(int(c)) if c > 0 else ''}"  for a, b, c in zip(buyer_name_, hp_, sales_)),
                   f_buyers='\n - '.join(f"{a.ljust(2)} {b} {'{:,}'.format(int(c)).rjust(5)}" for a, b,c in zip(f_buyer_name_, f_hp_,f_sales_)),
                   c_buyers='\n - '.join(f"{a.ljust(2)} {b}" for a, b in zip(c_buyer_name_, c_hp_)),
                   _buyers='\n - '.join(f"{a.ljust(2)} {b} {'{:,}'.format(int(c)).rjust(5)}" for a, b,c in zip(_buyer_name_, _hp_,_sales_)),
                   reservation_buyers='\n - '.join(f"{a.ljust(2)} {b}" for a, b in zip(reservation_buyer_name_, reservation_hp_)),
                   )
        data = {
            'chat_id': chat_id,
            'text': text
        }
        requests.post(url, data=data) 
    ######## 금일토탈 ##############
    # 총출고금액
    total_sales = sum(var['sales'] for var in result if var['status'] in ['출고완료','현장완료','미입금'])
    # 총출고건 수
    total_finish = len([var for var in result if var['status'] in ['출고완료','현장완료','미입금']])
    # 총현완 금액
    total_live = sum(var['sales'] for var in result if var['status'] in ['현장완료'])
    # 총현완건 수
    total_live_finish = len([var for var in result if var['status'] in ['현장완료']])
    # 총 메이드금액
    total_made = sum(var['sales'] for var in result if var['status'] in ['메이드완료'])
    # 총 메이드건 수
    total_made_ct = sum(1 for var in result if var['status'] in ['메이드완료'])
    # 수리불가 환불금
    _total = sum(var['sales'] for var in result if var['status'] in ['환불'])
    # 총콜수
    total_od = sum(1 for var in result if var['start_date'] == sql_today)
    # 총입고수
    total_ = len([var for var in result if var['status'] == '입고완료'])
    # 총외주입고수
    total_subcontractor = len([var for var in result if var['status'] == '외주입고'])
    # 총 취소건수 (수리불가 포함)
    cancel = len([var for var in result if var['status'] in ['입고취소','환불']])
    # 예약건 수
    total_reservation =  sum(1 for var in result if var['status'] in ['예약']) 
    # 취소
    total_cancel =  sum(1 for var in result if var['status'] in ['방문전취소','현장취소']) 
    text = f'''
    {today[0]}월 {today[1]}일 {weekd} [TOTAL] 
    \n 접수 {total_od}건 방취 : {total_cancel}건\
    \n 입고 {total_}건 예약 {total_reservation}건\
    \n 외주입고 {total_subcontractor}건 \
    \n {line}\
    \n 출고 {total_finish}건 금액 +{'{:,}'.format(total_sales)}\
    \n 현완 {total_live_finish}건 금액 +{'{:,}'.format(total_live)}\
    \n {line}\
    \n 메이드 {total_made_ct}건 금액 : {'{:,}'.format(total_made)}\
    \n {line}\
    \n 입고취소 {cancel}건 환불금 : {'{:,}'.format(_total)}\
    \n {line}\
    '''
    if any(val > 0 for val in [total_od, total_, total_subcontractor, total_finish, total_live_finish]):
       data = {
            'chat_id': chat_id,
            'text': text
            }
       requests.post(url, data=data) 


daily_report = os.getenv('DAILY_REPORT')
schedule.every().day.at('21:00').do(send_telegram_message,daily_report)

while True:
   schedule.run_pending()
   now = datetime.now()
   time.sleep(300)


