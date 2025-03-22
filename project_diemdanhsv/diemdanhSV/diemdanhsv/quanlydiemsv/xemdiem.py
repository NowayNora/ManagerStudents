import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

class XemDiem:
    def __init__(self, parent, db, auth_info=None):
        if not auth_info or not auth_info[0]:
            messagebox.showerror("Lỗi", "Thiếu thông tin xác thực sinh viên")
            return

        
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.auth_info = auth_info
        self.username = auth_info[0]  # Lấy username từ tài khoản sinh viên
        
        self.parent.configure(bg="#f0f0f0")
        
        # Lấy ID sinh viên và tên sinh viên từ tài khoản
        self.id_sinhvien, self.ten_sinhvien = self.get_student_info()
        if self.id_sinhvien is None:
            messagebox.showerror("Lỗi", "Không tìm thấy sinh viên cho tài khoản này")
            return
        
        self.create_ui()
        self.load_diem()
    def create_ui(self):
        header_frame = tk.Frame(self.parent, bg="#007acc")
        header_frame.pack(fill=tk.X, padx=20, pady=(20,10))
        header_label = tk.Label(header_frame, text=f"📊 Xem Điểm - {self.ten_sinhvien}", font=("Segoe UI", 20, "bold"), fg="white", bg="#007acc", pady=10)
        header_label.pack()
        
        # Khung tìm kiếm
        search_frame = tk.Frame(self.parent, bg="#f0f0f0")
        search_frame.pack(pady=5)
        search_label = tk.Label(search_frame, text="Tìm kiếm:", font=("Segoe UI", 12), bg="#f0f0f0")
        search_label.pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 12), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.load_diem())
        search_btn = tk.Button(search_frame, text="🔍", font=("Segoe UI", 12), bg="#007acc", fg="white", command=self.load_diem, width=5)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Bảng điểm
        columns = ("Mã Môn", "Tên Môn", "Học kỳ", "Niên khóa", "Điểm 1", "Điểm 2", "Tổng Kết", "Điểm Chữ", "Thang Điểm 4", "Xếp Loại")
        self.tree = ttk.Treeview(self.parent, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            width = 180 if col == "Tên Môn" else 120
            self.tree.column(col, anchor=tk.CENTER, width=width)
        self.tree.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    def get_student_info(self):
        try:
            self.cursor.execute(
                """
                SELECT sv.ID_SINHVIEN, sv.TENSINHVIEN 
                FROM taikhoansv tk 
                JOIN sinhvien sv ON tk.ID_SINHVIEN = sv.ID_SINHVIEN 
                WHERE tk.USERNAME = %s
                """, (self.username,)
            )
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể lấy thông tin sinh viên: {err}")
            return None, "Lỗi"
    
    def convert_grade(self, score):
        if score is None:
            return "", "", ""
        try:
            score = float(score)
        except ValueError:
            return "", "", ""
        if score < 4.0:
            return "E", 0.0, "Kém"
        elif 4.0 <= score < 5.0:
            return "D", 1.0, "Yếu"
        elif 5.0 <= score < 5.5:
            return "D+", 1.5, "Trung Bình Yếu"
        elif 5.5 <= score < 6.5:
            return "C", 2.0, "Trung Bình"
        elif 6.5 <= score < 7.0:
            return "C+", 2.5, "Trung Bình Khá"
        elif 7.0 <= score < 8.0:
            return "B", 3.0, "Khá"
        elif 8.0 <= score < 9.0:
            return "B+", 3.5, "Giỏi"
        elif 9.0 <= score <= 10.0:
            return "A", 4.0, "Xuất Sắc"
        return "", "", ""
    
    def load_diem(self):
        search_text = self.search_entry.get().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            query = """
                SELECT mh.ID_MON, mh.TENMON, d.HOCKY, d.NIENKHOA, d.DIEM1, d.DIEM2, d.KETQUA
                FROM dangky d
                JOIN monhoc mh ON d.ID_MON = mh.ID_MON
                WHERE d.ID_SINHVIEN = %s
            """
            params = [self.id_sinhvien]
            if search_text:
                query += " AND (mh.TENMON LIKE %s OR d.NIENKHOA LIKE %s)"
                params.extend([f"%{search_text}%", f"%{search_text}%"])
            
            self.cursor.execute(query, params)
            for row in self.cursor.fetchall():
                letter, gpa, classification = self.convert_grade(row[6])
                self.tree.insert("", tk.END, values=row + (letter, gpa, classification))
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách điểm: {err}")