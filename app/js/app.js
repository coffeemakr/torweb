'use strict';

/* App Module */

var torstatApp = angular.module('torstatApp', [
  'ngRoute',
  'torstatControllers',
  'torstatFilters',
  'torstatServices'
]);


torstatApp.config(['$provide', function($provide){
        $provide.decorator('$rootScope', ['$delegate', function($delegate){

            Object.defineProperty($delegate.constructor.prototype, '$onRootScope', {
                value: function(name, listener){
                    var unsubscribe = $delegate.$on(name, listener);
                    this.$on('$destroy', unsubscribe);

                    return unsubscribe;
                },
                enumerable: false
            });


            return $delegate;
        }]);
}]);

torstatApp.config(['$routeProvider',
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
      when('/circuits/:circuitId', {
        templateUrl: 'partials/circuit-detail.html',
        controller: 'CircuitDetailCtrl'
      }).
      otherwise({
        redirectTo: '/circuits'
      });
  }]);


torstatApp.config(function($resourceProvider) {
  $resourceProvider.defaults.stripTrailingSlashes = false;
});