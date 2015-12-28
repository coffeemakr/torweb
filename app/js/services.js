'use strict';

/* Services */

var torstatServices = angular.module('torstatServices', ['ngResource', 'ngWebSocket']);

torstatServices
	.factory('baseURL', ['$location', function($location) {
  		return "//" + window.location.host + "/api/";
	}])
	.factory('onionooURL', function(){
		return "https://onionoo.torproject.org/";
	});

function updateObject(src, dst){
	for (var key in src) {
		if (src.hasOwnProperty(key) && !(key.charAt(0) === '$' && key.charAt(1) === '$')) {
			dst[key] = src[key];
		}
	}
}
function clearObject(obj){
	for (var member in obj){
		delete obj[member];
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
	this.parent = config.parent;
	this.url = config.url;
	this.name = config.name;
	this.description = config.description;
	if(angular.isUndefined(this.description)){
		this.description = null;
	}
	this.templateUrl = config.templateUrl;
	this.templateName = null;
	if(angular.isUndefined(this.url)){
		console.log("Undefined url");
	}
	if(angular.isUndefined(this.name)){
		console.log("Undefined name in ", this.url);
	}
	this.path = null;
}


MenuTreeNode.prototype.getTemplateName = function(){
	if(this.templateName === null){
		if(this.templateUrl){
			var name = this.templateUrl;
			var index = name.lastIndexOf('/');
			if(index >= 0){
				name = name.substring(index + 1);
			}
			index = name.lastIndexOf('.');
			if(index > 0){
				name = name.substring(0, index);
			}
			this.templateName = name;
		}else{
			return null;
		}
	}
	return this.templateName;
}
MenuTreeNode.prototype.getReversePath = function(){
	if(this.path === null){
		this.path = [];
		for(var node = this; node !== null; node = node.parent){
			if(this.path.indexOf(node) >= 0){
				console.error("Infinite loop!", node);
				break;
			}
			this.path.push(node);
		}
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

function _formatString(format, params){
	if(format && params){
		for(var replaceName in params){
			format = format.replace(':' + replaceName, params[replaceName]);
		}
	}
	return format
}

MenuTreeNode.prototype.getUrl = function(params){
	return _formatString(this.url, params);
}

MenuTreeNode.prototype.getName  = function(params){
	if(!this.name){
		console.log("Name not defined!!", this.name, this.url);
	}
	return _formatString(this.name, params);
}

/**
 * Returns the full, unformatted url.
 * @return {@dict}
 */
MenuTreeNode.prototype.getLink = function(params){
	return {
		"name": this.getName(params),
		"url": this.getUrl(params),
		"description": this.description
	}
}

/** @constructor */
function MenuHandler(scope, route){
	this.scope = scope;
	this.clear();
	this.setRoute(route);
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

function _getUrlParent(url){
	var index = url.lastIndexOf('/');
	if(index == 0 && url == '/'){
		return null;
	}else if(index <= 0){
		return '/';
	}else{
		return url.substring(0, index);
	}
}
MenuHandler.prototype.setRoute = function(route){
	if(angular.isUndefined(route)){
		this.nodes = {};
	}else{
		console.log("Routes: ", route.routes)
		for (var url in route.routes) {
			if(url === null){
				continue;
			}
			var name = route.routes[url].name;
			if(!name){
				continue;
			}
			var config = {};
			config.parent = null;
			config.url = url;
			config.name = name;
			config.templateUrl = route.routes[url].templateUrl;
			this.nodes[url] = new MenuTreeNode(config);
		};
		// resolve parent
		for(var url in this.nodes){
			if (this.nodes[url].parent === null){
				var parentUrl = _getUrlParent(this.nodes[url].url);
				while(parentUrl !== null && !route.routes.hasOwnProperty(parentUrl)){
					console.log("Unresolved parent url:", parentUrl)
					parentUrl = _getUrlParent(parentUrl);
				}
				if(parentUrl !== null){
					this.nodes[url].parent = this.nodes[parentUrl];
				}
			}
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

MenuHandler.prototype.getCurrent = function(){
	return this.currentNode;
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

MenuHandler.prototype.getUrlForTemplateName = function(name, format_args){
	for (var url in this.nodes) {
		if(this.nodes[url].getTemplateName() == name){
			return this.nodes[url].getUrl(format_args);
		}
	};
	return null;
}

MenuHandler.prototype.update = function(){
	this.breadcrumbs.length = 0;
	var node = this.currentNode;
	var url = '/';
	var path = node.getReversePath();
	for (var i = path.length - 1; i >= 0; i--) {
		var crumb = path[i].getLink(this.format_args);
		if(i == 0){
			crumb["class"] = "active";
			crumb["active"] = true;
		}
		this.breadcrumbs.push(crumb);
	};
}

torstatServices
	.factory('$TorResource', ['$resource', 'baseURL',
		function($resource, baseURL){
			/** @dict */
			var resources = {};
			var error = {};

			function createRessource(name){
				if(!name){
					return null;
				}
				/** @type{string} */
				var url = baseURL + 'tor/:instanceId/';
				/** @type{string} */
				var idName;
				/** @dict */
				var queryParams = {};
				if(name == "instance"){
					idName = 'instanceId';
				}else{
					idName = name + 'Id';
					url += name + '/:' + idName;
				}
				queryParams[idName] = ''; 
				
				var res = $resource(url, {}, {query: {method:'GET', params: queryParams, isArray:false}});
				

				return {
					content: {
						object: {},
						list: [],
						error: error,
						async_errors: []
					},
					ressource: res,
					delete: res.delete,
					
					/** @dict */
					contentById: {},
					addObject: function(content){
						if(this.content.list){
							this.content.list.push(content);
							this.contentById[content.id] = content;
						}
					},
					clear: function(){
						clearObject(this.content.object);
						this.content.list.length = 0;
						this.content.error = null;
						this.content.async_errors.length = 0;
					},
					_getCallback: function(async){
						if(angular.isUndefined(async)){
							async = false;
						}
						var that = this;
						return function(data){
							if(data.error) {
								console.log(data.error);
								if(async){
									that.content.async_errors.push(data.error);
								}else{
									that.content.error = data.error;
								}
							}else{
								that.content.error = null;
								if(angular.isUndefined(data.objects)) {
									console.log("get", data);
									// get/update or something else
									// TODO: update only
									var id = data.id;
									if(angular.isUndefined(id)){
										console.error("Didn't find id.", data);
									} else {
										if(that.contentById.hasOwnProperty(id)){
											updateObject(data, that.contentById[id]);
										} else {
											that.contentById[id] = data;
										}
										updateObject(that.contentById[id], that.content.object);
										console.log(that.content.object);
									}
								} else {
									console.log("query", data);
									var objects = data.objects;
									that.contentById = {};
									that.content.list.length = 0;
									for (var i = 0; i < objects.length; i++) {
										that.contentById[objects[i].id] = objects[i];
										that.content.list.push(objects[i]);
									};
								}
							}
						};
					},
					_getErrback: function(){
						var that = this;
						return function(error){
							var errorObject = {name: "Error", message: "Unknown Error"};
							if(error.status == -1){
								errorObject.name = "Connection Error";
								errorObject.message = "Unable to connect to the server.";
							}else{
								errorObject.name = "HTTP Error";
								errorObject.message = error.statusText;
							}
							that.content.error = errorObject;
						}
					},
					_call: function(func_name, params, data){
						var response = this.ressource[func_name](params, data);
						response.$promise.then(this._getCallback());
						response.$promise.catch(this._getErrback());
						return this.content;						
					},
					_async_call: function(func_name, params, data){
						var response = this.ressource[func_name](params, data);
						response.$promise.then(this._getCallback(true));
						response.$promise.catch(this._getErrback(true));
						return this.content;
					},
					query: function(params){
						return this._call("query", params);
					},
					get: function(params){
						return this._call("get", params);
					},
					save: function(params, data){
						return this._async_call("save", params, data);
					},
					delete: function(params){
						return this._async_call("delete", params);
					},
					update: function(object){
						if(angular.isUndefined(object)){
							return object;
						}
						if(object.id){
							if(this.content.object.id && this.content.object.id == object.id){
								updateObject(object, this.content.object);
							}
							if(this.contentById.hasOwnProperty(object.id)){
								updateObject(object, this.contentById[object.id]);
							}else{
								this.contentById[object.id] = object;
								this.content.list.push(object);
							}
						}
					}
				}; // return

			};

			function getRessourceByName(name){
				if(!resources.hasOwnProperty(name)){
					console.log("creating ", name);
					resources[name] = createRessource(name);
				}
				return resources[name];
			};
			return getRessourceByName;
	}])
	.factory('MenuHandler', ['$rootScope', '$route', '$routeParams', function($rootScope, $route, $routeParams){
		return new MenuHandler($rootScope, $route, $routeParams);
	}])
	.factory('TorInstance', ['$resource', 'baseURL', function($resource, baseURL) {
		return $resource(baseURL + 'tor/:instanceId', {}, {query: {method:'GET', params:{instanceId:''}, isArray:true}})
	}])
	.factory('OnionooRouter', ['$resource', 'onionooURL', function($resource, onionooURL){
		return $resource(onionooURL + "details?lookup=:routerId");
	}])
	.factory('ReverseDNS', ['$resource', 'baseURL', function($resource, baseURL) {
	    return $resource(baseURL + 'dns/reverse/:ip');
	}])
	.factory('LogService', function(){
		if(GlobalLogService === null){
			GlobalLogService = new LogService();
		}
		console.log("logger", GlobalLogService);
		return GlobalLogService;
	})
	.factory('TorstatWebsocket', ['$websocket', 'baseURL', '$TorResource', function($websocket, baseURL, $TorResource) {
		var currentRessource = null;
		var ws = {
			websocket: null,
			currentId: undefined,
			scope: null,
			resourceArraySuffix: "s",
			connect: function(instanceId){
				if(instanceId != this.currentId){
					if(this.websocket !== null){
						console.log("closing websocket");
						this.websocket.close();
						this.websocket = null;
					}
					if(!angular.isUndefined(instanceId)){
						this.websocket = $websocket('ws://' + baseURL + "tor/" + instanceId + "/websocket/");
						this.websocket.onMessage(this.getOnMessageFunction());
					}
					this.currentId = instanceId;
				}
				return this;
			},
			getOnMessageFunction: function(){
				var that = this;
				return function(message){
					if(!angular.isUndefined(message.data)){
						var update = JSON.parse(message.data);
						if(update && update.type && update.data && update.data[update.type] && update.data[update.type].id){
							that.updateObject(update.type, update.data[update.type]);
						}
					}
				}
			},
			updateObject: function(resourceName, data){
				var res = $TorResource(resourceName);
				res.update(data);
			},
			close: function(){
				if(this.websocket !== null){
					this.websocket.close();
					this.websocket = null;
				}
				return this;
			},
			setScope: function(scope){
				this.scope = scope;
				return this;
			}
		};

		$(window).on('beforeunload', function(){
			ws.close();	
		});
		return ws;
	}]);