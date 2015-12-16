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
	.controller('InstanceListCtrl', ['$scope', 'MenuHandler', 'TorInstance', function($scope, MenuHandler, TorInstance){
		MenuHandler.setCurrent("instanceList");
		$scope.instances = TorInstance.query({},function(data){console.log(data)});
	}])
	.controller('InstanceDetailCtrl', ['$scope', 'MenuHandler', '$routeParams', 'TorInstance', function($scope, MenuHandler, $routeParams, TorInstance){
		MenuHandler.setCurrent("instanceDetails");
		$scope.tor = TorInstance.get({id: $routeParams.instanceId});
	}])
	.controller('StreamListCtrl', ['$scope', 'MenuHandler', '$location', '$routeParams', 'Stream', function($scope, MenuHandler, $location, $routeParams, Stream){
		MenuHandler.setCurrent("streamList");
		$scope.streams = Stream.query({instanceId: $routeParams.instanceId});
		$scope.streamDetails = function(stream){
			$location.path(MenuHandler.getUrl('streamDetails', {instanceId: $routeParams.instanceId, streamId: stream.id}).url);
		}
		$scope.deleteStream = function(stream){
			Stream.delete({id: stream.id, instanceId: $routeParams.instanceId}, function(){
				console.log("stream closed")
			});
		};

	}])
	.controller('CircuitListCtrl', ['$scope', 'MenuHandler', '$location', '$routeParams', 'Circuits',
		function($scope,  MenuHandler, $location, $routeParams, Circuits) {
			MenuHandler.setCurrent("circuitList");
			MenuHandler.setArgs({instanceId: $routeParams.instanceId});

			$scope.circuits = Circuits.query({instanceId: $routeParams.instanceId});
			$scope.deleteCircuit = function(id) {
				var promise = Circuits.delete({id: id, instanceId: $routeParams.instanceId});
			}
			$scope.circuitDetails = function(circuit){
				$location.path(MenuHandler.getUrl('circuitDetails', {instanceId: $routeParams.instanceId, circuitId: circuit.id}).url);
			}
			$scope.routerDetails = function(router){
				$location.path(MenuHandler.getUrl('routerDetails', {instanceId: $routeParams.instanceId, routerId: router.id}).url);
			}

			$scope.update = function(){
				$scope.circuits = Circuits.query({instanceId: $routeParams.instanceId}); 
			}
		}
	])
	.controller('CircuitDetailCtrl', ['$scope', 'MenuHandler', '$location', '$routeParams', 'Circuits',
		function($scope, MenuHandler, $location, $routeParams, Circuits) {
			MenuHandler.setCurrent("circuitDetails");
			MenuHandler.setArgs($routeParams);

			$scope.routerDetails = function(router){
				$location.path(MenuHandler.getUrl('routerDetails', {instanceId: $routeParams.instanceId, routerId: router.id}).url);
			}

			$scope.circuit = Circuits.get({id: $routeParams.circuitId, instanceId: $routeParams.instanceId});
		}
	])
	.controller('RouterDetailCtrl', ['$scope', 'MenuHandler', '$routeParams', 'Router', 'OnionooRouter', 'ReverseDNS',
		function($scope, MenuHandler, $routeParams, Router, OnionooRouter, ReverseDNS) {
			MenuHandler.setCurrent("routerDetails");
			MenuHandler.setArgs($routeParams);
			$scope.router = Router.get({id: $routeParams.routerId, instanceId: $routeParams.instanceId}, 
				function(router){
					MenuHandler.updateArgs({routerName: router.name});
				});
			
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
