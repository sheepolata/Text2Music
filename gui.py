from tkinter import *
 
import sys

class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text_space = text_widget

        # self.flush = False

    def write(self,string,end='\n',flush=False):
        self.text_space.configure(state="normal")
        _end = end
        if string[-1] == '\n':
            _end=''
        self.text_space.insert(END, "{}{}".format(string, _end))
        self.text_space.see(END)
        self.text_space.configure(state="disabled")

    def flush(self):
        return
        self.text_space.configure(state="normal")
        self.text_space.delete(2.0, END)
        self.text_space.configure(state="disabled")

class T2M_GUI(Frame):
    """docstring for T2M_GUI"""
    def __init__(self):
        super(T2M_GUI, self).__init__()

        self.initUI()
        
    def initUI(self):
        self.master.title("Text2Music")
        self.pack(fill=BOTH, expand=True)

        # self.columnconfigure(1, weight=1)
        # self.columnconfigure(3, pad=7)
        # self.rowconfigure(3, weight=1)
        # self.rowconfigure(5, pad=7)
         
        self.filename_entry_label = Label(self, text="File name : data/")
        self.filename_entry = Entry(self)
        

        self.filename_entry_label.grid (column=0, row=0, sticky=W, pady=2)
        self.filename_entry.grid       (column=1, row=0, sticky=W, pady=2)

        def clicked():
            if(self.filename_entry.get() == ""):
                print("Empty", flush=True)
            else:
                print(self.filename_entry.get())

        self.btn = Button(self, text="Submit", command=clicked)
        self.btn.grid(column=0, row=1, columnspan=2)


        self.display_console = Text(self)
        self.display_console.configure(state="disabled")
        self.display_console.grid(column=0, row=2, columnspan=2, rowspan=2)
        
        self.print_on_console("Just a text Widget\nin two lines\n")

        sys.stdout = StdoutRedirector(self.display_console)

    def print_on_console(self, txt, opt=END):
        self.display_console.configure(state="normal")
        self.display_console.insert(opt, txt)
        self.display_console.configure(state="disabled")


def main():
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