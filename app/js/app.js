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
      $routeProvider.
        when('/router/:routerId', {
          templateUrl: 'partials/router-detail.html',
          controller: 'RouterDetailCtrl'
        }).
        when('/streams', {
          templateUrl: 'partials/stream-list.html',
          controller: 'StreamListCtrl'
        }).
        when('/circuits', {
          templateUrl: 'partials/circuit-list.html',
          controller: 'CircuitListCtrl'
        }).
        when('/circuit/:circuitId', {
          templateUrl: 'partials/circuit-detail.html',
          controller: 'CircuitDetailCtrl'
        }).
        otherwise({
          redirectTo: '/circuits'
        });
    }
  ])
  .config(['$resourceProvider', 
    function($resourceProvider) {
      $resourceProvider.defaults.stripTrailingSlashes = false;
    }
  ]);