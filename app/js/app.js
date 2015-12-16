'use strict';

/* App Module */

var torstatApp = angular.module('torstatApp', [
	'ngRoute',
	'torstatControllers',
	'torstatFilters',
	'torstatServices'
]);


torstatApp
	.config(['$routeProvider',
		function($routeProvider) {
			$routeProvider
				.when('/', {
					templateUrl: 'partials/instance-list.html',
					controller: 'InstanceCtrl'
				})
				.when('/:instanceId', {
					templateUrl: 'partials/instance-detail.html',
					controller: 'InstanceCtrl'
				})
				.when('/:instanceId/router/:routerId', {
					templateUrl: 'partials/router-detail.html',
					controller: 'RouterCtrl'
				})
				.when('/:instanceId/stream', {
					templateUrl: 'partials/stream-list.html',
					controller: 'StreamCtrl'
				})
				.when('/:instanceId/circuit', {
					templateUrl: 'partials/circuit-list.html',
					controller: 'CircuitCtrl'
				})
				.when('/:instanceId/circuit/:circuitId', {
					templateUrl: 'partials/circuit-detail.html',
					controller: 'CircuitCtrl'
				})
				.otherwise({
					redirectTo: '/'
				});
		}
	])
	.config(['$resourceProvider', 
		function($resourceProvider) {
			$resourceProvider.defaults.stripTrailingSlashes = false;
		}
	]);