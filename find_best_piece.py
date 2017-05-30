# encoding=utf8
from datetime import datetime as dt
import sqlalchemy
from sqlalchemy.pool import NullPool
import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, and_, bindparam
import logging
import urllib2
from urllib import urlencode
import numpy as np
from package import PackerSolution

HOST = 'LS201510141838'
HOST_USER = 'bsdb'
HOST_PASSWORD = 'ls123123'
DB = 'BSPRODUCTCENTER'

TABLE = 'T_BOM_Best_Piece'
RUNNING_STATUS = 1
FINISH_STATUS = 2
ERROR_STATUS = 3

# TODO: 测试调高了，正式环境换成0.00001
MAX_VAR_RATE = 0.001   # 方差阈值
# 保存之前的五个结果，求方差
NUM_SAVE = 5

# TODO: 正式：http://192.168.3.187:8089/product_use_rate
BASE_URL = 'http://119.145.166.182:8090/'
URL_POST = 'http://192.168.1.11:8989/product_use_rate'


def log_init(file_name):
    """
    logging.debug('This is debug message')
    logging.info('This is info message')
    logging.warning('This is warning message')
    """
    level = logging.DEBUG
    logging.basicConfig(level=level,
                        format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=file_name,
                        filemode='a+')
    return logging


def init_connection():
    # 'mysql://uid:pwd@localhost/mydb?charset=utf8'
    engine = create_engine('mssql+pymssql://%s:%s@%s/?charset=utf8' % (
        HOST_USER,
        HOST_PASSWORD,
        HOST
    ), poolclass=NullPool)

    connection = engine.connect()
    metadata = sqlalchemy.schema.MetaData(bind=engine, reflect=True)
    table_schema = sqlalchemy.Table(TABLE, metadata, autoload=True)
    return engine, connection, table_schema


def update_data(data):
    # init output connection
    log.info('Saving the result into DB.......')
    _, connection, table_schema = init_connection()
    sql_text = table_schema.update().where(
        table_schema.columns.id == bindparam('row_id')).values(Status=bindparam('status'), Result=bindparam('result'))
    try:
        connection.execute(sql_text, data)
    except Exception as e:
        log.error('error reason', e)
    finally:
        connection.close()


def get_data():
    # init output connection
    log.info('initiate the table class....')
    engine, connection, table_schema = init_connection()
    # 创建Session:
    Session = sessionmaker(bind=engine)
    session = Session()
    # 获取任务
    res = session.query(table_schema).filter(table_schema.columns.Status == 0).all()
    if len(res) == 0:
        log.info('without work to do, exit now.')
        exit(1)
    # 更新为运行中状态
    sql_text = table_schema.update().where(
        table_schema.columns.id == bindparam('row_id')).values(Status=bindparam('status'))
    content = list()
    for input_data in res:
        content.append({
            'row_id': input_data.id,
            'status': RUNNING_STATUS
        })
    connection.execute(sql_text, content)
    # 断开连接
    session.close()
    connection.close()
    return res


def find_best_piece(shape_data, bin_data):

    rate_res = list()
    num_pic = 1
    best_pic = 1
    best_rate = 0
    best_rates = {}

    while True:
        # 创建分析对象
        packer = PackerSolution(
            shape_data,
            bin_data,
            border=5,
            num_pic=num_pic
        )
        if packer.is_valid():
            # 选择几种经常用的算法
            res = packer.find_solution(algo_list=[0, 4, 40, 8, 20, 44, 24])
            # 平均使用率
            total_rate = 0
            for data in res:
                total_rate += data['rate']
            tmp_avg_rate = total_rate / len(res)

            # 记录最大值
            if best_rate < tmp_avg_rate:
                best_rate = tmp_avg_rate
                best_pic = num_pic
                for data in res:
                    best_rates[data['bin_key']] = data['rate']

            if num_pic > NUM_SAVE:
                rate_res.append(tmp_avg_rate)
                np_arr = np.array(rate_res[-1 * NUM_SAVE:])
                var_rate = np_arr.var()
                if var_rate < MAX_VAR_RATE:
                    # 少于阈值返回最佳值
                    return False, {'piece': best_pic, 'rates': best_rates}
            else:
                rate_res.append(tmp_avg_rate)

        else:
            return True, {'info': packer.error_info()}

        num_pic += 1


def http_post(num_piece, shape_data, bin_data):
    url = URL_POST
    # 整理input data
    s_data, b_data = multi_piece(result['piece'], shape_data, bin_data)

    values = {
        'project_comment': '最优利用率推荐生产数量=%d' % num_piece,
        'border': 5,
        'shape_data': s_data,
        'bin_data': b_data
    }
    data = urlencode(values)
    req = urllib2.Request(url, data)       # 生成页面请求的完整数据
    response_url = None
    response = None
    try:
        response = urllib2.urlopen(req)       # 发送页面请求
        response_url = response.read()
    except urllib2.URLError as e:
        code = None
        reason = None
        if hasattr(e, 'code'):
            log.error('there is error in http post,error code:%d' % e.code)
            code = e.code
        if hasattr(e, 'reason'):
            log.error('there is error in http post,error reason:%s' % e.reason)
            reason = e.reason
        # 如果出错发送邮件通知
    finally:
        if response_url:
            response.close()

    return response_url


def multi_piece(num_piece, shape_data, bin_data):
    shape_data = shape_data.encode('utf-8')
    bin_data = bin_data.encode('utf-8')
    shape_data = json.loads(shape_data)
    for shape in shape_data:
        shape['Amount'] = shape['Amount'] * num_piece
    shape_data = json.dumps(shape_data)
    return shape_data, bin_data

if __name__ == '__main__':
    end_day = dt.today()
    log = log_init('find_best_piece%s.log' % end_day.strftime('%Y_%m_%d'))
    rows = get_data()
    log.info('connect to the DB and get the data, there are %d works today' % len(rows))
    # 结果保存,批量更新
    content = list()
    for input_data in rows:
        # TODO: try 中途出错，返回状态0， 发送邮件，记录信息
        error, result = find_best_piece(input_data.ShapeData, input_data.BinData)
        if error:
            content.append({
                'row_id': input_data.id,
                'status': ERROR_STATUS,
                'result': result['info'],
            })
            log.error('work id=%d has error in input data ' % input_data.id)
        else:
            log.info('finish work id=%d and begin to draw the solution' % input_data.id)
            # 访问API
            http_response = http_post(result['piece'], input_data.ShapeData, input_data.BinData)
            rate_list = list()
            for bin_info in json.loads(input_data.BinData):
                if bin_info['SkuCode'] in result['rates'].keys():
                    bin_info['rate'] = result['rates'][bin_info['SkuCode']]
                    rate_list.append(bin_info)

            result['rates'.encode('utf-8')] = rate_list
            result['url'] = BASE_URL + http_response[1:-1]
            content.append({
                'row_id': input_data.id,
                'status': FINISH_STATUS,
                'result': json.dumps(result, ensure_ascii=False),
            })

    update_data(content)
    log.info('-------------------All works has done----------------------------')
