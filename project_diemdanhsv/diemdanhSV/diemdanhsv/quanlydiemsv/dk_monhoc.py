import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class DKMonhoc:
    def __init__(self, parent, db, auth_info_array):
        """
        auth_info_array: [USERNAME, role, (có thể là ID nếu có)]
        Trong trường hợp sinh viên tự đăng ký, chúng ta sẽ lấy ID_SINHVIEN từ bảng taikhoansv dựa trên USERNAME.
        Nếu role là "teacher", giao diện sẽ có combobox để chọn sinh viên.
        """
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.auth_info_array = auth_info_array
        self.student_class = None  # Dành cho sinh viên: thông tin lớp học
        self.create_ui()

    def create_ui(self):
        self.parent.configure(bg="#f0f0f0")
        
        # Header
        header_frame = tk.Frame(self.parent, bg="#007acc")
        header_frame.pack(fill=tk.X, padx=20, pady=(20,10))
        header_label = tk.Label(header_frame, text="Đăng ký môn học", 
                                font=("Segoe UI", 20, "bold"), fg="white", bg="#007acc", pady=10)
        header_label.pack()
        
        # Nếu role là sinh viên, hiển thị thông tin sinh viên
        if self.auth_info_array[1] == "student":
            info_label = tk.Label(self.parent, text=f"Người dùng: {self.auth_info_array[0]}",
                                  font=("Segoe UI", 16, "bold"), bg="#f0f0f0")
            info_label.pack(pady=5)
        
        # Main Frame chia làm 2 phần: bảng đăng ký & menu chức năng
        main_frame = tk.Frame(self.parent, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        
        # Bảng danh sách đăng ký môn học
        table_frame = tk.Frame(main_frame, bg="#f0f0f0")
        table_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=10)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        
        columns = ("Học kỳ", "Niên khóa", "Tên Sinh Viên", "Tên Môn")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, anchor=tk.CENTER, width=150)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.load_dangky_data()
        
        # Menu chức năng
        menu_frame = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, borderwidth=2)
        menu_frame.grid(row=0, column=1, sticky="nsew", pady=10)
        menu_frame.columnconfigure(0, weight=1)
        
        # Nếu role là teacher, cho phép chọn sinh viên từ combobox
        if self.auth_info_array[1] == "teacher":
            lbl_sv = tk.Label(menu_frame, text="Chọn sinh viên:", font=("Segoe UI", 12, "bold"), bg="white")
            lbl_sv.pack(pady=(10,5), padx=10, anchor="w")
            self.combo_sinhvien = ttk.Combobox(menu_frame, state="readonly", font=("Segoe UI", 12))
            self.combo_sinhvien.pack(padx=10, pady=(0,10), fill="x")
            self.load_sinhvien()
        else:
            # Sinh viên: tự lấy thông tin lớp học
            self.load_student_info()
            # Chỉ hiển thị thông tin lớp nếu có
            if self.student_class:
                lbl_class = tk.Label(menu_frame, text=f"Lớp: {self.student_class}", font=("Segoe UI", 12, "bold"), bg="white")
                lbl_class.pack(pady=(10,5), padx=10, anchor="w")
        
        # Combobox chọn môn học
        lbl_mon = tk.Label(menu_frame, text="Chọn môn học:", font=("Segoe UI", 12, "bold"), bg="white")
        lbl_mon.pack(pady=(10,5), padx=10, anchor="w")
        self.combo_mon = ttk.Combobox(menu_frame, state="readonly", font=("Segoe UI", 12))
        self.combo_mon.pack(padx=10, pady=(0,10), fill="x")
        
        # Nếu role là teacher, cần chọn lớp học để nạp môn; nếu sinh viên, tự nạp môn dựa vào lớp của sinh viên.
        if self.auth_info_array[1] == "teacher":
            lbl_lop = tk.Label(menu_frame, text="Chọn lớp học:", font=("Segoe UI", 12, "bold"), bg="white")
            lbl_lop.pack(pady=(10,5), padx=10, anchor="w")
            self.combo_lop = ttk.Combobox(menu_frame, state="readonly", font=("Segoe UI", 12))
            self.combo_lop.pack(padx=10, pady=(0,10), fill="x")
            self.combo_lop.bind("<<ComboboxSelected>>", self.load_monhoc_theo_lop)
            self.load_lop_hoc()
        else:
            self.load_monhoc_theo_student()
        
        # Nhập Học kỳ
        lbl_hocky = tk.Label(menu_frame, text="Học kỳ:", font=("Segoe UI", 12, "bold"), bg="white")
        lbl_hocky.pack(pady=(10,5), padx=10, anchor="w")
        self.entry_hocky = tk.Entry(menu_frame, font=("Segoe UI", 12))
        self.entry_hocky.pack(padx=10, pady=(0,10), fill="x")
        
        # Nhập Niên khóa
        lbl_nienkhoa = tk.Label(menu_frame, text="Niên khóa:", font=("Segoe UI", 12, "bold"), bg="white")
        lbl_nienkhoa.pack(pady=(10,5), padx=10, anchor="w")
        self.entry_nienkhoa = tk.Entry(menu_frame, font=("Segoe UI", 12))
        self.entry_nienkhoa.pack(padx=10, pady=(0,10), fill="x")
        
        self.btn_xacnhan = tk.Button(menu_frame, text="Xác nhận", font=("Segoe UI", 12, "bold"),
                                     bg="#007acc", fg="white", command=self.dangky_monhoc)
        self.btn_xacnhan.pack(pady=10, padx=10, fill="x")

    # def load_dangky_data(self):
    #     self.tree.delete(*self.tree.get_children())
    #     try:
    #         query = """
    #             SELECT d.HOCKY, d.NIENKHOA, s.TENSINHVIEN, m.TENMON
    #             FROM dangky d
    #             JOIN sinhvien s ON d.ID_SINHVIEN = s.ID_SINHVIEN
    #             JOIN monhoc m ON d.ID_MON = m.ID_MON
    #         """
    #         self.cursor.execute(query)
    #         for row in self.cursor.fetchall():
    #             self.tree.insert("", tk.END, values=row)
    #     except mysql.connector.Error as err:
    #         messagebox.showerror("Lỗi", f"Không thể tải danh sách đăng ký: {err}")

    def load_dangky_data(self):
        """Tải danh sách đăng ký môn học của tất cả sinh viên trong lớp của sinh viên đang đăng nhập."""
        self.tree.delete(*self.tree.get_children())  # Xóa dữ liệu cũ trong bảng hiển thị

        try:
            # Lấy ID_LOP của sinh viên đang đăng nhập
            sinhvien_id = self.auth_info_array[2]  # ID của sinh viên đăng nhập
            self.cursor.execute("SELECT ID_LOP FROM SINHVIEN WHERE ID_SINHVIEN = %s", (sinhvien_id,))
            res = self.cursor.fetchone()

            if not res:
                messagebox.showerror("Lỗi", "Không lấy được lớp học của sinh viên.")
                return

            lop_id = res[0]  # ID của lớp mà sinh viên thuộc về

            # Truy vấn danh sách đăng ký của tất cả sinh viên trong lớp đó
            query = """
                SELECT d.HOCKY, d.NIENKHOA, s.TENSINHVIEN, m.TENMON
                FROM DANGKY d
                JOIN SINHVIEN s ON d.ID_SINHVIEN = s.ID_SINHVIEN
                JOIN MONHOC m ON d.ID_MON = m.ID_MON
                WHERE s.ID_LOP = %s
            """
            self.cursor.execute(query, (lop_id,))

            # Hiển thị dữ liệu lên giao diện
            for row in self.cursor.fetchall():
                self.tree.insert("", tk.END, values=row)

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách đăng ký: {err}")

    def load_sinhvien(self):
        """Nạp danh sách sinh viên từ bảng SINHVIEN."""
        try:
            self.cursor.execute("SELECT ID_SINHVIEN, TENSINHVIEN FROM SINHVIEN")
            rows = self.cursor.fetchall()
            self.sv_dict = {r[1]: r[0] for r in rows}
            if self.auth_info_array[1] == "teacher":
                self.combo_sinhvien["values"] = list(self.sv_dict.keys())
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên: {err}")

    def load_lop_hoc(self):
        """Nạp danh sách lớp học vào combobox."""
        try:
            self.cursor.execute("SELECT ID_LOP, TENLOP FROM LOPHOC")
            rows = self.cursor.fetchall()
            self.lop_dict = {lop[1]: lop[0] for lop in rows}
            self.combo_lop["values"] = list(self.lop_dict.keys())
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp: {err}")

    def load_monhoc_theo_lop(self, event):
        """Nạp danh sách môn học theo lớp được chọn."""
        lop_selected = self.combo_lop.get()
        lop_id = self.lop_dict.get(lop_selected)
        if not lop_id:
            return
        try:
            self.cursor.execute("""
                SELECT M.ID_MON, M.TENMON FROM MONHOC M
                JOIN LOPHOC_MONHOC LM ON M.ID_MON = LM.ID_MON
                WHERE LM.ID_LOP = %s
            """, (lop_id,))
            rows = self.cursor.fetchall()
            self.mon_dict = {mon[1]: mon[0] for mon in rows}
            self.combo_mon["values"] = list(self.mon_dict.keys())
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách môn học: {err}")

    def load_monhoc_theo_student(self):
        """Dành cho sinh viên: tự nạp danh sách môn học từ lớp của sinh viên."""
        try:
            # Lấy lớp của sinh viên từ bảng SINHVIEN thông qua taikhoansv
            self.cursor.execute("SELECT ID_SINHVIEN FROM TAIKHOANSV WHERE USERNAME = %s", (self.auth_info_array[0],))
            result = self.cursor.fetchone()
            if result:
                sinhvien_id = result[0]
                # Lấy lớp của sinh viên từ bảng SINHVIEN
                self.cursor.execute("SELECT ID_LOP FROM SINHVIEN WHERE ID_SINHVIEN = %s", (sinhvien_id,))
                res = self.cursor.fetchone()
                if res:
                    lop_id = res[0]
                    self.cursor.execute("SELECT TENLOP FROM LOPHOC WHERE ID_LOP = %s", (lop_id,))
                    res2 = self.cursor.fetchone()
                    self.student_class = res2[0] if res2 else ""
                    
                    # Nạp môn học theo lớp
                    self.cursor.execute("""
                        SELECT M.ID_MON, M.TENMON FROM MONHOC M
                        JOIN LOPHOC_MONHOC LM ON M.ID_MON = LM.ID_MON
                        WHERE LM.ID_LOP = %s
                    """, (lop_id,))
                    rows = self.cursor.fetchall()
                    self.mon_dict = {mon[1]: mon[0] for mon in rows}
                    self.combo_mon["values"] = list(self.mon_dict.keys())
                else:
                    messagebox.showerror("Lỗi", "Không lấy được lớp học của sinh viên.")
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin tài khoản sinh viên trong TAIKHOANSV.")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể nạp môn học: {err}")

    def load_student_info(self):
        """Lấy thông tin lớp của sinh viên (dành cho sinh viên tự đăng ký)."""
        try:
            self.cursor.execute("SELECT ID_LOP FROM SINHVIEN WHERE ID_SINHVIEN = %s", (self.auth_info_array[2],))
            result = self.cursor.fetchone()
            if result:
                lop_id = result[0]
                self.cursor.execute("SELECT TENLOP FROM LOPHOC WHERE ID_LOP = %s", (lop_id,))
                res = self.cursor.fetchone()
                self.student_class = res[0] if res else ""
            else:
                self.student_class = ""
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể lấy thông tin sinh viên: {err}")

    def dangky_monhoc(self):
        # Nếu role là teacher, lấy sinh viên từ combobox; nếu là student, lấy ID từ taikhoansv của sinh viên
        if self.auth_info_array[1] == "teacher":
            sv_selected_name = self.combo_sinhvien.get()
            sinhvien_id = self.sv_dict.get(sv_selected_name)
            if sinhvien_id is None:
                messagebox.showerror("Lỗi", "Sinh viên không tồn tại trong hệ thống.")
                return
        else:
            try:
                self.cursor.execute("SELECT ID_SINHVIEN FROM TAIKHOANSV WHERE USERNAME = %s", (self.auth_info_array[0],))
                result = self.cursor.fetchone()
                if result:
                    sinhvien_id = result[0]
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy thông tin sinh viên trong TAIKHOANSV.")
                    return
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Không thể lấy ID sinh viên: {err}")
                return
        
        # Kiểm tra sự tồn tại của sinh viên trong bảng SINHVIEN
        try:
            self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN WHERE ID_SINHVIEN = %s", (sinhvien_id,))
            if self.cursor.fetchone()[0] == 0:
                messagebox.showerror("Lỗi", "Sinh viên không tồn tại trong hệ thống. Vui lòng liên hệ bộ phận quản trị!")
                return
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Kiểm tra sinh viên thất bại: {err}")
            return

        mon_selected = self.combo_mon.get()
        hocky = self.entry_hocky.get().strip()
        nienkhoa = self.entry_nienkhoa.get().strip()
        
        if not mon_selected or not hocky or not nienkhoa:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")
            return
        
        mon_id = self.mon_dict.get(mon_selected)
        if mon_id is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học hợp lệ.")
            return
        
        # Kiểm tra đăng ký trùng lặp
        try:
            self.cursor.execute("SELECT COUNT(*) FROM dangky WHERE ID_SINHVIEN = %s AND ID_MON = %s",
                                (sinhvien_id, mon_id))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showwarning("Cảnh báo", "Sinh viên đã đăng ký môn học này rồi.")
                return
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra trùng lặp: {err}")
            return
        
        try:
            self.cursor.execute("INSERT INTO dangky (HOCKY, NIENKHOA, ID_SINHVIEN, ID_MON) VALUES (%s, %s, %s, %s)",
                                (hocky, nienkhoa, sinhvien_id, mon_id))
            self.db.commit()
            messagebox.showinfo("Thông báo", "Đăng ký môn học thành công!")
            self.load_dangky_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể đăng ký môn học: {err}")
