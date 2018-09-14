import pymysql
import datetime
import os

def init():
  return pymysql.connect(
    host= os.environ('DATABASE_HOST'),
    user=os.environ('DATABASE_USER'),
    password=os.environ('DATABASE_PASSWORD'),
    db=os.environ('DATABASE_NAME'),
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
    table = 'schedule_tf' + KELAS.lower()
    weekday = datetime.datetime.today().weekday()
    sql = """SELECT * from {}.{} WHERE week_day = {};""".format(db, table, weekday)
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows
  except pymysql.Error as e:
    print(e)
    return None