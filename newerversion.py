from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import threading
import subprocess
from tkinter import filedialog
from tkinter import simpledialog
import json
import os

class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("GUI with Tabs and Input Boxes")
        self.master.geometry("1000x600")

        # create a notebook with tabs
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(side="top", fill="both", expand=True)

        # create 10 tabs
        self.tabs = []
        self.text_boxes = []
        self.input_boxes = []  # add this line
        for i in range(10):
            # create a tab
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=f"Tab {i+1}")

            # set the notebook style
            style = ttk.Style()
            style.configure("TNotebook.Tab", font=('Verdana', 10), foreground='#fff')
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])

            # create a console output area with a text widget
            text_box = tk.Text(tab, background="#2a2a2a", foreground="green")
            text_box.pack(side="top", fill="both", expand=True)
            self.text_boxes.append(text_box)

            # create input boxes on the left side of the tab
            input_box = tk.Entry(tab, bg="#2a2a2a", fg="white", width=50, font=("Arial", 12))
            input_box.pack(side="left")
            self.input_boxes.append(input_box)  # add this line

            # create a button next to the input box to run the command
            run_button = tk.Button(tab, text="Run", bg="#4d2f5d", command=lambda tb=text_box, ib=input_box, st=style: self.run_command(tb, ib, st))
            run_button.pack(side="left")

            # create a stop button next to the run button to stop the command process
            stop_button = tk.Button(tab, text="Stop", bg="#4d2f5d", command=lambda tb=text_box, ib=input_box, st=style: self.stop_command(tb, ib, st))
            stop_button.pack(side="left")

            # create a clear button next to the stop button to clear the input box and text box
            clear_button = tk.Button(tab, text="Clear", bg="#4d2f5d", command=lambda tb=text_box, st=style: self.clear_command(tb))
            clear_button.pack(side="left")

            # create a rename button to rename the tab
            rename_button = tk.Button(tab, text="Rename", bg="#4d2f5d", command=lambda t=tab: self.rename_tab(t))
            rename_button.pack(side="right")

            self.tabs.append(tab)

        # keep track of the running command process for each tab
        self.running_processes = [None] * 10
        self.processes = {}

        # add a "+" tab to create new tabs
        plus_tab = ttk.Frame(self.notebook)
        plus_tab.pack(side="top", fill="both", expand=True)
        plus_button = tk.Button(plus_tab, text="+", command=self.create_tab)
        plus_button.pack(side="top", fill="both", expand=True)
        self.notebook.add(plus_tab, text="+")


        # create a menu bar
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        # create a file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_data)
        file_menu.add_command(label="Load", command=self.load_data)

        # initialize the saved data to an empty dictionary
        self.saved_data = {}

        self.status_bar = tk.Label(self.master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    def clear_command(self, text_box):
        text_box.config(state="normal")
        text_box.delete(1.0, "end")
    
        # define function to run the command in a separate thread and capture its output
    def run_command(self, text_box, input_box, style):
        try:
            # get the command from the input box
            command = input_box.get()
    
            # check if there is already a running process for this tab
            tab_index = self.tabs.index(text_box.master)
            if self.running_processes[tab_index] is not None and self.running_processes[tab_index].poll() is None:
                messagebox.showinfo("Info", "Please wait until previous command is finished.")
                return
    
            # Change tab color when the command is running
            style.map("TNotebook.Tab", background=[("selected", "orange"), ("!disabled", "orange"), ("active", "orange")])
    
            # create a new process to run the command
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.processes[process.pid] = process
            self.running_processes[tab_index] = process
    
            # create a new thread to capture the process output
            thread = threading.Thread(target=self.run_command_in_thread, args=(text_box, process, style, tab_index))
            thread.start()
    
            # store the process object in the button so it can be stopped later
            stop_button = text_box.master.children["!button2"]
            stop_button["command"] = lambda p=process: self.stop_command(p)
        except Exception:
            text_box.configure(state="normal")
            text_box.insert(tk.END, "There was an error with your command\n")
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])    
    
    def run_command_in_thread(self, text_box, process, style, tab_index):
        try:
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    text_box.configure(state="normal")
                    text_box.insert(tk.END, output.decode())
        except Exception:
            text_box.configure(state="normal")
            text_box.insert(tk.END, "There was an error with your command\n")
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])    
    
    def create_tab(self, name="", input_text="", text="", pid_label_text=""):
        """Create a new tab."""
        # create a new tab with a text widget
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        self.notebook.add(tab, text=name, state='normal')
    
        # set the notebook style
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=('Verdana', 10), foreground='#fff')
        style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])
    
        # create a console output area with a text widget
        text_box = tk.Text(tab, background="#2a2a2a", foreground="green")
        text_box.pack(side="top", fill="both", expand=True)
        self.text_boxes.append(text_box)
    
        # create input boxes on the left side of the tab
        input_box = tk.Entry(tab, bg="#2a2a2a", fg="white", width=50, font=("Arial", 12))
        input_box.pack(side="left")
        self.input_boxes.append(input_box)
    
        # create a button next to the input box to run the command
        run_button = tk.Button(tab, text="Run", bg="#4d2f5d", command=lambda tb=text_box, ib=input_box, st=style: self.run_command(tb, ib, st))
        run_button.pack(side="left")
    
        # create a stop button next to the run button to stop the command process
        stop_button = tk.Button(tab, text="Stop", bg="#4d2f5d", command=lambda tb=text_box, ib=input_box, st=style: self.stop_command(tb, ib, st))
        stop_button.pack(side="left")
    
        # create a clear button next to the stop button to clear the input box and text box
        clear_button = tk.Button(tab, text="Clear", bg="#4d2f5d", command=lambda tb=text_box, st=style: self.clear_command(tb))
        clear_button.pack(side="left")
    
        # create a label to display the process ID of the running command
        pid_label = tk.Label(tab, text=pid_label_text, fg="white", bg="#2a2a2a", font=("Arial", 10))
        pid_label.pack(side="left", padx=5)
    
        # create a rename button to rename the tab
        rename_button = tk.Button(tab, text="Rename", bg="#4d2f5d", command=lambda t=tab: self.rename_tab(t))
        rename_button.pack(side="right")
    
        # add the tab to the notebook
        self.tabs.append(tab)
    
        # populate the tab with saved data
        input_box.insert(0, input_text)
        text_box.insert("end", text)
        pid_label.config(text=pid_label_text)
    
        # select the new tab
        self.notebook.select(tab)
    
        # set the window title to the active tab name
        self.master.title(name + " - " + self.title)
    
 
    def rename_tab(self, tab, new_name=None):
        # get the current name of the tab
        current_name = self.notebook.tab(tab, "text")
        # if new_name is not provided, ask for a new tab name using a pop-up dialog
        if not new_name:
            new_name = tk.simpledialog.askstring("Rename Tab", "Enter a new name for the tab:", initialvalue=current_name)
        if new_name:
            # set the new tab name
            self.notebook.tab(tab, text=new_name)
    
    def do_rename_tab(self, tab, name):
        # rename the tab
        index = self.notebook.index(tab)
        self.notebook.tab(index, text=name)

    def save_data(self):
        # Create a dictionary containing the current state of the GUI
        data = {
            "tabs": [],
            "saved_data": self.saved_data
        }
        for i, tab in enumerate(self.tabs):
            tab_data = {
                "name": self.notebook.tab(i, option="text"),
                "input": tab.children["!entry"].get(),
                "text": tab.children["!text"].get("1.0", tk.END),
                "pid_label_text": tab.children.get("!label", {}).get("text", ""), # handle missing key
                "index": i  # add the index of the tab
            }
            data["tabs"].append(tab_data)
    
        # Ask the user to choose a file name and location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="."
        )
    
        # Write the data to the file using JSON format
        if file_path:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
                self.status_bar.config(text=f"Saved data to {file_path}")
        else:
            self.status_bar.config(text="Save cancelled.")

    def load_data(self):
        # ask the user to select a file to load
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file", filetypes=(("JSON files", "*.json"),))
    
        # return if the user cancels the file selection
        if not file_path:
            return
    
        # destroy all existing tabs
        for tab_index in reversed(range(len(self.tabs))):
            tab = self.tabs[tab_index]
            self.notebook.forget(tab)
            tab.destroy()
        
        # clear the tabs list
        self.tabs.clear()
    
        # clear the list of tabs and input boxes
        self.tabs = []
        self.input_boxes = []
    
        # load the data from the file and create new tabs
        with open(file_path, "r") as f:
            data = json.load(f)
    
        # define pid_label outside of the loop
        pid_label = None
    
        for tab_data in data["tabs"]:
            tab_input = tab_data["input"]
            tab_text = tab_data["text"]
            tab_pid_label_text = tab_data["pid_label_text"]
            tab_name = tab_data["name"]
            tab_index = tab_data["index"]
        
            # create a new tab with the saved data
            tab = ttk.Frame(self.notebook)
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
            self.notebook.add(tab, text=tab_name, state='normal')
        
            # set the notebook style
            style = ttk.Style()
            style.configure("TNotebook.Tab", font=('Verdana', 10), foreground='#fff')
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])
        
            # create a console output area with a text widget
            text_box = tk.Text(tab, background="#2a2a2a", foreground="green")
            text_box.pack(side="top", fill="both", expand=True)
            self.text_boxes.append(text_box)
        
            # create input boxes on the left side of the tab
            input_box = tk.Entry(tab, bg="#2a2a2a", fg="white", width=50, font=("Arial", 12))
            input_box.pack(side="left")
            self.input_boxes.append(input_box)
        
            # create a button next to the input box to run the command
            run_button = tk.Button(tab, text="Run", bg="#4d2f5d", command=lambda tb=text_box, ib=input_box, st=style: self.run_command(tb, ib, st))
            run_button.pack(side="left")
        
            # create a stop button next to the run button to stop the command process
            stop_button = tk.Button(tab, text="Stop", bg="#4d2f5d", command=lambda tb=text_box, ib=input_box, st=style: self.stop_command(tb, ib, st))
            stop_button.pack(side="left")
        
            # create a clear button next to the stop button to clear the input box and text box
            clear_button = tk.Button(tab, text="Clear", bg="#4d2f5d", command=lambda tb=text_box, st=style: self.clear_command(tb))
            clear_button.pack(side="left")
        
            # create a rename button to rename the tab
            rename_button = tk.Button(tab, text="Rename", bg="#4d2f5d", command=lambda t=tab: self.rename_tab(t))
            rename_button.pack(side="right")
        
            self.tabs.append(tab)
        
        
            # populate the tab with saved data
            input_box.insert(0, tab_data["input"])
            text_box.insert("end", tab_data["text"])
            
            # find the pid_label widget in the current tab
            pid_label = tab.nametowidget(tab_data["pid_label_widget"])
            # configure the text of the pid_label widget
            pid_label.config(text=tab_pid_label_text)
            
            # add the tab to the notebook
            self.notebook.add(tab, text=tab_data["name"], underline=0, padding=2)
            
        # select the first tab
        self.notebook.select(self.tabs[0])
        
        # set the window title to the active tab name
        self.master.title(self.tabs[0]["name"] + " - " + self.title)

    
    
    def stop_command(self, style):
        try:
            # get the tab index and the process object from the stop button
            stop_button = self.master.focus_get()
            tab_index = self.tabs.index(stop_button.master)
            process = self.running_processes[tab_index]
            
            # stop the process and remove it from the running processes list
            process.terminate()
            self.running_processes[tab_index] = None
            
            # Change tab color when the command is stopped
            style = ttk.Style()
            style.configure("TNotebook.Tab", font=('Verdana', 10), foreground='#fff')
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])
        except Exception:
            pass
        else:
            # Update tab style if the process was successfully stopped
            style = ttk.Style()
            style.configure("TNotebook.Tab", font=('Verdana', 10), foreground='#000')
            style.map("TNotebook.Tab", background=[("selected", "#ddd"), ("!disabled", "#ddd"), ("active", "#ddd")])
        finally:
            try:
                text_box.configure(state="normal")
                text_box.insert(tk.END, "Command stopped by user\n")
                text_box.configure(state="disabled")
                style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])
            except NameError:
                pass

    def stop_all_processes(self):
        # Stop all running processes
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
root = tk.Tk()
app = GUI(root)
root.mainloop()
