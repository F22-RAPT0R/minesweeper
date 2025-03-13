import tkinter as tk
from tkinter import messagebox
from random import sample
from shelve import open
from os import mkdir, path
from threading import Thread
from time import time, sleep

class GAME:
    def __init__(self):
        MENU()        

class CELL:
    def __init__(self, row_index, column_index, master, board):
        self.row_index=row_index
        self.column_index=column_index
        self.board=board
        self.texts=[" ", "*", "?"]
        self.bgs=["grey", "red", "yellow"]
        self.states=[tk.NORMAL, tk.DISABLED, tk.DISABLED]
        self.cell_state_index=0
        self.button=tk.Button(master=master, text=self.texts[self.cell_state_index], width=1, height=1, bg=self.bgs[self.cell_state_index])
        self.button.bind("<Button-1>", self.left_click)
        self.button.bind("<Button-3>", self.right_click)
        self.button.bind("<Enter>", lambda *args:self.board.cell_hover_on(self.row_index, self.column_index))
        self.button.bind("<Leave>", lambda *args:self.board.cell_hover_off(self.row_index, self.column_index))
        self.is_mine=False
        self.is_chosen=False

    def left_click(self, *args):
        if self.is_chosen==False and self.cell_state_index==0:
            self.is_chosen=True

            if self.is_mine==True:
                self.board.lose()
            else:
                self.button.config(bg="green", relief=tk.SUNKEN, text=self.board.adjacent_mines(self.row_index, self.column_index))    
                self.board.check_win()

    def right_click(self, *args):
        if self.is_chosen==False:
            self.cell_state_index=(self.cell_state_index+1)%len(self.texts)  
            self.button.config(text=self.texts[self.cell_state_index], bg=self.bgs[self.cell_state_index], state=self.states[self.cell_state_index])            

class PLAY:
    def __init__(self, parent):
        self.parent=parent

        self.thread=Thread(target=self.timer, daemon=True)
        self.thread.start()

        data=DATABASE().read_settings()
        self.row_number=data["row_number"]
        self.column_number=data["column_number"]
        self.mine_number=data["mine_number"]

        self.gui()

    def gui(self):
        self.window=tk.Toplevel(master=self.parent)
        self.window.title("MINESWEEPER")
        self.window.rowconfigure(index=[0], weight=1, minsize=50)
        self.window.rowconfigure(index=[1], weight=3, minsize=150)
        self.window.columnconfigure(index=[0], weight=1)

        self.window.protocol("WM_DELETE_WINDOW", self.exit)

        self.info_frame=tk.Frame(master=self.window)
        self.info_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.info_label=tk.Label(master=self.info_frame, bg="black", fg="white")
        self.info_label.pack(expand=True, fill=tk.BOTH)
        self.cells_frame=tk.Frame(master=self.window)
        self.cells_frame.rowconfigure(index=[i for i in range(self.row_number)], weight=1)
        self.cells_frame.columnconfigure(index=[i for i in range(self.column_number)], weight=1)
        self.cells_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=10)

        self.cells=[]   #2D list
        for i in range(self.row_number):
            self.cells.append([])
            for j in range(self.column_number):
                cell=CELL(row_index=i, column_index=j, master=self.cells_frame, board=self)
                cell.button.grid(row=i, column=j, sticky="nswe", padx=1, pady=1)
                self.cells[i].append(cell)

        self.plant_mines()
        self.print_board()
        self.window.mainloop()        

    def print_board(self):
        print()
        for row in self.cells:
            for cell in row:
                print(cell.is_mine, end="\t")
            print()    
        print()

    def lose(self):
        self.info_label.configure(text="YOU LOST", fg="white", bg="red")
        messagebox.showinfo("you lost")
        self.exit()

    def win(self):
        self.info_label.configure(text="YOU WON", fg="white", bg="green")
        messagebox.showinfo("you won")
        self.exit()

    def adjacent_cells(self, row_index, column_index):
        adjacent_cells=[]
        top_left_cell_row_index=max(0, row_index-1)
        top_left_cell_column_index=max(0, column_index-1)
        bottom_right_cell_row_index=min(self.row_number-1, row_index+1)
        bottom_right_cell_column_index=min(self.column_number-1, column_index+1)
        
        for i in range(top_left_cell_row_index, bottom_right_cell_row_index+1):
            for j in range(top_left_cell_column_index, bottom_right_cell_column_index+1):
                if not(i==row_index and j==column_index):
                    adjacent_cells.append(self.cells[i][j])

        return adjacent_cells
    
    def adjacent_mines(self, row_index, column_index):
        adjacent_cells=self.adjacent_cells(row_index, column_index)

        adjacent_mines_number=0
        for cell in adjacent_cells:
            if cell.is_mine==True:
                adjacent_mines_number+=1
        
        if adjacent_mines_number==0:
            for cell in adjacent_cells:
                cell.left_click()
                            
        return adjacent_mines_number

    def plant_mines(self):
        cells_tmp=[]
        for i in range(self.row_number):
            for j in range(self.column_number):
                cells_tmp.append(self.cells[i][j])

        for cell in sample(cells_tmp, self.mine_number):
            cell.is_mine=True

    def check_win(self):
        win_flag=True
        for row in self.cells:
            for cell in row:
                if cell.is_mine==False and cell.is_chosen==False:
                    win_flag=False
                    break
        
        if win_flag==True:
            self.win()

    def cell_hover_on(self, row_index, column_index):
        for cell in self.adjacent_cells(row_index, column_index):
            if cell.is_chosen==False and cell.cell_state_index==0:
                cell.button.configure(relief=tk.SUNKEN)

    def cell_hover_off(self, row_index, column_index):
        for cell in self.adjacent_cells(row_index, column_index):
            if cell.is_chosen==False and cell.cell_state_index==0:
                cell.button.configure(relief=tk.RAISED)

    def exit(self):      
        self.window.destroy()
        self.parent.deiconify() 
        # del self

    def timer(self):
        i=1
        while True:
            sleep(1)
            # self.info_label.configure(text=f"ELAPSED TIME: {i}")
            i+=1
            print(time())

class MENU:
    def __init__(self):
        self.gui()

    def gui(self):
        self.window=tk.Tk()
        self.window.rowconfigure([0, 1, 2, 3], weight=1)
        self.window.columnconfigure([0], weight=1)

        self.window.protocol("WM_DELETE_WINDOW", self.exit)

        self.play_button=tk.Button(master=self.window, text="play", width=10, height=2, bg="black", fg="white", command=lambda :self.play())
        self.play_button.grid(row=0, column=0)
        self.settings_button=tk.Button(master=self.window, text="settings", width=10, height=2, bg="black", fg="white", command=lambda :self.settings())
        self.settings_button.grid(row=1, column=0)
        self.about_button=tk.Button(master=self.window, text="about", width=10, height=2, bg="black", fg="white", command=lambda :self.about())
        self.about_button.grid(row=2, column=0)        
        self.exit_button=tk.Button(master=self.window, text="exit", width=10, height=2, bg="black", fg="white", command=lambda :self.exit())
        self.exit_button.grid(row=3, column=0)

        self.window.mainloop()    

    def play(self):
        self.window.withdraw()
        PLAY(self.window)        
        
    def settings(self):
        self.window.withdraw()
        SETTINGS(self.window)

    def about(self):
        self.window.withdraw()
        ABOUT(self.window)        

    def exit(self):
        self.window.destroy()

class SETTINGS:
    def __init__(self, parent):
        self.parent=parent
        self.database=DATABASE()
        self.data=self.database.read_settings()
        self.gui()
   
    def gui(self):
        self.window=tk.Toplevel(master=self.parent)
        self.window.rowconfigure([0, 1, 2, 3], weight=1)
        self.window.columnconfigure([0, 1], weight=1)

        self.window.protocol("WM_DELETE_WINDOW", self.exit)

        row_index=0
        self.row_number_label=tk.Label(master=self.window, text="row number", width=12, height=1, bg="black", fg="white")                
        self.row_number_label.grid(row=row_index, column=0, sticky="e", padx=2)
        self.row_number_entry=tk.Entry(master=self.window, width=10)   
        self.row_number_entry.insert(0, self.data["row_number"])             
        self.row_number_entry.grid(row=row_index, column=1, sticky="w", padx=2)

        row_index+=1
        self.column_number_label=tk.Label(master=self.window, text="column number", width=12, height=1, bg="black", fg="white")                
        self.column_number_label.grid(row=row_index, column=0, sticky="e", padx=2)
        self.column_number_entry=tk.Entry(master=self.window, width=10)  
        self.column_number_entry.insert(0, self.data["column_number"])             
        self.column_number_entry.grid(row=row_index, column=1, sticky="w", padx=2)

        row_index+=1
        self.mine_number_label=tk.Label(master=self.window, text="mine number", width=12, height=1, bg="black", fg="white")                
        self.mine_number_label.grid(row=row_index, column=0, sticky="e", padx=2)
        self.mine_number_entry=tk.Entry(master=self.window, width=10)
        self.mine_number_entry.insert(0, self.data["mine_number"])             
        self.mine_number_entry.grid(row=row_index, column=1, sticky="w", padx=2)

        row_index+=1
        self.save_button=tk.Button(master=self.window, text="save", width=10, height=2, command=self.save)
        self.save_button.grid(row=row_index, column=0, sticky="e", padx=5)
        self.abort_button=tk.Button(master=self.window, text="abort", width=10, height=2, command=self.abort)
        self.abort_button.grid(row=row_index, column=1, sticky="w", padx=5)

        self.window.mainloop()

    def save(self, *args):
        data={"row_number":int(self.row_number_entry.get()), "column_number":int(self.column_number_entry.get()), "mine_number":int(self.mine_number_entry.get())}      
        self.database.write_settings(data)
        self.exit()

    def abort(self, *args):
        self.exit()

    def exit(self):
        self.window.destroy()   
        self.parent.deiconify() 

class ABOUT:
    def __init__(self, parent):
        self.parent=parent
        self.gui()

    def gui(self):
        # self.window=tk.Toplevel(master=self.parent)
        # self.window.protocol("WM_DELETE_WINDOW", self.exit)
        self.exit()
        # self.window.mainloop()

    def exit(self):
        # self.window.destroy()
        self.parent.deiconify() 

class DATABASE:
    def __init__(self):
        self.database_folder="DATA_BASE"
        self.db_path=f"{self.database_folder}/DB"
        self.create_DB()
    
    def create_DB(self):
        if not path.exists(self.database_folder):
            mkdir(self.database_folder)
        with open(self.db_path) as db:
            if db:
                pass
            else:   #db does not exist or its empty
                data={"row_number":5, "column_number":5, "mine_number":5}
                db["settings"]=data

    def read_settings(self):
        with open(self.db_path) as db:
            return db["settings"]    

    def write_settings(self, data):
        with open(self.db_path) as db:
            db["settings"]=data

if __name__=="__main__":
    game=GAME()