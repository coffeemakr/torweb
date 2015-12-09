'use strict';

/* Services */

var torstatServices = angular.module('torstatServices', ['ngResource', 'ngWebSocket']);

torstatServices
	.factory('baseURL', function() {
  		return "//" + window.location.host + "/api/";
	})
	.factory('onionooURL', function(){
		return "https://onionoo.torproject.org/";
	})
;

torstatServices
	.factory('Circuits', ['$resource', 'baseURL',
	  function($resource, baseURL) {
	    return $resource(baseURL + 'circuit/:circuitId', {}, {
	      query: {method:'GET', params:{circuitId:''}, isArray:true}
	    });
	  }]
	)
	.factory('Stream', ['$resource', 'baseURL',
	  function($resource, baseURL) {
	    return $resource(baseURL + 'stream/:id', {}, {
	      query: {method:'GET', params:{id:''}, isArray:true}
	    });
	  }]
	)
	.factory('OnionooRouter', ['$resource', 'onionooURL', function($resource, onionooURL){
		return $resource(onionooURL + "details?lookup=:routerId", {}, {});
	}])
	.factory('Router', ['$resource', 'baseURL',
	  function($resource, baseURL) {
	    return $resource(baseURL + 'router/:routerId', {}, {
	      //query: {method:'GET', params:{routerId:''}, isArray:true}
	    });
	  }]
	)
	.factory('ReverseDNS', ['$resource', 'baseURL',
	  function($resource, baseURL) {
	    return $resource(baseURL + 'dns/reverse/:ip', {}, {});
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