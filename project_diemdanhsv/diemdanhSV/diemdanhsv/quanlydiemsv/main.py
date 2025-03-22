import tkinter as tk
from tkinter import messagebox, colorchooser
import mysql.connector

# Import các module quản lý
from sinhvien import QuanLySinhVien
from lophoc import QuanLyLopHoc
from khoa import QuanLyKhoa
from ql_monhoc import QuanLyMonHoc
from ql_taikhoan import QuanLyTaiKhoan
from ql_diem import QuanLyDiem
from dk_monhoc import DKMonhoc
from ql_guongmat import QuanLyGuongMat
from ql_giangvien import QuanLyGiangVien
from add_guongmat import ThemGuongMat
from ql_giangday import QuanLyGiangDay
from xemdiem import XemDiem

# Import module LichHoc
from lichhoc import LichHoc

class QuanLySinhVienApp(tk.Tk):
    def __init__(self, user_info):
        super().__init__()
        # user_info: [USERNAME, role, ID_SINHVIEN (nếu có)]
        self.user_info_auth = user_info
        if self.user_info_auth[1] == "teacher":
            self.Auth = "Giáo Viên"
        else:
            self.Auth = "Sinh Viên"

        self.title("Quản Lý Sinh Viên và Lớp Học")
        self.geometry("1200x700")
        self.configure(bg="#f5f5f5")

        self.sidebar_visible = True
        self.connect_database()
        self.create_header()
        self.create_sidebar()
        self.create_main_content()

    def connect_database(self):
        try:
            self.db = mysql.connector.connect(
                host="localhost", user="root", password="", database="diemdanhsv"
            )
            self.cursor = self.db.cursor()
            print("Kết nối cơ sở dữ liệu thành công!")
        except mysql.connector.Error as err:
            print(f"Lỗi kết nối database: {err}")

    def create_header(self):
        header = tk.Frame(self, bg="#007acc", height=50)
        header.pack(fill=tk.X)

        toggle_btn = tk.Button(header, text="☰", fg="white", bg="#007acc", bd=0,
                               font=("Arial", 16, "bold"), command=self.toggle_sidebar)
        toggle_btn.pack(side=tk.LEFT, padx=10)

        title_label = tk.Label(header,
                               text=f"Quản Lý Sinh Viên ({self.user_info_auth[0]}) | ({self.Auth})",
                               fg="white", bg="#007acc", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=20)

        settings_btn = tk.Button(header, text="⚙️ Cài đặt", fg="white", bg="#007acc", bd=0,
                                 font=("Arial", 12, "bold"), command=self.open_settings)
        settings_btn.pack(side=tk.RIGHT, padx=10)

        logout_btn = tk.Button(header, text="Đăng xuất", fg="white", bg="#e74c3c", bd=0,
                               font=("Arial", 12, "bold"), command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=10)

        info_btn = tk.Button(header, text="ℹ️ Thông tin", fg="white", bg="#007acc", bd=0,
                             font=("Arial", 12, "bold"), command=self.show_info)
        info_btn.pack(side=tk.LEFT, padx=10)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.sidebar_visible = True

    def create_sidebar(self):
        self.sidebar = tk.Frame(self, bg="#333", width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        if self.user_info_auth[1] == "teacher":
            menu_items = [
                ("🏠 Trang chủ", lambda: self.show_module("Trang chủ")),
                ("📚 Quản lý sinh viên", lambda: self.show_module(QuanLySinhVien)),
                ("🏫 Quản lý lớp học", lambda: self.show_module(QuanLyLopHoc)),
                ("🏫 Quản lý khoa", lambda: self.show_module(QuanLyKhoa)),
                ("📑 Quản lý môn học", lambda: self.show_module(QuanLyMonHoc)),
                ("👨‍🏫 Quản lý giảng viên", lambda: self.show_module(QuanLyGiangVien)),
                ("👨‍🏫 Quản lý giảng dạy", lambda: self.show_module(QuanLyGiangDay)),
                ("🔑 Quản lý tài khoản", lambda: self.show_module(QuanLyTaiKhoan)),
                ("📊 Quản lý điểm", lambda: self.show_module(QuanLyDiem)),
                ("📊 Điểm danh sinh viên", lambda: self.show_module(QuanLyGuongMat)),
                ("📚 Quản lý thêm gương mặt sinh viên", lambda: self.show_module(ThemGuongMat)),
            ]
        else:
            # Menu cho Sinh viên
            menu_items = [
                ("🏠 Trang chủ", lambda: self.show_module("Trang chủ")),
                ("🖼 Đăng ký môn học", lambda: self.show_module(DKMonhoc)),
                ("📝 Thông tin cá nhân", self.show_personal_info),
                ("📅 Lịch học", self.show_schedule),
                ("📊 Xem điểm", lambda: self.show_module(XemDiem))
            ]

        for text, command in menu_items:
            btn = tk.Button(self.sidebar, text=text, font=("Arial", 12), fg="white", bg="#444",
                            bd=0, relief=tk.FLAT, command=command, anchor="w", padx=20)
            btn.pack(fill=tk.X, pady=5)

    def create_main_content(self):
        self.main_content = tk.Frame(self, bg="white")
        self.main_content.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.show_dashboard()

    def show_dashboard(self):
        # Xóa nội dung cũ
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Header trang chủ
        header_label = tk.Label(self.main_content, text="🏠 Trang chủ", font=("Arial", 20, "bold"),
                                bg="white", fg="#007acc")
        header_label.pack(pady=10)

        if self.user_info_auth[1] == "teacher":
            # Dashboard của Giáo viên
            stats_frame = tk.Frame(self.main_content, bg="#e3f2fd", padx=20, pady=20, bd=2, relief=tk.GROOVE)
            stats_frame.pack(pady=20)
            data_labels = ["📘 Sinh viên", "🏫 Lớp học", "👨‍🏫 Giảng viên", "📖 Môn học"]
            self.stats_values = []
            for i , label in enumerate(data_labels):
                frame = tk.Frame(stats_frame, bg="white", relief=tk.RIDGE, bd=2)
                frame.grid(row=0, column=i, padx=15, pady=10)
                title_label = tk.Label(frame, text=label, font=("Arial", 12, "bold"), bg="white", fg="#333")
                title_label.pack(padx=10, pady=5)
                val_label = tk.Label(frame, text="0", font=("Arial", 16, "bold"), bg="white", fg="#d32f2f")
                val_label.pack(pady=5, padx=10)
                self.stats_values.append(val_label)
        else:
            # Dashboard của Sinh viên
            stats_frame = tk.Frame(self.main_content, bg="#e3f2fd", padx=20, pady=20, bd=2, relief=tk.GROOVE)
            stats_frame.pack(pady=20)
            data_labels = ["🏫 Lớp học", "📖 Môn học", "📊 Điểm trung bình"]
            self.stats_values = []
            for i, label in enumerate(data_labels):
                frame = tk.Frame(stats_frame, bg="white", relief=tk.RIDGE, bd=2)
                frame.grid(row=0, column=i, padx=15, pady=10)
                title_label = tk.Label(frame, text=label, font=("Arial", 12, "bold"), bg="white", fg="#333")
                title_label.pack(padx=10, pady=5)
                val_label = tk.Label(frame, text="0", font=("Arial", 16, "bold"), bg="white", fg="#d32f2f")
                val_label.pack(pady=5, padx=10)
                self.stats_values.append(val_label)
        
        # Nút cập nhật dữ liệu với hiệu ứng hover
        refresh_btn = tk.Button(self.main_content, text="🔄 Cập nhật", font=("Arial", 12, "bold"),
                                bg="#007acc", fg="white", padx=10, pady=5, relief=tk.RAISED,
                                command=self.update_dashboard)
        refresh_btn.pack(pady=15)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#005f99"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg="#007acc"))
        self.update_dashboard()

    def update_dashboard(self):
        try:
            if self.user_info_auth[1] == "teacher":
                queries = [
                    "SELECT COUNT(*) FROM sinhvien",
                    "SELECT COUNT(*) FROM lophoc",
                    "SELECT COUNT(*) FROM giaovien",
                    "SELECT COUNT(*) FROM monhoc"
                ]
            else:
                queries = [
                    "SELECT COUNT(*) FROM lophoc",
                    "SELECT COUNT(*) FROM monhoc",
                    # Giả sử bạn có bảng diem để tính điểm trung bình
                ]

            for i, query in enumerate(queries):
                self.cursor.execute(query)
                result = self.cursor.fetchone()
                if result is not None:
                    count = result[0]
                    print(f"Kết quả từ truy vấn {query}: {count}")  # Debug
                    self.stats_values[i].config(text=str(count))
                else:
                    print(f"Không có kết quả từ truy vấn {query}")  # Debug

            # Xử lý điểm trung bình (nếu là sinh viên)
            if self.user_info_auth[1] != "teacher":
                query = "SELECT ROUND(IFNULL(AVG(KETQUA), 0), 2) FROM dangky WHERE id_sinhvien = %s" % \
                        self.user_info_auth[2]
                self.cursor.execute(query)
                get_result = self.cursor.fetchone()[0]
                get_result = float(get_result)
                if get_result < 4.0:
                    count = 0.0
                elif 4.0 <= get_result < 5.0:
                    count = 1.0
                elif 5.0 <= get_result < 5.5:
                    count = 1.5
                elif 5.5 <= get_result < 6.5:
                    count = 2.0
                elif 6.5 <= get_result < 7.0:
                    count = 2.5
                elif 7.0 <= get_result < 8.0:
                    count = 3.0
                elif 8.0 <= get_result < 9.0:
                    count = 3.5
                elif 9.0 <= get_result < 10.0:
                    count = 4.0
                self.stats_values[2].config(text=str(count))

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể cập nhật dữ liệu: {err}")

    def show_module(self, module_class):
        # Xóa nội dung main content trước khi chuyển trang
        for widget in self.main_content.winfo_children():
            widget.destroy()
        # Nếu module thêm mà cần id của sv hoặc giáo viên hay bất cứ thông tin nào khác thì thêm vào array Special_Module_List
        # Vd: Special_Module_List = [DKMonhoc] => Special_Module_List = [DKMonhoc, XemDiem]
        Special_Module_List = [DKMonhoc, XemDiem]
        if module_class == "Trang chủ":
            self.show_dashboard()
        elif module_class in Special_Module_List:
            module_class(self.main_content, self.db, self.user_info_auth)
        else:
            module_class(self.main_content, self.db)

    # Các hàm bổ sung cho menu sinh viên
    def show_personal_info(self):
        # Xóa nội dung cũ trong main_content
        for widget in self.main_content.winfo_children():
            widget.destroy()

        # Lấy thông tin sinh viên từ cơ sở dữ liệu
        db = self.db
        cursor = db.cursor()
        query = """
            SELECT sv.TENSINHVIEN, sv.NGAYSINH, sv.GIOITINH, lh.TENLOP, sv.KHUONMAT
            FROM sinhvien sv
            LEFT JOIN lophoc lh ON sv.ID_LOP = lh.ID_LOP
            WHERE sv.ID_SINHVIEN = %s
        """
        cursor.execute(query, (self.user_info_auth[2],))  # Lấy ID sinh viên từ user_info_auth
        student = cursor.fetchone()

        # Kiểm tra nếu không tìm thấy sinh viên
        if not student:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin sinh viên")
            return

        # Xác định giới tính
        gioi_tinh = "Nam" if student[2] == 1 else "Nữ"

        # Hiển thị thông tin sinh viên trong main_content
        tk.Label(
            self.main_content,
            text="Thông tin Sinh Viên",
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#007acc"
        ).pack(pady=10)

        # Hiển thị các thông tin chi tiết
        tk.Label(self.main_content, text=f"Tên: {student[0]}", font=("Arial", 12), bg="white").pack(pady=5)
        tk.Label(self.main_content, text=f"Ngày sinh: {student[1]}", font=("Arial", 12), bg="white").pack(pady=5)
        tk.Label(self.main_content, text=f"Giới tính: {gioi_tinh}", font=("Arial", 12), bg="white").pack(pady=5)
        tk.Label(self.main_content, text=f"Lớp: {student[3]}", font=("Arial", 12), bg="white").pack(pady=5)

    def show_schedule(self):
        # Xóa nội dung cũ
        for widget in self.main_content.winfo_children():
            widget.destroy()
        # Thay vì hiển thị label tĩnh, ta gọi module LichHoc
        LichHoc(self.main_content, self.db, self.user_info_auth)

    def show_grades(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        header_label = tk.Label(self.main_content, text="📊 Xem điểm", font=("Arial", 20, "bold"),
                                bg="white", fg="#007acc")
        header_label.pack(pady=10)
        tk.Label(self.main_content, text="(Bảng điểm của bạn)", font=("Arial", 14),
                 bg="white", fg="#333").pack(pady=10)

    def logout(self):
        self.destroy()
        from dang_nhap import LoginWindow
        LoginWindow().mainloop()

    def open_settings(self):
        color = colorchooser.askcolor(title="Chọn màu nền ứng dụng")
        if color[1]:
            self.configure(bg=color[1])
            self.sidebar.configure(bg=color[1])
            self.main_content.configure(bg=color[1])

    def show_info(self):
        messagebox.showinfo("Thông tin ứng dụng",
                            "Ứng dụng Quản lý Sinh viên - Phiên bản 1.0\nLiên hệ: support@taydo.edu.vn")

    def on_exit(self):
        if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát không?"):
            self.destroy()


if __name__ == "__main__":
    from dang_nhap import LoginWindow
    LoginWindow().mainloop()
