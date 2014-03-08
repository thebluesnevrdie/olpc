'use strict';

var UsrAdmApp = angular.module('UsrAdmApp', ['ngAnimate', 'ui.bootstrap']);

UsrAdmApp.controller('UsrAdmCtrl', function ($scope, $http, $timeout) {
    /* Init scope */
    $scope.show_form = true;
    $scope.show_ok = false;
    $scope.show_invalid = false;
    $scope.uploading = false;
    $scope.user = {
        name: username,
        token: token
    };
    
    /* Alert Handling */
    $scope.alerts = [];
    $scope.closeAlert = function (index) {
        $scope.alerts.splice(index, 1);
    };
    
    /* Update password to server */
    $scope.update = function (user) {
        $scope.uploading = true;
        $http.post("changePassword", user).success(
            function (data, status, headers, config) {
                $scope.uploading = false;
                if (data["errors"].length > 0) {
                    $scope.alerts = $scope.alerts.concat(data["errors"]);
                    if (data["can_retry"] == 0) {
                        $scope.show_form = false;
                        $scope.show_ok = false;
                        $scope.show_invalid = true;
                    }
                }
                else {
                    $scope.show_form = false;
                    $scope.show_ok = true;
                    $scope.show_invalid = false;
                }
            }
        ).error(
            function (data, status, headers, config) {
                $scope.uploading = false;
                $scope.alerts.push({
                    type: "danger",
                    msg: "Error during communication with server, you may try later"
                });
            }
        );
    };
});
