from datetime import date, datetime, time
import requests

from trip import Trip
from telegram import send_tg_message
from const import CITY_ID, PHONE1, PHONE2

class TripService:
  booked_trip: Trip = None

  def __init__(self, domain_url: str, station_id: int) -> None:
    self.domain_url = domain_url
    self.can_book = True
    self.station_id = station_id


  def get_departure_datetime(self, trip: Trip) -> datetime:
    return datetime.fromisoformat(trip.datetime)
    
  def get_departure_time(self, trip: Trip) -> time:
    return time(
      int(trip.departure_time[0:2]),
      int(trip.departure_time[3:5])
    )
  
  def find_closest(self, trips: list[Trip], t_target: time) -> Trip:
    if len(trips) == 0:
      return None
    
    today = date.today()
    return min(trips, key=lambda t: abs(datetime.combine(today, self.get_departure_time(t)) - datetime.combine(today, t_target)))
    

  def find_suitable(self, trips: list[Trip], t_start: time, t_end: time, t_target: time):
    suitable_trips = []
    for trip in trips:
      departure_time = self.get_departure_time(trip)
      if departure_time > t_end or departure_time < t_start:
        continue
      if trip.free_seats < 1:
        continue
      if not trip.active:
        continue
      # if booked_trip['datetime'] is not None and booked_trip['datetime'] >= departure_time:
      #     continue

      suitable_trips.append(trip)
    closest_suitable = self.find_closest(suitable_trips, t_target)
    if self.booked_trip is None:
      return closest_suitable

    closest = self.find_closest([self.booked_trip, closest_suitable], t_target)
    if closest.departure_time == self.booked_trip.departure_time:
      return None
    return closest

  
  def send_log(self, relative_url: str, log: str):
    message = f'{self.domain_url}{relative_url}\n{log}'
    print(message)
    send_tg_message(message)


  def get_trips(self, target_date: date):
    relative_url = '/timetable/trips/'
    body = {
      'date': target_date.strftime('%Y-%m-%d'),
      'from_city': CITY_ID
    }
    response = requests.post(f'{self.domain_url}{relative_url}', data=body)
    if response.status_code != 200:
      send_tg_message(f'ERROR. {response.status_code} status. {relative_url}, body={body}')
      return []
    
    result = response.json()
    trips = result['data']['trips']
    trips = [Trip(**trip_json) for trip_json in trips.values()]
    trips = [trip for trip in trips if self.get_departure_datetime(trip).date() == target_date]
    return trips
  
    
  def book_trip(self, trip: Trip, firstname: str, phone: str = PHONE1):
    relative_url = '/timetable/reservation/'
    body = {
      'firstname': firstname,
      'lastname': '',
      'middlename': '',
      'date': trip.date,
      'departure_time': trip.departure_time,
      'trip_id': trip.id,
      'phone': phone,
      'seats': {'1':1},
      'weekday': trip.weekday,
      'route_id': trip.route_id,
      'station': self.station_id,
      'station_out': '',
      'description': '',
      'needsms': 0,
      'pay_method': None,
      'location_url': f'{self.domain_url}/'
    }

    if not self.can_book:
      message = 'Error: Was not able to order trip. Field can_book is False'
      self.send_log(relative_url, message)
      return None

    response = requests.post(f'{self.domain_url}{relative_url}', json=body)
    result = response.json()
    data = result.get('data', None)
    
    if data is None:
      message = 'Error: data is None'
      self.send_log(relative_url, message)
      return None
    
    if 'no_free_seats' in data:
      message = 'Error: no free seats'
      self.send_log(message)
      return None


    success = data.get('every_was_fine', None)
    if success is None:
      message = f'Error: {data}'
      self.send_log(relative_url, message)
      
      if phone == PHONE2 and 'trip_max_seat_limit' in data:
        self.can_book = False
        message = 'Error: Hit trip limit on 2nd phone. Service disabled'
        self.send_log(relative_url, message)
        return None
      
      if 'trip_max_seat_limit' in data:
        return self.book_trip(trip, firstname, PHONE2)
      
      return None

    success_message = f'''Ordered trip on {phone}
{trip.date} {trip.departure_time}
{trip.route}
{trip.transport}'''
    self.send_log(relative_url, success_message)
    self.booked_trip = trip

    if phone == PHONE2:
      self.can_book = False
      message = 'Ordered both. Service disabled'
      self.send_log(relative_url, message)

    return trip
