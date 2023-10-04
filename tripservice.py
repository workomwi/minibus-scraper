import abc
from abc import ABC, abstractmethod
import json
from datetime import date
from typing import Self
import requests

from Trip import Trip
from telegram import send_tg_message
from const import CITY_ID, STATION_ID

class TripService(ABC):
  can_book = True

  def __init__(self, domain_url: str, booked_trip: Trip = None) -> None:
    self.domain_url = domain_url

  @abstractmethod
  def get_trips(self, target_date: date):
    relative_url = '/timetable/reservation/'
    body = {
      'date': date.strftime('%Y-%m-%d'),
      'from_city': CITY_ID
    }
    response = requests.post(f'{self.domain_url}{relative_url}', data=body)
    if response.status_code != 200:
      send_tg_message(f'ERROR. {response.status_code} status. {relative_url}, body={body}')
      return []
    
    result = response.json()
    trips = result['data']['trips']
    res = [Trip(**trip_json) for trip_json in trips]
    return res


  @abstractmethod
  def book_trip(self, trip: Trip, firstname: str, phone: str):
    relative_url = '/timetable/reservation/'
    body = {
      'firstname': firstname,
      'lastname': '',
      'middlename': '',
      'date': trip['date'],
      'departure_time': trip['departure_time'],
      'trip_id': trip['id'],
      'phone': phone,
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

    response = requests.post(f'{domain_url}{relative_url}', json=body)
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


class MinskExpressService(TripService):
  pass


class AvtoslavaService(TripService):
  pass