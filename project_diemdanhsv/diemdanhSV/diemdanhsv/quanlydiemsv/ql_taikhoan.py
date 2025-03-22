import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import openpyxl
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image, ImageTk


class QuanLyTaiKhoan:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.create_ui()
        self.load_giao_vien()
        self.load_data()

    def create_ui(self):
        tk.Label(self.parent, text="Quản Lý Tài Khoản", font=("Arial", 16, "bold"), fg="white", bg="blue").pack(pady=10, fill=tk.X)

        # Tạo Notebook chứa 2 tab
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Frame cho Giáo Viên
        self.giaovien_frame = tk.Frame(self.notebook, bg="lightgray", padx=10, pady=10)
        self.notebook.add(self.giaovien_frame, text="Giảng viên")

        # Frame cho Sinh Viên
        self.sinhvien_frame = tk.Frame(self.notebook, bg="lightgray", padx=10, pady=10)
        self.notebook.add(self.sinhvien_frame, text="Sinh Viên")

        # Giao diện quản lý tài khoản Giáo Viên
        self.create_giaovien_ui()
        self.create_sinhvien_ui()

    def create_giaovien_ui(self):
        self.giaovien_frame.configure(bg="lightgray")

        tk.Label(self.giaovien_frame, text="Giảng viên", font=("Arial", 18, "bold"), fg="black", bg="lightgray").grid(
            row=0, column=0, columnspan=2, pady=15)

        fields = [
            ("Tên tài khoản:", "entry_taikhoan", "entry"),
            ("Mật khẩu:", "entry_matkhau", "entry"),
            ("Quyền hạn:", "combobox_quyenhan", "combobox"),
            ("Giáo viên:", "combobox_giaovien", "combobox")  # Đổi tên để nhất quán
        ]

        self.entry_widgets = {}

        for i, (label_text, widget_name, widget_type) in enumerate(fields):
            tk.Label(self.giaovien_frame, text=label_text, bg="lightgray", font=("Arial", 12)).grid(
                row=i + 1, column=0, padx=10, pady=5, sticky="w"
            )

            if widget_type == "combobox":
                entry = ttk.Combobox(self.giaovien_frame, width=22, font=("Arial", 12), state="readonly")

                # Đặt giá trị cho combobox_quyenhan
                if widget_name == "combobox_quyenhan":
                    entry["values"] = ["Giáo viên", "Admin"]  # Giá trị hiển thị
                    entry.current(0)  # Chọn mặc định là Giáo viên

            else:
                entry = tk.Entry(self.giaovien_frame, font=("Arial", 12))

            if widget_name == "entry_matkhau":
                entry.config(show="")

            entry.grid(row=i + 1, column=1, padx=10, pady=5, sticky="ew")

            self.entry_widgets[widget_name] = entry  # Lưu vào dictionary để dễ quản lý

        button_frame = tk.Frame(self.giaovien_frame, bg="lightgray")
        button_frame.grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")

        self.buttons = {}  # Dictionary để lưu các button

        buttons = [
            ("Thêm tài khoản", "green", self.add_account, "GV_btn_add"),
            ("Sửa tài khoản", "orange", self.edit_account, "GV_btn_edit"),
            ("Xóa tài khoản", "red", self.delete_account, "GV_btn_delete"),
            ("Làm mới", "gray", self.refresh_data, "GV_btn_refresh")
        ]

        for i, (text, color, cmd, btn_name) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, bg=color, fg="white", font=("Arial", 12), width=12, command=cmd)
            btn.grid(row=0, column=i, padx=5)

            self.buttons[btn_name] = btn  # Lưu button vào dictionary với tiền tố "GV_"

        filter_frame = tk.Frame(self.giaovien_frame)
        filter_frame.grid(row=6, column=0, columnspan=2, pady=5, sticky="nsew")

        tk.Label(filter_frame, text="Tìm kiếm tài khoản:").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(filter_frame)
        self.search_entry.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text="🔍", command=self.search_account).grid(row=0, column=2, padx=5)

        tk.Button(filter_frame, text="Xuất Excel", command=self.export_to_excel).grid(row=0, column=6, padx=5)
        tk.Button(filter_frame, text="Thống kê", command=self.show_statistics).grid(row=0, column=7, padx=5)

        # Thêm cột "Mật khẩu" vào Treeview
        columns = ("ID", "Username", "Mật khẩu", "Quyền Hạn", "Giáo Viên")
        self.tree = ttk.Treeview(self.giaovien_frame, columns=columns, show="headings", height=8)
        self.tree.grid(row=7, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=160, anchor="center")

        self.tree.bind("<ButtonRelease-1>", self.on_treeview_select)

        self.giaovien_frame.grid_columnconfigure(0, weight=1)
        self.giaovien_frame.grid_columnconfigure(1, weight=1)
        self.load_giao_vien()
        self.load_data()

    def create_sinhvien_ui(self):
        self.sinhvien_frame.configure(bg="lightgray")

        tk.Label(self.sinhvien_frame, text="Sinh Viên", font=("Arial", 18, "bold"), fg="black", bg="lightgray").grid(
            row=0, column=0, columnspan=2, pady=15)

        fields_SV = [
            ("Tên tài khoản:", "entry_taikhoan"),
            ("Mật khẩu:", "entry_matkhau"),
            ("Sinh Viên:", "combobox_sinhvien")
        ]

        self.entry_widgets_SV = {}

        for i, (label_text, widget_name) in enumerate(fields_SV):
            tk.Label(self.sinhvien_frame, text=label_text, bg="lightgray", font=("Arial", 12)).grid(
                row=i + 1, column=0, padx=10, pady=5, sticky="w"
            )

            if "combobox" in widget_name:
                entry = ttk.Combobox(self.sinhvien_frame, width=22, font=("Arial", 12))
            else:
                entry = tk.Entry(self.sinhvien_frame, font=("Arial", 12))

            if widget_name == "entry_matkhau":
                entry.config(show="")

            entry.grid(row=i + 1, column=1, padx=10, pady=5, sticky="ew")

            self.entry_widgets_SV[widget_name] = entry  # Lưu vào dictionary để quản lý dễ dàng

        button_frame = tk.Frame(self.sinhvien_frame, bg="lightgray")
        button_frame.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")

        # Dictionary để lưu các button Sinh Viên
        self.buttons_SV = {}

        # Danh sách các button với thông tin: (Tên hiển thị, Màu sắc, Hàm xử lý, Tên biến)
        buttons_SV = [
            ("Thêm tài khoản", "green", self.add_student, "btn_add_student"),
            ("Sửa tài khoản", "orange", self.edit_student, "btn_edit_student"),
            ("Xóa tài khoảnn", "red", self.delete_student, "btn_delete_student"),
            ("Làm mới", "gray", self.refresh_student_data, "btn_refresh_student")
        ]

        # Tạo và lưu button vào dictionary
        for i, (text, color, cmd, btn_name) in enumerate(buttons_SV):
            btn = tk.Button(
                button_frame, text=text, bg=color, fg="white",
                font=("Arial", 12), width=12, command=cmd
            )
            btn.grid(row=0, column=i, padx=5)

            # Lưu button vào dictionary để dễ quản lý
            self.buttons_SV[btn_name] = btn
        filter_frame = tk.Frame(self.sinhvien_frame)
        filter_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky="nsew")

        tk.Label(filter_frame, text="Tìm kiếm tài khoản:").grid(row=0, column=0, padx=5)
        self.search_student_entry = tk.Entry(filter_frame)
        self.search_student_entry.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text="🔍", command=self.search_student).grid(row=0, column=2, padx=5)

        tk.Button(filter_frame, text="Xuất Excel", command=self.export_students_to_excel).grid(row=0, column=6, padx=5)
        tk.Button(filter_frame, text="Thống kê", command=self.show_student_statistics).grid(row=0, column=7, padx=5)

        # Thêm cột "Mật khẩu" vào Treeview
        columns = ("ID", "Username", "Mật khẩu", "Sinh Viên")
        self.tree_sv = ttk.Treeview(self.sinhvien_frame, columns=columns, show="headings", height=8)
        self.tree_sv.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        for col in columns:
            self.tree_sv.heading(col, text=col, anchor="center")
            self.tree_sv.column(col, width=160, anchor="center")

        self.tree_sv.bind("<ButtonRelease-1>", self.on_treeview_select_student)

        self.sinhvien_frame.grid_columnconfigure(0, weight=1)
        self.sinhvien_frame.grid_columnconfigure(1, weight=1)

        self.load_sinh_vien()
        self.load_data_sv()

    def load_giao_vien(self):
        self.cursor.execute("SELECT ID_GIAOVIEN, TENGIAOVIEN FROM giaovien")
        self.giaovien_list = {row[1]: row[0] for row in self.cursor.fetchall()}

        # Cập nhật danh sách vào Combobox
        combobox = self.entry_widgets["combobox_giaovien"]
        combobox["values"] = list(self.giaovien_list.keys())  # Gán danh sách vào Combobox

    def load_data(self):
        """Tải danh sách tài khoản giáo viên vào Treeview"""

        # Xóa dữ liệu cũ trên tree trước khi tải mới
        self.tree.delete(*self.tree.get_children())

        # Truy vấn lấy dữ liệu tài khoản giáo viên, bao gồm mật khẩu
        query = "SELECT ID_TKGV, USERNAME, PASSWORD, QUYENHAN, ID_GIAOVIEN FROM taikhoangv"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            # Chuyển đổi quyền hạn
            quyen = "Admin" if row[3] == 1 else "Giáo Viên"

            # Lấy tên giáo viên từ ID_GIAOVIEN
            giaovien_name = next((name for name, id_ in self.giaovien_list.items() if id_ == row[4]), "")

            # Hiển thị mật khẩu đầy đủ
            password = row[2]

            # Chèn dữ liệu vào bảng Treeview
            self.tree.insert("", "end", values=(row[0], row[1], password, quyen, giaovien_name))
    def add_account(self):
        username = self.entry_widgets["entry_taikhoan"].get().strip()
        password = self.entry_widgets["entry_matkhau"].get().strip()
        quyen = self.entry_widgets["combobox_quyenhan"].get()
        giaovien_name = self.entry_widgets["combobox_giaovien"].get()

        # Kiểm tra nếu bỏ trống
        if not username or not password or not quyen or not giaovien_name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Chuyển đổi quyền hạn
        quyen_value = 1 if quyen == "Admin" else 0

        # Kiểm tra giáo viên tồn tại
        id_giaovien = self.giaovien_list.get(giaovien_name)
        if id_giaovien is None:
            messagebox.showwarning("Lỗi", f"Giáo viên '{giaovien_name}' không tồn tại!")
            return

        try:
            # Kiểm tra username đã tồn tại chưa
            self.cursor.execute("SELECT COUNT(*) FROM taikhoangv WHERE USERNAME = %s", (username,))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi", "Tên tài khoản đã tồn tại!")
                return

            # Thêm tài khoản vào database
            query = "INSERT INTO taikhoangv (USERNAME, PASSWORD, QUYENHAN, ID_GIAOVIEN) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (username, password, quyen_value, id_giaovien))
            self.db.commit()

            messagebox.showinfo("Thành công", "Thêm tài khoản thành công!")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm tài khoản: {e}")

    def edit_account(self):
        # Kiểm tra xem có tài khoản nào được chọn hay không
        if not hasattr(self, "selected_account_id") or not self.selected_account_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một tài khoản để chỉnh sửa!")
            return

        # Lấy dữ liệu từ các ô nhập liệu
        username = self.entry_widgets["entry_taikhoan"].get().strip()
        password = self.entry_widgets["entry_matkhau"].get().strip()  # Nếu muốn thay đổi mật khẩu
        quyen = self.entry_widgets["combobox_quyenhan"].get()
        giaovien_name = self.entry_widgets["combobox_giaovien"].get()

        # Kiểm tra nếu các trường không được để trống
        if not username or not password:
            messagebox.showwarning("Lỗi", "Tên tài khoản và mật khẩu không được để trống!")
            return

        # Chuyển 'Quyền Hạn' thành giá trị số: 0 = Giáo viên, 1 = Admin
        quyen_value = 1 if quyen == "Admin" else 0

        # Tìm ID của giáo viên từ danh sách
        teacher_id = next((id_ for name, id_ in self.giaovien_list.items() if name == giaovien_name), None)

        if teacher_id is None:
            messagebox.showerror("Lỗi", f"Không tìm thấy giáo viên: {giaovien_name}")
            return

        # Chuẩn bị truy vấn SQL để cập nhật tài khoản
        query = """
              UPDATE taikhoangv
              SET USERNAME = %s, PASSWORD = %s, QUYENHAN = %s, ID_GIAOVIEN = %s
              WHERE ID_TKGV = %s
          """

        try:
            self.cursor.execute(query, (username, password, quyen_value, teacher_id, self.selected_account_id))
            self.db.commit()
            messagebox.showinfo("Thành công", "Tài khoản đã được cập nhật!")

            # Cập nhật lại dữ liệu hiển thị trên Treeview
            self.refresh_data()

            # Vô hiệu hóa nút chỉnh sửa sau khi cập nhật xong
            self.buttons["GV_btn_edit"].config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi cập nhật tài khoản:\n{str(e)}")

    def delete_account(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn tài khoản cần xóa!")
            return

        item = self.tree.item(selected_item[0])
        account_id = item["values"][0]

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tài khoản này?")
        if not confirm:
            return

        try:
            query = "DELETE FROM taikhoangv WHERE ID_TKGV = %s"
            self.cursor.execute(query, (account_id,))
            self.db.commit()
            messagebox.showinfo("Thành công", "Xóa tài khoản thành công!")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa tài khoản: {e}")

    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["ID", "Username", "Quyền Hạn", "Giáo Viên"])

        for row in self.tree.get_children():
            values = self.tree.item(row)['values']
            account_id, username, quyenhan, giaovien_name = values

            # Chuyển đổi quyền hạn từ số sang chữ
            # Ghi vào file Excel
            sheet.append([account_id, username, quyenhan, giaovien_name])

        workbook.save(file_path)
        messagebox.showinfo("Thành công", "Xuất file Excel thành công!")

    def show_statistics(self):
        # Thực hiện truy vấn SQL để thống kê quyền hạn tài khoản
        self.cursor.execute("SELECT QUYENHAN, COUNT(*) FROM taikhoangv GROUP BY QUYENHAN")
        data = self.cursor.fetchall()

        # Kiểm tra nếu không có dữ liệu
        if not data:
            messagebox.showinfo("Thống kê", "Không có dữ liệu.")
            return

        # Ánh xạ giá trị QUYENHAN (1: Admin, 0: Giáo viên)
        role_map = {1: "Admin", 0: "Giáo viên"}

        # Hiển thị thống kê quyền hạn tài khoản
        statistics = "\n".join([f"{role_map.get(row[0], 'Không xác định')}: {row[1]} tài khoản" for row in data])

        # Hiển thị kết quả thống kê trong một hộp thông báo
        messagebox.showinfo("Thống kê quyền hạn tài khoản", statistics)

    def filter_accounts(self):
        selected_role = self.filter_role.get()

        # Chuyển đổi vai trò thành giá trị số (0 cho 'Giáo Viên', 1 cho 'Admin')
        if selected_role == "Tất cả":
            query = "SELECT ID_TKGV, USERNAME, QUYENHAN, ID_GIAOVIEN FROM taikhoangv"
            self.cursor.execute(query)
        else:
            # Xác định giá trị số tương ứng với vai trò
            quyen_value = 1 if selected_role == "Admin" else 0

            query = "SELECT ID_TKGV, USERNAME, QUYENHAN, ID_GIAOVIEN FROM taikhoangv WHERE QUYENHAN = %s"
            self.cursor.execute(query, (quyen_value,))

        # Xóa dữ liệu cũ và cập nhật Treeview
        self.tree.delete(*self.tree.get_children())
        rows = self.cursor.fetchall()
        for row in rows:
            giaovien_name = next((name for name, id_ in self.giaovien_list.items() if id_ == row[3]), "")

            # Chuyển đổi QUYENHAN từ số về dạng string để hiển thị
            quyen = "Admin" if row[2] == 1 else "Giáo Viên"

            self.tree.insert("", "end", values=(row[0], row[1], quyen, giaovien_name))

    def search_account(self):
        keyword = self.search_entry.get()

        query = "SELECT ID_TKGV, USERNAME, QUYENHAN, ID_GIAOVIEN FROM taikhoangv WHERE USERNAME LIKE %s"
        self.cursor.execute(query, (f"%{keyword}%",))
        rows = self.cursor.fetchall()

        # Xóa tất cả dữ liệu cũ trong Treeview
        self.tree.delete(*self.tree.get_children())

        for row in rows:
            account_id, username, quyenhan, giaovien_id = row

            # Chuyển đổi quyền hạn từ số sang chữ
            quyen_text = "Admin" if quyenhan == 1 else "Giáo viên"

            # Lấy tên giáo viên từ ID_GIAOVIEN
            giaovien_name = next((name for name, id_ in self.giaovien_list.items() if id_ == giaovien_id),
                                 "Không xác định")

            # Chèn vào Treeview
            self.tree.insert("", "end", values=(account_id, username, quyen_text, giaovien_name))

    def refresh_data(self):
        """Xóa dữ liệu nhập vào và tải lại danh sách tài khoản"""
        try:
            # Xóa dữ liệu trong các ô nhập liệu
            if "entry_taikhoan" in self.entry_widgets:
                self.entry_widgets["entry_taikhoan"].delete(0, tk.END)
            if "entry_matkhau" in self.entry_widgets:
                self.entry_widgets["entry_matkhau"].delete(0, tk.END)
            if "combobox_quyenhan" in self.entry_widgets:
                self.entry_widgets["combobox_quyenhan"].set("")  # Reset quyền hạn
            if "combobox_giaovien" in self.entry_widgets:
                self.entry_widgets["combobox_giaovien"].set("")  # Reset giáo viên

            if hasattr(self, "search_entry"):
                self.search_entry.delete(0, tk.END)  # Xóa ô tìm kiếm
            if hasattr(self, "filter_role") and isinstance(self.filter_role, ttk.Combobox):
                self.filter_role.current(0)  # Đặt lại bộ lọc về "Tất cả"

            # Vô hiệu hóa các button sửa & xóa nếu không có tài khoản nào được chọn
            if hasattr(self, "edit_button"):
                self.edit_button.config(state="disabled")
            if hasattr(self, "delete_button"):
                self.delete_button.config(state="disabled")

            # Load lại dữ liệu danh sách tài khoản
            self.load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể làm mới dữ liệu: {e}")

    def on_treeview_select(self, event):
        """Xử lý khi chọn một tài khoản giáo viên trong Treeview"""

        # Lấy mục được chọn trong Treeview
        selected_item = self.tree.selection()
        if not selected_item:
            return  # Không có mục nào được chọn, thoát khỏi hàm

        # Lấy các giá trị từ mục đã chọn
        item = self.tree.item(selected_item[0])
        values = item.get("values", [])

        # Kiểm tra xem có đủ dữ liệu hay không
        if len(values) < 5:
            return  # Nếu dữ liệu không đầy đủ, thoát khỏi hàm để tránh lỗi

        account_id, username, password, quyen, giaovien_name = values

        # Lưu ID tài khoản đã chọn để sử dụng sau này
        self.selected_account_id = account_id

        # Điền dữ liệu vào các ô nhập liệu
        self.entry_widgets["entry_taikhoan"].delete(0, tk.END)
        self.entry_widgets["entry_taikhoan"].insert(0, username)

        # Hiển thị mật khẩu bình thường
        self.entry_widgets["entry_matkhau"].delete(0, tk.END)
        self.entry_widgets["entry_matkhau"].insert(0, password)

        # Đặt giá trị cho combobox quyền hạn
        self.entry_widgets["combobox_quyenhan"].set(quyen)

        # Đặt giá trị cho combobox giáo viên
        self.entry_widgets["combobox_giaovien"].set(giaovien_name)

        # Kích hoạt nút sửa và xóa
        self.buttons["GV_btn_edit"].config(state="normal")
        self.buttons["GV_btn_delete"].config(state="normal")

    # Sinh Viên
    def load_sinh_vien(self):
        """Load danh sách sinh viên vào combobox"""
        self.cursor.execute("SELECT ID_SINHVIEN, TENSINHVIEN FROM sinhvien")
        self.sinhvien_list = {row[1]: row[0] for row in self.cursor.fetchall()}  # Lưu tên sinh viên và ID tương ứng
        # Cập nhật danh sách vào Combobox
        combobox = self.entry_widgets_SV["combobox_sinhvien"]
        combobox["values"] = list(self.sinhvien_list.keys())   # Gán danh sách vào Combobox

    def load_data_sv(self):
        """Tải danh sách tài khoản sinh viên vào Treeview"""

        # Xóa dữ liệu cũ trên tree_sv trước khi tải mới
        self.tree_sv.delete(*self.tree_sv.get_children())

        # Truy vấn lấy dữ liệu tài khoản sinh viên, bao gồm mật khẩu
        query = "SELECT ID_TKSV, USERNAME, PASSWORD, ID_SINHVIEN FROM taikhoansv"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        for row in rows:
            # Lấy tên sinh viên từ ID_SINHVIEN
            sinhvien_name = next((name for name, id_ in self.sinhvien_list.items() if id_ == row[3]), "Không xác định")

            # Hiển thị mật khẩu đầy đủ
            password = row[2]

            # Chèn dữ liệu vào bảng Treeview
            self.tree_sv.insert("", "end", values=(row[0], row[1], password, sinhvien_name))
    def add_student(self):
        # Lấy dữ liệu từ các Entry và Combobox
        username = self.entry_widgets_SV["entry_taikhoan"].get().strip()
        password = self.entry_widgets_SV["entry_matkhau"].get().strip()
        sinhvien = self.entry_widgets_SV["combobox_sinhvien"].get().strip()

        # Kiểm tra dữ liệu nhập vào
        if not username or not password or not sinhvien:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Kiểm tra ID sinh viên từ danh sách (nếu có)
        id_sv = self.sinhvien_list.get(sinhvien, None)
        if id_sv is None:
            messagebox.showwarning("Lỗi", "Sinh viên không hợp lệ!")
            return

        try:
            # Chèn dữ liệu vào bảng 'taikhoansv'
            query = "INSERT INTO taikhoansv (USERNAME, PASSWORD, ID_SINHVIEN) VALUES (%s, %s, %s)"
            self.cursor.execute(query, (username, password, id_sv))
            self.db.commit()  # Lưu vào CSDL

            messagebox.showinfo("Thành công", "Thêm sinh viên thành công!")
            self.refresh_student_data()  # Làm mới danh sách sinh viên

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm sinh viên: {e}")

    def edit_student(self):
        """Cập nhật thông tin sinh viên sau khi chỉnh sửa"""

        # Lấy dữ liệu từ các ô nhập liệu
        username = self.entry_widgets_SV["entry_taikhoan"].get().strip()
        password = self.entry_widgets_SV["entry_matkhau"].get().strip()  # Nếu người dùng muốn thay đổi mật khẩu
        sinhvien_name = self.entry_widgets_SV["combobox_sinhvien"].get().strip()

        # Kiểm tra nếu chưa chọn sinh viên nào để chỉnh sửa
        if not hasattr(self, "selected_student_id") or not self.selected_student_id:
            messagebox.showerror("Lỗi", "Vui lòng chọn một sinh viên để chỉnh sửa!")
            return

        # Kiểm tra xem các trường nhập liệu có hợp lệ không
        if not username or not password or not sinhvien_name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Lấy ID sinh viên từ tên sinh viên được chọn
        student_id = self.sinhvien_list.get(sinhvien_name, None)

        # Nếu không tìm thấy sinh viên trong danh sách, hiển thị lỗi
        if student_id is None:
            messagebox.showerror("Lỗi", "Sinh viên không tồn tại!")
            return

        # Chuẩn bị câu lệnh SQL để cập nhật tài khoản sinh viên
        query = "UPDATE taikhoansv SET USERNAME = %s, PASSWORD = %s, ID_SINHVIEN = %s WHERE ID_TKSV = %s"

        try:
            self.cursor.execute(query, (username, password, student_id, self.selected_student_id))
            self.db.commit()  # Lưu thay đổi vào cơ sở dữ liệu

            # Hiển thị thông báo thành công
            messagebox.showinfo("Thành công", "Cập nhật thông tin sinh viên thành công!")

            # Làm mới danh sách sinh viên sau khi cập nhật
            self.refresh_student_data()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin sinh viên: {e}")

    def delete_student(self):
        selected_item = self.tree_sv.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn tài khoản cần xóa!")
            return

        item = self.tree_sv.item(selected_item[0])
        student_id = item["values"][0]  # Giả sử cột ID sinh viên là cột đầu tiên

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tài khoản này?")
        if not confirm:
            return

        try:
            # Câu lệnh SQL để xóa tài khoản sinh viên dựa trên ID
            query = "DELETE FROM taikhoansv WHERE ID_TKSV = %s"
            self.cursor.execute(query, (student_id,))
            self.db.commit()

            messagebox.showinfo("Thành công", "Xóa tài khoản sinh viên thành công!")
            self.refresh_student_data()  # Làm mới lại dữ liệu sau khi xóa

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa tài khoản sinh viên: {e}")

    def refresh_student_data(self):
        """Xóa dữ liệu nhập vào và tải lại danh sách tài khoản sinh viên"""

        # Xóa dữ liệu trong các ô nhập liệu
        self.entry_widgets_SV["entry_taikhoan"].delete(0, tk.END)
        self.entry_widgets_SV["entry_matkhau"].delete(0, tk.END)
        self.entry_widgets_SV["combobox_sinhvien"].set("")  # Reset combobox sinh viên

        # Kiểm tra nếu ô tìm kiếm tồn tại trước khi xóa dữ liệu
        if hasattr(self, "search_student_entry"):
            self.search_student_entry.delete(0, tk.END)  # Xóa ô tìm kiếm
        # Đặt lại trạng thái của các nút "Sửa" và "Xóa"
        if "btn_edit_student" in self.buttons_SV:
            self.buttons_SV["btn_edit_student"].config(state="disabled")
        if "btn_delete_student" in self.buttons_SV:
            self.buttons_SV["btn_delete_student"].config(state="disabled")

        # Tải lại dữ liệu danh sách sinh viên vào treeview
        self.load_sinh_vien()  # Hàm này cần phải load lại dữ liệu từ CSDL và hiển thị lên Treeview
        self.load_data_sv()  # Nếu cần, bạn có thể sử dụng thêm hàm này để tải lại dữ liệu sinh viên vào giao diện.

    def search_student(self):
        keyword = self.search_student_entry.get().strip()  # Lấy từ khóa từ ô tìm kiếm

        # Câu lệnh SQL sử dụng JOIN để lấy tên sinh viên từ bảng sinhvien
        query = """
            SELECT t.ID_TKSV, t.USERNAME, s.TENSINHVIEN
            FROM taikhoansv t
            JOIN sinhvien s ON t.ID_SINHVIEN = s.ID_SINHVIEN
            WHERE t.USERNAME LIKE %s
        """

        try:
            self.cursor.execute(query, (f"%{keyword}%",))
            rows = self.cursor.fetchall()

            # Xóa dữ liệu cũ trong Treeview
            self.tree_sv.delete(*self.tree_sv.get_children())

            # Thêm dữ liệu mới vào bảng Treeview
            for row in rows:
                self.tree_sv.insert("", "end", values=row)  # Chèn trực tiếp vì row đã có đầy đủ thông tin

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tìm kiếm sinh viên: {e}")

    def export_students_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # Cập nhật tên cột theo thông tin sinh viên
        sheet.append(["ID", "Username", "Sinh Viên"])

        # Lấy dữ liệu từ Treeview chứa sinh viên (self.tree_sv)
        for row in self.tree_sv.get_children():
            sheet.append(self.tree_sv.item(row)['values'])

        workbook.save(file_path)
        messagebox.showinfo("Thành công", "Xuất file Excel thành công!")

    def show_student_statistics(self):
        # Thống kê tổng số tài khoản và tổng số sinh viên có tài khoản
        self.cursor.execute("SELECT COUNT(DISTINCT ID_SINHVIEN) FROM taikhoansv")
        total_students = self.cursor.fetchone()[0]  # Tổng số sinh viên có tài khoản

        self.cursor.execute("SELECT COUNT(*) FROM taikhoansv")
        total_accounts = self.cursor.fetchone()[0]  # Tổng số tài khoản

        # Hiển thị thống kê
        statistics = f"Tổng số tài khoản: {total_accounts}\nTổng số sinh viên có tài khoản: {total_students}"

        messagebox.showinfo("Thống kê tài khoản sinh viên", statistics)

    def on_treeview_select_student(self, event):
        """Xử lý khi chọn một sinh viên trong Treeview"""

        # Lấy mục được chọn trong Treeview
        selected_item = self.tree_sv.selection()
        if not selected_item:
            return  # Không có mục nào được chọn, thoát khỏi hàm

        # Lấy các giá trị từ mục đã chọn
        item = self.tree_sv.item(selected_item[0])
        values = item.get("values", [])

        # Kiểm tra xem có đủ dữ liệu hay không
        if len(values) < 4:
            return  # Nếu dữ liệu không đầy đủ, thoát khỏi hàm để tránh lỗi

        student_id, username, password, sinhvien_name = values

        # Lưu ID sinh viên được chọn để sử dụng sau này
        self.selected_student_id = student_id

        # Điền dữ liệu vào các ô nhập liệu
        self.entry_widgets_SV["entry_taikhoan"].delete(0, tk.END)
        self.entry_widgets_SV["entry_taikhoan"].insert(0, username)

        # Hiển thị mật khẩu bình thường
        self.entry_widgets_SV["entry_matkhau"].delete(0, tk.END)
        self.entry_widgets_SV["entry_matkhau"].insert(0, password)

        # Điền tên sinh viên vào combobox
        self.entry_widgets_SV["combobox_sinhvien"].set(sinhvien_name)

        # Kích hoạt các nút "Sửa" và "Xóa" khi có sinh viên được chọn
        if "btn_edit_student" in self.buttons_SV:
            self.buttons_SV["btn_edit_student"].config(state="normal")
        if "btn_delete_student" in self.buttons_SV:
            self.buttons_SV["btn_delete_student"].config(state="normal")