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

/** @constructor */
function TorResource(resource){
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
	return this.value;
}

TorResource.prototype.get = function(args){
	this.value = this.resource.get.apply(this.resource, arguments);
	var thatValue = this.value;
	this.value.$promise.then(
		function(value){
			console.log(value);
		},
		function(error){
			thatValue["error"] = error;
		}
	);
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
	if(typeof this.value.length != 'undefined'){
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


/** @constructor */
function LogService(){
	this.logs = [];
}

LogService.prototype.log = function(message) {
	this.logs.push({
		time: new Date(),
		message: message
	})
}

/** @type{LogService} */
var GlobalLogService = null;

/** @constructor */
function MenuHandler(scope, config){
	this.scope = scope;
	this.clear();
	this.setNodes(config["nodes"])
}

MenuHandler.prototype.clear = function(){
	this.nodes = {}
	this.format_args = {}
	this.currentNode = null;
	this.breadcrumbs = [];
	this.appendSlashBeforeRelative = true;
	this.scope["breadcrumbs"] = this.breadcrumbs;
}


MenuHandler.prototype.setNodes = function(nodes){
	if(typeof nodes == 'undefined' || typeof nodes.length == 'undefined'){
		this.nodes = {};
	}else{
		for (var i = 0; i < nodes.length; i++) {
			var node = nodes[i];
			var parentName = "parent";
			if(node.hasOwnProperty(parentName)) {
				node[parentName] = this.nodes[node[parentName]];
				if(typeof node[parentName] == 'undefined'){
					console.log("invalid parent");
					continue;
				}
			}
			this.nodes[node["id"]] = node;
		};
	}
}

MenuHandler.prototype.setCurrent = function(id){
	if(!this.nodes.hasOwnProperty(id)){
		console.log("Invalid ID: ", id);
	}else{
		this.currentNode = this.nodes[id];
		this.update();
	}
}

MenuHandler.prototype.getBreadcrumbs = function(){
	return this.breadcrumbs;
}

function _formatString(value, args){
	if(!args) {
		return value;
	}
	for(var replaceName in this.format_args){
		var replaceVal = this.format_args[replaceName];
		console.log("Replace ", replaceName , " with ", replaceVal);
		nodeUrl = nodeUrl.replace(':' + replaceName, replaceVal);
		nodeName = nodeName.replace(':' + replaceName, replaceVal);
	}
}

MenuHandler.prototype.setArgs = function(args){
	this.format_args = args;
	this.update();
}

MenuHandler.prototype.update = function(){
	this.breadcrumbs.length = 0;
	var node = this.currentNode;
	var nodes = [];
	var url = '/';
	do{
		nodes.push(node);
		node = node["parent"];
	}while(node.hasOwnProperty("parent"));
	
	// notes are in reversed order so we begin at the end
	for (var i = nodes.length - 1; i >= 0; i--) {
		node = nodes[i];
		var nodeUrl = node["url"];
		var nodeName = node["name"];
		if(this.format_args){
			console.log("Replace args: ", this.format_args);
			for(var replaceName in this.format_args){
				var replaceVal = this.format_args[replaceName];
				console.log("Replace ", replaceName , " with ", replaceVal);
				nodeUrl = nodeUrl.replace(':' + replaceName, replaceVal);
				nodeName = nodeName.replace(':' + replaceName, replaceVal);
			}
		}
		if(node["isrelative"]){
			if(this.appendSlashBeforeRelative && url[url.length - 1] != '/' && nodeUrl[0] != '/'){
				console.log("appending / to ", url);
				url += '/'
			}
			url += nodeUrl;
		}else{
			url = nodeUrl;
		}
		this.breadcrumbs.push({
			name: nodeName,
			url: "#" + url
		});
	};
}

torstatServices
	.factory('$TorResource', ['$resource', 'baseURL', '$rootScope',
		function($resource, baseURL, $rootScope){
			return function(ressourceName){
				var res = new TorResource(
					$resource(
						baseURL + 'tor/:instanceId/' + ressourceName + '/:id', 
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
	.factory('MenuHandler', ['$rootScope', function($rootScope){
		var mh = new MenuHandler($rootScope, {
			"nodes": [
			{	'id': 'root',
				'name': "Torweb",
				"url": "/"
			},
			{	'id': 'instanceList',
				'parent': 'root',
				'name': "Instances",
				"url": "/"
			},
			{	'id': 'instanceDetails',
				'parent': 'instanceList',
				'name': "Instance :instanceId",
				"url": "/:instanceId/"
			},
			{	"id": 'streamList',
				"parent": 'instanceDetails',
				"name": "Streams",
				"url": "/streams",
				"isrelative": true
			},
			{	"id": 'circuitList',
				"parent": 'instanceDetails',
				"name": "Circuits",
				"url": "/circuits",
				"isrelative": true
			},
			{	"id": 'streamDetails',
				"parent": 'instanceDetails',
				"name": "Stream :streamId",
				"url": "/stream/:streamId/",
				"isrelative": true
			},
			{	"id": 'circuitDetails',
				"parent": 'instanceDetails',
				"name": "Circuit :streamId",
				"url": "/Circuit/:streamId/",
				"isrelative": true
			},
		]});
		return mh;
	}])
	.factory('Circuits', ['$TorResource', function($TorResource) {
		return $TorResource('circuit');
	}])
	.factory('TorInstance', ['$resource', 'baseURL', function($resource, baseURL) {
		return $resource(baseURL + 'tor/:id', {}, {query: {method:'GET', params:{id:''}, isArray:true}})
	}])
	.factory('Stream', ['$TorResource', function($TorResource) {
	    return $TorResource('stream');
	}])
	.factory('OnionooRouter', ['$resource', 'onionooURL', function($resource, onionooURL){
		return $resource(onionooURL + "details?lookup=:routerId", {}, {});
	}])
	.factory('Router', ['$TorResource', function($TorResource){
		return $TorResource('router');
	}])
	.factory('ReverseDNS', ['$resource', 'baseURL', function($resource, baseURL) {
	    return $resource(baseURL + 'dns/reverse/:ip', {}, {});
	}])
	.factory('LogService', function(){
		if(GlobalLogService === null){
			GlobalLogService = new LogService();
		}
		console.log("logger", GlobalLogService);
		return GlobalLogService;
	})
	.factory('TorstatWebsocket', ['$websocket', 'baseURL', function($websocket, baseURL) {
		return function(instanceId){
			return $websocket('ws://' + baseURL + "tor/" + instanceId + "/websocket/");
		}
	}]);