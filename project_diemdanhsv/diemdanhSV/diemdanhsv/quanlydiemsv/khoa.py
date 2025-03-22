import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class QuanLyKhoa:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.create_ui()

    def create_ui(self):
        # Tiêu đề ứng dụng
        tk.Label(
            self.parent,
            text="Quản Lý Khoa",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="blue"
        ).pack(pady=10, fill=tk.X)

        # --- Form Thêm Khoa (các thành phần nằm ngang) ---
        add_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        add_frame.pack(pady=10, fill=tk.X)

        tk.Label(add_frame, text="Tên Khoa:", bg="lightgray").grid(row=0, column=0, padx=5, pady=5)
        self.department_name_entry = tk.Entry(add_frame)
        self.department_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Nút Thêm (màu xanh) nằm ngay cạnh ô nhập
        add_btn = tk.Button(add_frame, text="Thêm", bg="green", fg="white",
                            font=("Arial", 10, "bold"), command=self.add_department)
        add_btn.grid(row=0, column=2, padx=5, pady=5)

        # --- Treeview hiển thị danh sách khoa ---
        tree_frame = tk.Frame(self.parent)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        columns = ("ID", "Tên Khoa")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Khi chọn 1 dòng, mở popup Sửa/Xóa
        self.tree.bind("<ButtonRelease-1>", self.open_edit_popup)

        self.load_data()

    def add_department(self):
        department_name = self.department_name_entry.get().strip()
        if not department_name:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên khoa!")
            return

        query = "INSERT INTO khoa (TENKHOA) VALUES (%s)"
        try:
            self.cursor.execute(query, (department_name,))
            self.db.commit()
            messagebox.showinfo("Thành công", "Thêm khoa thành công!")
            self.load_data()
            self.department_name_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm khoa: {e}")
            self.db.rollback()

    def open_edit_popup(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # Lấy dữ liệu từ dòng được chọn (ID và Tên Khoa)
        item = self.tree.item(selected_item[0], "values")
        department_id = item[0]
        current_name = item[1]

        popup = tk.Toplevel(self.parent)
        popup.title("Sửa / Xóa Khoa")
        popup.grab_set()
        popup.resizable(False, False)

        # Form chỉnh sửa trong popup
        tk.Label(popup, text="Tên Khoa:").grid(row=0, column=0, padx=10, pady=10)
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.insert(0, current_name)

        # Hàm cập nhật khoa
        def update_department():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showwarning("Lỗi", "Vui lòng nhập tên khoa!")
                return

            query = "UPDATE khoa SET TENKHOA=%s WHERE ID_KHOA=%s"
            try:
                self.cursor.execute(query, (new_name, department_id))
                self.db.commit()
                messagebox.showinfo("Thành công", "Cập nhật khoa thành công!")
                self.load_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật khoa: {e}")
                self.db.rollback()

        # Hàm xóa khoa
        def delete_department():
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa khoa này?")
            if confirm:
                query = "DELETE FROM khoa WHERE ID_KHOA=%s"
                try:
                    self.cursor.execute(query, (department_id,))
                    self.db.commit()
                    messagebox.showinfo("Thành công", "Xóa khoa thành công!")
                    self.load_data()
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể xóa khoa: {e}")
                    self.db.rollback()

        # Nút Sửa (màu vàng) và Nút Xóa (màu đỏ)
        update_btn = tk.Button(popup, text="Sửa", bg="yellow", fg="black",
                               font=("Arial", 10, "bold"), command=update_department)
        update_btn.grid(row=1, column=0, padx=10, pady=10)

        delete_btn = tk.Button(popup, text="Xóa", bg="red", fg="white",
                               font=("Arial", 10, "bold"), command=delete_department)
        delete_btn.grid(row=1, column=1, padx=10, pady=10)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        query = "SELECT ID_KHOA, TENKHOA FROM khoa"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

