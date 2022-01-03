'use strict'

UsrAdmApp = angular.module 'UsrAdmApp', ['ngAnimate', 'ui.bootstrap']

UsrAdmApp.controller 'UsrAdmCtrl', class

    constructor: (@$scope, @$http, @$timeout) ->
        # Init scope
        @show_form = true
        @show_ok = false
        @show_invalid = false
        @uploading = false
        @user = {
            name: username,
            token: token
        }
    
        # Alert Handling
        @alerts = []
        return null
    
    closeAlert: (index) ->
        @alerts.splice(index, 1)
        return null
    
    # Update password to server
    update: (user) ->
        @uploading = true
        @$http.post("changePassword", user).success(
            (data, status, headers, config) =>
                @uploading = false
                if data["errors"].length > 0
                    @alerts = @alerts.concat(data["errors"])
                    if data["can_retry"] is 0
                        @show_form = false
                        @show_ok = false
                        @show_invalid = true
                else
                    @show_form = false
                    @show_ok = true
                    @show_invalid = false
                return null
        ).error(
            (data, status, headers, config) =>
                @uploading = false
                @alerts.push({
                    type: "danger",
                    msg: "Error during communication with server, you may try later"
                })
                return null
        )
        return null
