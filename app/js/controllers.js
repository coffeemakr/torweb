'use strict';

/* Controllers */
var torstatControllers = angular.module('torstatControllers',[]);

torstatControllers
	.controller('UpdateCtrl', ['$scope', 'LogService', 'TorstatWebsocket', '$rootScope', function($scope, LogService, TorstatWebsocket, $rootScope){
		$scope.Events = [];
		$scope.Logs = LogService.logs;
		LogService.log("Waiting for messages.");
		TorstatWebsocket.onMessage(function(message){
			var evt = JSON.parse(message.data);
			var scope = $scope;
			var logger = LogService;
			if(typeof evt != 'undefined') {
				$rootScope.$broadcast(evt.type, evt.data);
				logger.log(evt.data.action + " " + evt.type +": " + evt.data.id);
			}
		});
	}])
	.controller('StreamListCtrl', ['$scope', 'Stream', function($scope, Stream){
		$scope.streams = Stream.query();
		
		$scope.deleteStream = function(stream){
			Stream.delete({id: stream.id}, function(){
				console.log("stream closed")
			});
		};

	}])
	.controller('CircuitListCtrl', ['$scope', 'Circuits', 'LogService',
		function($scope, Circuits, logger) {
			$scope.circuits = Circuits.query();

			$scope.deleteCircuit = function(id) {
				var promise = Circuits.delete({id: id});
			}
			$scope.update = function(){
				$scope.circuits = Circuits.query(); 
			}
		}
	])
	.controller('CircuitDetailCtrl', ['$scope', '$routeParams', 'Circuits',
		function($scope, $routeParams, Circuits) {
			$scope.circuit = Circuits.get({id: $routeParams.circuitId}, function(circuit){
				// get circuit callback
			});
		}
	])
	.controller('RouterDetailCtrl', ['$scope', '$routeParams', 'Router', 'OnionooRouter', 'ReverseDNS',
		function($scope, $routeParams, Router, OnionooRouter, ReverseDNS) {
			$scope.router = Router.get({id: $routeParams.routerId}, function(router){});
			
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
