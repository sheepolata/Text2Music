from tkinter import *
from tkinter import ttk

from os import listdir
from os.path import isfile, join

import sys

import text2music as t2m

import threading, time

import myglobals

class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text_space = text_widget

        self.last_print = ""
        self.text_space.mark_set(END, "1.0")
        self.last_end_index = self.text_space.index(END)
        # self.flush = False

        self.end = ['\n', '']

    # def write(self,string,end="",flush=False):
    #     self.text_space.configure(state="normal")
    #     # _end = end
    #     # if len(string) > 0 and string[-1] == '\n':
    #     #     _end=""
    #     _end = ""
    #     self.text_space.insert(END, "{}{}".format(string, _end))
    #     self.text_space.see(END)
    #     self.text_space.configure(state="disabled")

    def write(self, the_string):
        if not the_string in self.end:
            self.last_print = the_string
            self.last_end_index = self.text_space.index(END)

        self.text_space.configure(state="normal")
        self.text_space.tag_remove("last_insert", "1.0", "end")

        self.text_space.delete(END, self.text_space.index(END).split(".")[0]+"."+str(len(self.last_print)))

        self.text_space.insert("end", the_string, "last_insert")
        self.text_space.see("end")
        self.text_space.configure(state="disabled")

    def flush(self):
        self.text_space.configure(state="normal")
        self.text_space.mark_set(END, self.last_end_index)
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

class RunAppThread(threading.Thread):
    """docstring for RunAppThread"""
    def __init__(self, UI, filename, opt):
        super(RunAppThread, self).__init__()
        self.UI = UI
        self.filename = filename
        self.opt = opt
        # self.parent = current_thread()

    def start(self):
        super(RunAppThread, self).start()

    def run(self):
        self.UI.app_running = True
        for uie in self.UI.ui_elements:
            uie.configure(state="disabled")

        # self.UI.run_app()
        t2m.text_2_music(
                self.filename,
                **self.opt
            )

        self.UI.app_running = False
        for uie in self.UI.ui_elements:
            uie.configure(state="normal")
        print("done")

class LoopingThread(threading.Thread):
    """docstring for LoopingThread"""
    def __init__(self, target=None, freq=200):
        super(LoopingThread, self).__init__()
        self.target = target
        self.freq = freq
        self._stop = False

    def run(self):
        if self.target == None:
            self.join()
            return

        while not self._stop:
            self.target()
            time.sleep(self.freq/1000.0)

    def stop(self):
        self._stop = True
        

class T2M_GUI(Frame):
    """docstring for T2M_GUI"""
    def __init__(self):
        super(T2M_GUI, self).__init__()

        self.ui_elements = []
        self.app_running = False

        self.update_thread = LoopingThread(target=self.update)

        self.initUI()

        self.update_thread.start()
        
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
            if fstr[-4:] == ".txt" and fstr != "tmp.txt":
                file_list.append(fstr)

        self.filename_select = ttk.Combobox(self, values=file_list)
        self.ui_elements.append(self.filename_select)
        self.own_txt_var   = IntVar()
        self.own_txt_check = Checkbutton(self, text="Using custom text", variable=self.own_txt_var)
        self.ui_elements.append(self.own_txt_check)
        self.own_txt_entry = Text(self)
        self.own_txt_entry.configure(state="disabled")
        self.ui_elements.append(self.own_txt_entry)


        self.filename_entry_label.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1
        self.filename_select.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1
        self.own_txt_check.grid(column=_column, row=_row, sticky=W, pady=2)
        _column += 1
        self.own_txt_entry_col, self.own_txt_entry_row = _column, _row

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
        self.display_console.grid(column=_column, row=_row, columnspan=6, sticky=W+E)
        
        _column = 0; _row += 1;
        self.working_progressbar = ttk.Progressbar(self, orient=HORIZONTAL, length=100, mode='indeterminate')
        self._working_progressbar_change = 0

        sys.stdout = StdoutRedirector(self.display_console)
        sys.stderr = sys.stdout
        # self._after_id = self.after(200, self.update)

    def update(self):

        self.display_console.update()
        
        if not self.app_running:
            self.working_progressbar.grid_forget()

            if self.own_txt_var.get() == 1:
                self.own_txt_entry.configure(state="normal")
                self.own_txt_entry.grid(column=self.own_txt_entry_col, row=self.own_txt_entry_row, sticky=W+E, pady=2, columnspan=3)
            else:
                self.own_txt_entry.delete("1.0", END)
                self.own_txt_entry.configure(state="disabled")
                self.own_txt_entry.grid_forget()

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
        else:
            self.working_progressbar.grid(columnspan=6, sticky=W+E)
            if self.working_progressbar['value'] >= 100:
                self._working_progressbar_change = -5
            elif self.working_progressbar['value'] <= 0:
                self._working_progressbar_change = 5
            self.working_progressbar['value'] = self.working_progressbar['value'] + self._working_progressbar_change

        # self._after_id = self.after(200, self.update)

    def destroy(self):
        if not self.app_running:
            # self.after_cancel(self._after_id)
            self.update_thread.stop()
            super(T2M_GUI, self).destroy()

    def run_app(self):
        if self.own_txt_var.get() == 0 and self.filename_select.get() == "":
            print("Please select a file",flush=True)
            # print("No Flush")
            # print("Flush",flush=True)
            return
        elif self.own_txt_var.get() == 1:
            if self.own_txt_entry.compare("end-1c", "==", "1.0"):
                print("Please enter some text",flush=True)
                return
            else:
                _txt = self.own_txt_entry.get("1.0", END)
                if _txt.strip() == "":
                    print("Please enter some text",flush=True)
                    return


        # self.UI.app_running = True
        # for uie in self.UI.ui_elements:
        #     uie.configure(state="disabled")

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

        if self.own_txt_var.get() == 1:
            own_text = self.own_txt_entry.get("1.0", END).strip()
            self.filename_select.set("tmp.txt")
            _f = open("./data/"+self.filename_select.get(), "w")
            _f.write(own_text)
            _f.close()

        t = RunAppThread(self, self.filename_select.get(), option_values)
        t.start()

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


# main_thread = threading.Thread(target=main)
# main_thread.start()
# main_thread.join()

if __name__ == '__main__':
    main_thread = threading.Thread(target=main)
    main_thread.start()
    main_thread.join()

    # main()