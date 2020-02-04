import tkinter as tk
import datetime

class TextRedirector(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.tag_configure("last_insert", background="bisque")

    def write(self, the_string):
        self.text_widget.configure(state="normal")
        self.text_widget.tag_remove("last_insert", "1.0", "end")
        self.text_widget.insert("end", the_string, "last_insert")
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")

    def overwrite(self, the_string):
        self.text_widget.configure(state="normal")
        last_insert = self.text_widget.tag_ranges("last_insert")
        self.text_widget.delete(last_insert[0], last_insert[1])
        self.write(the_string)

def overwrite():
    stdout.overwrite(str(datetime.datetime.now()) + "\n")

def append():
    stdout.write(str(datetime.datetime.now()) + "\n")

root = tk.Tk()
text = tk.Text(root)
stdout = TextRedirector(text)

append = tk.Button(root, text="append", command=append)
overwrite = tk.Button(root, text="overwrite", command=overwrite)

append.pack()
overwrite.pack()
text.pack()

root.mainloop()