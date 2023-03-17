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

        # create a frame to hold the notebook
        frame = tk.Frame(self.master)
        frame.pack(fill="both", expand=True)

        # create a notebook with tabs
        self.notebook = ttk.Notebook(frame)  # set padding
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
            style.map("TNotebook.Tab", background=[("selected", "green"), ("!disabled", "#4d2f5d"), ("active", "green")])

            # create a console output area with a text widget
            text_box = tk.Text(tab, background="#2a2a2a", foreground="green")
            text_box.pack(side="top", fill="both", expand=True)
            self.text_boxes.append(text_box)

            # create input boxes on the left side of the tab
            input_box = tk.Entry(tab, bg="#2a2a2a", fg="white", width=50, font=("Arial", 12))
            input_box.pack(side="left")
            input_box.bind("<Return>", lambda event, tb=text_box, ib=input_box, st=style: self.run_command(tb, ib, st)) # bind the <Return> event to run_command
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

        # create a menu bar
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        # create a file menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.configure(bg='blue')  # set the background color to blue
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save", command=self.save_data)
        file_menu.add_command(label="Load", command=self.load_data)

        # initialize the saved data to an empty dictionary
        self.saved_data = {}

        self.status_bar = tk.Label(self.master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_data(self):
        # open a file dialog to choose the data file
        file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not file_path:
            return
    
        # load the data from the file
        with open(file_path, "r") as f:
            data = json.load(f)
    
        # delete all current tabs
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        # create new tabs based on the data
        for i, tab_data in enumerate(data.get('tabs', [])):
            name = tab_data.get("name", f"Tab {i+1}")
            input_text = tab_data.get("input", "")
            text = tab_data.get("text", "")
            pid_label_text = tab_data.get("pid_label_text", "")
            self.populate_tab(name=name, input_text=input_text, text=text, pid_label_text=pid_label_text)

    def populate_tab(self, name, input_text="", text="", pid_label_text="", index=None):
            # create new tab with name
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=name)
            self.tabs.append(tab) # add this line to append the new tab to the list
            style = ttk.Style()
            style.configure('TButton', background="#4d2f5d")
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
        
            # populate input box, text box, and pid label
            input_box.delete(0, "end")
            input_box.insert(0, input_text)
            text_box.delete("1.0", "end")
            text_box.insert("end", text)
            pid_label = ttk.Label(tab, text=pid_label_text)
            pid_label.pack(side='bottom', pady=5)
    
            # add a None value to the running_processes list for the newly created tab
            self.running_processes.append(None)
    
    def clear_command(self, text_box):
        text_box.config(state="normal")
        text_box.delete(1.0, "end")
    
        # define function to run the command in a separate thread and capture its output
    def run_command(self, text_box, input_box, style):
        try:
            # get the command from the input box
            command = input_box.get()

            # check if there is already a running process for this tab
            try:
                tab_index = self.tabs.index(text_box.master)
            except ValueError:
                return
            if self.running_processes[tab_index] is not None and self.running_processes[tab_index].poll() is None:
                messagebox.showinfo("Info", "Please wait until previous command is finished.")
                return

            # create a new process to run the command
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.processes[process.pid] = process
            self.running_processes[tab_index] = process

            # create a new thread to capture the process output
            thread = threading.Thread(target=self.run_command_in_thread, args=(text_box, process, style, tab_index))
            thread.start()

            # store the process object in the button so it can be stopped later
            stop_button = text_box.master.children["!button2"]
            stop_button["command"] = lambda tb=text_box, ib=input_box, st=style, p=process, idx=tab_index: self.stop_command(tb, ib, st, p, idx)
        except Exception as e:
            text_box.configure(state="normal")
            text_box.insert(tk.END, f"There was an error with your command: {e}\n")
            style.map("TNotebook.Tab", background=[("selected", "green"), ("!disabled", "#4d2f5d"), ("active", "green")])
    
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

    def stop_command(self, text_box, input_box, style, process, index):
        if index is not None and index < len(self.running_processes) and self.running_processes[index] is not None:
            self.running_processes[index].kill()
            self.running_processes[index] = None
            style.configure("Stop.TButton", state="disabled")
            style.configure("Run.TButton", state="normal")
            text_box.insert(tk.END, "\nProcess stopped.\n")
        else:
            text_box.insert(tk.END, "\nNo process to stop.\n")
    
    
    
    def stop_all_processes(self):
        # Stop all running processes
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
    
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
            pid_label_widget = tab.children.get("!label")
            pid_label_text = pid_label_widget["text"] if pid_label_widget else ""
            tab_data = {
                "name": self.notebook.tab(i, option="text"),
                "input": tab.children["!entry"].get(),
                "text": tab.children["!text"].get("1.0", tk.END),
                "pid_label_text": pid_label_text,
                "pid_label_widget": pid_label_widget.winfo_pathname(pid_label_widget.winfo_id()) if pid_label_widget else "",
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


root = tk.Tk()
app = GUI(root)
root.mainloop()
