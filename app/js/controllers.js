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
				console.log("found");
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
			console.log(circuit);
		}
  	}

   $rootScope.$on('circuit', function(bc, evt){
   		var circuit_desc = evt.circuit;
		switch(evt.action) {
			case "new":
				logger.log("Circuit new");
				break;
			case "launched":
				logger.log("Circuit launched");
				break;
			case "extend":
				logger.log("Circuit extend");
				break;
			case "built":
				logger.log("Circuit built");
				break;
			case "closed":
				logger.log("Circuit closed");
				break;
			case "failed":
				logger.log("Circuit failed");
				break;
		}
		updateCircuit(circuit_desc);
    });

	$scope.update = function(){
		var scope = $scope;
		scope.circuits = Circuits.query(); 
	}
    
	// var nodes = [{id: "You"}];
	// var edges = [];
	// for (var c = $scope.circuits.length - 1; i >= 0; i--) {
	// 	var last_node = null;
	// 	for (var i = $scope.circuits[c].path.length - 1; i >= 0; i--) {
	// 		var node = $scope.circuits[c].path[i];
	// 		nodes.push({
	// 			id: node[0],
	// 			name: node[1],
	// 			x: 0,
	// 			y: 1
	// 		});
	// 		if (!(last_node === null)) {
	// 			edges.push({
	// 				'id': last_node[0] + node[0],
	// 				'source': last_node[0],
	// 				'target': node[0]
	// 			});
	// 		};
	// 		last_node = node;
	// 	};
	// };
	// $scope.graph_line = -1;
 //    $scope.drawGraph = function(container) {
 //    	var scope = $scope;
 //    	document.getElementById(container).innerHTML = '';
 //    	var graph = {
 //    		nodes: [{
 //    			"x": 0,
 //    			"y": 0,
 //    			"label": "You",
 //    			"id": "you",
 //    			"size": 1
 //    		}]
 //    	}
	// 	  var s = new sigma({
	// 	  	graph: graph,
	// 	    container: container,
	// 	    settings: {
	// 	      defaultNodeColor: '#ec5148'
	// 	    }
	// 	  });
	// 	s.refresh();
	// 	scope.sigma = s;
 //    };
 //    $scope.addToGraph = function(circuit) {
 //    	var scope = $scope;
	// 	var previous_id = null;
 //    	var line = scope.graph_line++;
 //    	for (var i = 0; i < circuit.path.length; i++) {
 //    		var id = circuit.path[i][0];
 //    		var name = circuit.path[i][1];
 //    		var node = null;
 //    		var getId = function(node){
 //    			return node.id == id;
 //    		}
 //    		var existing_node = scope.sigma.graph.nodes().filter(getId); 
 //    		if(existing_node.length == 0){
	//     		node = {
	//     			"x": 1 + i*3,
	//     			"y": line,
	//     			"label": name,
	//     			"id": id,
	//     			"size": 1
	//     		};
	//     		scope.sigma.graph.addNode(node);
 //    		}else{
 //    			existing_node[0].size++;
 //    		}
 //    		if(previous_id === null) {
 //    			previous_id = 'you';
 //    		}
 //    		{
	//     		var edgeid = previous_id + id;
	//     		var getId = function(edge){
	//     			return edge.id == edgeid;
	//     		}
	//     		if(scope.sigma.graph.edges().filter(getId).length == 0) {
	// 	    		console.log(previous_id + " -> " + id);
	// 	    		scope.sigma.graph.addEdge({
	// 	   				'id': edgeid,
	// 					'source': previous_id,
	// 					'target': id
	// 	    		});
	//     		}
	//     	}
 //    		previous_id = id;
 //    	};
 // 		scope.sigma.graph.nodes()[0].y = line / 2;
 //   		scope.sigma.refresh();
 //   		console.log(scope.sigma.graph.nodes());
 //   		//console.log(scope.sigma.graph.edges());
 //    };
}]);

torstatControllers.controller('CircuitDetailCtrl', ['$scope', '$routeParams', 'Circuits',
  function($scope, $routeParams, Circuits) {
    $scope.circuit = Circuits.get({circuitId: $routeParams.circuitId}, function(circuit) {
    	
    });

  }]);
