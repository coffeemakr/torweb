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
					controller: 'InstanceListCtrl'
				})
				.when('/:instanceId', {
					redirectTo: '/:instanceId/circuits',
					templateUrl: 'partials/instance-detail.html',
					controller: 'InstanceDetailCtrl'
				})
				.when('/:instanceId/router/:routerId', {
					templateUrl: 'partials/router-detail.html',
					controller: 'RouterDetailCtrl'
				})
				.when('/:instanceId/streams', {
					templateUrl: 'partials/stream-list.html',
					controller: 'StreamListCtrl'
				})
				.when('/:instanceId/circuits', {
					templateUrl: 'partials/circuit-list.html',
					controller: 'CircuitListCtrl'
				})
				.when('/:instanceId/circuit/:circuitId', {
					templateUrl: 'partials/circuit-detail.html',
					controller: 'CircuitDetailCtrl'
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