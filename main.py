import requests
from ratelimit import limits, sleep_and_retry
import datetime
import sys

BASE_URL = 'https://mogilevminsk.by'
CITY_ID = 2
STATION_ID = 87
PHONE1 = '293659214'
PHONE2 = '293713829'
TG_TOKEN = '6460109876:AAGzuhAJRvGpKNvQrJhvPrnbrpuMDykgedw'
TG_CHAT_ID = '875208331'

booked_trip = {
  # 'time': None
  'time': datetime.time(18, 0)
}
can_book = True

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
  "Accept": "application/json, text/plain, */*",
  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br",
  "Content-Type": "application/json;charset=utf-8"
}



def get_trips(date: datetime.date):
  RELATIVE_URL = '/timetable/trips'
  body = {
    'date': date.strftime('%Y-%m-%d'),
    'from_city': CITY_ID
  }
  response = requests.post(f'{BASE_URL}{RELATIVE_URL}', data=body)
  if response.status_code != 200:
    print(f'ERROR. {response.status_code} status. {RELATIVE_URL}, body={body}')
    return []
  
  # result = json.loads(response.text)
  result = response.json()
  return result['data']['trips']

def book_trip(trip: object, phone=PHONE1):
  RELATIVE_URL = '/timetable/reservation/'
  body = {
    'firstname': 'Владислав',
    'lastname': '',
    'middlename': '',
    'date': trip['date'],
    'departure_time': trip['departure_time'],
    'trip_id': trip['id'],
    'phone': PHONE1,
    'seats': {'1':1},
    'weekday': trip['weekday'],
    'route_id': trip['route_id'],
    'station': STATION_ID,
    'station_out': '',
    'description': '',
    'needsms': 0,
    'pay_method': None,
    'location_url':'https://mogilevminsk.by/'
  }

  response = requests.post(f'{BASE_URL}{RELATIVE_URL}', json=body)
  result = response.json()
  data = result.get('data', None)
  if data is None:
    send_tg_message('something fucked up, data is None from book trip')
    sys.exit()

  success = data.get('every_was_fine', None)
  if success is None:
    send_tg_message(f'error: {data}')
    global can_book
    if phone == PHONE2:
      can_book = False
      send_tg_message('cant book on phone2, end')
    book_trip(trip, PHONE2)
    return

  if phone == PHONE2:
    send_tg_message('cant book; booked on phone2')

  booked_trip['time'] = get_trip_departure_time(trip)

  send_tg_message(f'booked trip(phone: {phone}) on {trip["departure_time"]}')


def send_tg_message(message: str):
  requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&text={message}")
  


def find_closest_trip(trips: list[dict], target_time: datetime.time):
  if len(trips) == 0:
    return None
  
  return min(trips, key=lambda t: abs(
    datetime.datetime.combine(datetime.date.today(), datetime.time(int(t['departure_time'][0:2]),int(t['departure_time'][3:5]))) - datetime.datetime.combine(datetime.date.today(), target_time)))
  
def find_closest_time(time1: datetime.time, time2: datetime.time, target_time: datetime.time):
  today = datetime.date.today()
  return min([time1, time2], key=lambda t: abs(datetime.datetime.combine(today, t) - datetime.datetime.combine(today, target_time)))

def get_trip_departure_time(trip: dict) -> datetime.time:
  return datetime.time(
    int(trip['departure_time'][0:2]),
    int(trip['departure_time'][3:5])
  )

# latest trip before time_end and after booked trip/time_start
def find_suitable_trip(trips: list[dict], time_start: datetime.time, time_end: datetime.time, target_time: datetime.time):
  suitable_trips = []
  for trip in trips.values():
    departure_time = get_trip_departure_time(trip)
    if departure_time > time_end or departure_time < time_start:
      continue
    if trip['free_seats'] < 1:
      continue
    if not trip['active']:
      continue
    # if booked_trip['datetime'] is not None and booked_trip['datetime'] >= departure_time:
    #     continue

    suitable_trips.append(trip)
  closest_suitable = find_closest_trip(suitable_trips, target_time)
  if booked_trip['time'] is None:
    return closest_suitable

  closest_time = find_closest_time(get_trip_departure_time(closest_suitable), booked_trip['time'], target_time)
  if closest_time == booked_trip['time']:
    return None
  return closest_suitable

@sleep_and_retry
@limits(1, 300)
def lookup_trip(date_of_interest, time_start, time_end, target_time):
  trips = get_trips(date_of_interest)
  suitable_trip = find_suitable_trip(trips, time_start, time_end, target_time)
  if suitable_trip is None:
    return
  message = f'''Найдена поездка {suitable_trip['date']} {suitable_trip['departure_time']}
{suitable_trip['price']} р.
{suitable_trip['free_seats']} свободных мест
{BASE_URL}'''
  send_tg_message(message)
  book_trip(suitable_trip)



def main():
  date_of_interest = datetime.date(2023, 10, 11)
  time_start = datetime.time(16, 30)
  time_end = datetime.time(19, 30)
  target_time = datetime.time(18, 00)

  # date_of_interest = datetime.date(2023, 10, 10)
  # time_start = datetime.time(16, 30)
  # time_end = datetime.time(19, 30)
  # target_time = datetime.time(17, 31)

  while can_book:
    lookup_trip(date_of_interest, time_start, time_end, target_time)
  

if __name__ == '__main__':
  main()
