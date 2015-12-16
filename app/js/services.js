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
function MenuTreeNode(config){
	this.name = config["name"];
	/** @type{MenuTreeNode} */
	this.parent = config["parent"];
	this.path = null;
	this.id = config["id"];
	this.isrelative = config["isrelative"];
	this.url = config["url"];
	this.fullUrl = null;
}


MenuTreeNode.prototype.getReversePath = function(){
	if(this.path === null){
		var node = this;
		var path = [];
		do{
			path.push(node);
			node = node.parent;
		}while(node.parent !== null);
		this.path = path;
	}
	return this.path;
}

/** 
 * @return {string}
 */
function _joinUrl(pre, post){
	if(pre[pre.length - 1] != "/" && post[post.length - 1] != "/") {
		return pre + "/" + post;
	}else{
		return pre + post;
	}
}

/**
 * Returns the full, unformatted url.
 * @return {string}
 */
MenuTreeNode.prototype.getUrl = function(){
	if(this.fullUrl === null) {
		if(!this.isrelative){
			this.fullUrl = this.url;
		}else{
			/** @type{string} */
			var parentUrl = "/";
			if(this.parent !== null){
				// recursive should be fine because nobody want a link
				// tree a large depth
				parentUrl = this.parent.getUrl();
			}
			this.fullUrl = _joinUrl(parentUrl, this.url);
		}
	}
	return this.fullUrl;
}

function _formatString(format, name, value){
	return format.replace(':' + name, value);
}

/**
 * Returns the full, unformatted url.
 * @return {@dict}
 */
MenuTreeNode.prototype.getFormattedUrlObject = function(args){
	var url = this.getUrl();
	var name = this.name;
	for(var replaceName in args){
		var replacveValue = args[replaceName]
		name = _formatString(name, replaceName, replacveValue);
		url = _formatString(url, replaceName, replacveValue);
	}
	return {
		"name": name,
		"url": url,
		"id": this.id
	}
}

/** @constructor */
function MenuHandler(scope, config){
	this.scope = scope;
	this.clear();
	this.setNodes(config["nodes"])
}

MenuHandler.prototype.clear = function(){
	/** @dict */
	this.nodes = {}
	/** @dict */
	this.format_args = {}
	/** @type{MenuTreeNode} */
	this.currentNode = null;
	/** @Array<Object> */
	this.breadcrumbs = [];
	/** @type{boolean} */ 
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
					console.log("parent could not be resolved");
					continue;
				}
			}else{
				node[parentName] = null;
			}
			this.nodes[node["id"]] = new MenuTreeNode(node);
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

MenuHandler.prototype.setArgs = function(args){
	this.format_args = args;
	this.update();
}

MenuHandler.prototype.updateArgs = function(args){
	for(name in args){
		this.format_args[name] = args[name];
	}
	this.update();
}

MenuHandler.prototype.getUrl = function(id, format_args){
	if (typeof format_args == 'undefined'){
		format_args = this.format_args;
	}
	if(!this.nodes.hasOwnProperty(id)){
		return;
	}
	return this.nodes[id].getFormattedUrlObject(format_args);
}

MenuHandler.prototype.update = function(){
	this.breadcrumbs.length = 0;
	var node = this.currentNode;
	var nodes = node.getReversePath();
	var url = '/';
	var path = node.getReversePath();
	for (var i = path.length - 1; i >= 0; i--) {
		var crumb = nodes[i].getFormattedUrlObject(this.format_args);
		if(i == 0){
			crumb["class"] = "active";
			crumb["active"] = true;
		}
		this.breadcrumbs.push(crumb);
	};
}

torstatServices
	.factory('$TorResource', ['$resource', 'baseURL', '$rootScope',
		function($resource, baseURL, $rootScope){
			return function(ressourceName){
				var res = new TorResource(
					$resource(baseURL + 'tor/:instanceId/' + ressourceName + '/:id', {}, {query: {method:'GET', params:{id:''}, isArray:true}})
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
				"url": ":instanceId"
			},
			{	"id": 'streamList',
				"parent": 'instanceDetails',
				"name": "Streams",
				"url": "streams",
				"isrelative": true
			},
			{	"id": 'circuitList',
				"parent": 'instanceDetails',
				"name": "Circuits",
				"url": "circuits",
				"isrelative": true
			},
			{	"id": 'streamDetails',
				"parent": 'streamList',
				"name": "Stream :streamId",
				"url": ":instanceId/stream/:circuitId",
			},
			{	"id": 'circuitDetails',
				"parent": 'circuitList',
				"name": "Circuit :circuitId",
				"url": ":instanceId/circuit/:circuitId",
			},
			{	"id": 'routerDetails',
				"parent": 'circuitList',
				"name": "Router :routerName",
				"url": ":instanceId/router/:routerId",
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