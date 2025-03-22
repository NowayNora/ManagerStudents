import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector

class QuanLyDiem:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.create_ui()
        self.load_diem()

    def create_ui(self):
        # Cài đặt nền cho cửa sổ chính
        self.parent.configure(bg="#f0f0f0")
        
        # Header
        header_frame = tk.Frame(self.parent, bg="#007acc")
        header_frame.pack(fill=tk.X, padx=20, pady=(20,10))
        header_label = tk.Label(header_frame, text="📊 Quản Lý Điểm Số", 
                                font=("Segoe UI", 20, "bold"), fg="white", bg="#007acc", pady=10)
        header_label.pack()
        
        # Main Frame chứa khung chức năng và bảng điểm
        main_frame = tk.Frame(self.parent, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)  # Dòng 1 dành cho bảng Treeview
        
        # Frame chức năng: đặt ở trên bảng
        func_frame = tk.Frame(main_frame, bg="#f0f0f0")
        func_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        
        # Bỏ nút thêm điểm; chỉ còn nút nhập điểm (đổi từ sửa điểm)
        btn_style = {"font": ("Segoe UI", 12, "bold"), "fg": "white", "width": 15}
        edit_btn = tk.Button(func_frame, text="📝 Nhập điểm", bg="#f0ad4e", **btn_style, command=self.edit_grade)
        edit_btn.pack(side=tk.LEFT, padx=5, pady=5)


        # delete_btn = tk.Button(func_frame, text="❌ Xoá điểm", bg="#d9534f", **btn_style, command=self.delete_grade)
        # delete_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Khung tìm kiếm (đặt bên phải)
        search_frame = tk.Frame(func_frame, bg="#f0f0f0")
        search_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        search_label = tk.Label(search_frame, text="Tìm kiếm:", font=("Segoe UI", 12), bg="#f0f0f0")
        search_label.pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 12), width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.search_grades())
        search_btn = tk.Button(search_frame, text="🔍", font=("Segoe UI", 12), bg="#007acc", fg="white", command=self.search_grades, width=5)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame bảng điểm: chứa Treeview và thanh trượt dọc/ngang
        table_frame = tk.Frame(main_frame, bg="#f0f0f0")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        columns = (
            "ID sinh viên", "Tên Sinh Viên", "Mã Môn", "Tên Môn",
            "Học kỳ", "Niên khóa", "Điểm 1", "Điểm 2", "Tổng Kết",
            "Điểm Chữ", "Thang Điểm 4", "Xếp Loại"
        )
        self.grade_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.grade_table.heading(col, text=col, anchor=tk.CENTER)
            width = 180 if col == "Tên Sinh Viên" else 120
            self.grade_table.column(col, anchor=tk.CENTER, width=width)
        self.grade_table.grid(row=0, column=0, sticky="nsew")
        
        # Thanh trượt dọc
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.grade_table.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.grade_table.configure(yscrollcommand=scroll_y.set)
        
        # Thanh trượt ngang
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.grade_table.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        self.grade_table.configure(xscrollcommand=scroll_x.set)

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
        # Xóa dữ liệu cũ trên bảng
        for row in self.grade_table.get_children():
            self.grade_table.delete(row)
        try:
            query = """
                SELECT sv.ID_SINHVIEN, sv.TENSINHVIEN, 
                       mh.ID_MON, mh.TENMON, 
                       dk.HOCKY, dk.NIENKHOA,
                       dk.DIEM1, dk.DIEM2, dk.KETQUA
                FROM DANGKY dk
                JOIN SINHVIEN sv ON dk.ID_SINHVIEN = sv.ID_SINHVIEN
                JOIN MONHOC mh ON dk.ID_MON = mh.ID_MON
            """
            self.cursor.execute(query)
            for row in self.cursor.fetchall():
                mssv, ten_sv, id_mon, ten_mon, hocky, nienkhoa, diem1, diem2, tong_ket = row
                diem1 = float(diem1) if diem1 is not None else ""
                diem2 = float(diem2) if diem2 is not None else ""
                tong_ket = float(tong_ket) if tong_ket is not None else ""
                letter, gpa, classification = self.convert_grade(tong_ket)
                self.grade_table.insert("", tk.END, values=(
                    mssv, ten_sv, id_mon, ten_mon,
                    hocky if hocky is not None else "",
                    nienkhoa if nienkhoa is not None else "",
                    diem1, diem2, tong_ket, letter, gpa, classification
                ))
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách điểm số: {err}")
    
    def grade_form(self, grade=None):
        form = tk.Toplevel(self.parent)
        # Nếu có bản ghi được chọn thì xem như đang nhập điểm (chỉnh sửa)
        form_title = "Nhập điểm" if grade else "Nhập điểm"
        form.title(form_title)
        form.geometry("400x400")
        form.config(bg="white")
        
        header_text = "📝 Nhập điểm" if grade else "➕ Nhập điểm"
        header_label = tk.Label(form, text=header_text, font=("Segoe UI", 20, "bold"), bg="white", fg="#007acc")
        header_label.pack(pady=10)
        
        form_frame = tk.Frame(form, bg="white")
        form_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Hiển thị thông tin cơ bản (không cho sửa)
        info_fields = [("ID sinh viên", "ID_SINHVIEN"), ("Tên Sinh Viên", "TENSINHVIEN"),
                       ("Mã Môn", "ID_MON"), ("Tên Môn", "TENMON")]
        data = grade if grade else {}
        row_idx = 0
        for label_text, key in info_fields:
            lbl = tk.Label(form_frame, text=label_text+":", font=("Segoe UI", 12, "bold"), bg="white")
            lbl.grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
            val = data.get(key, "") if data else ""
            val_lbl = tk.Label(form_frame, text=val, font=("Segoe UI", 12), bg="white")
            val_lbl.grid(row=row_idx, column=1, sticky="w", padx=10, pady=5)
            row_idx += 1
        
        # Ô nhập điểm
        diem_fields = ["Điểm 1", "Điểm 2"]
        entries = {}
        for field in diem_fields:
            lbl = tk.Label(form_frame, text=field+":", font=("Segoe UI", 12, "bold"), bg="white")
            lbl.grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
            ent = tk.Entry(form_frame, font=("Segoe UI", 12), bg="#f5f5f5", width=10)
            ent.grid(row=row_idx, column=1, sticky="w", padx=10, pady=5)
            if grade and field in grade:
                ent.insert(0, grade[field])
            entries[field] = ent
            row_idx += 1
        
        button_frame = tk.Frame(form, bg="white")
        button_frame.pack(pady=20)
        save_btn = tk.Button(button_frame, text="Lưu", font=("Segoe UI", 12, "bold"), bg="#007acc", fg="white",
                             command=lambda: self.save_grade(entries, grade, form))
        save_btn.grid(row=0, column=0, padx=10)
        cancel_btn = tk.Button(button_frame, text="Thoát", font=("Segoe UI", 12, "bold"), bg="#ff4d4d", fg="white",
                               command=form.destroy)
        cancel_btn.grid(row=0, column=1, padx=10)
    
    def save_grade(self, entries, grade=None, form=None):
        for field in ["Điểm 1", "Điểm 2"]:
            if not entries[field].get():
                messagebox.showwarning("Cảnh báo", f"Vui lòng nhập {field.lower()}!")
                return
        try:
            diem1 = float(entries["Điểm 1"].get())
            diem2 = float(entries["Điểm 2"].get())
            if not (0 <= diem1 <= 10) or not (0 <= diem2 <= 10):
                messagebox.showwarning("Cảnh báo", "Điểm phải nằm trong khoảng từ 0 đến 10!")
                return
            ketqua = round(diem1 * 0.3 + diem2 * 0.7, 2)
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Điểm phải là số hợp lệ!")
            return
        if not grade:
            messagebox.showwarning("Cảnh báo", "Không có thông tin bản ghi để cập nhật!")
            return
        id_sinhvien = grade.get("ID_SINHVIEN")
        id_mon = grade.get("ID_MON")
        try:
            self.cursor.execute("SELECT * FROM DANGKY WHERE ID_SINHVIEN = %s AND ID_MON = %s", (id_sinhvien, id_mon))
            existing_record = self.cursor.fetchone()
            if existing_record:
                query = """
                    UPDATE DANGKY
                    SET DIEM1 = %s, DIEM2 = %s, KETQUA = %s
                    WHERE ID_SINHVIEN = %s AND ID_MON = %s
                """
                self.cursor.execute(query, (diem1, diem2, ketqua, id_sinhvien, id_mon))
                self.db.commit()
                messagebox.showinfo("Thành công", "Cập nhật điểm số thành công!")
                self.load_diem()
                if form:
                    form.destroy()
            else:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy bản ghi điểm cho sinh viên đã đăng ký môn học!")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể cập nhật điểm số: {err}")
    
    def edit_grade(self):
        selected_item = self.grade_table.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một bản ghi để nhập điểm.")
            return
        grade_values = self.grade_table.item(selected_item)["values"]
        if len(grade_values) < 9:
            messagebox.showwarning("Lỗi", "Dữ liệu bản ghi không đầy đủ.")
            return
        grade_data = {
            "ID_SINHVIEN": grade_values[0],
            "TENSINHVIEN": grade_values[1],
            "ID_MON": grade_values[2],
            "TENMON": grade_values[3],
            "Điểm 1": grade_values[6],
            "Điểm 2": grade_values[7]
        }
        self.grade_form(grade_data)
    
    # def delete_grade(self):
    #     selected_item = self.grade_table.selection()
    #     if not selected_item:
    #         messagebox.showwarning("Cảnh báo", "Vui lòng chọn bản ghi để xoá.")
    #         return
    #     grade_values = self.grade_table.item(selected_item)["values"]
    #     if not grade_values:
    #         return
    #     id_sinhvien = grade_values[0]
    #     id_mon = grade_values[2]
    #     try:
    #         self.cursor.execute("DELETE FROM DANGKY WHERE ID_SINHVIEN = %s AND ID_MON = %s", (id_sinhvien, id_mon))
    #         self.db.commit()
    #         messagebox.showinfo("Thành công", "Xoá điểm thành công!")
    #         self.load_diem()
    #     except mysql.connector.Error as err:
    #         messagebox.showerror("Lỗi", f"Không thể xoá điểm: {err}")
    
    def search_grades(self):
        search_text = self.search_entry.get().strip()
        for row in self.grade_table.get_children():
            self.grade_table.delete(row)
        try:
            query = """
                SELECT sv.ID_SINHVIEN, sv.TENSINHVIEN, 
                       mh.ID_MON, mh.TENMON, 
                       dk.HOCKY, dk.NIENKHOA,
                       dk.DIEM1, dk.DIEM2, dk.KETQUA
                FROM DANGKY dk
                JOIN SINHVIEN sv ON dk.ID_SINHVIEN = sv.ID_SINHVIEN
                JOIN MONHOC mh ON dk.ID_MON = mh.ID_MON
                WHERE sv.TENSINHVIEN LIKE %s OR sv.ID_SINHVIEN LIKE %s
            """
            self.cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            for row in self.cursor.fetchall():
                letter, gpa, classification = self.convert_grade(row[8])
                self.grade_table.insert("", tk.END, values=row + (letter, gpa, classification))
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm: {err}")
