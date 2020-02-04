from tkinter import *
from tkinter import ttk

from os import listdir
from os.path import isfile, join

import sys

import text2music as t2m

import threading

import myglobals

class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text_space = text_widget

        # self.flush = False

    def write(self,string,end="",flush=False):
        self.text_space.configure(state="normal")
        _end = end
        # if len(string) > 0 and string[-1] == '\n':
        #     _end=""
        self.text_space.insert(END, "{}{}".format(string, _end))
        self.text_space.see(END)
        self.text_space.configure(state="disabled")

    def flush(self):
        return
        self.text_space.configure(state="normal")
        self.text_space.delete(2.0, END)
        self.text_space.configure(state="disabled")

class Lotfi(Entry):
    def __init__(self, master=None, **kwargs):
        self.var = StringVar()
        Entry.__init__(self, master, textvariable=self.var, **kwargs)
        self.old_value = ''
        self.var.trace('w', self.check)
        self.get, self.set = self.var.get, self.var.set

    def check(self, *args):
        if self.get().isdigit() or self.get() == "": 
            # the current value is only digits; allow this
            self.old_value = self.get()
        elif len(self.get()) > 0 and self.get()[0] == "-":
            self.old_value = "-1"
            self.set("-1")
        else:
            # there's non-digit characters in the input; reject this 
            self.set(self.old_value)

class T2M_GUI(Frame):
    """docstring for T2M_GUI"""
    def __init__(self):
        super(T2M_GUI, self).__init__()

        self.ui_elements = []

        self.initUI()
        
    def initUI(self):
        self.master.title("Text2Music")
        self.pack(fill=BOTH, expand=True)

        _column = 0
        _row    = 0

        # self.columnconfigure(1, weight=1)
        # self.columnconfigure(3, pad=7)
        # self.rowconfigure(3, weight=1)
        # self.rowconfigure(5, pad=7)
         
        self.filename_entry_label = Label(self, text="File name : data/")

        tmp_file_list = [str(f) for f in listdir("./data/") if isfile(join("./data", f))]
        file_list = []
        for fstr in tmp_file_list:
            if fstr[-4:] == ".txt":
                file_list.append(fstr)

        self.filename_select = ttk.Combobox(self, values=file_list)
        self.ui_elements.append(self.filename_select)
        
        self.filename_entry_label.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1
        self.filename_select.grid(column=_column, row=_row, sticky=W, pady=2)

        self.bpm_var = -1
        self.bpm_label = Label(self, text="BPM (-1=default) ->")
        self.bpm_entry = ttk.Combobox(self, values=[-1,120, 160, 200, 220, 240])
        self.bpm_entry.set(-1)
        self.ui_elements.append(self.bpm_entry)

        self.instrument_var = -1
        self.instrument_label = Label(self, text="Instrument (none=default) ->")
        self.instrument_entry = ttk.Combobox(self, values=["none","a","b","c","d","e","p","s"])
        self.instrument_entry.set("none")
        self.ui_elements.append(self.instrument_entry)

        self.octave_var = -1
        self.octave_label = Label(self, text="Octave (-1=default) ->")
        self.octave_entry = ttk.Combobox(self, values=[-1,2,3,4,5,6])
        self.octave_entry.set(-1)
        self.ui_elements.append(self.octave_entry)

        _column = 0; _row += 1;
        self.bpm_label.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1;
        self.bpm_entry.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1;
        self.instrument_label.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1;
        self.instrument_entry.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1;
        self.octave_label.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1;
        self.octave_entry.grid(column=_column, row=_row, sticky=W, pady=2)

        self.markov_var   = IntVar()
        self.markov_check = Checkbutton(self, text="Markov Gen.", variable=self.markov_var)
        self.ui_elements.append(self.markov_check)

        self.markov_length = 100
        self.markov_length_label = Label(self, text="Markov Length ---->")
        self.markov_length_entry = Lotfi(self)
        self.markov_length_entry.configure(state="disabled")
        self.ui_elements.append(self.markov_length_entry)

        self.markov_seed   = -1
        self.markov_seed_label = Label(self, text="Markov seed ---->")
        self.markov_seed_entry = Lotfi(self)
        self.markov_seed_entry.configure(state="disabled")
        self.ui_elements.append(self.markov_seed_entry)

        self.reload_markov_var   = IntVar()
        self.reload_markov_check = Checkbutton(self, text="Reload Markov", variable=self.reload_markov_var)
        self.reload_markov_check.configure(state="disabled")
        self.ui_elements.append(self.reload_markov_check)

        _column = 0; _row += 1;
        self.markov_check.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1;
        self.markov_length_label.grid(column=_column, row=_row, sticky=W)
        _column += 1;
        self.markov_length_entry.grid(column=_column, row=_row, sticky=W)
        _column += 1;
        self.markov_seed_label.grid(column=_column, row=_row, sticky=W)
        _column += 1;
        self.markov_seed_entry.grid(column=_column, row=_row, sticky=W)
        _column += 1;
        self.reload_markov_check.grid(column=_column, row=_row, sticky=W)

        _column = 0; _row += 1;
        self.submit_button = Button(self, text="Submit", command=self.run_app)
        self.ui_elements.append(self.submit_button)
        self.submit_button.grid(column=_column, row=_row, columnspan=6)


        _column = 0; _row += 1;
        self.display_console = Text(self)
        self.display_console.configure(state="disabled")
        self.display_console.grid(column=_column, row=_row, columnspan=6, rowspan=3)
        
        # self.print_on_console("Console\n")

        sys.stdout = StdoutRedirector(self.display_console)
        self.after(200, self.update)

    def update(self):
        # self.print_on_console("etsf")
        self.display_console.update()
        if self.markov_var.get() == 1:
            self.markov_length_entry.configure(state="normal")
            self.markov_seed_entry.configure(state="normal")
            self.reload_markov_check.configure(state="normal")
        else:
            self.markov_length_entry.set(self.markov_length)
            self.markov_length_entry.configure(state="disabled")
            self.markov_seed_entry.set(self.markov_seed)
            self.markov_seed_entry.configure(state="disabled")
            self.reload_markov_check.configure(state="disabled")

        self.after(200, self.update)

    def run_app(self):
        if self.filename_select.get() == "":
            print("Please select a file")
            return

        option_values = {
                    "bpm"                    : int(self.bpm_entry.get()),
                    "instrument"             : self.instrument_entry.get(),
                    "generator"              : "chain",
                    "octave"                 : int(self.octave_entry.get()),
                    "markov"                 : self.markov_var.get()==1,
                    "markovgenerationlength" : int(self.markov_length_entry.get()),
                    "markovseed"             : int(self.markov_seed_entry.get()),
                    "reloadmarkov"           : self.reload_markov_var.get()==1,
                    "showgraph"              : False
                    }

        for uie in self.ui_elements:
            uie.configure(state="disabled")

        def t2m_tread_target():
            _t = threading.currentThread()
            t2m.text_2_music(
                self.filename_select.get(),
                **option_values
            )
            _t.join()

        t = threading.Thread(target=t2m_tread_target)
        t.start()
        # t2m.text_2_music(
        #         self.filename_select.get(),
        #         **option_values
        #     )

        for uie in self.ui_elements:
            uie.configure(state="normal")

    def print_on_console(self, txt, opt=END):
        self.display_console.configure(state="normal")
        self.display_console.insert(opt, txt)
        self.display_console.configure(state="disabled")


def main():
    myglobals.RUN_GUI = True

    main_window = Tk()

    screen_width = main_window.winfo_screenwidth()
    screen_height = main_window.winfo_screenheight()

    mw_height, mw_width = int(screen_width/2), int(screen_height/2)
    # main_window.geometry("{}x{}+{}+{}".format(mw_height, mw_width, int(mw_height/2), int(mw_width/2)))
    main_window.geometry("+{}+{}".format(int(mw_height/2), int(mw_width/2)))
    main_window.resizable(False, False)

    app = T2M_GUI()

    main_window.mainloop()

if __name__ == '__main__':
    main()