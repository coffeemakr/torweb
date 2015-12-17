'use strict';

/* Controllers */
var torstatControllers = angular.module('torstatControllers',[]);

torstatControllers
	.controller('InstanceCtrl', ['$scope', 'MenuHandler', '$route', '$routeParams', 'TorInstance', function($scope, MenuHandler, $route, $routeParams, TorInstance){
		MenuHandler.setCurrent($route.current.$$route.originalPath);
		MenuHandler.setArgs($routeParams);		
		if($routeParams.instanceId) {
			$scope.instance = TorInstance.get($routeParams);
		}else{
			$scope.instances = TorInstance.query({},function(data){console.log(data)});
		}
	}])
	.controller('TorRessourceCtrl', ['TorstatWebsocket', '$scope', 'MenuHandler', '$location', '$routeParams', '$TorResource', '$route', 'OnionooRouter', 'ReverseDNS',
		function(TorstatWebsocket, $scope, MenuHandler, $location, $routeParams, $TorResource, $route, OnionooRouter, ReverseDNS) {
			MenuHandler.setCurrent($route.current.$$route.originalPath);
			MenuHandler.setArgs($routeParams);
			
			function UpdateView(){
				var view = MenuHandler.getCurrent().getTemplateName();
				var ressource = $TorResource(view.split('-')[0]);
				switch(view){
					case 'circuit-detail':
						$scope.circuit = ressource.get($routeParams);
						break;
					case 'circuit-list':
						$scope.circuits = ressource.query($routeParams);
						break;
					case 'router-detail':
						$scope.router = ressource.get($routeParams);
						break;
					case 'router-list':
						$scope.routers = ressource.query($routeParams);
						break;
					case 'stream-detail':
						$scope.stream = ressource.get($routeParams);
						break;
					case 'stream-list':
						$scope.streams = ressource.query($routeParams);
						break;
					default:
						console.error("view not implemented: ", view);		
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
			$scope.routerDetails = function(router){
				$location.path(MenuHandler.getUrlForTemplateName('router-detail', {instanceId: $routeParams.instanceId, routerId: router.id}));
			};
			$scope.streamDetails = function(stream){
				$location.path(MenuHandler.getUrlForTemplateName('stream-detail', {instanceId: $routeParams.instanceId, streamId: stream.id}).url);
			};
			$scope.deleteStream = function(stream){
				$TorResource('stream').delete({streamId: stream.id, instanceId: $routeParams.instanceId});
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
						var attributes = ['platform', 'dir_address']
						for (var i = 0; i < attributes.length; i++){
							$scope.router[attributes[i]] = router[attributes[i]];
						}
					});
				});
			};
		}
	])