#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, request
import json
import os.path
import ldapom

# Change the default template syntax as it conflicts with angular's
class FlaskSpecialJinja(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update({
        "block_start_string": '<%',
        "block_end_string": '%>',
        "variable_start_string": '<<',
        "variable_end_string": '>>',
        "comment_start_string": '<#',
        "comment_end_string": '#>'
    })

# Create application object and configure it from config.py
app = FlaskSpecialJinja(__name__)
app.config.from_object("config")

# Helper functions to create JSON error messages that can be displayed by NG
err_danger = lambda msg:{"type": "danger", "msg": msg}
err_warning = lambda msg:{"type": "warning", "msg": msg}

def change_password(dn, password):
    """
        Change the password of a user identified by ``dn``.
        
        Return empty list if success, or list of errors if failure.
    """
    try:
        # Connect and Authenticate as administrator
        con = ldapom.LDAPConnection(
            app.config["LDAPURL"],
            app.config["USEROU"],
            app.config["ADMINDN"],
            app.config["ADMINPWD"]
        )
    except ldapom.LDAPServerDownError as e:
        app.logger.error("Unable to connect LDAP server: {!s}".format(e))
        return [err_danger("Could not access LDAP server")]
    except ldapom.LDAPInvalidCredentialsError as e:
        app.logger.error("Invalid credentials for LDAP: {!s}".format(e))
        return [err_danger("Could not access LDAP server")]
    # Get handle to user entry
    entry = con.get_entry(dn)
    if not entry.exists():
        app.logger.error("Error changing the password: User not found")
        return [err_danger("The specified user doesn't exist in the database")]
    # Change password on entry
    try:
        entry.set_password(password)
    except ldapom.LDAPError as e:
        app.logger.error("Error changing the password: {}".format(e))
        return [err_danger("Unable to change the password")]
    return []

def open_token(token):
    """
        Read the data contained in a token file and returns it as a dict.
    """
    fullpath = validate_token(token)
    if fullpath:
        with open(fullpath, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return None

def validate_token(token):
    """
        Try to get the full path to a token file. Return ``None`` if token
        is invalid.
    """
    fullpath = os.path.join(app.instance_path, "tokens", token)
    if os.path.exists(fullpath):
        return fullpath
    else:
        return None

def delete_token(token):
    """
        Delete a token file
    """
    fullpath = validate_token(token)
    if fullpath is None: return
    try:
        os.remove(fullpath)
    except OSError as e:
        app.logger.exception("Cannot delete token {}".format(token), e)

@app.route("/")
def route_root():
    """
        The default route is useless, main page must be accessed with a specific
        URL containing the token.
    """
    return render_template('nothingtosee.html')

@app.route("/<token>")
def route_token(token):
    """
        Main page with a token. Validates the token and return the main page or
        an error page if token is invalid.
    """
    # Special treatment for the file used to make git track the empty folder
    if token == ".keep": return render_template('nothingtosee.html')
    # Obtain information about the user based on token
    data = open_token(token)
    if data:
        # Main page
        return render_template(
            'form.html',
            token=token,
            username=data["username"]
        )
    else:
        # Unknown token, display error page
        return render_template('linkinvalid.html')

@app.route("/changePassword" , methods=['POST'])
def route_changePassword():
    """
        Action to change the password. This route expected to be called with
        XHR and receives its data as JSON.
        It validates the input, changes the password and deletes the token.
    """
    # Get JSON POST data
    post = request.get_json(force=True)
    # Get data from token
    data = open_token(post["token"])
    if not data:
        # Validates token in case of malicious request
        return jsonify({
            "can_retry": 0,
            "errors": [
                {
                    "type": "danger",
                    "msg": "Provided token is invalid"
                }
            ]
        })
    # Validates input in case data was not crafted by NG or client code is
    # deficient.
    if (   post["password"] != post["password_confirm"]
        or len(post["password"]) == 0
    ):
        return jsonify({
            "can_retry": 1,
            "errors": [
                {
                    "type": "danger",
                    "msg": "Password and confirmation do not match"
                }
            ]
        })
    # Change password
    errors = change_password(data["dn"], post["password"])
    if len(errors) == 0:
        # If password has been changed, delete token
        delete_token(post["token"])
        return jsonify({
            "can_retry": 0,
            "errors": []
        })
    else:
        return jsonify({
            "can_retry": 1,
            "errors": errors
        })

if __name__ == "__main__":
    app.run()
