import pymysql, os
import datetime

def init():
  return pymysql.connect(
    host=DATABASE_HOST,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    db=DATABASE_DB,
    cursorclass=pymysql.cursors.DictCursor)

def insert(sql):
  try:
    connection = init()
    with connection.cursor() as cursor:
      cursor.execute(sql)
    connection.commit()
    connection.close()
    return True
  except pymysql.Error as e:
    print(e)
    return False
	
def today_schedule(KELAS):
  try:
    connection = init()
    cursor = connection.cursor()
    TABLE = 'schedule_tf' + KELAS.lower()
    sql = """SELECT * from {}.{} WHERE week_day = {};""".format(DATABASE_DB, TABLE, WEEK_DAY)
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows
  except pymysql.Error as e:
    rows = "Kelas {} tidak ada.\nInput kelas: A, B atau C.".format(KELAS.upper())
    return rows
