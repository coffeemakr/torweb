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