'use strict';

/* Controllers */
var torstatControllers = angular.module('torstatControllers',[]);


var UpdateCtrl = torstatControllers.controller('UpdateCtrl', ['$scope', 'LogService', 'TorstatWebsocket', '$rootScope',
	function($scope, LogService, TorstatWebsocket, $rootScope){
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
	}

]);

torstatControllers
	.controller('StreamListCtrl', ['$scope', '$rootScope', 'Stream', function($scope, $rootScope, Stream){
		$scope.streams = Stream.query();
		
		function updateStream(stream){
			var found = false;
			for (var i = $scope.streams.length - 1; i >= 0; i--) {
				if($scope.streams[i].id !== null && $scope.streams[i].id == stream.id){
					var circuit = $scope.streams[i].circuit;
					$scope.streams[i] = stream;
					$scope.streams[i].circuits = circuit;
					found = true;
					break;
				}
			};
			if(!found){
				$scope.streams.push(stream)
			}
		}
		$rootScope.$on('stream', function(bc, evt){
			updateStream(evt.stream);
		});

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
	  		Circuits.delete({id: id}, function(response){
	  			console.log("Circuit deleted: " + response)
	  		});
	  	}
		$scope.update = function(){
			$scope.circuits = Circuits.query(); 
		}
}]);

torstatControllers.controller('CircuitDetailCtrl', ['$scope', '$routeParams', 'Circuits',
  function($scope, $routeParams, Circuits) {
    $scope.circuit = Circuits.get({id: $routeParams.circuitId}, function(circuit){
  		// get circuit callback
    });
  }]);

torstatControllers.controller('RouterDetailCtrl', ['$scope', '$routeParams', 'Router', 'OnionooRouter', 'ReverseDNS',
  function($scope, $routeParams, Router, OnionooRouter, ReverseDNS) {
    $scope.router = Router.get({routerId: $routeParams.routerId}, function(router){
  		// get circuit callback
    });
    $scope.router.reverseDNSLookup = function(){
    	console.log("this", this);
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

  }]);
