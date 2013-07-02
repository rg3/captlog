#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of captlog.
#
# captlog - Captain's Log (secret diary and notes application)
#
# Written in 2013 by Ricardo Garcia <public@rg3.name>
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
import os.path

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
        self.done_button = ttk.Button(self.frame,
                                      text=self.BUTTON_NORMAL_TEXT,
                                      command=self._init_backend)
        self.root.bind('<Return>', self._init_backend)
        self.root.bind('<KP_Enter>', self._init_backend)

        # Layout.
        padding = { 'padx': 5, 'pady': 5 }
        self.frame.grid(row=0, column=0, **padding)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(2, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.frame.rowconfigure(4, weight=1)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        row = 0
        self.help_label.grid(row=row,column=0, columnspan=2, sticky=Tkinter.W,
                             **padding)
        row += 1
        self.passphrase_label.grid(row=row, column=0, sticky=Tkinter.E,
                                   **padding)
        self.passphrase_entry.grid(row=row, column=1, **padding)
        row += 1
        if self._confirmation:
            self.confirm_label.grid(row=row, column=0, sticky=Tkinter.E,
                                    **padding)
            self.confirm_entry.grid(row=row, column=1, **padding)
        row += 1
        self.result_label.grid(row=row, column=0, columnspan=2, **padding)
        row += 1
        self.done_button.grid(row=row, column=0, columnspan=2, **padding)

        self._gui_reset()

    def _gui_reset(self):
        self.done_button['text'] = self.BUTTON_NORMAL_TEXT
        self.done_button['state'] = 'enabled'
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
            self.done_button['state'] = 'disabled'
            self.done_button['text'] = self.BUTTON_WAIT_TEXT
            self.result_label['text'] = ''
            self.root.update()
            backend = self._backend_class(p)
            self._backend = backend
            self.root.destroy()
        except (StorageBackend.Error, ), e:
            self.result_label['text'] = 'Error: %s' % e.message
            self._gui_reset()

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

    def __init__(self, backend):
        self._backend = backend

        #
        # Widgets.
        # 

        # Main window frame.
        self.root = Tkinter.Tk(className=WINDOW_CLASS)
        self.root.title("%s: The Captain's Log" % (WINDOW_CLASS, ))
        self.main_frame = ttk.Frame(self.root)

        # Images.
        self.new_img = Tkinter.PhotoImage(file=os.path.join(self.IMAGE_PATH,
                                                            'new.png'))
        self.del_img = Tkinter.PhotoImage(file=os.path.join(self.IMAGE_PATH,
                                                            'delete.png'))
        self.save_img = Tkinter.PhotoImage(file=os.path.join(self.IMAGE_PATH,
                                                             'save.png'))
        self.exit_img = Tkinter.PhotoImage(file=os.path.join(self.IMAGE_PATH,
                                                             'exit.png'))

        # Fonts.
        self.bold_font = tkFont.nametofont('TkDefaultFont').copy()
        self.bold_font.configure(weight='bold')

        # Left pane with tabs.
        self.notebook = ttk.Notebook(self.main_frame)
        self.entries_frame = ttk.Frame(self.notebook)
        self.bookmarks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.entries_frame, text='Entries')
        self.notebook.add(self.bookmarks_frame, text='Bookmarks')

        # Entries tab.
        self.new_entry_button = ttk.Button(self.entries_frame, text='New Entry',
                                           image=self.new_img,
                                           compound=self.DEFAULT_COMPOUND)
        self.del_entry_button = ttk.Button(self.entries_frame,
                                           text='Delete Entry',
                                           image=self.del_img,
                                           compound=self.DEFAULT_COMPOUND)
        self.entry_list_frame = ttk.Button(self.entries_frame)
        self.entry_listbox = Tkinter.Listbox(self.entry_list_frame,
                                             height=self.DEFAULT_LISTBOX_HEIGHT)
        # XXX
        for i in [x for x in xrange(1, 30+1)][::-1]:
            self.entry_listbox.insert('end', 'Entry from 2013-06-%02d' % i)

        self.entry_listbox_sb = ttk.Scrollbar(self.entry_list_frame,
                                              command=self.entry_listbox.yview)
        self.entry_listbox.configure(yscrollcommand=self.entry_listbox_sb.set)

        # Bookmarks tab.
        self.new_bookmark_button = ttk.Button(self.bookmarks_frame,
                                              text='New Bookmark',
                                              image=self.new_img,
                                              compound=self.DEFAULT_COMPOUND)
        self.del_bookmark_button = ttk.Button(self.bookmarks_frame,
                                              text='Delete Bookmark',
                                              image=self.del_img,
                                              compound=self.DEFAULT_COMPOUND)
        self.bookmark_list_frame = ttk.Button(self.bookmarks_frame)
        self.bookmark_listbox = Tkinter.Listbox(
                self.bookmark_list_frame, height=self.DEFAULT_LISTBOX_HEIGHT)
        # XXX
        for i in xrange(1, 30+1):
            self.bookmark_listbox.insert('end', 'Bookmark number %s' % i)
        self.bookmark_listbox_sb = ttk.Scrollbar(
                self.bookmark_list_frame, command=self.bookmark_listbox.yview)
        self.bookmark_listbox.configure(
                yscrollcommand=self.bookmark_listbox_sb.set)
        self.notebook_sep = ttk.Separator(self.main_frame, orient='vertical')

        # Right pane displaying an entry.
        self.entry_display_frame = ttk.Frame(self.main_frame)
        self.ctime_label = ttk.Label(self.entry_display_frame,
                                     text='Created on:', font=self.bold_font)
        self.ctime_value_label = ttk.Label(self.entry_display_frame,
                                           text='2013-06-26T20:15:00Z') # XXX
        self.mtime_label = ttk.Label(self.entry_display_frame,
                                     text='Modified on:', font=self.bold_font)
        self.mtime_value_label = ttk.Label(self.entry_display_frame,
                                           text='2013-06-26T20:16:01Z') # XXX
        self.save_button = ttk.Button(self.entry_display_frame,
                                      text='Save Entry', image=self.save_img,
                                      compound=self.DEFAULT_COMPOUND)
        self.save_button.configure(state='disabled')
        self.entry_text_sep = ttk.Separator(self.entry_display_frame,
                                            orient='horizontal')
        self.entry_text_frame = ttk.Frame(self.entry_display_frame)
        self.entry_text = Tkinter.Text(self.entry_text_frame, width=80,
                                       wrap='word', relief='solid')
        #entry_text.insert('0.0', lorem_ipsum)
        self.entry_text_sb = ttk.Scrollbar(self.entry_text_frame,
                                           command=self.entry_text.yview)
        self.entry_text.configure(yscrollcommand=self.entry_text_sb.set)

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

        style = ttk.Style()
        #s.theme_use('alt')
        style.theme_use('clam')

    def mainloop(self):
        self.root.mainloop()

def main():
    backend_class = StorageBackend.DefaultStorageBackend
    backend = BackendInitializer(backend_class).get_backend()
    if backend is not None:
        gui = DefaultGUI(backend)
        gui.mainloop()

if __name__ == '__main__':
    main()

#answer = tkMessageBox.askyesno(
#    title='Sooperimportant Question',
#    message='Is 'no' the answer to this question?')
#print 'Answer: %r' % answer


