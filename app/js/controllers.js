'use strict';

/* Controllers */
var torstatControllers = angular.module('torstatControllers',[]);

torstatControllers
	.controller('TorRessourceCtrl', 
	   			['TorstatWebsocket', '$scope', '$rootScope', 'MenuHandler', '$location', '$routeParams', '$TorResource', '$route', 'OnionooRouter', 'ReverseDNS',
		function(TorstatWebsocket,    $scope,   $rootScope,   MenuHandler,   $location,   $routeParams,   $TorResource,   $route,   OnionooRouter,   ReverseDNS) {
			MenuHandler.setCurrent($route.current.$$route.originalPath);
			MenuHandler.setArgs($routeParams);

			function UpdateView(){
				var view = MenuHandler.getCurrent().getTemplateName();
				var ressource_name = view.split('-')[0];
				var ressource = $TorResource(ressource_name);
				ressource.clear();
				$scope.content = ressource.content;
				switch(view.split('-')[1]){
					case 'detail':
						console.log(ressource_name);
						$scope.content = ressource.get($routeParams);
						$scope[ressource_name] = $scope.content.object;
						break;
					case 'list':
						$scope.content = ressource.get($routeParams);
						$scope[ressource_name + 's'] = $scope.content.list;
						break;
					default:
						console.log("unknown view");
				}
			}
			UpdateView();
			TorstatWebsocket.connect($routeParams.instanceId).setScope($scope);
			$scope.deleteCircuit = function(circuit) {
				$TorResource('circuit').delete({circuitId: circuit.id, instanceId: $routeParams.instanceId});
			};
			$scope.circuitDetails = function(circuit){
				$location.path(MenuHandler.getUrlForTemplateName('circuit-detail', {instanceId: $routeParams.instanceId, circuitId: circuit.id}));
			};
			$rootScope.route = $routeParams;
			$rootScope.go = function(templateName){
				$location.path(MenuHandler.getUrlForTemplateName(templateName, $routeParams));
			}
			$scope.routerDetails = function(router){
				$location.path(MenuHandler.getUrlForTemplateName('router-detail', {instanceId: $routeParams.instanceId, routerId: router.id}));
			};
			$scope.streamDetails = function(stream){
				$location.path(MenuHandler.getUrlForTemplateName('stream-detail', {instanceId: $routeParams.instanceId, streamId: stream.id}));
			};
			$scope.deleteStream = function(stream){
				$TorResource('stream').delete({streamId: stream.id, instanceId: $routeParams.instanceId});
			};
			$scope.configDetails = function(config){
				$location.path(MenuHandler.getUrlForTemplateName('config-detail', {instanceId: $routeParams.instanceId, configId: config.name}));
			};
			$scope.updateConfig = function(config){
				$TorResource('config').save({instanceId: $routeParams.instanceId, configId: config.name}, {value: config.value});
			};
			$scope.reverseDNS = function(router){
				ReverseDNS.get({ip: router.ip}, function(data){
					data.$promise.then(function(data){
						$scope.router.hostname = data.host;
					});
				})
			};
			$scope.askOnionooo = function(){
				OnionooRouter.get({routerId: $routeParams.routerId}, function(data){
					data.$promise.then(function(data){
						var router = data.relays[0];
						router.id = router.fingerprint;
						$TorResource('router').update(router);
					});
				});
			};
		}
	])