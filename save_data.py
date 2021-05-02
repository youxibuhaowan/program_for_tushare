"""
Time:2021/4/30 13:45
Author:中庸猿
奋斗不止，赚钱不停    
"""

"""
本模块包括：1.将所有从post接口获取的数据进行再次接口化，为程序内部提供数据接口。
          2.还包括所有的常用变量和sql语句
          3.基础配置
"""

from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
import time
from function_save_data import get_mysql, save_mysql
import requests

number = 0
token = 'c43d43d2f232eba8a6c58928cb248be964fb271fa3ab48d2b9a60d40'
# token = 'f281dbc422d80e2350e94b1878bd3b86971de985641877fc42ccd836'
url = 'http://api.waditu.com'
todaytime = datetime.now().strftime('%Y%m%d')


# 创建所有语句表
create_tb_daily = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_daily`  (
  `ts_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `trade_date` date NOT NULL,
  `open` decimal(10, 5) NOT NULL,
  `close` decimal(10, 5) NOT NULL,
  `high` decimal(10, 5) NOT NULL,
  `low` decimal(10, 5) NOT NULL,
  `change` decimal(10, 5) NOT NULL,
  `pct_chg` decimal(10, 5) NOT NULL,
  `vol` decimal(20, 5) NOT NULL,
  `amount` decimal(20, 5) NOT NULL,
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE,
  INDEX `ts_code_and_trade_date`(`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2437769 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_daily_basic = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_daily_basic`  (
  `ts_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `trade_date` date NOT NULL,
  `close` decimal(10, 5) NULL DEFAULT NULL,
  `volume_ratio` decimal(10, 5) NULL DEFAULT NULL,
  `pe` decimal(10, 5) NULL DEFAULT NULL,
  `pb` decimal(10, 5) NULL DEFAULT NULL,
  `total_share` decimal(20, 5) NULL DEFAULT NULL,
  `total_mv` decimal(20, 5) NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15271 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_index_basic = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_index_basic`  (
  `ts_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `market` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `publisher` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `category` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `base_date` date NULL DEFAULT NULL,
  `base_point` decimal(20, 5) NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_index_daily = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_index_daily`  (
  `ts_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `market` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `publisher` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `category` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `base_date` date NULL DEFAULT NULL,
  `base_point` decimal(20, 5) NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_index_dailybasic = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_index_dailybasic`  (
  `ts_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `trade_date` date NOT NULL,
  `total_mv` decimal(10, 5) NULL DEFAULT NULL,
  `float_mv` decimal(10, 5) NULL DEFAULT NULL,
  `total_share` decimal(10, 5) NULL DEFAULT NULL,
  `float_share` decimal(10, 5) NULL DEFAULT NULL,
  `free_share` decimal(10, 5) NULL DEFAULT NULL,
  `turnover_rate` decimal(10, 5) NULL DEFAULT NULL,
  `turnover_rate_f` decimal(20, 5) NULL DEFAULT NULL,
  `pe` decimal(20, 5) NULL DEFAULT NULL,
  `pe_ttm` decimal(20, 5) NULL DEFAULT NULL,
  `pb` decimal(20, 5) NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_stock_base = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_stock_base`  (
  `ts_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'ts代码',
  `symbol` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '代码',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '股票名称',
  `area` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '地域',
  `industry` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '领域',
  PRIMARY KEY (`ts_code`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4176 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_ths_daily = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_ths_daily`  (
  `ts_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `trade_date` date NOT NULL,
  `close` decimal(21, 5) NULL DEFAULT NULL,
  `open` decimal(21, 5) NULL DEFAULT NULL,
  `high` decimal(21, 5) NULL DEFAULT NULL,
  `low` decimal(21, 5) NULL DEFAULT NULL,
  `change` decimal(21, 5) NULL DEFAULT NULL,
  `vol` decimal(21, 5) NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`, `trade_date`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
"""

create_tb_ths_index = """
CREATE TABLE IF NOT EXISTS `tushare_for_ali`.`tb_ths_index`  (
  `ts_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `count` decimal(10, 5) NULL DEFAULT NULL,
  `exchange` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `list_date` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`ts_code`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;
"""

save_mysql(create_tb_daily)
save_mysql(create_tb_daily_basic)
save_mysql(create_tb_index_basic)
save_mysql(create_tb_index_daily)
save_mysql(create_tb_index_dailybasic)
save_mysql(create_tb_stock_base)
save_mysql(create_tb_ths_daily)
save_mysql(create_tb_ths_index)










# 股票列表
stock_basic_api = "stock_basic"
stock_basic_fields = "ts_code, symbol, name, area, industry"
stock_basic = {
    "exchange": "",
    "list_status": "L"
}

# 股票日线行情、周线、月线
daily_api = "daily"
daily_fields = "ts_code, trade_date, open, high, low, close, change, pct_chg, vol, amount"
daily = {
    "ts_code": "",
    "start_date": "19990101",
    "end_date": datetime.now().strftime('%Y%m%d')
}

# 每日指标
daily_basic_api = "daily_basic"
daily_basic_fields = "ts_code, trade_date, close, volume_ratio, pe, pb, total_share, total_mv"
daily_basic = {
    "ts_code": "",
    "start_date": "19990101",
    "end_date": datetime.now().strftime('%Y%m%d')
}

# 同花顺概念板块列表
ths_index_api = "ths_index"
ths_index_fields = "ts_code, name, count, exchange, list_date, type"
ths_index = {
    # 'ts_code': "",
    "exchange": "A",
    "type": "N"
}

# 同花顺概念板块行情
ths_daily_api = "ths_daily"
ths_daily_fields = "ts_code, trade_date, open, close, high, low, change, vol"
ths_daily = {
    'ts_code': "",
    "start_date": "19990101",
    "end_date": datetime.now().strftime('%Y%m%d')
}

# 上证基本信息
index_basic_api = "index_basic"
index_basic_fields = "ts_code, name, market, publisher, category, base_date, base_point"
index_basic = {
    'market': "SSE"
}

# 上证指数日线行情、周线、月线
index_daily_api = "index_daily"
index_daily_fields = "ts_code, trade_date, open, close, high, low, change, pct_chg, vol, amount"
index_daily = {
    'ts_code': "",
    "start_date": "19990101",
    "end_date": datetime.now().strftime('%Y%m%d')
}

# 大盘指数每日指标
index_dailybasic_api = "index_dailybasic"
index_dailybasic_fields = "ts_code, trade_date, total_mv, turnover_rate, pe, pb"
index_dailybasic = {
    "start_date": "20040101",
    "end_date": datetime.now().strftime('%Y%m%d')
}


def get_data_from_tushare(apiname, params, fields):
    # with ThreadPoolExecutor(max_workers=100) as pool:
    json = {
        "api_name": apiname,
        "token": token,
        "params": params,
        "fields": fields
    }
    response = requests.post(url=url, json=json)
    print(response.json())
    list_result = []
    result = response.json()['data']['items']
    for i in result:
        list_result.append(tuple(i))
    # print(response.json()['data']['items'])
    # return response.json()['data']['items']
    print(list_result)
    return list_result


sql_select_all_tscode = "select `ts_code` from tb_stock_base order by symbol asc;"
sql_select_all_ths_tscode = "select `ts_code` from `tb_ths_index`;"
sql_select_all_index_basic = "select `ts_code` from `tb_index_basic`;"

# 股票列表 ts_code, symbol, name, area, industry
sql_save_stock_basic = "insert into `tb_stock_base`(`ts_code`, `symbol`, `name`, `area`, `industry`) values(%s" + ", %s" * 4 + ");"

# 日线行情 ts_code, trade_date, open, close, high, low, change, pct_chg, vol, amount
sql_save_daily = "insert into `tb_daily`(`ts_code`, `trade_date`, `open`, `close`, `high`, `low`, `change`, `pct_chg`, `vol`, `amount`) values(%s" + ", %s" * 9 + ");"

# 每日指标 ts_code, trade_date, close, volume_ratio, pe, pb, total_share, total_mv
sql_save_daily_basic = "insert into `tb_daily_basic`(ts_code, trade_date, `close`, volume_ratio, pe, pb, total_share, total_mv) values(%s" + ", %s" * 7 + ");"

# 同花顺概念板块列表 ts_code, name, count, exchange, list_date, type
sql_save_ths_index = "insert into `tb_ths_index`(`ts_code`, `name`, `count`, `exchange`, `list_date`, `type`) values(%s" + ", %s" * 5 + ");"

# 同花顺概念板块行情 ts_code, trade_date, open, close, high, low,  change,  vol
sql_save_ths_daily = "insert into `tb_ths_daily`(`ts_code`, `trade_date`, `open`, `close`, `high`, `low`,  `change`, `vol`) values(%s" + ", %s" * 7 + ");"

# 上证指数基本信息 ts_code, name, market, publisher, category, base_date, base_point
sql_save_index_basic = "insert into `tb_index_basic`(`ts_code`, `name`,  `market`, `publisher`, `category`, `base_date`, `base_point`) values(%s" + ", %s" * 6 + ");"

# 上证指数日线行情 ts_code, trade_date, close, open, high, low, change, pct_chg,vol, amount
sql_save_index_daily = "insert into `tb_index_daily`(`ts_code`, trade_date, `close`, `open`, `high`, `low`, `change`, `pct_chg`,vol, amount) values(%s" + ", %s" * 9 + ");"

# 大盘指数每日指标 ts_code, trade_date, total_mv, float_mv, total_share, float_share, turnover_rate, turnover_rate_f, pe, pe_ttm, pb
sql_save_index_dailybasic = "insert into `tb_index_dailybasic`(ts_code, trade_date, total_mv, float_mv, total_share, float_share, turnover_rate, turnover_rate_f, pe, pe_ttm, pb) values(%s" + ", %s" * 10 + ");"


def perfect_request(apiname, params, fields, sql):
    if apiname == 'ths_daily':
        count = 0
        list1 = get_mysql(sql_select_all_ths_tscode)
        for i in list1:
            count += 1
            if count == 5:
                time.sleep(60)
                count = 0
            params['ts_code'] = i[0]
            print(params)
            save_mysql(sql, get_data_from_tushare(apiname, params, fields))
    elif apiname == 'index_daily_api':
        list1 = get_mysql(sql_select_all_index_basic)
        for i in list1:
            params['ts_code'] = i[0]
            print(params)
            save_mysql(sql, get_data_from_tushare(apiname, params, fields))
    elif 'ts_code' in params:
        # 如果需要股票的代码，从数据库中查找
        list1 = get_mysql(sql_select_all_tscode)
        for i in list1:
            print(i)
            params['ts_code'] = i[0]
            print(params)
            save_mysql(sql, get_data_from_tushare(apiname, params, fields))
    else:
        save_mysql(sql, get_data_from_tushare(apiname, params, fields))


# 股票列表
# stock_basic_data = perfect_request(stock_basic_api, stock_basic, stock_basic_fields, sql_save_stock_basic)
# 还没有经过savedata

# 在读取完股票列表之后，才进行下一步，因为下一步中需要股票列表的参数
# time.sleep(10)
# # 日线行情
# daily_data = perfect_request(daily_api, daily, daily_fields, sql_save_daily)
#
# # 每日指标
# dailybasic_data = perfect_request(daily_basic_api, daily_basic, daily_basic_fields, sql_save_daily_basic)
#
# # 同花顺概念板块列表
# ths_index_data = perfect_request(ths_index_api, ths_index, ths_index_fields, sql_save_ths_index)
#
# # 同花顺概念板块行情
# ths_daily_data = perfect_request(ths_daily_api, ths_daily, ths_daily_fields, sql_save_ths_daily)
#
# # 上证指数基本信息
# 这个有问题
# index_basic_data = perfect_request(index_basic_api, index_basic, index_basic_fields, sql_save_index_basic)

# # 上证指数日线行情
# index_daily_data = perfect_request(index_daily_api, index_daily, index_daily_fields, sql_save_index_daily)
#
# # 大盘指数每日指标
# index_dailybasic_data = perfect_request(index_dailybasic_api, index_dailybasic, index_dailybasic_fields,
#                                         sql_save_index_dailybasic)
