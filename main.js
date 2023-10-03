transformRequest = function (data, headersGetter) {
    var formData = new FormData();
    angular.forEach(data, function (value, key) {
        formData.append(key, value);
    });

    var headers = headersGetter();
    delete headers['Content-Type'];

    return formData;
}


getTrips = function() {
    var data = {};
    if (trips_load_in_progress) return;

    trips_load_in_progress = true;

    data['date'] = $filter('date')(selectedDate, "yyyy-MM-dd");
    if (from_city) {
        data.from_city = from_city.city.id;
    } else {
        dest_city = null;
    }

    // console.log(from_city);

    if (dest_city) {
        data.dest_city = dest_city.id;
    }
    // $http.post('/timetable/trips/', data).
    $http({
            method: 'POST',
            url: '/timetable/trips/',
            //headers: { "X-CSRFToken": 1},
            data: data,
            transformRequest: transformRequest
    })
    .success(function(data, status, headers, config) {
        trips = data.data.trips;
    })
    .error(function(data, status, headers, config) {
        console.log('Error getting data: ' + data);
        trips_load_in_progress = false;
    })
    .then(function(){
        trips_load_in_progress = false;
        // console.log(data);
    });
    return trips;
}

