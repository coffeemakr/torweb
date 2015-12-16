'use strict';

/* Controllers */
var torstatControllers = angular.module('torstatControllers',[]);

torstatControllers
	.controller('UpdateCtrl', ['$scope', 'LogService', 'TorstatWebsocket', '$rootScope', function($scope, LogService, TorstatWebsocket, $rootScope){
		var currentId = -1;
		var websocket = null;
		function getIdFromUrl(url){
			url = url.split('#', 2);
			if(url.length < 2){
				return -1;
			}
			var id = url[1];
			if(id.length <= 1){
				return -1;
			}
			id = id.substr(1);
			if(id.contains('/')){
				id = id[0];				
			}
			id = parseInt(id);
			if(! (id >= 0)){
				return -1;
			}
			return id;
		}

		$scope.Events = [];
		$scope.Logs = LogService.logs;
		$scope.$on('$locationChangeStart', function(event, next, current) {
			var id = getIdFromUrl(next);
			console.log("id", id);
			if(currentId != id){
				websocket = TorstatWebsocket(id);
				websocket.onMessage(
					function(message) {
						var evt = JSON.parse(message.data);
						var scope = $scope;
						var logger = LogService;
						if(typeof evt != 'undefined') {
							$rootScope.$broadcast(evt.type, evt.data);
							logger.log(evt.data.action + " " + evt.type +": " + evt.data.id);
						}
					}
				);
			}
		});
	}])
	.controller('InstanceCtrl', ['$scope', 'MenuHandler', '$routeParams', 'TorInstance', function($scope, MenuHandler, $routeParams, TorInstance){
		if($routeParams.instanceId) {
			MenuHandler.setCurrent("instanceDetails");
			$scope.instance = TorInstance.get($routeParams);
		}else{
			MenuHandler.setCurrent("instanceList");
			$scope.instances = TorInstance.query({},function(data){console.log(data)});
		}
		MenuHandler.setArgs($routeParams);
	}])
	.controller('StreamCtrl', ['$scope', 'MenuHandler', '$location', '$routeParams', 'Stream', function($scope, MenuHandler, $location, $routeParams, Stream){
		if($routeParams.streamId){

		}else{
			MenuHandler.setCurrent("streamList");
			$scope.streams = Stream.query($routeParams);
		}
		MenuHandler.setArgs($routeParams);
		$scope.streamDetails = function(stream){
			$location.path(MenuHandler.getUrl('streamDetails', {instanceId: $routeParams.instanceId, streamId: stream.id}).url);
		}
		$scope.deleteStream = function(stream){
			Stream.delete({streamId: stream.id, instanceId: $routeParams.instanceId}, function(){
				console.log("stream closed")
			});
		};

	}])
	.controller('CircuitCtrl', ['$scope', 'MenuHandler', '$location', '$routeParams', 'Circuits',
		function($scope, MenuHandler, $location, $routeParams, Circuits) {
			if($routeParams.circuitId){
				MenuHandler.setCurrent("circuitDetails");
				$scope.circuit = Circuits.get($routeParams);
			}else{
				MenuHandler.setCurrent("circuitList");
				$scope.circuits = Circuits.query($routeParams);
			}
			MenuHandler.setArgs($routeParams);

			$scope.routerDetails = function(router){
				$location.path(MenuHandler.getUrl('routerDetails', {instanceId: $routeParams.instanceId, routerId: router.id}).url);
			}

			$scope.deleteCircuit = function(circuit) {
				Circuits.delete({circuitId: circuit.id, instanceId: $routeParams.instanceId});
			}
			$scope.circuitDetails = function(circuit){
				$location.path(MenuHandler.getUrl('circuitDetails', {instanceId: $routeParams.instanceId, circuitId: circuit.id}).url);
			}
			$scope.routerDetails = function(router){
				$location.path(MenuHandler.getUrl('routerDetails', {instanceId: $routeParams.instanceId, routerId: router.id}).url);
			}
		}
	])
	.controller('RouterCtrl', ['$scope', 'MenuHandler', '$routeParams', 'Router', 'OnionooRouter', 'ReverseDNS',
		function($scope, MenuHandler, $routeParams, Router, OnionooRouter, ReverseDNS) {
			if($routeParams.routerId) {
				MenuHandler.setCurrent("routerDetails");
				$scope.router = Router.get($routeParams, function(router){
					MenuHandler.updateArgs({routerName: router.name});
				});
			}
			MenuHandler.updateArgs($routeParams);
			
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
	]);
