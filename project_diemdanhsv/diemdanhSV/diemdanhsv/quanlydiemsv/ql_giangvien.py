import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class QuanLyGiangVien:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.create_ui()

    def create_ui(self):
        # Tiêu đề cửa sổ
        title = tk.Label(self.parent, text="Quản Lý Giảng Viên", 
                         font=("Arial", 16, "bold"), fg="white", bg="blue")
        title.pack(pady=10, fill=tk.X)

        # --- Form Thêm Giảng Viên (nằm ngang) ---
        add_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        add_frame.pack(pady=10, fill=tk.X)

        tk.Label(add_frame, text="Tên Giảng Viên:", bg="lightgray").grid(row=0, column=0, padx=5, pady=5)
        self.entry_tengv = tk.Entry(add_frame)
        self.entry_tengv.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Chọn Khoa:", bg="lightgray").grid(row=0, column=2, padx=5, pady=5)
        self.combo_khoa = ttk.Combobox(add_frame, state="readonly")
        self.combo_khoa.grid(row=0, column=3, padx=5, pady=5)
        self.load_khoa()

        add_btn = tk.Button(add_frame, text="Thêm", command=self.add_gv, 
                            bg="blue", fg="white", font=("Arial", 10, "bold"))
        add_btn.grid(row=0, column=4, padx=5, pady=5)

        # --- Treeview hiển thị danh sách Giảng Viên ---
        tree_frame = tk.Frame(self.parent)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        columns = ("ID", "Tên Giảng Viên", "Tên Khoa")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Khi chọn 1 dòng, mở popup Sửa/Xóa
        self.tree.bind("<<TreeviewSelect>>", self.open_edit_popup)

        self.load_data()

    def load_khoa(self):
        """Load danh sách khoa từ bảng 'khoa' vào combobox và lưu vào từ điển."""
        self.cursor.execute("SELECT ID_KHOA, TENKHOA FROM khoa")
        rows = self.cursor.fetchall()
        self.khoa_dict = {row[1]: row[0] for row in rows}  # {Tên Khoa: ID_KHOA}
        self.combo_khoa["values"] = list(self.khoa_dict.keys())

    def load_data(self):
        """Load dữ liệu giảng viên lên Treeview."""
        self.tree.delete(*self.tree.get_children())
        query = """
            SELECT giaovien.ID_GIAOVIEN, giaovien.TENGIAOVIEN, khoa.TENKHOA 
            FROM giaovien 
            INNER JOIN khoa ON giaovien.ID_KHOA = khoa.ID_KHOA
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def add_gv(self):
        """Thêm giảng viên mới vào CSDL."""
        tengv = self.entry_tengv.get().strip()
        selected_khoa = self.combo_khoa.get().strip()

        if not tengv or not selected_khoa:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        khoa_id = self.khoa_dict.get(selected_khoa)
        if khoa_id is None:
            messagebox.showerror("Lỗi", "Khoa không hợp lệ!")
            return

        try:
            query = "INSERT INTO giaovien (TENGIAOVIEN, ID_KHOA) VALUES (%s, %s)"
            self.cursor.execute(query, (tengv, khoa_id))
            self.db.commit()
            messagebox.showinfo("Thành công", "Thêm giảng viên thành công!")
            # Xóa nội dung form thêm
            self.entry_tengv.delete(0, tk.END)
            self.combo_khoa.set("")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm giảng viên: {e}")
            self.db.rollback()

        self.load_data()

    def open_edit_popup(self, event):
        """Mở cửa sổ popup chứa form Sửa/Xóa khi người dùng chọn một dòng trong Treeview."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0], "values")
        gv_id = item[0]
        current_tengv = item[1]
        current_khoa = item[2]

        popup = tk.Toplevel(self.parent)
        popup.title("Sửa / Xóa Giảng Viên")
        popup.grab_set()
        popup.resizable(False, False)

        tk.Label(popup, text="Tên Giảng Viên:").grid(row=0, column=0, padx=10, pady=10)
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        name_entry.insert(0, current_tengv)

        tk.Label(popup, text="Chọn Khoa:").grid(row=1, column=0, padx=10, pady=10)
        khoa_combo = ttk.Combobox(popup, state="readonly")
        khoa_combo.grid(row=1, column=1, padx=10, pady=10)
        khoa_combo["values"] = list(self.khoa_dict.keys())
        khoa_combo.set(current_khoa)

        btn_frame = tk.Frame(popup)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        def update_gv():
            new_name = name_entry.get().strip()
            new_khoa = khoa_combo.get().strip()
            if not new_name or not new_khoa:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return
            new_khoa_id = self.khoa_dict.get(new_khoa)
            if new_khoa_id is None:
                messagebox.showerror("Lỗi", "Khoa không hợp lệ!")
                return
            try:
                query = "UPDATE giaovien SET TENGIAOVIEN = %s, ID_KHOA = %s WHERE ID_GIAOVIEN = %s"
                self.cursor.execute(query, (new_name, new_khoa_id, gv_id))
                self.db.commit()
                messagebox.showinfo("Thành công", "Cập nhật giảng viên thành công!")
                self.load_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật giảng viên: {e}")
                self.db.rollback()

        def delete_gv():
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giảng viên này?")
            if not confirm:
                return
            try:
                query = "DELETE FROM giaovien WHERE ID_GIAOVIEN = %s"
                self.cursor.execute(query, (gv_id,))
                self.db.commit()
                messagebox.showinfo("Thành công", "Xóa giảng viên thành công!")
                self.load_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa giảng viên: {e}")
                self.db.rollback()

        # Nút Sửa (màu vàng) và Nút Xóa (màu đỏ)
        update_btn = tk.Button(btn_frame, text="Sửa", command=update_gv, 
                               bg="yellow", fg="black", font=("Arial", 10, "bold"))
        update_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = tk.Button(btn_frame, text="Xóa", command=delete_gv, 
                               bg="red", fg="white", font=("Arial", 10, "bold"))
        delete_btn.pack(side=tk.LEFT, padx=5)

