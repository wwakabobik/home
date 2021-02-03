from db.db import get_db, close_db

data_update_period = 5


def store_weather_data(data):
    connection = get_db()
    sql = f'''INSERT INTO weather_data(ts,meas_type,temperature,humidity,pressure,dew_point) VALUES({data});'''
    cur = connection.cursor()
    cur.execute(sql)
    connection.commit()
    close_db()
    return cur.lastrowid


def store_wind_data(data):
    connection = get_db()
    sql = f'''INSERT INTO wind_data(ts,unix_ts,
                                    avg_rps,max_rps,min_rps,
                                    avg_ms,max_ms,min_ms,
                                    avg_kmh,max_kmh,min_knh,
                                    avg_knots,max_knots,min_knots,
                                    heading,heading_abbr) VALUES({data});'''
    cur = connection.cursor()
    cur.execute(sql)
    connection.commit()
    close_db()
    return cur.lastrowid


def store_power_data(data):
    connection = get_db()
    sql = f'''INSERT INTO wind_data(ts,unix_ts,avg_voltage,avg_current,avg_power,avg_consumption) VALUES({data});'''
    cur = connection.cursor()
    cur.execute(sql)
    connection.commit()
    close_db()
    return cur.lastrowid


def get_one_measurement(table, param, offset, meas_type):
    connection = get_db()
    criteria = f'WHERE meas_type = \'{meas_type}\'' if meas_type else ''
    sql = f''' SELECT {param} FROM {table} {criteria} ORDER BY RowId DESC LIMIT 2 OFFSET {offset}; '''
    cur = connection.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    if row:
        retval = dict(zip(row.keys(), row))[param]
    else:
        retval = 0
    return retval


def get_last_measurement_pack(table, offset, meas_type=None):
    connection = get_db()
    criteria = f'WHERE meas_type = \'{meas_type}\'' if meas_type else ''
    sql = f''' SELECT * FROM {table} {criteria} ORDER BY RowId DESC LIMIT 2 OFFSET {offset}; '''
    cur = connection.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    if row:
        retval = dict(zip(row.keys(), row))
    else:
        retval = 0
    return retval


def get_one_last_average_measurement(table, param, period, meas_type=None):
    connection = get_db()
    criteria = f'WHERE meas_type = \'{meas_type}\'' if meas_type else ''
    number = str(2 + (period / data_update_period))
    sql = f''' avg({param}) from (SELECT {param} FROM {table} {criteria} ORDER BY RowId DESC  LIMIT {number}); '''
    cur = connection.cursor()
    cur.execute(sql)
    row = cur.fetchone()
    if cur.rowcount > 0:
        retval = dict(zip(row.keys(), row))[param]
    else:
        retval = 0
    return retval


def get_last_series_measurement(table, param, period, meas_type=None):
    connection = get_db()
    criteria = f'WHERE meas_type = \'{meas_type}\'' if meas_type else ''
    number = int(period / data_update_period)
    sql = f''' SELECT ts, {param} FROM {table} {criteria} ORDER BY RowId DESC  LIMIT {number}; '''
    cur = connection.cursor()
    cur.execute(sql)

    columns = [column[0] for column in cur.description]
    results = []
    for row in cur.fetchall():
        results.append(dict(zip(columns, row)))
    x = []
    y = []
    for result in results:
        x.append(result['ts'])
        y.append(result[param])
    return x, y
