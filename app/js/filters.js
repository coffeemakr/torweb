'use strict';

/* Filters */
angular.module('torstatFilters', [])
	.filter('statusStyleSuffix', function() {
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
				'CLOSED': 'default',
				'DETACHED': 'default',
			}
			var prefix = css[input];
			if(typeof prefix == 'undefined'){
				prefix = 'default';
			}
			return prefix;
		};
	})
	.filter('Bytes', function() { 
		return function(input) {
			if (typeof input == 'number') {
				var unit_index = 0;
				while(input > 1000 && unit_index < 4) {
					input /= 1000.0;
					unit_index++;
				}
				var unit = [
					'B',
					'KB',
					'MB',
					'GB',
					'TB'
				];
				unit = unit[unit_index];
				input = input.toFixed(2).toString() + unit;
			}
			return input;
		};
	})
	.filter('RouterFlags', function(){
		return function(input){
			return{
				'fast': 'rocket',
				'exit': 'sign-out',
				'guard': 'sign-in',
				'stable': 'clock',
				'running': 'check'
			}[input];
		}
	});
