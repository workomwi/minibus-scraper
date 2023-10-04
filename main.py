from datetime import date, time
from ratelimit import sleep_and_retry, limits

from telegram import send_tg_message
from tripservice import TripService
from const import MINSK_EXPRESS_STATION_ID, AVTOSLAVA_STATION_ID

minsk_express_service = TripService('https://mogilevminsk.by', MINSK_EXPRESS_STATION_ID)
avto_slava_service = TripService('https://avto-slava.by', AVTOSLAVA_STATION_ID)


def check_trips(service: TripService, target_date: date, t_start: time, t_end: time, t_target: time):
  trips = service.get_trips(target_date)
  suitable_trip = service.find_suitable(trips, t_start, t_end, t_target)
  print(f'Suitable: {suitable_trip}')
  if suitable_trip is None:
    return
  service.book_trip(suitable_trip, 'Владислав')


count = 0

@sleep_and_retry
@limits(1, 60)
def lookup_trips(target_date: date, t_start: time, t_end: time, t_target: time):
  global count
  count += 1
  if count == 10:
    count = 0
    send_tg_message('active')
  # check_trips(minsk_express_service, target_date, t_start, t_end, t_target)
  check_trips(avto_slava_service, target_date, t_start, t_end, t_target)


def main():
  target_date = date(2023, 10, 9)
  t_start = time(16, 30)
  t_end = time(19, 30)
  t_target = time(17, 31)
  while minsk_express_service.can_book or avto_slava_service.can_book:
    lookup_trips(target_date, t_start, t_end, t_target)


main()
