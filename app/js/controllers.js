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
				logger.log(evt.type+ ": " + evt.data);
			}
			
		});
	}

]);

torstatControllers.controller('CircuitListCtrl', [
	'$scope', 'Circuits', '$rootScope', 'LogService',
  function($scope, Circuits, $rootScope, logger) {
  	
  	$scope.circuits = Circuits.query();
  	$scope.deleteCircuit = function(id) {
  		var scope = $scope;
  		Circuits.delete({circuitId: id}, function(response){
  			console.log("Circuit deleted: " + response)
  		});
  	}

  	function updateCircuit(circuit_desc){
  		var circuit = null;
  		for (var i = $scope.circuits.length - 1; i >= 0; i--) {
			if($scope.circuits[i].id == circuit_desc.id){
				circuit = $scope.circuits[i];
				break;
			}
		};
		if(circuit === null) {
			var circuit = circuit_desc;
			$scope.circuits.push(circuit);
		}else{
			console.log(circuit);
			for(var attr in circuit_desc){
				circuit[attr] = circuit_desc[attr];
			}
		}
  	}

   $rootScope.$on('circuit', function(bc, evt){
		updateCircuit(evt.circuit);
    });

	$scope.update = function(){
		var scope = $scope;
		scope.circuits = Circuits.query(); 
	}
}]);

torstatControllers.controller('CircuitDetailCtrl', ['$scope', '$routeParams', 'Circuits',
  function($scope, $routeParams, Circuits) {
    $scope.circuit = Circuits.get({circuitId: $routeParams.circuitId}, function(circuit){
  		// get circuit callback
    });
  }]);

