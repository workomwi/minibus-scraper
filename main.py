import os
from datetime import date, datetime, time

from ratelimit import limits, sleep_and_retry

from keepalive import keep_alive
from telegram import tg_log, tg_notify
from trip import Trip
from tripservice import TripService

# local only
from dotenv import load_dotenv
load_dotenv()

MINSK_EXPRESS_STATION_ID = int(os.getenv('MINSK_EXPRESS_STATION_ID'))
AVTOSLAVA_STATION_ID = int(os.getenv('AVTOSLAVA_STATION_ID'))

minsk_express_service = TripService('https://mogilevminsk.by', MINSK_EXPRESS_STATION_ID)

booked_trip = Trip(**{"id": "000000","route": "Могилев -> Минск","route_id": 2,"transport": "VOLKSWAGEN CRAFTER (бел)","price": "25.00","currency": "руб.","weekday": 0,"departure_time": "18:05","seats": 0,"free_seats": 0,"show_free_seats": True,"all_seats": 15,"date": "08-10-2023","datetime": "2023-10-08T18:05:00","active": True,"trip_key": 178761})
avto_slava_service = TripService('https://avto-slava.by', AVTOSLAVA_STATION_ID, booked_trip)


def check_trips(service: TripService, target_date: date, t_start: time, t_end: time, t_target: time):
  trips = service.get_trips(target_date)
  suitable_trip = service.find_suitable(trips, t_start, t_end, t_target)
  print(f'Suitable({service.domain_url})  {datetime.now().strftime("%H:%M:%S")}: {suitable_trip}')
  message = f'Suitable: {suitable_trip}'
  if suitable_trip is None:
    return
  tg_log(message)
  tg_notify(message)
  service.book_trip(suitable_trip, 'Владислав')


last_lookup = datetime.now()
PERIOD = 30
count = 0

@sleep_and_retry
@limits(1, PERIOD)
def lookup_trips(target_date: date, t_start: time, t_end: time, t_target: time):
  global last_lookup
  current_datetime = datetime.now()
  seconds_passed = (current_datetime - last_lookup).total_seconds()
  global count
  count += 1
  if count == 20:
    count = 0
    tg_log('alive')
  if seconds_passed > PERIOD * 2:
    tg_notify(f'Downtime: {seconds_passed}')
  last_lookup = current_datetime
  
  check_trips(minsk_express_service, target_date, t_start, t_end, t_target)
  check_trips(avto_slava_service, target_date, t_start, t_end, t_target)


def main():
  # target_date = date(2023, 10, 8)
  # t_start = time(17, 30)
  # t_end = time(19, 30)
  # t_target = time(18, 0)
  while minsk_express_service.can_book or avto_slava_service.can_book:
    lookup_trips(target_date, t_start, t_end, t_target)


keep_alive()
main()
