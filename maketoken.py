#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  
#  Copyright 2014 Cilyan Olowen <gaknar@gmail.com>
# 
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the  nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  


import argparse
import sys
import config
import ldapom
import base64
import struct
import os.path
import json
import os

def error(*args, **kwargs):
    kwargs.update(dict(file=sys.stderr))
    print(*args, **kwargs)

def fnv64(data):
    hash_ = 0xcbf29ce484222325
    for b in data:
        hash_ *= 0x100000001b3
        hash_ &= 0xffffffffffffffff
        hash_ ^= b
    return hash_

def hash_dn(dn, salt):
    # Turn dn into bytes with a salt, dn is expected to be ascii data
    data = salt.encode("ascii") + dn.encode("ascii")
    # Hash data
    hash_ = fnv64(data)
    # Pack hash (int) into bytes
    bhash = struct.pack("<Q", hash_)
    # Encode in base64. There is always a padding "=" at the end, because the
    # hash is always 64bits long. We don't need it.
    return base64.urlsafe_b64encode(bhash)[:-1].decode("ascii")

def get_user_info(uid):
    """
        Get the LDAPEntry corresponding to uid, or raises a RuntimeError
    """
    try:
        # Connect and Authenticate as administrator
        con = ldapom.LDAPConnection(
            config.LDAPURL,
            config.USEROU,
            config.ADMINDN,
            config.ADMINPWD
        )
    except ldapom.LDAPServerDownError as e:
        raise RuntimeError("Unable to connect to server") from e
    except ldapom.LDAPInvalidCredentialsError as e:
        raise RuntimeError("Invalid credentials for connection") from e
    # Get handle to user entry
    dn = "uid={},{}".format(uid, config.USEROU)
    entry = con.get_entry(dn)
    if not entry.exists():
        raise RuntimeError("User not found in database")
    return entry

def create(uid, quiet=False):
    # Little helper for properties that are enclosed in sets
    get = lambda x:list(x)[0]
    # Get entry for user
    try:
        entry = get_user_info(uid)
    except RuntimeError as e:
        error("ERROR: {!s}".format(e))
        return -1
    # Hash dn to get unique token
    token = hash_dn(entry.dn, config.SALT)
    filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "instance",
        "tokens",
        token
    )
    # Verify that user doesn't has opened token
    if os.path.exists(filepath):
        error("ERROR: That user already has an opened token")
        return -2
    # Create token file
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                {"dn": entry.dn, "username": get(entry.cn)},
                f, ensure_ascii=False
            )
    except IOError as e:
        error("ERROR: creation of token file failed: {!s}".format(e))
        return -3
    if quiet:
        print(token)
    else:
        print("Created token for {}: {}".format(uid, token))
    return 0
    

def delete(uid, quiet=False):
    # Create dn
    dn = "uid={},{}".format(uid, config.USEROU)
    # Hash dn to get unique token
    token = hash_dn(dn, config.SALT)
    filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "instance",
        "tokens",
        token
    )
    # Verify that user has opened token
    if not os.path.exists(filepath):
        error("ERROR: That user doesn't have a token at the moment")
        return -2
    # Delete token
    try:
        os.remove(filepath)
    except OSError as e:
        error("ERROR: Could not remove token: {!s}".format(e))
        return -3
    if not quiet:
        print("Removed token for {}".format(uid))
    return 0
    

def _cmdline_parser():
    parser = argparse.ArgumentParser(
        description='Manage tokens for user password change'
    )
    parser.add_argument("uid", help="UID of the user")
    parser.add_argument("-q", "--quiet", action="store_true", dest="quiet",
                        help="Fewer information, suitable for automatisation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--create", action="store_const", const="create",
                        dest="action", help="Create token for user")
    group.add_argument("-d", "--delete", action="store_const", const="delete",
                        dest="action", help="Delete token for user")
    return parser

def main():
    args = _cmdline_parser().parse_args()
    action = getattr(sys.modules[__name__], args.action)
    exit(action(args.uid, args.quiet))

if __name__ == "__main__":
    main()
