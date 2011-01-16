var map;
var marker;
var current_position = {
    lat: undefined,
    lng: undefined
}

function checkin_initialize() {
    mapOptions = {
        googleBarOptions : {
            resultList: $('checkin-search-results'),
            onGenerateMarkerHtmlCallback: renderSearchPoint
        }
    }
    map = new google.maps.Map2($('checkin-map'), mapOptions);
    map.setCenter(new google.maps.LatLng(37.4419, -122.1419), 13);
    map.enableGoogleBar();
    
    fu.notify.fire("Attempting to determine your location");
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            fu.notify.fire("We found you!");
            sensorPoint(position.coords.latitude, position.coords.longitude);
        }, function(error) {
            fu.notify.fire("Location can't be determined");
        });
    } else if (window.google && google.gears && typeof(google.gears.factory.create) != 'undefined') {
        var geo = google.gears.factory.create('beta.geolocation');
        geo.getCurrentPosition(function(position) {
            fu.notify.fire("We found you!");
            sensorPoint(position.latitude, position.longitude);
        }, null);
    } else {
        fu.notify.fire("Location can't be determined");
    }
};

function sensorPoint(lat, lng) {
    var mapOptions = {
        draggable: true
    }
    
    var center = new google.maps.LatLng(lat, lng)
    marker = new GMarker(center, mapOptions);
    GEvent.addListener(marker, "dragend", function(marker) {
        current_position.lat = marker.lat();
        current_position.lng = marker.lng();
    });
    map.setCenter(center, 13);
    map.addOverlay(marker);
    current_position.lat = lat;
    current_position.lng = lng;
};

function renderSearchPoint(point, html, result) {
    html = $(html);
    current_position.lat = point.getLatLng().lat();
    current_position.lng = point.getLatLng().lng();
    $('place').value = html.getElement('.gels-title-link').get('text');
    
    html.getElement('.gels-title').set('html', '<strong>'+html.getElement('.gels-title-link').get('text')+'</strong>');
    html.getElement('.gels-directions').dispose();
    
    if(is_mobile) {
        html.getElement('.gels-phone').dispose();
        html.getElements('.gels-addressline')[0].getAllNext().dispose();
    }
    return html;
};

function clear_messages() {
    $('service-messages').empty();
}

function submit_checkin() {
    params = {
        'place': $('place').value,
        'message': $('message').value,
        'lat': current_position.lat,
        'lng': current_position.lng
    }
    
    if(!params.place.length || !params.lat || !params.lng) {
        pageTracker._trackPageview("/post/argerror"); 
        fu.notify.fire("Please select a place on the map and give your spot a name", "error");
        return;
    }
    
    clear_messages();
    
    fu.notify.fire("Checking in...");
    pageTracker._trackPageview("/post"); 
    
    if (is_mobile) { // checkin with one HTTP request on mobile
        var req = new Request.JSON({
            method: 'get',
            url: '/post',
            data: params,
            onComplete: function(o) {
                if(typeof(o) == "undefined") {
                    fu.notify.fire("Something seems to have gone wrong, please try again", "error");
                } else {
                    fu.notify.fire("Success!");
                    messages = o['services'];
                    for (var i = 0; i < messages.length; i++) {
                        $('service-messages').grab(new Element('div', {'text':messages[i]['service']+" says: "+messages[i]['message']}));
                    }
                    $('service-messages').setStyle('background-color', '#fdffbe');
                    $('service-messages').set('tween', {duration: 'long'});
                    $('service-messages').tween('background-color', '#fff');
                }
            }
        }).send();
    } else { // Thread checkins on the desktop
        for (var i = 0; i < active_services.length; i++) {
            var req = new Request.JSON({
                method: 'get',
                url: '/post/' + active_services[i],
                data: params,
                onComplete: function(o) {
                    if(typeof(o) == "undefined") {
                        fu.notify.fire("Something seems to have gone wrong, please try again", "error");
                    } else {
                        messages = o['services'];
                        for (var i = 0; i < messages.length; i++) {
                            message = new Element('div', {'text':messages[i]['service']+" says: "+messages[i]['message']})
                            $('service-messages').grab(message);
                            message.setStyle('background-color', '#fdffbe');
                            message.set('tween', {duration: 'long'});
                            message.tween('background-color', '#fff');
                        }
                    }
                }
            }).send();
        }
    }
}

window.addEvent('domready', function() {
    if($('checkin-map')) {
        google.load("maps", "2",{"other_params":"sensor=true", 'callback': function() {
            checkin_initialize();
        }});
        
        $('post-form').addEvent('submit', function(e) {
            e.stop();
            submit_checkin(); 
        });
    }
    
    if(!is_mobile) {
        $('service-adder').addEvent('mouseover', function() {
            $('service-adder-list').set('tween', {});
            $('service-adder-list').setStyle('display', 'block');
            $('service-adder-list').tween('height', '115px');
        }).addEvent('mouseout', function() {
            $('service-adder-list').set('tween', {
                'onComplete': function() {
                    $('service-adder-list').setStyle('display', 'none');
                }
            });
            $('service-adder-list').tween('height', '0');
        });
    }
    
    $$('.current-postings-service').addEvent('click', function(e) {
        e.stop();
        target = $(e.target);
        href = target.get('href');
        fu.notify.fire("Service has been removed");
        target.destroy();
        new Request.JSON({
            method: 'get',
            url: href,
            onComplete: function(o) {
                if(!$$('.current-postings-service').length) {
                    window.location.reload(true)
                }
            }
        }).send();
    });
});