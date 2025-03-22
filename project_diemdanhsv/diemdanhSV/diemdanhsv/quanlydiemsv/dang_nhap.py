import tkinter as tk
from tkinter import messagebox, PhotoImage, ttk
import mysql.connector

class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập hệ thống")
        self.geometry("400x500")  # Kích thước cửa sổ
        self.center_window()  # Căn giữa màn hình
        self.configure(bg="#f0f2f5")
        self.resizable(False, False)

        # Frame chứa nội dung đăng nhập
        self.frame = tk.Frame(self, bg="white", bd=2, relief="flat")
        self.frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=450)

        # Logo
        self.original_logo = PhotoImage(file="logo.png")
        self.logo = self.original_logo.subsample(6, 6)
        logo_label = tk.Label(self.frame, image=self.logo, bg="white")
        logo_label.pack(pady=10)

        # Tiêu đề đăng nhập
        tk.Label(self.frame, text="ĐĂNG NHẬP", font=("Arial", 20, "bold"), bg="white", fg="#007acc").pack(pady=10)
       
        # Ô nhập tên đăng nhập
        tk.Label(self.frame, text="Tên đăng nhập:", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.username_entry = tk.Entry(self.frame, font=("Arial", 12), relief="solid", bd=1)
        self.username_entry.pack(padx=20, pady=5, fill="x", ipady=5)

        # Ô nhập mật khẩu với nút hiển thị mật khẩu
        tk.Label(self.frame, text="Mật khẩu:", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.password_frame = tk.Frame(self.frame, bg="white", relief="solid", bd=1, highlightbackground="#ccc", highlightthickness=1)
        self.password_frame.pack(padx=20, pady=5, fill="x")
        self.password_entry = tk.Entry(self.password_frame, show="*", font=("Arial", 12), relief="flat", bd=0)
        self.password_entry.pack(side="left", expand=True, fill="x", ipady=5, padx=(5, 0))
        self.show_password_var = tk.BooleanVar()
        self.show_password_button = tk.Button(
            self.password_frame, text="👁", font=("Arial", 12, "bold"), bg="white", bd=0, 
            command=self.toggle_password, padx=5, pady=2, width=3, height=1, relief="flat"
        )
        self.show_password_button.pack(side="right", padx=5)

        # Chọn quyền đăng nhập (Sinh viên / Giảng viên)
        tk.Label(self.frame, text="Chọn quyền:", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.role_var = tk.StringVar()
        self.role_dropdown = ttk.Combobox(self.frame, textvariable=self.role_var, values=["Sinh viên", "Giảng viên"], font=("Arial", 12), state="readonly")
        self.role_dropdown.pack(padx=20, pady=5, fill="x", ipady=5)
        self.role_dropdown.current(0)

        # Nút đăng nhập
        self.login_btn = tk.Button(self.frame, text="Đăng nhập", bg="#007acc", fg="white", font=("Arial", 14, "bold"), relief="flat", bd=2, command=self.login)
        self.login_btn.pack(pady=20, ipadx=10, ipady=5, fill="x", padx=20)

        # Gán sự kiện nhấn phím Enter
        self.bind_enter_key()

    def bind_enter_key(self):
        """Gán sự kiện Enter để chuyển focus hoặc đăng nhập."""
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda event: self.login())

    def toggle_password(self):
        """Bật/tắt hiển thị mật khẩu."""
        if self.show_password_var.get():
            self.password_entry.config(show="*")
            self.show_password_var.set(False)
        else:
            self.password_entry.config(show="")
            self.show_password_var.set(True)

    def connect_database(self):
        """Kết nối đến cơ sở dữ liệu MySQL."""
        try:
            return mysql.connector.connect(host="localhost", user="root", password="", database="diemdanhsv")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối tới cơ sở dữ liệu: {err}")
            return None

    def login(self):
        """Xử lý đăng nhập và chuyển hướng đến giao diện phù hợp dựa theo vai trò."""
        username = self.username_entry.get().strip().lower()
        password = self.password_entry.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        db = self.connect_database()
        if db:
            cursor = db.cursor()

            # Chọn bảng và câu lệnh SQL dựa trên quyền đăng nhập
            if role == "Giảng viên":
                query = "SELECT ID_TKGV, USERNAME, QUYENHAN, ID_GIAOVIEN FROM taikhoangv WHERE USERNAME=%s AND PASSWORD=%s"
            else:
                query = "SELECT ID_TKSV, USERNAME, ID_SINHVIEN FROM taikhoansv WHERE USERNAME=%s AND PASSWORD=%s"

            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                # Xác định vai trò và giá trị ID, tên người dùng từ kết quả truy vấn
                if role == "Giảng viên":
                    acc_id = result[0]
                    user_role = "teacher"
                    user_id = result[3]  # ID_TKGV
                    user_name_value = result[1]

                else:
                    acc_id = result[0]
                    user_role = "student"
                    user_id = result[2]  # ID_TKSV
                    user_name_value = result[1]

                messagebox.showinfo("Thành công", f"Chào mừng {user_name_value}!")
                self.destroy()
                # Chuyển hướng đến giao diện chính phù hợp
                from main import QuanLySinhVienApp
                # Giao diện chính (dashboard) sẽ hiển thị các chức năng khác nhau tùy vào user_role.
                QuanLySinhVienApp([user_name_value, user_role, user_id, acc_id], ).mainloop()
            else:
                messagebox.showerror("Lỗi đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")

            db.close()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width() or 400
        height = self.winfo_height() or 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    LoginWindow().mainloop()
