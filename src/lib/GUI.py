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

# Standard modules.
import Tkinter
import ttk
import tkFont
import tkMessageBox
import tkSimpleDialog
import os.path
from datetime import datetime

# Our modules.
import StorageBackend

WINDOW_CLASS = 'captlog'

class BackendInitializer(object):
    BUTTON_NORMAL_TEXT = 'Done'
    BUTTON_WAIT_TEXT = 'Generating key...'

    def __init__(self, backend_class):
        self._backend_class = backend_class
        self._backend = None
        self._confirmation = self._backend_class.first_run()

        if self._confirmation:
            title_text = 'Initial Setup'
            help_text = 'Please enter and confirm a passphrase below:'
        else:
            title_text = 'Passphrase Confirmation'
            help_text = 'Please enter the passphrase below:'

        self.root = Tkinter.Tk(className=WINDOW_CLASS)
        self.root.title('%s: %s' % (WINDOW_CLASS, title_text))

        # Widgets.
        self.frame = ttk.Frame(self.root)
        self.help_label = ttk.Label(self.frame, text=help_text)
        self.passphrase_label = ttk.Label(self.frame, text='Passphrase:')
        self.confirm_label = (ttk.Label(self.frame, text='Confirm passphrase:')
                if self._confirmation else None)
        self.passphrase_entry = ttk.Entry(self.frame, show='*')
        self.confirm_entry = (ttk.Entry(self.frame, show='*')
                if self._confirmation else None)
        self.result_label = ttk.Label(self.frame, foreground='red')
        self.done_button = ttk.Button(self.frame, command=self._init_backend)
        self.root.bind('<Return>', self._init_backend)
        self.root.bind('<KP_Enter>', self._init_backend)

        # Layout.
        pad = { 'padx': 5, 'pady': 5 }
        self.frame.grid(row=0, column=0, **pad)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        row = 0
        self.help_label.grid(row=row, column=0, columnspan=2,
                             sticky=Tkinter.W, **pad)
        row += 1
        self.passphrase_label.grid(row=row, column=0, sticky=Tkinter.E, **pad)
        self.passphrase_entry.grid(row=row, column=1, **pad)
        row += 1
        if self._confirmation:
            self.confirm_label.grid(row=row, column=0, sticky=Tkinter.E, **pad)
            self.confirm_entry.grid(row=row, column=1, **pad)
        row += 1
        self.result_label.grid(row=row, column=0, columnspan=2, **pad)
        row += 1
        self.done_button.grid(row=row, column=0, columnspan=2, **pad)

        self._gui_reset('', self.BUTTON_NORMAL_TEXT, 'enabled')

    def _gui_reset(self, rtext, btext, bstate):
        self.result_label['text'] = rtext
        self.done_button['text'] = btext
        self.done_button['state'] = bstate
        self.passphrase_entry.focus()
        self.root.update()

    def _init_backend(self, *args, **kwargs):
        p = self.passphrase_entry.get()
        if len(p) <= 0:
            self.result_label['text'] = 'Passphrase cannot be empty'
            return
        if self._confirmation:
            pk2 = self.confirm_entry.get()
            if p != pk2:
                self.result_label['text'] = 'Passphrases do not match'
                return
        try:
            self._gui_reset('', self.BUTTON_WAIT_TEXT, 'disabled')
            backend = self._backend_class(p)
            self._backend = backend
            self.root.destroy()
        except (StorageBackend.Error, ), e:
            self._gui_reset('Error: %s' % e.message,
                            self.BUTTON_NORMAL_TEXT, 'enabled')

    def get_backend(self):
        self.root.mainloop()
        return self._backend

class DefaultGUI(object):
    DEFAULT_PADDING = 10
    DEFAULT_COMPOUND = 'left'
    DEFAULT_LISTBOX_HEIGHT = 25

    EXPAND = { 'sticky': (Tkinter.N, Tkinter.W, Tkinter.E, Tkinter.S) }
    VPADEXPAND = dict({ 'pady': DEFAULT_PADDING }, **EXPAND)
    HPADEXPAND = dict({ 'padx': DEFAULT_PADDING }, **EXPAND)
    PADEXPAND = dict({
        'padx': DEFAULT_PADDING,
        'pady': DEFAULT_PADDING, },
        **EXPAND )
    FULLPADEXPAND = dict({
        'ipadx': DEFAULT_PADDING,
        'ipady': DEFAULT_PADDING, },
        **PADEXPAND )

    IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'pixmap')
    TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

    def _display_backend_error(self, e):
        tkMessageBox.showerror(title="%s: Storage Error" % WINDOW_CLASS,
                               message=("Error: %s" % (e.message, )))

    def _is_valid_list_index(self, i, lst):
        return (i is not None and i >= 0 and i < len(lst))

    def _is_valid_entry_index(self, index):
        return self._is_valid_list_index(index, self._entries_list)

    def _is_valid_bookmark_index(self, index):
        return self._is_valid_list_index(index, self._bookmarks_list)

    def _select_entry_in_listbox(self, index):
        self.entry_listbox.selection_clear(0, 'end')
        if index is not None:
            self.entry_listbox.selection_set(index)
        self._current_entry_index = index

    def _select_bookmark_in_listbox(self, index):
        self.bookmark_listbox.selection_clear(0, 'end')
        if index is not None:
            self.bookmark_listbox.selection_set(index)
        self._current_bookmark_index = index

    def _do_select_bookmark(self, index):
        if (self._is_valid_bookmark_index(index) and
            index == self._current_bookmark_index):
            return

        if self._is_valid_bookmark_index(index):
            entry_index = self._entry_index_by_id(
                    self._bookmarks_list[index].id_le)
            self._do_change_entry(entry_index)
            self.del_bookmark_button['state'] = 'enabled'
        else:
            self.del_bookmark_button['state'] = 'disabled'

        self._select_bookmark_in_listbox(index)

    def _do_change_entry(self, index):
        if (self._is_valid_entry_index(index) and
            index == self._current_entry_index):
            return

        if self.entry_text.edit_modified():
            if tkMessageBox.askyesno(
                "%s: Current entry modified" % WINDOW_CLASS,
                "Save current entry?"):
                self._save_button_handler()

        if self._is_valid_entry_index(index):
            log_entry = self._entries_list[index]

            if log_entry.data is None:
                try:
                    log_entry = self._backend.get_entry(log_entry.id_le)
                except (StorageBackend.Error, ), e:
                    self._display_backend_error(e)
                    return

            ctime = log_entry.ctime.strftime(self.TIME_FORMAT)
            mtime = log_entry.mtime.strftime(self.TIME_FORMAT)
            self.ctime_value_label['text'] = ctime
            self.mtime_value_label['text'] = mtime
            self.entry_text.delete('0.0', 'end')
            self.entry_text['state'] = 'normal'
            if log_entry.data is not None:
                self.entry_text.insert('0.0', log_entry.data)
            self.save_button['state'] = 'enabled'
            self.new_bookmark_button['state'] = 'enabled'
            self.del_entry_button['state'] = 'enabled'
            self.entry_text.focus()
        else:
            self.ctime_value_label['text'] = ''
            self.mtime_value_label['text'] = ''
            self.entry_text.delete('0.0', 'end')
            self.entry_text['state'] = 'disabled'
            self.save_button['state'] = 'disabled'
            self.new_bookmark_button['state'] = 'disabled'
            self.del_entry_button['state'] = 'disabled'

        self._select_entry_in_listbox(index)
        self.entry_text.edit_modified(False)

    def _entry_index_by_id(self, entry_id):
        if entry_id is None:
            return None

        positions = [x for x in xrange(len(self._entries_list))
                     if self._entries_list[x].id_le == entry_id]
        return (None if len(positions) <= 0 else positions[0])

    def _bookmark_index_by_id(self, bookmark_id):
        if bookmark_id is None:
            return None

        positions = [x for x in xrange(len(self._bookmarks_list))
                     if self._bookmarks_list[x].id_bm == bookmark_id]
        return (None if len(positions) <= 0 else positions[0])

    def _update_entry_list(self):
        current_entry_id = (None if self._current_entry_index is None else
                            self._entries_list[self._current_entry_index].id_le)

        try:
            self._entries_list = self._backend.list_entries()
        except (StorageBackend.Error, ), e:
            self._display_backend_error(e)
            return

        self._entries_list.sort(reverse=True)
        self.entry_listbox.delete(0, 'end')
        for e in self._entries_list:
            self.entry_listbox.insert('end', e.ctime.strftime(self.TIME_FORMAT))

        pos = self._entry_index_by_id(current_entry_id)
        self._do_change_entry(pos)

    def _update_bookmarks_list(self):
        current_bookmark_id = (None if self._current_bookmark_index is None else
            self._bookmarks_list[self._current_bookmark_index].id_bm)

        try:
            self._bookmarks_list = self._backend.list_bookmarks()
        except (StorageBackend.Error, ), e:
            self._display_backend_error(e)
            return

        self._bookmarks_list.sort()

        self.bookmark_listbox.delete(0, 'end')
        for b in self._bookmarks_list:
            self.bookmark_listbox.insert('end', b.text)

        pos = self._bookmark_index_by_id(current_bookmark_id)
        self._do_select_bookmark(pos)

    def _get_current_entry(self):
        if not self._is_valid_entry_index(self._current_entry_index):
            return None
        return self._entries_list[self._current_entry_index]

    def _save_button_handler(self, *args):
        entry = self._get_current_entry()
        if entry is None:
            return
        entry.data = self.entry_text.get('0.0', 'end')
        entry.mtime = datetime.utcnow()

        try:
            self._backend.save_entry(entry)
        except (StorageBackend.Error, ), e:
            self._display_backend_error(e)
            return

        self.save_button['state'] = 'disabled'
        self.save_button['state'] = 'enabled'
        mtime_text = entry.mtime.strftime(self.TIME_FORMAT)
        self.mtime_value_label['text'] = mtime_text
        self.entry_text.edit_modified(False)

    def _new_entry_button_handler(self, *args):
        try:
            new_entry = self._backend.new_entry()
        except (StorageBackend.Error, ), e:
            self._display_backend_error(e)
            return

        self._entries_list[:0] = [new_entry]
        if self._current_entry_index is not None:
            self._current_entry_index += 1
        self.entry_listbox.insert(0, new_entry.ctime.strftime(self.TIME_FORMAT))
        self._do_change_entry(0)

    def _del_entry_button_handler(self, *args):
        entry = self._get_current_entry()
        if entry is None:
            return
        if tkMessageBox.askyesno(
                "%s: Confirm deletion",
                "Are you sure you want to delete this entry?"):
            # Mark as not modified to avoid being asked to save entry.
            try:
                self._backend.del_entry(entry.id_le)
            except (StorageBackend.Error, ), e:
                self._display_backend_error(e)
                return

            self.entry_text.edit_modified(False)
            self._update_entry_list()
            self._update_bookmarks_list()

    def _new_bookmark_button_handler(self, *args):
        entry = self._get_current_entry()
        if entry is None:
            return
        text = tkSimpleDialog.askstring(
                "%s: New Bookmark" % WINDOW_CLASS, "Bookmark name:")
        if text is None:
            return

        try:
            bookmark = self._backend.new_bookmark(entry.id_le, text)
        except (StorageBackend.Error, ), e:
            self._display_backend_error(e)
            return

        self._update_bookmarks_list()
        pos = self._bookmark_index_by_id(bookmark.id_bm)
        self._do_select_bookmark(pos)

    def _del_bookmark_button_handler(self, *args):
        if not self._is_valid_bookmark_index(self._current_bookmark_index):
            return
        bookmark = self._bookmarks_list[self._current_bookmark_index]

        try:
            self._backend.del_bookmark(bookmark.id_bm)
        except (StorageBackend.Error, ), e:
            self._display_backend_error(e)
            return

        self._do_select_bookmark(None)
        self._update_bookmarks_list()

    def _entry_listbox_select_handler(self, *args):
        selection = self.entry_listbox.curselection()
        if len(selection) <= 0:
            return
        sel = selection[0]
        if not self._is_valid_entry_index(sel):
            return
        # Selected bookmark no longer valid after this.
        self._current_bookmark_index = None
        self._do_change_entry(sel)

    def _bookmark_listbox_select_handler(self, *args):
        selection = self.bookmark_listbox.curselection()
        if len(selection) <= 0:
            return
        sel = selection[0]
        if not self._is_valid_bookmark_index(sel):
            return
        self._do_select_bookmark(sel)

    def __init__(self, backend):
        self._backend = backend
        self._entries_list = []
        self._bookmarks_list = []
        self._current_entry_index = None
        self._current_bookmark_index = None

        #
        # Widgets.
        # 

        # Main window frame.
        self.root = Tkinter.Tk(className=WINDOW_CLASS)
        self.root.title("%s: The Captain's Log" % (WINDOW_CLASS, ))
        self.main_frame = ttk.Frame(self.root)

        # Images.
        new_img_path = os.path.join(self.IMAGE_PATH, 'new.png')
        del_img_path = os.path.join(self.IMAGE_PATH, 'delete.png')
        save_img_path = os.path.join(self.IMAGE_PATH, 'save.png')
        exit_img_path = os.path.join(self.IMAGE_PATH, 'exit.png')
        self.new_img = Tkinter.PhotoImage(file=new_img_path)
        self.del_img = Tkinter.PhotoImage(file=del_img_path)
        self.save_img = Tkinter.PhotoImage(file=save_img_path)
        self.exit_img = Tkinter.PhotoImage(file=exit_img_path)

        # Fonts.
        self.bold_font = tkFont.nametofont('TkDefaultFont').copy()
        self.bold_font['weight'] = 'bold'

        # Left pane with tabs.
        self.notebook = ttk.Notebook(self.main_frame)
        self.entries_frame = ttk.Frame(self.notebook)
        self.bookmarks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entries_frame, text='Entries')
        self.notebook.add(self.bookmarks_frame, text='Bookmarks')

        # Entries tab.
        self.new_entry_button = ttk.Button(
                self.entries_frame, text='New Entry', image=self.new_img,
                compound=self.DEFAULT_COMPOUND,
                command=self._new_entry_button_handler)
        self.del_entry_button = ttk.Button(
                self.entries_frame, text='Delete Entry', image=self.del_img,
                compound=self.DEFAULT_COMPOUND,
                command=self._del_entry_button_handler)
        self.entry_list_frame = ttk.Button(self.entries_frame)
        self.entry_listbox = Tkinter.Listbox(self.entry_list_frame,
                                             height=self.DEFAULT_LISTBOX_HEIGHT)
        self.entry_listbox.bind('<<ListboxSelect>>',
                                self._entry_listbox_select_handler)
        self.entry_listbox_sb = ttk.Scrollbar(self.entry_list_frame,
                                              command=self.entry_listbox.yview)
        self.entry_listbox['yscrollcommand'] = self.entry_listbox_sb.set

        # Bookmarks tab.
        self.new_bookmark_button = ttk.Button(
                self.bookmarks_frame, text='New Bookmark', image=self.new_img,
                compound=self.DEFAULT_COMPOUND,
                command=self._new_bookmark_button_handler)
        self.del_bookmark_button = ttk.Button(
                self.bookmarks_frame, text='Delete Bookmark',
                image=self.del_img, compound=self.DEFAULT_COMPOUND,
                command=self._del_bookmark_button_handler)
        self.bookmark_list_frame = ttk.Button(self.bookmarks_frame)
        self.bookmark_listbox = Tkinter.Listbox(
                self.bookmark_list_frame, height=self.DEFAULT_LISTBOX_HEIGHT)
        self.bookmark_listbox.bind('<<ListboxSelect>>',
                self._bookmark_listbox_select_handler)
        self.bookmark_listbox_sb = ttk.Scrollbar(
                self.bookmark_list_frame, command=self.bookmark_listbox.yview)
        self.bookmark_listbox['yscrollcommand'] = self.bookmark_listbox_sb.set
        self.notebook_sep = ttk.Separator(self.main_frame, orient='vertical')

        # Right pane displaying an entry.
        self.entry_display_frame = ttk.Frame(self.main_frame)
        self.ctime_label = ttk.Label(self.entry_display_frame,
                                     text='Created on:', font=self.bold_font)
        self.ctime_value_label = ttk.Label(self.entry_display_frame)
        self.mtime_label = ttk.Label(self.entry_display_frame,
                                     text='Modified on:', font=self.bold_font)
        self.mtime_value_label = ttk.Label(self.entry_display_frame)
        self.save_button = ttk.Button(self.entry_display_frame,
                                      text='Save Entry', image=self.save_img,
                                      compound=self.DEFAULT_COMPOUND,
                                      command=self._save_button_handler)
        self.save_button['state'] = 'disabled'
        self.entry_text_sep = ttk.Separator(self.entry_display_frame,
                                            orient='horizontal')
        self.entry_text_frame = ttk.Frame(self.entry_display_frame)
        self.entry_text = Tkinter.Text(self.entry_text_frame, width=80,
                                       wrap='word', relief='solid')
        self.entry_text_sb = ttk.Scrollbar(self.entry_text_frame,
                                           command=self.entry_text.yview)
        self.entry_text['yscrollcommand'] = self.entry_text_sb.set

        # Exit button.
        self.exit_button = ttk.Button(self.main_frame, text='Exit Program',
                                      command=self.root.destroy,
                                      image=self.exit_img,
                                      compound=self.DEFAULT_COMPOUND)

        #
        # Layout.
        #

        # Main window frame.
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.grid(row=0, column=0, **self.PADEXPAND)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Left pane with tabs.
        self.notebook.grid(row=0, column=0, **self.EXPAND)

        # Entries tab.
        self.entries_frame.columnconfigure(0, weight=1)
        self.entries_frame.columnconfigure(1, weight=1)
        self.entries_frame.rowconfigure(1, weight=1)
        self.new_entry_button.grid(row=0, column=0, **self.PADEXPAND)
        self.del_entry_button.grid(row=0, column=1, **self.PADEXPAND)
        self.entry_list_frame.grid(row=1, column=0, columnspan=2, **self.EXPAND)
        self.entry_list_frame.columnconfigure(0, weight=1)
        self.entry_list_frame.rowconfigure(0, weight=1)
        self.entry_listbox.grid(row=0, column=0, **self.EXPAND)
        self.entry_listbox_sb.grid(row=0, column=1,
                                   sticky=(Tkinter.N, Tkinter.S))

        # Bookmarks tab.
        self.bookmarks_frame.columnconfigure(0, weight=1)
        self.bookmarks_frame.columnconfigure(1, weight=1)
        self.bookmarks_frame.rowconfigure(1, weight=1)
        self.new_bookmark_button.grid(row=0, column=0, **self.PADEXPAND)
        self.del_bookmark_button.grid(row=0, column=1, **self.PADEXPAND)
        self.bookmark_list_frame.grid(row=1, column=0, columnspan=2,
                                      **self.EXPAND)
        self.bookmark_list_frame.columnconfigure(0, weight=1)
        self.bookmark_list_frame.rowconfigure(0, weight=1)
        self.bookmark_listbox.grid(row=0, column=0, **self.EXPAND)
        self.bookmark_listbox_sb.grid(row=0, column=1,
                                      sticky=(Tkinter.N, Tkinter.S))
        self.notebook_sep.grid(row=0, column=1, **self.HPADEXPAND)

        # Right pane displaying an entry.
        self.entry_display_frame.grid(row=0, column=2, **self.EXPAND)
        self.entry_display_frame.columnconfigure(1, weight=1)
        self.entry_display_frame.rowconfigure(2, weight=1)
        self.ctime_label.grid(row=0, column=0, sticky=Tkinter.W)
        self.ctime_value_label.grid(row=0, column=1, sticky=Tkinter.W)
        self.mtime_label.grid(row=1, column=0, sticky=Tkinter.W)
        self.mtime_value_label.grid(row=1, column=1, sticky=Tkinter.W)
        self.save_button.grid(row=0, column=2, rowspan=2, **self.EXPAND)
        self.entry_text_frame.grid(row=2, column=0, columnspan=3,
                                   pady=(self.DEFAULT_PADDING, 0),
                                   **self.EXPAND)
        self.entry_text_frame.columnconfigure(0, weight=1)
        self.entry_text_frame.rowconfigure(0, weight=1)
        self.entry_text.grid(row=0, column=0, **self.EXPAND)
        self.entry_text_sb.grid(row=0, column=1, **self.EXPAND)

        # Exit button.
        self.exit_button.grid(row=1, column=0, columnspan=3,
                              pady=(self.DEFAULT_PADDING, 0), sticky=Tkinter.E)

        #style = ttk.Style()
        #s.theme_use('alt')
        #style.theme_use('clam')

        self._update_entry_list()
        self._update_bookmarks_list()
        self._do_change_entry(None)
        self._do_select_bookmark(None)

    def mainloop(self):
        self.root.mainloop()

def main():
    backend_class = StorageBackend.DefaultStorageBackend
    backend = BackendInitializer(backend_class).get_backend()
    if backend is not None:
        gui = DefaultGUI(backend)
        gui.mainloop()

