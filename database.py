from datetime import datetime, timedelta
from pytz import timezone
import pymysql, os

# Set Jakarta as Default Timezone because Heroku detect US timezone.
def get_weekday(index):
  tz = timezone('Asia/Jakarta')
  weekday = datetime.now(tz) + timedelta(days=index)
  weekday = weekday.weekday()
  return weekday

def init():
  return pymysql.connect(
    host=os.environ.get('DATABASE_HOST', None),
    user=os.environ.get('DATABASE_USER', None),
    password=os.environ.get('DATABASE_PASSWORD', None),
    db=os.environ.get('DATABASE_DB', None),
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

def get_schedule(KELAS, index):
  connection = init()
  cursor = connection.cursor()
  TABLE = 'schedule_tf' + KELAS.lower()
  WEEK_DAY = get_weekday(index)
  print(WEEK_DAY)
  sql = """SELECT * from {}.{} WHERE week_day = {};""".format(os.environ.get('DATABASE_DB', None), TABLE, WEEK_DAY)
  cursor.execute(sql)
  rows = cursor.fetchall()
  return rows
	
def today_schedule(KELAS):
  rows = get_schedule(KELAS, index=0)
  return rows

def tomorrow_schedule(KELAS):
  rows = get_schedule(KELAS, index=1)
  return rows