#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of captlog.
#
# captlog - The Captain's Log (secret diary and notes application)
#
# Written in 2013 by Ricardo Garcia <r@rg3.name>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along with
# this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

# Standard libraries.
from datetime import datetime
import os
import os.path
import sqlite3
from exceptions import Exception, NotImplementedError, StandardError

# PyCrypto.
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256

class Error(Exception):
    """An exception from the storage backend."""
    def __init__(self, msg):
        Exception.__init__(self, msg)

class LogEntry(object):
    """A diary log entry, containing the following items:

    id_le   The log entry identifier.
    ctime   The log entry creation time.
    mtime   The log entry modification time.
    data    The log entry contents, which may be None.

    Note: log entries can be sorted by creation time.
    """
    def __init__(self, id_le, ctime, mtime, data=None):
        self.id_le = id_le
        self.ctime = ctime
        self.mtime = mtime
        self.data = data

    def __cmp__(self, other):
        return cmp(self.ctime, other.ctime)

class Bookmark(object):
    """A bookmark to an entry in the log. Contains:

    id_bm   The bookmark identifier.
    id_le   The log entry identifier the bookmark refers to.
    text    The bookmark text or name.

    Note: bookmarks can be sorted by text.
    """
    def __init__(self, id_bm, id_le, text):
        self.id_bm = id_bm
        self.id_le = id_le
        self.text = text

    def __cmp__(self, other):
        return cmp(self.text, other.text)

class StorageBackend(object):
    """Storage backend. Handles storing and retrieving entries and bookmarks.
    
    This is an abstract class from which to derive classes that implement real
    storage backends. Most methods can raise an exception from the storage
    backend."""

    @classmethod
    def first_run(cls):
        """Before creating an instance, this method can be called to check
        wether this would be the first time an instance of this class is
        initialized in the system. This helps initializers ask for a passphrase
        twice instead of one or perform other external initialization routines.
        """
        raise NotImplementedError()

    def __init__(self, passphrase):
        """Builds an instance. Requires a passphrase to initialize the
        backend."""
        raise NotImplementedError()

    def list_entries(self):
        """Returns a list of entries. The entry data members in the list may be
        None even if actual content was previusly stored for each entry.
        
        For backends implemeting encryption, doing this helps delaying entry
        decryption until it's really needed."""
        raise NotImplementedError()

    def new_entry(self):
        """Creates and returns a new entry."""
        raise NotImplementedError()

    def save_entry(self, entry):
        """Saves an entry."""
        raise NotImplementedError()

    def get_entry(self, id_le):
        """Given the entry identifier, returns an entry. This method only
        returns None in the entry data if no data was stored for the entry."""
        raise NotImplementedError()

    def del_entry(self, id_le):
        """Deletes an entry by its entry identifier."""
        raise NotImplementedError()

    def list_bookmarks(self):
        """Returns the list of stored bookmarks."""
        raise NotImplementedError()

    def new_bookmark(self, id_le, text):
        """Creates a new bookmark for the given entry with the given text."""
        raise NotImplementedError()

    def del_bookmark(self, id_bm):
        """Deletes a bookmark given its identifier."""
        raise NotImplementedError()

#class _SafetyNet(object):
#    def __init__(self, msg):
#        self.message = msg
#
#    def __call__(self, fn):
#        def ret(*args, **kwargs):
#            try:
#                fn(*args, **kwargs)
#            except Error:
#                raise
#            except (StandardError, ), e:
#                raise Error(self.message + ': ' + '%r' % (e, ))
#        return ret

class DefaultStorageBackend(StorageBackend):
    """Default storage backend, implementing entry data encryption by using
    AES-256 in CTR mode."""

    DB_PATH = os.path.join(os.path.expanduser('~'), '.captlog', 'captlog.db')
    SALT_SIZE = 32
    AES_KEY_SIZE = 32
    PBKDF2_ITERATIONS = 20000
    REFERENCE_TEXT = 'CAPTAINS LOG'

    def _create_empty_db(self):
        self._dbcon.execute("""
            create table verification (prop_name, prop_value);
            """)
        self._dbcon.execute("""
            create table logentry (
                id_le integer primary key,
                ctime text,
                mtime text,
                data text
            );
            """)
        self._dbcon.execute("""
            create table logentry_crypto (
                id_le integer references logentry(id_le),
                prop_name, prop_value
            );
            """)
        self._dbcon.execute("""
            create table bookmark (
                id_bm integer primary key,
                id_le integer references logentry(id_le),
                bookmark_text text
            );
            """)
        self._dbcon.execute("""
            create trigger logentry_clean before delete on logentry
            begin
                delete from logentry_crypto where id_le = OLD.id_le;
                delete from bookmark where id_le = OLD.id_le;
            end;
            """)

    def _get_key(self, passphrase, salt, iterations):
        return PBKDF2(passphrase, salt, self.AES_KEY_SIZE, iterations)

    def _get_hmac(self):
        return HMAC.new(self._key, digestmod=SHA256)

    def _get_cipher_nonce(self, nonce=None):
        if nonce is None:
            nonce = self._rbg.read(AES.block_size)
        val = sum(ord(e)*(256**x) for (x, e) in enumerate(nonce))
        counter = Counter.new(AES.block_size*8, initial_value=val)
        cipher = AES.new(self._key, mode=AES.MODE_CTR, counter=counter)
        return (cipher, nonce)

    @classmethod
    def first_run(cls):
        p = cls.DB_PATH
        return not (os.path.exists(p) and os.path.isfile(p))

    def __init__(self, passphrase):
        # Members needed at the end of this constructor.
        # self._dbcon   Database connection.
        # self._rbg     Random bytes generator.
        # self._key     Encoding key.

        self._rbg = Random.new() # Random bytes generator.
        db_path = self.DB_PATH

        if not os.path.exists(db_path):
            # Make directories.
            dirname = os.path.dirname(db_path)
            try:
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
            except (IOError, OSError), e:
                raise Error('unable to create directory %s' % (dirname, ))

            if not (os.path.isdir(dirname) and os.access(dirname, os.W_OK)):
                raise Error('%s not a writable directory' % (dirname, ))

            # Prepare verification table.
            salt = self._rbg.read(self.SALT_SIZE)
            self._key = self._get_key(passphrase, salt, self.PBKDF2_ITERATIONS)
            cipher, nonce = self._get_cipher_nonce()
            verifier = cipher.encrypt(self.REFERENCE_TEXT)

            table = [
                     ('kdf', 'PBKDF2'),
                     ('salt', salt.encode('base64')),
                     ('iterations', self.PBKDF2_ITERATIONS),
                     ('cipher', 'AES-256'),
                     ('nonce', nonce.encode('base64')),
                     ('verifier', verifier.encode('base64')),
                    ]

            # Create database and store table.
            try:
                self._dbcon = sqlite3.connect(
                        db_path, detect_types=(sqlite3.PARSE_DECLTYPES |
                                               sqlite3.PARSE_COLNAMES))
                self._create_empty_db()
                self._dbcon.executemany("""
                    insert into verification (prop_name, prop_value)
                        values (?, ?);""", table)
                self._dbcon.commit()
            except (IOError, OSError, sqlite3.error), e:
                raise Error('unable to create database')

        else:
            # Connect to database and retrieve verification table.
            if not (os.path.isfile(db_path) and
                    os.access(db_path, (os.R_OK | os.W_OK))):
                raise Error('%s not readable and writable' % (db_path, ))

            try:
                self._dbcon = sqlite3.connect(
                        db_path, detect_types=(sqlite3.PARSE_COLNAMES |
                                               sqlite3.PARSE_DECLTYPES))
                cursor = self._dbcon.cursor()
                cursor.execute('select * from verification;')
                table = dict(cursor.fetchall())
            except (sqlite3.error, ), e:
                raise Error('unable to access verification table')

            for k in ['kdf','salt','iterations','cipher','nonce','verifier']:
                if k not in table:
                    raise Error('verification table missing "%s"' % (k, ))

            # Check basic metadata fields.
            if table['kdf'] != 'PBKDF2':
                raise Error('unknown key derivation function')
            if table['cipher'] != 'AES-256':
                raise Error('unknown cipher')

            # Generate key and verify it.
            salt = table['salt'].decode('base64')
            self._key = self._get_key(passphrase, salt, table['iterations'])
            nonce = table['nonce'].decode('base64')
            cipher, nonce = self._get_cipher_nonce(nonce=nonce)
            verifier = table['verifier'].decode('base64')
            if cipher.decrypt(verifier) != self.REFERENCE_TEXT:
                raise Error('wrong passphrase')

    #@_SafetyNet('unable to list entries')
    def list_entries(self):
        cursor = self._dbcon.cursor()
        cursor.execute(
            """select id_le,
                      ctime as "ctime [timestamp]",
                      mtime as "mtime [timestamp]"
               from logentry;""")
        rows = cursor.fetchall()
        entries = [LogEntry(*x) for x in rows]
        return entries
        
    #@_SafetyNet('unable to create new entry')
    def new_entry(self):
        cursor = self._dbcon.cursor()
        now = datetime.utcnow()
        cursor.execute(
                'insert into logentry(ctime, mtime) values (?, ?);', (now, now)
                )
        self._dbcon.commit()
        return LogEntry(cursor.lastrowid, now, now)

    #@_SafetyNet('unable to save entry')
    def save_entry(self, entry):
        cursor = self._dbcon.cursor()
        cursor.execute(
            'select * from logentry where id_le = ?;', (entry.id_le, ))
        if len(cursor.fetchall()) == 0:
            raise Error('entry %r does not exist yet' % (entry.id_le, ))
        cursor.execute(
                'delete from logentry_crypto where id_le = ?;', (entry.id_le, )
                )
        if entry.data is None:
            stored_data = None
        else:
            cipher, nonce = self._get_cipher_nonce()
            stored_data = cipher.encrypt(entry.data)
            hmac = self._get_hmac()
            hmac.update(stored_data)
            digest = hmac.hexdigest()
        if stored_data is not None:
            properties = [
                    (entry.id_le, 'cipher', 'AES-256'),
                    (entry.id_le, 'nonce', nonce.encode('base64')),
                    (entry.id_le, 'hmac', 'HMAC-SHA256'),
                    (entry.id_le, 'digest', digest),
                    ]
            cursor.executemany(
                    'insert into logentry_crypto values(?, ?, ?);', properties
                    );
            stored_data = stored_data.encode('base64')
        cursor.execute("""
            update logentry set ctime = ?, mtime = ?, data = ? where id_le = ?;
            """,
            (entry.ctime, entry.mtime, stored_data, entry.id_le))
        self._dbcon.commit()

    #@_SafetyNet('unable to get entry')
    def get_entry(self, id_le):
        cursor = self._dbcon.cursor()
        cursor.execute(
                """select id_le, ctime as "ctime [timestamp]",
                          mtime as "mtime [timestamp]", data
                   from logentry where id_le = ?;""", (id_le, )
                )
        row = cursor.fetchone()
        if row is None:
            raise Error('entry not found')
        entry = LogEntry(*row)
        if entry.data is not None:
            cursor.execute("""
                select prop_name, prop_value from logentry_crypto
                    where id_le = ?;""", (id_le, ))
            props = dict(cursor.fetchall())
            for k in ['cipher', 'nonce', 'hmac', 'digest']:
                if k not in props:
                    raise Error('"%s" missing from entry crypto metadata' %
                                (k,))
            if props['cipher'] != 'AES-256' or props['hmac'] != 'HMAC-SHA256':
                raise Error('unknown cipher or hmac for entry')

            # Decrypt and verify entry contents.
            encrypted = entry.data.decode('base64')
            hmac = self._get_hmac()
            hmac.update(encrypted)
            if hmac.hexdigest() != props['digest']:
                raise Error('entry digest does not match')
            nonce = props['nonce'].decode('base64')
            cipher, nonce = self._get_cipher_nonce(nonce=nonce)
            decrypted = cipher.decrypt(encrypted)
            entry.data = decrypted

        return entry

    #@_SafetyNet('unable to delete entry')
    def del_entry(self, id_le):
        self._dbcon.execute('delete from logentry where id_le = ?;', (id_le, ))
        self._dbcon.commit()

    #@_SafetyNet('unable to list bookmarks')
    def list_bookmarks(self):
        cursor = self._dbcon.cursor()
        cursor.execute('select * from bookmark;')
        rows = cursor.fetchall()
        rows = [(x, y, z.decode('base64')) for (x, y, z) in rows]
        bookmarks = [Bookmark(*x) for x in rows]
        return bookmarks

    #@_SafetyNet('unable to bookmark entry')
    def new_bookmark(self, id_le, text):
        cursor = self._dbcon.cursor()
        cursor.execute(
            'insert into bookmark (id_le, bookmark_text) values (?, ?);',
            (id_le, text.encode('base64')))
        id_bm = cursor.lastrowid
        self._dbcon.commit()
        return Bookmark(id_bm, id_le, text)

    #@_SafetyNet('unable to delete bookmark')
    def del_bookmark(self, id_bm):
        self._dbcon.execute('delete from bookmark where id_bm = ?;', (id_bm, ))
        self._dbcon.commit()

