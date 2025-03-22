import tkinter as tk

class QuanLyHinhAnh:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.parent, text="Quản lý Giảng viên").pack()
        # ... code ...