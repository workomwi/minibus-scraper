import pprint
from bs4 import BeautifulSoup
import requests
import json

BASE_URL = 'https://mogilevminsk.by'

MOGILEV_ID = 2
PARK_CITY_ID = 87


def get_trips(date: str, ):
    RELATIVE_URL = '/timetable/trips'
    data = {
        'date': date,
        'from_city': MOGILEV_ID
    }
    response = requests.post(f'{BASE_URL}{RELATIVE_URL}', data)
    if response.status_code != 200:
        print(f'ERROR. {response.status_code} status. {RELATIVE_URL}, data={data}')
        return
    
    data = json.loads(response.text)
    return data['data']['trips']


def find_suitable_trip(trips: list[dict], suitable_times: list[str]):
    for trip in trips.values():
        if trip['departure_time'][:2] not in suitable_times:
            continue
        if trip['free_seats'] < 1:
            continue

        print(f'Found suitable trip: {trip}; {trip["free_seats"]} free seats')
        return trip
    print('No suitable trips')

def book_trip(trip: object, date: str):
    RELATIVE_URL = '/timetable/reservation'
    data = {
        "firstname": "Владислав",
        "lastname": "",
        "middlename": "",
        "date": f'{date[-2:]}-{date[5:7]}-{date[0:4]}' # "dd-mm-yyyy",
        "departure_time": trip['departure_time'],
        "trip_id": trip['id'],
        "phone": "293659214",
        "seats": {"1":1},
        "weekday": 0,
        "route_id": trip['route_id'],
        "station": PARK_CITY_ID,
        "station_out": "",
        "description": "",
        "needsms": 0,
        "pay_method": None,
        "location_url":"https://mogilevminsk.by/"
    }
    requests

def main():
    date_of_interest = '2023-10-08'
    times = ['17', '18', '19', '20', '14']
    trips = get_trips(date_of_interest)
    suitable_trip = find_suitable_trip(trips, times)

if __name__ == '__main__':
    main()
