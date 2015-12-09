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


var TorResource = function(resource){
	this.value = {};
	this.valueIsArray = false;
	this.setResource(resource);
	this.idAttribute = "id";
}

TorResource.prototype.setResource = function(resource){
	this.resource = resource;
	for(var key in resource){
		if(key != "get" && key != "query"){
			console.log(key);
			this[key] = function(fnc){
				return function(args){
					return fnc.apply(resource, arguments);
				};
			}(resource[key]);
		}
	}
}

TorResource.prototype.query = function(args){
	this.value = this.resource.query.apply(this.resource, arguments);
	this.valueIsArray = true;
	return this.value;
}

TorResource.prototype.get = function(args){
	this.value = this.resource.get.apply(this.resource, arguments);
	this.valueIsArray = false;
	return this.value;
}

function updateObject(src, dst){
	for (var key in src) {
		if (src.hasOwnProperty(key) && !(key.charAt(0) === '$' && key.charAt(1) === '$')) {
			dst[key] = src[key];
		}
	}
}

TorResource.prototype.update = function(src){
	var dest = null;
	if(this.valueIsArray){
		for (var i = this.value.length - 1; i >= 0; i--) {
			if(this.value[i][this.idAttribute] == src[this.idAttribute]) {
				dest = this.value[i];
			}
		};
		if(dest === null){
			dest = {}
			this.value.push(dest);
		}
	}else{
		if(src[this.idAttribute] == this.value[this.idAttribute]){
			dest = this.value;
		}
	}
	if(dest !== null){
		updateObject(src, dest);
	}
}


torstatServices
	.factory('$TorResource', ['$resource', 'baseURL', '$rootScope',
		function($resource, baseURL, $rootScope){
			return function(ressourceName){
				var res = new TorResource(
					$resource(
						baseURL + ressourceName + '/:id', 
						{},
						{
							query: {method:'GET', params:{id:''}, isArray:true}
						}
					)
				);
				// Register broadcast listener
				$rootScope.$on(ressourceName, function(bc, evt){
					res.update(evt[ressourceName])
				});
				return res;
			};
		}]
	)
	.factory('Circuits', ['$TorResource', function($TorResource) {
		return $TorResource('circuit');
	}])
	.factory('Stream', ['$TorResource', function($TorResource) {
	    return $TorResource('stream');
	}])
	.factory('OnionooRouter', ['$resource', 'onionooURL', function($resource, onionooURL){
		return $resource(onionooURL + "details?lookup=:routerId", {}, {});
	}])
	.factory('Router', ['$resource', '$TorResource', function($TorResource){
		return $TorResource($resource);
	}])
	.factory('ReverseDNS', ['$resource', 'baseURL', function($resource, baseURL) {
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