'use strict';

/* Controllers */
var torstatControllers = angular.module('torstatControllers',[]);

torstatControllers
	.controller('TorRessourceCtrl', 
	   			['TorstatWebsocket', '$scope', '$rootScope', 'MenuHandler', '$location', '$routeParams', '$TorResource', '$route', 'OnionooRouter', 'DNSLookup',
		function(TorstatWebsocket,    $scope,   $rootScope,   MenuHandler,   $location,   $routeParams,   $TorResource,   $route,   OnionooRouter,   DNSLookup) {
			MenuHandler.setCurrent($route.current.$$route.originalPath);
			MenuHandler.setArgs($routeParams);

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
				$location.path(MenuHandler.getUrlForTemplateName('config-detail', {instanceId: $routeParams.instanceId, configId: config.id}));
			};
			$scope.updateConfig = function(config){
				$TorResource('config').save({instanceId: $routeParams.instanceId, configId: config.id}, {value: config.value});
			};

			$scope.guessHostname = function(ip, streams){
				for (var i = streams.length - 1; i >= 0; i--) {
					var stream = streams[i];
					if(stream.target_host != stream.target_addr && stream.target_port == 0){
						if(stream.target_addr == ip){
							return stream.target_host;
						}
					}
				};
				return ip;
			};
			$scope.reverseDNS = function(router){
			    var lookup_reverse = DNSLookup('reverse');
			    var lookup_A = DNSLookup('A');
			    
		    	var result = {};
		    	var reverse_result = lookup_reverse.get({name: router.ip, instanceId: $routeParams.instanceId});
		    	reverse_result.$promise.then(function(data){
		    		if(data.error){
		    			$scope.content.async_errors.push(data.error);
		    		}else{
		    			if(data.objects && data.objects.length > 0){
		    				router.hostname = data.objects[0].name;
		    				router.hostname_verified = false;
		    				var d = lookup_A.get({name: router.hostname, instanceId: $routeParams.instanceId});
		    				d.$promise.then(function(data){
		    					if(data.objects && data.objects[0].address){
		    						if(data.objects[0].address == router.ip){
		    							router.hostname_verified = true;
		    						}
		    					}
		    				});
		    			}
		    		}
		    	});
		    	reverse_result.$promise.catch(function(error){
		    		$scope.content.async_errors.push({
		    			name: 'HTTP Error ' + error.status,
		    			message: error.statusText
		    		});
		    	});
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