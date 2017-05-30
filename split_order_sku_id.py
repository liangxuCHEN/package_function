# encoding=utf8
import sql
import logging
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings
import argparse
from datetime import timedelta
from datetime import datetime as dt

ORDER_STRUCT = ['Tid', 'BuyerNick', 'Created', 'Num', 'Status', 'OuterSkuId', 'CombineSubSkuId']
INDEX_ID = 0
INDEX_TID = 1
INDEX_NUM = 3
INDEX_OUTER_SKUID = 5
connection = engine = table_schema = None


def init_parser():
    parser = argparse.ArgumentParser(
        description='split out all the combine Sku code  in the orders')
    parser.add_argument(
        '-begin_date', '--b',  dest='begin_date', help='select the order after the date what you give ')
    parser.add_argument(
        '-db_table', '--t', dest='db_table', help='select the table where you want to save your data ')
    args = parser.parse_args()
    if args.begin_date is not None:
        try:
            args.begin_date = dt.strptime(args.begin_date, "%Y-%m-%d")
        except Exception as e:
            log.error(e)
            log.info('your begin date is not correct')
            exit(1)
    return args


def log_init(file_name):
    """
    logging.debug('This is debug message')
    logging.info('This is info message')
    logging.warning('This is warning message')
    """
    level = logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s [line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=file_name,
                        filemode='w')
    return logging


def init_connection(table_name):
    global connection, engine, table_schema
    engine = create_engine('mssql+pymssql://%s:%s@%s/%s' % (
        settings.HOST_253_USER,
        settings.HOST_PASSWORD,
        settings.HOST_253,
        settings.DB_Product
    ))
    connection = engine.connect()
    metadata = sqlalchemy.schema.MetaData(bind=engine, reflect=True)
    table_schema = sqlalchemy.Table(table_name, metadata, autoload=True)


def output_data_sql(list_write):

    # Open the session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Inser the dataframe into the database in one bulk
    # print(table_schema.insert())
    try:
        connection.execute(table_schema.insert(), list_write)
        session.commit()
    except Exception as e:
        print e
        for v in list_write:
            log.error(v['Tid'], v['Created'])

    session.close()


def input_combine_product_data():
    # 整理数据
    conn = sql.init_sql()
    sql_text = 'SELECT skuCode, subSkuCode, id from T_Kingdee_Combine'
    df = pd.io.sql.read_sql(sql_text, con=conn)
    return df


def find_product_combine_items(df_data, sku_code):
    res = df_data[df_data['skuCode'] == sku_code]
    return [res.iloc[i]['subSkuCode'] for i in range(0, len(res))]


def main_process(order_list):
    global input_rows
    log.info('There are %d orders' % len(order_list))
    for order in order_list:
        order_list = list(order)
        sub_skucodes = find_product_combine_items(df_combine_product, order[INDEX_OUTER_SKUID])
        for num in range(0, order[INDEX_NUM]):
            if len(sub_skucodes) > 0:
                for code in sub_skucodes:
                    order_list.append(code)
                    input_rows.append(dict((key, value) for key, value in zip(ORDER_STRUCT, order_list)))
                    order_list.pop()

            else:
                # 不是组合产品
                order_list.append(order[INDEX_OUTER_SKUID])
                input_rows.append(dict((key, value) for key, value in zip(ORDER_STRUCT, order_list)))
                order_list.pop()

        if len(input_rows) > 3000:
            # 导入到临时数据库
            output_data_sql(input_rows)
            input_rows = []
            log.info('output 3000 rows, pls wait.....')

if __name__ == '__main__':
    # combine product
    df_combine_product = input_combine_product_data()

    args = init_parser()
    end_day = dt.today()
    log = log_init('D:\python_script\spilt_order_sku%s.log' % end_day.strftime('%Y_%m_%d'))
    # db name :T_ERP_TaoBao_Order_CombineSubSku
    # 临时表
    # TODO: 填写表名参数
    if args.db_table and args.db_table != 'T_ERP_TaoBao_Order_CombineSubSku':
        tmp_table_name = args.db_table
        sql.init_order_temp_table(tmp_table_name)
    else:
        tmp_table_name = 'T_ERP_TaoBao_Order_CombineSubSku'

    # init output connection
    log.info('initiate the table class....')
    init_connection(tmp_table_name)

    input_rows = []
    # begin_day = None   dt.strptime('2017-03-01', '%Y-%m-%d')
    log.info('connect to the DB and get the data....')
    if args.begin_date:
        delta_days = (end_day-args.begin_date).days
        if delta_days <= 0:
            log.error('Begin day must be before today and programme is end now')
            # 有错误退出
            exit(1)
        else:
            for day in range(0, delta_days):
                res = sql.get_recent_order_data(
                    (end_day-timedelta(days=day+1)).strftime('%Y-%m-%d'),
                    (end_day-timedelta(days=day)).strftime('%Y-%m-%d'))
                main_process(res)
    else:
        res = sql.get_recent_order_data(
            (end_day - timedelta(days=1)).strftime('%Y-%m-%d'),
            end_day.strftime('%Y-%m-%d'))
        main_process(res)

    # 把剩下的全部导入到临时数据库
    if len(input_rows) > 0:
        output_data_sql(input_rows)
    # 更新到主库
    #sql.merge_order_table()

    log.info('Very done, Finish!')
