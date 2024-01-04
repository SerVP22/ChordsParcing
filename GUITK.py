import tkinter as tk
from tkinter import ttk


# class ListFrame(tk.Frame):
#
#     def __init__(self, parent):
#         super().__init__(self, parent)
#         ttk.Label(self, text="test")



class MyTkApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.test_dict = {}

        self.title("Chords Parcing")
        self.geometry("800x600")

        string_1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        string_2 = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
        string_3 = "0..9"

        #    ПАНЕЛЬ ОПЦИЙ

        self.up_frame = ttk.LabelFrame(self, text="Опции" )
        self.up_frame.pack(fill=tk.BOTH, expand=False)
        # self.upfr_label_pic = tk.Label(self.up_frame, height=3)
        # self.upfr_label_pic.pack(side="left")
        self.pr_bar1 = ttk.Progressbar(self.up_frame, length=100).pack(side="left")
        btn1 = ttk.Button(self.up_frame,
                   text="Обновить список артистов",
                   command=lambda pr_b=self.pr_bar1: self.reload_artists(pr_b))
        btn1.pack(side="left")


        #     ПАНЕЛЬ НАВИГАЦИИ

        self.down_frame = ttk.LabelFrame(self, text="Исполнители",)
        self.down_frame.pack(fill=tk.BOTH, expand=True)

        self.main_book = ttk.Notebook(self.down_frame, padding=5)
        self.main_book.pack(expand=True, fill=tk.BOTH)

        self.frame1 = ttk.Frame(self.main_book)
        self.frame2 = ttk.Frame(self.main_book)
        self.frame3 = ttk.Frame(self.main_book)
        self.frame1.pack(fill=tk.BOTH, expand=True)
        self.frame2.pack(fill=tk.BOTH, expand=True)
        self.frame3.pack(fill=tk.BOTH, expand=True)



        self.main_book.add(self.frame2, text="    Русские буквы (А..Я)    ")
        if len(string_2)>0:
            self.rus_book = ttk.Notebook(self.frame2)
            self.rus_book.enable_traversal()
            self.rus_book.pack(expand=True, fill=tk.BOTH)
            for i in string_2:
                self.temp_frame = ttk.Frame(self.rus_book)
                self.temp_frame.pack(fill=tk.BOTH, expand=True)
                self.rus_book.add(self.temp_frame, text=i, underline=0)
                ttk.Label(self.temp_frame, text=f"test for {i} letter").pack()
                if i == "А":

                    self.tree = ttk.Treeview(self.temp_frame,
                                             columns=("name", "check", "in_db", "link"),
                                             show="headings",
                                             # image=img
                                             )
                    self.tree.heading("name", text="Исполнитель", anchor=tk.W)
                    self.tree.heading("check", text="Добавить", anchor=tk.W)
                    self.tree.heading("in_db", text="В базе", anchor=tk.W)
                    self.tree.heading("link", text="Ссылка", anchor=tk.W)
                    self.tree.column("#1", stretch=tk.NO, width=200)
                    self.tree.column("#2", stretch=tk.NO, width=100)
                    self.tree.column("#3", stretch=tk.NO, width=70)
                    self.tree.column("#4", stretch=tk.NO, width=400)
                    for char, data  in self.test_dict.items():
                        if i == char:
                            for artist, data_art in data[1].items():
                                self.tree.insert("", tk.END, values=(artist,
                                                                     "-",
                                                                     self.in_db_gen(data_art[0]),
                                                                     data_art[1]))
                    scroll = ttk.Scrollbar(self.temp_frame, command=self.tree.yview)
                    self.tree.configure(yscrollcommand=scroll.set)
                    scroll.pack(side=tk.RIGHT, fill=tk.Y)
                    self.tree.pack(expand=True, fill=tk.BOTH)
                    self.tree.bind("<<TreeviewSelect>>", lambda event, tree=self.tree:
                                                                self.item_selected(event, tree))

        self.main_book.add(self.frame1, text="    Английские буквы (A..Z)    ")
        if len(string_1) > 0:
            self.eng_book = ttk.Notebook(self.frame1)
            self.eng_book.enable_traversal()
            self.eng_book.pack(expand=True, fill=tk.BOTH)
            for i in string_1:
                self.temp_frame = ttk.Frame(self.eng_book)
                self.temp_frame.pack(fill=tk.BOTH, expand=True)
                self.eng_book.add(self.temp_frame, text=i, underline=0)
                ttk.Label(self.temp_frame, text=f"test for {i} letter").pack()

        self.main_book.add(self.frame3, text="    Цифровые символы (0..9)    ")
        if len(string_3)>0:
            self.digit_book = ttk.Notebook(self.frame3)
            self.digit_book.enable_traversal()
            self.digit_book.pack(expand=True, fill=tk.BOTH)
            for i in string_3:
                self.temp_frame = ttk.Frame(self.digit_book)
                self.temp_frame.pack(fill=tk.BOTH, expand=True)
                self.digit_book.add(self.temp_frame, text=i, underline=0)
                ttk.Label(self.temp_frame, text=f"test for {i} letter").pack()


    def item_selected(self, event, tree):
        # print(event.widget)
        # print(tree.selection(), tree.index(tree.selection()))
        # print(tree.item(tree.selection(), option="values"))

        if tree.item(tree.selection(), option="values")[1] == "-":
            val = "Добавлено"
        else:
            val = "-"

        tree.set(tree.selection(), column="#2", value=val)

    def in_db_gen(self, value):
        if value:
            return "Загружено"
        else:
            return "-"

    def get_progress_bar_link(self):
        return self.pr_bar1