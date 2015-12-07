'use strict';

/* Services */

var torstatServices = angular.module('torstatServices', ['ngResource', 'ngWebSocket']);

torstatServices.factory('baseURL', function() {
  		return "//" + window.location.host + "/api/";
	}
);

torstatServices.factory('Circuits', ['$resource', 'baseURL',
  function($resource, baseURL) {
    return $resource(baseURL + 'circuit/:circuitId', {}, {
      query: {method:'GET', params:{circuitId:''}, isArray:true}
    });
  }]
);



function LogService(){
	this.logs = [];
}

LogService.prototype.log = function(message) {
	this.logs.push({
		time: new Date(),
		message: message
	})
}

var GlobalLogService = null;
torstatServices.factory('LogService', function(){
	if(GlobalLogService === null){
		GlobalLogService = new LogService();
	}
	console.log("logger", GlobalLogService);
	return GlobalLogService;
});


torstatServices.factory('TorstatWebsocket', ['$websocket', 'baseURL',
	function($websocket, baseURL) {
		return $websocket('ws://' + baseURL +  "websocket/");
	}
]);


// torstatServices.factory('pollService', ['$http', '$q',
// 	function ($http, $q) {
//         return {
//             getData: function (url, param) {
//                 var defer = $q.defer();
//                 $http.get(restbase + route + '/' + param).success(function (data) {
//                         defer.resolve(data);
//                     }
//                 ).error(function () {
//                         defer.reject('An error has occurred :(');
//                     }
//                 );
//                 return defer.promise;
//             },
//             postData: function (id, data) {
//                 var defer = $q.defer();
//                 data = $.param(data);
//                 $http.post('http://localhost:8000/api/poll/' + id + '/option', data,
//                     {'headers': {
//                         'Content-Type': 'application/x-www-form-urlencoded,charset=UTF-8'
//                     }}).
//                     success(function (data) {
//                         defer.resolve(data);
//                     }
//                 ).error(function () {
//                         defer.reject('Cannot post data to the server :(');
//                     }
//                 );
//                 return defer.promise;
//             }
//         };
//     }
// ]);