import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import subprocess

from pyswip import Prolog

import threading


class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.prolog = Prolog()
        self.prolog.consult('mergesort.pl')

        self.tasks = {}

        setup_db_thread = threading.Thread(target=self.setup_database)
        get_tasks_thread = threading.Thread(target=self.get_tasks)

        setup_db_thread.start()
        get_tasks_thread.start()

        setup_db_thread.join()
        get_tasks_thread.join()

        self.setup_gui()

    def setup_database(self):
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER,
                task TEXT NOT NULL,
                priority INTEGER NOT NULL
            )''')
        conn.commit()
        conn.close()

    def get_tasks(self):
        try:
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('SELECT task,priority FROM tasks')
            rows = cursor.fetchall()
            self.tasks = {row[0]: row[1] for row in rows}
            conn.close()
        except sqlite3.OperationalError:
            pass

    def sort_tasks(self):
        high_priority_tasks = {}
        medium_priority_tasks = {}
        low_priority_tasks = {}

        for k, v in self.tasks.items():
            if v == 'High':
                high_priority_tasks[k] = v
            elif v == 'Medium':
                medium_priority_tasks[k] = v
            elif v == 'Low':
                low_priority_tasks[k] = v

        to_sort = [high_priority_tasks,
                   medium_priority_tasks, low_priority_tasks]
        ans = {}
        for sorta in to_sort:
            ascii_values = {k: ord(k[0]) for k in sorta}
            values = list(ascii_values.values())
            sorted_ascii = list(Prolog.query(
                'mergesort({},X)'.format(values)))[0]['X']
            for i in sorted_ascii:
                for k, v in ascii_values.items():
                    if i == v:
                        ans[k] = sorta[k]

        self.tasks = ans

    def update_listbox(self):
        self.sort_tasks()
        self.listbox.delete(0, tk.END)
        for task, prio in self.tasks.items():
            self.listbox.insert(tk.END, "{0}: {1}".format(task, prio))

    def add_task(self):
        task = self.task_entry.get().strip()
        priority = self.priority_var.get()
        if task != "":
            new_sentence = []
            for word in task.split(' '):
                command = ["cabal", "run", "todo-plus", word]

                run = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                stdout, _ = run.communicate()

                output_text = stdout.decode("utf-8").strip()
                tag = "@@OUTPUT:"
                output_decoded = ""
                for line in output_text.splitlines():
                    if line.startswith(tag):
                        output_decoded = line[len(tag):].strip()
                        break

                if output_decoded:
                    helped = output_decoded
                else:
                    helped = ''
                if helped == '' or helped == word:
                    new_sentence.append(word)
                elif helped != word:
                    q = messagebox.askyesno("?", f"Did you mean {helped}?")
                    if q:
                        new_sentence.append(helped)
                    else:
                        new_sentence.append(word.strip())
            if new_sentence != []:
                task = ' '.join(new_sentence)
            self.tasks[task] = priority
            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO tasks (task,priority) VALUES (?,?)', (task, priority))
            conn.commit()
            conn.close()
            self.update_listbox()
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Task can't be empty")

    def delete_task(self):
        try:
            task_index = self.listbox.curselection()[0]

            keys = list(self.tasks.keys())
            task = keys[task_index]
            self.tasks.pop(task)

            conn = sqlite3.connect('tasks.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE task = ?', (task,))
            conn.commit()
            conn.close()
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("Warning", "Please select a task to delete")

    def setup_gui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        self.listbox = tk.Listbox(frame, width=40, height=20, font=(
            "Helvetica", 12), bg='lightgray')
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        self.task_entry = tk.Entry(self.root, width=20, font=("Helvetica", 12))
        self.task_entry.pack(pady=20)

        self.priority_label = tk.Label(
            self.root, text="Select Priority:", font=("Helvetica", 12))
        self.priority_label.pack(pady=5)
        self.priority_var = tk.StringVar()
        self.priority_menu = ttk.Combobox(
            self.root, textvariable=self.priority_var, state="readonly", font=("Helvetica", 12))
        self.priority_menu['values'] = ('High', 'Medium', 'Low')
        self.priority_menu.current(1)
        self.priority_menu.pack(pady=5)

        add_button = tk.Button(self.root, text="Add Task",
                               width=20, command=self.add_task, bg="lightblue")
        add_button.pack(pady=5)

        delete_button = tk.Button(
            self.root, text="Delete Task", width=20, command=self.delete_task, bg="orange")
        delete_button.pack(pady=5)

        self.update_listbox()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('700x600')
    app = ToDoApp(root)
    root.mainloop()
