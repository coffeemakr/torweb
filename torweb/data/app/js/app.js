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
					controller: 'TorRessourceCtrl',
					name: 'Torweb'
				})
				.when('/:instanceId', {
					//redirectTo: '/:instanceId/circuit',
					templateUrl: 'partials/instance-detail.html',
					controller: 'TorRessourceCtrl',
					name: 'Instance :instanceId'
				})
				.when('/:instanceId/router/:routerId', {
					templateUrl: 'partials/router-detail.html',
					controller: 'TorRessourceCtrl',
					name: 'Router :routerName'
				})
				.when('/:instanceId/stream', {
					templateUrl: 'partials/stream-list.html',
					controller: 'TorRessourceCtrl',
					name: 'Streams'
				})
				.when('/:instanceId/circuit', {
					templateUrl: 'partials/circuit-list.html',
					controller: 'TorRessourceCtrl',
					name: 'Circuits'
				})
				.when('/:instanceId/circuit/:circuitId', {
					templateUrl: 'partials/circuit-detail.html',
					controller: 'TorRessourceCtrl',
					name: 'Circuit :circuitId'
				})
				.when('/:instanceId/config', {
					templateUrl: 'partials/config-list.html',
					controller: 'TorRessourceCtrl',
					name: 'Configuration'
				})
				.when('/:instanceId/config/:configId', {
					templateUrl: 'partials/config-detail.html',
					controller: 'TorRessourceCtrl',
					name: ':configId'
				})
				.otherwise({
					redirectTo: '/'
				});
		}
	]);