from dataclasses import dataclass

@dataclass
class Trip:
    id: str
    route: str
    route_id: int
    transport: str
    price: str
    currency: str
    weekday: int
    departure_time: str
    seats: int
    free_seats: int
    show_free_seats: bool
    all_seats: int
    date: str
    datetime: str
    active: bool
    trip_key: int
