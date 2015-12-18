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
			function createRessource(name){
				if(!name){
					return null;
				}
				/** @type{string} */
				var url = baseURL + 'tor/:instanceId/', idName;
				/** @dict */
				var queryParams = {};
				if(name == "instance"){
					idName = 'instanceId';
				}else{
					idName = name + 'Id';
					url += name + '/:' + idName;
				}
				queryParams[idName] = ''; 
				var res = $resource(url, {}, {query: {method:'GET', params: queryParams, isArray:true}});
				return {
					keyAttribute: "id", 
					content: null,
					ressource: res,
					delete: res.delete,
					/** @dict */
					contentById: null,
					contentIsArray: false,

					addObject: function(content){
						if(this.contentIsArray && this.content !== null){
							this.content.push(content);
							this.contentById[content.id] = content;
						}
					},

					setContent: function(content){
						var that = this;
						this.contentById = {};
						this.content = content;
						this.$promise = content.$promise;
						this.$promise.catch(function(error){
							console.error(error);
							if(error.status == -1){
								if(error.statusText.length == 0){
									error.statusText = "Unable to connect to the server.";
								}
							}
							that.content["error"] = error;
						});
					},
					query: function(params){
						var that = this;
						this.contentIsArray = true;
						this.setContent(this.ressource.query(params));
						this.$promise.then(function(data){
							that.contentById = {};
							for (var i = data.length - 1; i >= 0; i--) {
								that.contentById[data[i].id] = data[i];
							};
						});
						return this.content;
					},
					get: function(params){
						var that = this;
						this.setContent(this.ressource.get(params));
						this.$promise.then(function(data){
							that.contentById = {}
							that.contentById[data.id] = data;
						});
						return this.content;
					},
					update: function(content){
						var objectToUpdate = null;
						if(this.content !== null){
							if(this.contentById.hasOwnProperty(content.id)){
								updateObject(content, this.contentById[content.id]);
							}else if(this.contentIsArray){
								this.addObject(content);
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
		return {
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
		}
	}]);