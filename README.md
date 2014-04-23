Online LDAP Password Changer
============================

This little [Flask][] / [Angular.js][] application allows users to change their password online from an LDAP directory when they receive a secret URL from an administrator.

An administrator creates a token for a user using the `maketoken.py` script. They then sends this token to the user containing the token in the form `https://example.com/path_to_app/<token>`.

When following the link, the user is presented a form where they can change their password.

The application makes use of the nice [ldapom][] module to access the LDAP directory and should work with Python 2.7 and higher (tested with 2.7, 3.3 and 3.4).

[Flask]: http://flask.pocoo.org/
[Angular.js]: http://angularjs.org/
[ldapom]: https://github.com/HaDiNet/ldapom

Installation
------------

Simply clone this repository somewhere and make sure the `instance/tokens` folder is writable to the user running the application, but also to the user running `maketoken.py`.

Adapt the `config.py` file to your environment:

 - *DEBUG*: A boolean indicating Flask to run in debug mode or in production mode
 - *ADMINDN*: A string describing the LDAP bind administrator user that can change passwords for users
 - *ADMINPWD*: Password for the administrator account
 - *LDAPURL*: The url used to connect to the LDAP service
 - *USEROU*: The organisational unit where users will be searched
 - *SALT*: An **ASCII** string that will be used as salt to produce tokens

The application is contained in `app.py` which is a regular Flask application that you can run standalone or with any WSGI server.

Included External Resources
---------------------------

The image provided as default background is a modified version of an original work by [Wolfgang Arnold][arnie] proposed on [OpenPhoto][] under the [CC-BY-SA][] license. As such the resulting `bg.jpg` is also under the [Creative Commons BY-SA 3.0][CC-BY-SA] license.

[arnie]: http://openphoto.net/user/profile/arnie
[OpenPhoto]: http://openphoto.net/
[CC-BY-SA]: https://creativecommons.org/licenses/by-sa/3.0/

License
-------

Apart from the above mentioned work, this application is provided under the 3-Clause BSD license.
