'use strict';

/* Filters */

angular.module('torstatFilters', []).filter('checkmark', function() {
  return function(input) {
    return input ? '\u2713' : '\u2718';
  };
});


angular.module('torstatFilters', []).filter('statusButton', function() {
  return function(input) {
  	var css = {
  		'NEW': 'btn-info',
		'NEWRESOLVE': 'btn-info',
		'REMAP': 'btn-info',
		'SENTCONNECT': 'btn-info',
		'SENTRESOLVE': 'btn-info',
		'SUCCEEDED': 'btn-success',
		'BUILT': 'btn-success',
		'FAILED': 'btn-danger',
		'CLOSED': 'btn-secondary',
		'DETACHED': 'btn-secondary'
  	}
	return css[input];
  };
});

  	var statusText = {
		'NEW': 'New request to connect',
		'NEWRESOLVE': 'New request to resolve an address',
		'REMAP': 'Address re-mapped to another',
		'SENTCONNECT': 'Sent a connect cell along a circuit',
		'SENTRESOLVE': 'Sent a resolve cell along a circuit',
		'SUCCEEDED': 'Received a reply; stream established',
		'FAILED': 'Stream failed and not retriable',
		'CLOSED': 'Stream closed',
		'DETACHED': 'Detached from circuit; still retriable',
	};



 