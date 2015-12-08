'use strict';

/* Filters */

angular.module('torstatFilters', []).filter('checkmark', function() {
  return function(input) {
    return input ? '\u2713' : '\u2718';
  };
});


angular.module('torstatFilters', []).filter('statusStyleSuffix', function() {
  return function(input) {
  	var css = {
  		'NEW': 'info',
		'NEWRESOLVE': 'info',
		'REMAP': 'info',
		'SENTCONNECT': 'info',
		'SENTRESOLVE': 'info',
		'SUCCEEDED': 'success',
		'BUILT': 'success',
		'FAILED': 'danger',
		'CLOSED': 'secondary',
		'DETACHED': 'secondary'
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



 