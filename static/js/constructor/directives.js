Constructor.directive("pallet", function () {
    return {
        restrict: 'AE',
        scope: {
            scopeName: "=",
            blockName: "="
        },
        templateUrl: "/static/js/constructor/partials/pallet.html"
    }
});

Constructor.directive("blockDir", function (RecursionHelper) {
    return {
        restrict: 'AE',
        replace: true,
        scope: {
            block: "="
        },
        templateUrl: "/static/js/constructor/partials/block.html",
        compile: function(element) {
            return RecursionHelper.compile(element);
        }
    }
});

Constructor.directive("portsGroup", function () {
    return {
        restrict: 'A',
        replace: true,
        scope: {
            "groupName": '@',
            "block": '='
        },
        templateUrl: "/static/js/constructor/partials/port_group.html",
        controller: function ($scope, blockAccess) {

            $scope.access = blockAccess;
        }

    }
});

Constructor.directive('capitalize', function () {
    // from http://stackoverflow.com/questions/16388562/angularjs-force-uppercase-in-textbox
    return {
        require: 'ngModel',
        link: function (scope, element, attrs, modelCtrl) {
            var capitalize = function (inputValue) {
                if( inputValue == null || inputValue == undefined){
                    return inputValue;
                }
                var capitalized = inputValue.toUpperCase();
                if (capitalized !== inputValue) {
                    modelCtrl.$setViewValue(capitalized);
                    modelCtrl.$render();
                }
                return capitalized;
            }
            modelCtrl.$parsers.push(capitalize);
            capitalize(scope[attrs.ngModel]);  // capitalize initial value
        }
    };
});

Constructor.directive('sigmajs', function() {
		//over-engineered random id, so that multiple instances can be put on a single page
		var divId = 'sigmjs-dir-container-'+Math.floor((Math.random() * 999999999999))+'-'+Math.floor((Math.random() * 999999999999))+'-'+Math.floor((Math.random() * 999999999999));
		return {
			restrict: 'E',
			template: '<div id="'+divId+'" style="width: 100%;height: 100%;"></div>',
			scope: {
				//@ reads the attribute value, = provides two-way binding, & works with functions
				graph: '=',
				width: '@',
				height: '@',
				releativeSizeNode: '='
			},
			link: function (scope, element, attrs) {
				// Let's first initialize sigma:
				var s = new sigma({
					container: divId,
					settings: {
                        defaultNodeColor: '#ec5148',
                        labelThreshold: 4
                    }
				});


				scope.$watch('graph', function(newVal,oldVal) {
                    if(scope.graph) {
                        s.graph.clear();
                        s.graph.read(scope.graph);
                        s.refresh();
                        //if (scope.releativeSizeNode) {
                        //    //this feature needs the plugin to be added
                        //    sigma.plugins.relativeSize(s, 2);
                        //}
                    }
				});

				scope.$watch('width', function(newVal,oldVal) {
					console.log("graph width: "+scope.width);
					element.children().css("width",scope.width);
					s.refresh();
					window.dispatchEvent(new Event('resize')); //hack so that it will be shown instantly
				});
				scope.$watch('height', function(newVal,oldVal) {
					console.log("graph height: "+scope.height);
					element.children().css("height",scope.height);
					s.refresh();
					window.dispatchEvent(new Event('resize'));//hack so that it will be shown instantly
				});

				element.on('$destroy', function() {
					s.graph.clear();
				});

                //s.startForceAtlas2({worker: true, barnesHutOptimize: false});
			}
		};
});
