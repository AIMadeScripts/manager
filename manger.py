import json
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import threading
import subprocess
from tkinter import filedialog
from tkinter import simpledialog

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
            text_box = tk.Text(tab, state="disabled", background="#2a2a2a", foreground="green")
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



    def clear_command(self, text_box):
        text_box.config(state="normal")
        text_box.delete(1.0, "end")
        text_box.config(state="disabled")
    

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
            text_box.configure(state="disabled")
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
                    text_box.configure(state="disabled")

        except Exception:
            text_box.configure(state="normal")
            text_box.insert(tk.END, "There was an error with your command\n")
            text_box.configure(state="disabled")    
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])
        style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])


    def create_tab(self):
        # create a new tab
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=f"Tab {len(self.tabs)+1}")
    
        # create a console output area with a text widget
        text_box = tk.Text(tab, state="disabled", background="black", foreground="green")
        text_box.pack(side="top", fill="both", expand=True)
        self.text_boxes.append(text_box)
    
        # create input boxes on the left side of the tab
        input_box = tk.Entry(tab, bg="#2a2a2a", fg="#2a2a2a", width=50, font=("Arial", 12))
        input_box.config(highlightbackground="white", highlightcolor="white", highlightthickness=1, relief="flat")
        input_box.pack(side="left", padx=10, pady=10)
    
        # create a button next to the input box to run the command
        run_button = tk.Button(tab, text="Run", command=lambda tb=text_box, ib=input_box: self.run_command(tb, ib))
        run_button.pack(side="left")
    
        # create a stop button next to the run button to stop the command process
        stop_button = tk.Button(tab, text="Stop", command=self.stop_command)
        stop_button.pack(side="left")
    
        # create a label next to the stop button to display the process ID
        pid_label = tk.Label(tab, text="PID: None")
        pid_label.pack(side="left")
    
        # display the PID label in the GUI
        tab.pack(side="top", fill="both", expand=True) # added this line
 
    def rename_tab(self, tab, name):
        # create a pop-up dialog to ask the user for a new tab name
        name = tk.simpledialog.askstring("Rename Tab", "Enter a new name for the tab:")
        if name:
            # set the new tab name
            self.notebook.tab(tab, text=name)
    
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
                "pid_label_text": tab.children["!label"].cget("text"),
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
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        # open the file dialog to select a save file
        filename = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            # load the data from the save file
            with open(filename, "r") as f:
                data = json.load(f)
            # iterate over the saved data
            for tab_data in data["tabs"]:
                # get the tab name from the saved data
                tab_name = tab_data["name"]
                # rename the tab
                self.rename_tab(self.notebook.tabs()[tab_data["index"]], name=tab_name)
                # get the text box for the tab
                text_box = self.text_boxes[tab_data["index"]]
                # set the console output area text to the saved text
                text_box.config(state="normal")
                text_box.delete(1.0, tk.END)
                text_box.insert(tk.END, tab_data["text"])
                text_box.config(state="disabled")
                # get the input box for the tab
                input_box = self.input_boxes[tab_data["index"]]
                # set the input box text to the saved text
                input_box.delete(0, tk.END)
                input_box.insert(0, tab_data["input"])
            messagebox.showinfo("Load Successful", "Data loaded successfully.")

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
            style.map("TNotebook.Tab", background=[("selected", "#4d2f5d"), ("!disabled", "#4d2f5d"), ("active", "#4d2f5d")])
    
root = tk.Tk()
app = GUI(root)
root.mainloop()
