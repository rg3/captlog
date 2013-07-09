captlog - The Captain's Log (secret diary and notes application)
================================================================

Description
-----------

captlog is a small application that helps you keep a secret diary in your
computer. It encrypts the contents of every diary entry with a secret password
or passphrase you must provide the first time you run the program.

Entries are sorted by date and displayed in the left pane. In addition, it has a
bookmarks facility that helps you bookmark interesting entries (that you may
want to modify or update in the future, for example) by giving them a readable
name or title.

Under the hood, it uses AES-256 in CTR mode for encryption, combined with
HMAC-SHA256.


Installation
------------

captlog is distributed in source form and requires PyCrypto 2.6 or newer in
addition to a standard Python2 installation. It should work in every platform
supported by Python and PyCrypto. This includes Linux, Mac OSX and Windows.

To install it, first install Python2 and PyCrypto (sometimes distributed as
python-crypto in some Linux distributions). Then, from the source directory of
captlog, type the following from the command line.

---------------------------------
python setup.py install
---------------------------------


License
-------

This file is part of captlog.

captlog - The Captain's Log (secret diary and notes application)

Written in 2013 by Ricardo Garcia <public@rg3.name>

To the extent possible under law, the author(s) have dedicated all copyright
and related and neighboring rights to this software to the public domain
worldwide. This software is distributed without any warranty.

You should have received a copy of the CC0 Public Domain Dedication along with
this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
