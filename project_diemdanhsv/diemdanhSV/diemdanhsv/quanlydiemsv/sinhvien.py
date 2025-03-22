import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import mysql.connector
import csv
import openpyxl
from io import BytesIO
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from datetime import datetime

class QuanLySinhVien:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.selected_student_id = None  # Lưu ID sinh viên được chọn

        # Cấu hình style cho giao diện hiện đại
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#F0F0F0")
        self.style.configure("TLabel", background="#F0F0F0", font=("Helvetica", 11))
        self.style.configure("TButton", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 10))
        
        self.create_ui()

    def create_ui(self):
        # Khung chính
        container = ttk.Frame(self.parent, padding=(10, 10, 10, 10))
        container.pack(fill=tk.BOTH, expand=True)

        # Tiêu đề ứng dụng
        title = ttk.Label(container, text="Quản Lý Sinh Viên", anchor="center",
                          background="#1976D2", foreground="white", font=("Helvetica", 16, "bold"))
        title.pack(fill=tk.X, pady=(0, 10))

        # --- Form Thêm Sinh Viên Mới (nằm ngang) ---
        add_frame = ttk.LabelFrame(container, text="Thêm Sinh Viên Mới", padding=10)
        add_frame.pack(fill=tk.X, pady=5)

        # Sắp xếp theo hàng ngang:
        ttk.Label(add_frame, text="Họ Tên:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.add_name_entry = ttk.Entry(add_frame, width=20)
        self.add_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Ngày Sinh:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.add_dob_entry = DateEntry(add_frame, width=15, background="#1976D2",
                                       foreground="white", date_pattern="dd-MM-yyyy")
        self.add_dob_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Giới Tính:").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.add_gender_combobox = ttk.Combobox(add_frame, values=["Nam", "Nữ", "Khác"], width=10)
        self.add_gender_combobox.grid(row=0, column=5, padx=5, pady=5)
        self.add_gender_combobox.current(0)

        ttk.Label(add_frame, text="Lớp Học:").grid(row=0, column=6, sticky=tk.W, padx=5, pady=5)
        self.add_class_combobox = ttk.Combobox(add_frame, width=15)
        self.add_class_combobox.grid(row=0, column=7, padx=5, pady=5)
        self.load_classes_into(self.add_class_combobox)

        # Nút Thêm nằm ngang (màu xanh)
        add_btn = tk.Button(add_frame, text="Thêm", command=self.add_student,
                            bg="blue", fg="white", font=("Helvetica", 10, "bold"))
        add_btn.grid(row=0, column=8, padx=5, pady=5)

        # --- Các chức năng: Tìm kiếm, Lọc, Xuất Excel, Thống kê ---
        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(filter_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        # Nút Tìm kiếm với màu nền lightblue
        search_btn = tk.Button(filter_frame, text="🔍", command=self.search_student,
                               bg="lightblue", fg="black", font=("Helvetica", 10, "bold"))
        search_btn.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Lọc theo giới tính:").pack(side=tk.LEFT, padx=5)
        self.filter_gender = ttk.Combobox(filter_frame, values=["Tất cả", "Nam", "Nữ", "Khác"], width=10)
        self.filter_gender.current(0)
        self.filter_gender.pack(side=tk.LEFT, padx=5)
        # Nút Lọc với màu nền orange
        filter_btn = tk.Button(filter_frame, text="Lọc", command=self.filter_students,
                               bg="orange", fg="white", font=("Helvetica", 10, "bold"))
        filter_btn.pack(side=tk.LEFT, padx=5)

        # Nút Xuất Excel với màu nền purple và Thống kê với màu nền green, nằm bên phải
        export_btn = tk.Button(filter_frame, text="Xuất Excel", command=self.export_to_excel,
                               bg="purple", fg="white", font=("Helvetica", 10, "bold"))
        export_btn.pack(side=tk.RIGHT, padx=5)
        stats_btn = tk.Button(filter_frame, text="Thống kê", command=self.show_statistics,
                              bg="green", fg="white", font=("Helvetica", 10, "bold"))
        stats_btn.pack(side=tk.RIGHT, padx=5)

        # --- Treeview hiển thị danh sách sinh viên ---
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        columns = ("ID", "Họ Tên", "Ngày Sinh", "Giới Tính", "Lớp Học")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=150)

        # Scrollbar cho Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_data()
        self.tree.bind("<ButtonRelease-1>", self.select_student)

    def load_classes_into(self, combobox):
        """Lấy danh sách lớp học từ CSDL và cập nhật vào combobox."""
        query = "SELECT TENLOP FROM lophoc"
        self.cursor.execute(query)
        classes = [row[0] for row in self.cursor.fetchall()]
        combobox['values'] = classes

    def get_class_name(self, class_id):
        query = "SELECT TENLOP FROM lophoc WHERE ID_LOP=%s"
        self.cursor.execute(query, (class_id,))
        result = self.cursor.fetchone()
        if result is None:
            return "Không xác định"
        return result[0]

    def get_class_id(self, class_name):
        query = "SELECT ID_LOP FROM lophoc WHERE TENLOP=%s"
        self.cursor.execute(query, (class_name,))
        result = self.cursor.fetchone()
        if result is None:
            messagebox.showerror("Lỗi", f"Lớp học '{class_name}' không tồn tại!")
            return None
        return result[0]

    def select_student(self, event):
        """Khi click vào một dòng trong Treeview, hiển thị popup với thông tin chi tiết sinh viên."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = self.tree.item(selected_item, "values")
        self.selected_student_id = item[0]

        popup = tk.Toplevel(self.parent)
        popup.title("Thông Tin Sinh Viên")
        popup.geometry("350x250")
        popup.grab_set()

        ttk.Label(popup, text="Họ Tên:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, item[1])

        ttk.Label(popup, text="Ngày Sinh:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        dob_entry = DateEntry(popup, width=18, background="#1976D2", foreground="white", date_pattern="dd-MM-yyyy")
        dob_entry.grid(row=1, column=1, padx=10, pady=5)
        try:
            dob_entry.set_date(item[2])
        except Exception:
            pass

        ttk.Label(popup, text="Giới Tính:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        gender_combobox = ttk.Combobox(popup, values=["Nam", "Nữ", "Khác"], width=18)
        gender_combobox.grid(row=2, column=1, padx=10, pady=5)
        gender_combobox.set(item[3])

        ttk.Label(popup, text="Lớp Học:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        class_combobox = ttk.Combobox(popup, width=18)
        class_combobox.grid(row=3, column=1, padx=10, pady=5)
        self.load_classes_into(class_combobox)
        class_combobox.set(item[4])

        btn_frame = ttk.Frame(popup)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def update_student():
            name = name_entry.get()
            dob = dob_entry.get_date().strftime("%Y-%m-%d")
            gender_text = gender_combobox.get()
            if gender_text == "Nam":
                gender_value = 1
            elif gender_text == "Nữ":
                gender_value = 0
            elif gender_text == "Khác":
                gender_value = 2
            else:
                gender_value = None
            class_name = class_combobox.get()
            class_id = self.get_class_id(class_name)
            if class_id is None:
                return
            query = "UPDATE sinhvien SET TENSINHVIEN=%s, NGAYSINH=%s, GIOITINH=%s, ID_LOP=%s WHERE ID_SINHVIEN=%s"
            self.cursor.execute(query, (name, dob, gender_value, class_id, self.selected_student_id))
            self.db.commit()
            messagebox.showinfo("Thành công", "Sửa thông tin sinh viên thành công!")
            self.load_data()
            popup.destroy()

        def delete_student():
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sinh viên này?")
            if confirm:
                try:
                    query = "DELETE FROM sinhvien WHERE ID_SINHVIEN=%s"
                    self.cursor.execute(query, (self.selected_student_id,))
                    self.db.commit()
                    messagebox.showinfo("Thành công", "Xóa sinh viên thành công!")
                    self.load_data()
                    popup.destroy()
                except mysql.connector.IntegrityError:
                    messagebox.showerror("Lỗi", "Không thể xóa sinh viên này do có dữ liệu liên quan!")
                    self.db.rollback()

        update_btn = tk.Button(btn_frame, text="Sửa", command=update_student,
                               bg="yellow", fg="black", font=("Helvetica", 10, "bold"))
        update_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = tk.Button(btn_frame, text="Xóa", command=delete_student,
                               bg="red", fg="white", font=("Helvetica", 10, "bold"))
        delete_btn.pack(side=tk.LEFT, padx=5)

    def add_student(self):
        name = self.add_name_entry.get()
        dob = self.add_dob_entry.get_date().strftime("%Y-%m-%d")
        gender_text = self.add_gender_combobox.get()
        if gender_text == "Nam":
            gender_value = 1
        elif gender_text == "Nữ":
            gender_value = 0
        elif gender_text == "Khác":
            gender_value = 2
        else:
            gender_value = None
        class_name = self.add_class_combobox.get()
        class_id = self.get_class_id(class_name)
        if class_id is None:
            return
        query = "INSERT INTO sinhvien (TENSINHVIEN, NGAYSINH, GIOITINH, ID_LOP) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (name, dob, gender_value, class_id))
        self.db.commit()
        messagebox.showinfo("Thành công", "Thêm sinh viên thành công!")
        self.load_data()

        # Reset lại form thêm mới
        self.add_name_entry.delete(0, tk.END)
        self.add_dob_entry.set_date(datetime.today())
        self.add_gender_combobox.current(0)
        self.add_class_combobox.set("")

    def load_data(self, condition=""):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT ID_SINHVIEN, TENSINHVIEN, NGAYSINH, GIOITINH, ID_LOP FROM sinhvien" + condition
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            row = list(row)
            row[2] = row[2].strftime("%d-%m-%Y") if row[2] else ""
            gender_value = row[3]
            if gender_value == 1:
                row[3] = "Nam"
            elif gender_value == 0:
                row[3] = "Nữ"
            elif gender_value == 2:
                row[3] = "Khác"
            else:
                row[3] = "Không xác định"
            row[4] = self.get_class_name(row[4]) if row[4] else ""
            self.tree.insert("", "end", values=row)

    def search_student(self):
        keyword = self.search_entry.get()
        condition = f" WHERE TENSINHVIEN LIKE '%{keyword}%'"
        self.load_data(condition)

    def filter_students(self):
        gender = self.filter_gender.get()
        if gender == "Tất cả":
            self.load_data()
        else:
            if gender == "Nam":
                gender_value = 1
            elif gender == "Nữ":
                gender_value = 0
            elif gender == "Khác":
                gender_value = 2
            else:
                gender_value = None
            condition = f" WHERE GIOITINH = {gender_value}" if gender_value is not None else ""
            self.load_data(condition)

    def export_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["ID", "Họ Tên", "Ngày Sinh", "Giới Tính", "Lớp Học"])
        for row_id in self.tree.get_children():
            sheet.append(self.tree.item(row_id)['values'])
        workbook.save(file_path)
        messagebox.showinfo("Thành công", "Xuất file Excel thành công!")

    def show_statistics(self):
        self.cursor.execute("SELECT GIOITINH, COUNT(*) FROM sinhvien GROUP BY GIOITINH")
        data = self.cursor.fetchall()
        labels = []
        sizes = []
        for gender_value, count in data:
            if gender_value == 1:
                labels.append("Nam")
            elif gender_value == 0:
                labels.append("Nữ")
            elif gender_value == 2:
                labels.append("Khác")
            else:
                labels.append("Không xác định")
            sizes.append(count)
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#1976D2', '#E91E63', '#9E9E9E'])
        ax.set_title("Thống kê giới tính sinh viên")
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        img = Image.open(buffer)
        img = ImageTk.PhotoImage(img)
        popup = tk.Toplevel(self.parent)
        popup.title("Thống kê")
        ttk.Label(popup, image=img).pack(padx=10, pady=10)
        # Giữ tham chiếu ảnh để không bị thu gom rác
        popup.image = img
        popup.mainloop()
