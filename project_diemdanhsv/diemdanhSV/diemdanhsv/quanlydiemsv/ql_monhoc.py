import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class QuanLyMonHoc:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.create_ui()

    def create_ui(self):
        # Tiêu đề
        title = tk.Label(self.parent, text="Quản Lý Môn Học", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # --- Form Thêm Môn Học (nằm ngang) ---
        add_frame = tk.Frame(self.parent)
        add_frame.pack(pady=10, fill=tk.X)

        # Tên môn học
        tk.Label(add_frame, text="Tên môn học:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_name = tk.Entry(add_frame)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        # Số tín chỉ
        tk.Label(add_frame, text="Số tín chỉ:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_tinchi = tk.Entry(add_frame, width=5)
        self.entry_tinchi.grid(row=0, column=3, padx=5, pady=5)

        # Lớp học
        tk.Label(add_frame, text="Lớp học:").grid(row=0, column=4, padx=5, pady=5)
        self.combo_lop = ttk.Combobox(add_frame, state="readonly")
        self.combo_lop.grid(row=0, column=5, padx=5, pady=5)
        self.load_lop_hoc()

        # Giáo viên
        tk.Label(add_frame, text="Giáo viên:").grid(row=0, column=6, padx=5, pady=5)
        self.combo_giaovien = ttk.Combobox(add_frame, state="readonly")
        self.combo_giaovien.grid(row=0, column=7, padx=5, pady=5)
        self.load_giao_vien()

        # Nút Thêm (màu xanh)
        add_btn = tk.Button(add_frame, text="Thêm", command=self.add_monhoc, bg="blue", fg="white", font=("Arial", 10, "bold"))
        add_btn.grid(row=0, column=8, padx=5, pady=5)

        # --- Bảng danh sách Môn Học (Treeview) ---
        tree_frame = tk.Frame(self.parent)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        columns = ("ID", "Tên môn", "Số tín chỉ", "Lớp học", "Giáo viên")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Khi click vào dòng, mở popup Sửa/Xóa
        self.tree.bind("<ButtonRelease-1>", self.open_edit_popup)

        self.load_data()

    def load_data(self):
        """Load dữ liệu môn học (các bảng MONHOC, LOPHOC_MONHOC, LOPHOC, GIAOVIEN) lên Treeview"""
        self.tree.delete(*self.tree.get_children())
        query = """
        SELECT M.ID_MON, M.TENMON, M.SOTINCHI, L.TENLOP, G.TENGIAOVIEN
        FROM MONHOC M
        LEFT JOIN LOPHOC_MONHOC LM ON M.ID_MON = LM.ID_MON
        LEFT JOIN LOPHOC L ON LM.ID_LOP = L.ID_LOP
        LEFT JOIN GIAOVIEN G ON M.ID_GIAOVIEN = G.ID_GIAOVIEN
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def load_lop_hoc(self):
        """Load danh sách lớp học vào Combobox và lưu vào từ điển"""
        self.cursor.execute("SELECT ID_LOP, TENLOP FROM LOPHOC")
        rows = self.cursor.fetchall()
        self.lop_dict = {lop[1]: lop[0] for lop in rows}
        self.combo_lop["values"] = list(self.lop_dict.keys())

    def load_giao_vien(self):
        """Load danh sách giáo viên vào Combobox và lưu vào từ điển"""
        self.cursor.execute("SELECT ID_GIAOVIEN, TENGIAOVIEN FROM GIAOVIEN")
        rows = self.cursor.fetchall()
        self.giaovien_dict = {gv[1]: gv[0] for gv in rows}
        self.combo_giaovien["values"] = list(self.giaovien_dict.keys())

    def add_monhoc(self):
        name = self.entry_name.get().strip()
        tinchi = self.entry_tinchi.get().strip()
        lop_selected = self.combo_lop.get().strip()
        giaovien_selected = self.combo_giaovien.get().strip()

        if not name or not tinchi or not lop_selected or not giaovien_selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")
            return

        try:
            lop_id = self.lop_dict[lop_selected]
            giaovien_id = self.giaovien_dict[giaovien_selected]

            # Thêm môn học vào bảng MONHOC
            self.cursor.execute(
                "INSERT INTO MONHOC (TENMON, SOTINCHI, ID_GIAOVIEN) VALUES (%s, %s, %s)",
                (name, tinchi, giaovien_id)
            )
            monhoc_id = self.cursor.lastrowid

            # Thêm dữ liệu vào bảng trung gian LOPHOC_MONHOC
            self.cursor.execute(
                "INSERT INTO LOPHOC_MONHOC (ID_LOP, ID_MON) VALUES (%s, %s)",
                (lop_id, monhoc_id)
            )

            self.db.commit()
            messagebox.showinfo("Thông báo", "Thêm môn học thành công!")
            self.load_data()
            # Xóa nội dung form thêm
            self.entry_name.delete(0, tk.END)
            self.entry_tinchi.delete(0, tk.END)
            self.combo_lop.set("")
            self.combo_giaovien.set("")
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm môn học: {err}")
            self.db.rollback()

    def open_edit_popup(self, event):
        """Mở popup chứa form Sửa/Xóa khi người dùng chọn một dòng trong Treeview."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0], "values")
        monhoc_id = item[0]
        current_name = item[1]
        current_tinchi = item[2]
        current_lop = item[3]
        current_giaovien = item[4]

        popup = tk.Toplevel(self.parent)
        popup.title("Sửa / Xóa Môn Học")
        popup.grab_set()
        popup.resizable(False, False)

        # Form Sửa/Xóa trong popup
        tk.Label(popup, text="Tên môn học:").grid(row=0, column=0, padx=5, pady=5)
        name_entry = tk.Entry(popup)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, current_name)

        tk.Label(popup, text="Số tín chỉ:").grid(row=1, column=0, padx=5, pady=5)
        tinchi_entry = tk.Entry(popup, width=5)
        tinchi_entry.grid(row=1, column=1, padx=5, pady=5)
        tinchi_entry.insert(0, current_tinchi)

        tk.Label(popup, text="Lớp học:").grid(row=2, column=0, padx=5, pady=5)
        lop_combo = ttk.Combobox(popup, state="readonly")
        lop_combo.grid(row=2, column=1, padx=5, pady=5)
        lop_combo["values"] = list(self.lop_dict.keys())
        lop_combo.set(current_lop)

        tk.Label(popup, text="Giáo viên:").grid(row=3, column=0, padx=5, pady=5)
        gv_combo = ttk.Combobox(popup, state="readonly")
        gv_combo.grid(row=3, column=1, padx=5, pady=5)
        gv_combo["values"] = list(self.giaovien_dict.keys())
        gv_combo.set(current_giaovien)

        # Frame chứa các nút Sửa và Xóa
        btn_frame = tk.Frame(popup)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

        def update_monhoc():
            new_name = name_entry.get().strip()
            new_tinchi = tinchi_entry.get().strip()
            new_lop = lop_combo.get().strip()
            new_gv = gv_combo.get().strip()

            if not new_name or not new_tinchi or not new_lop or not new_gv:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")
                return

            try:
                new_lop_id = self.lop_dict[new_lop]
                new_gv_id = self.giaovien_dict[new_gv]

                # Cập nhật bảng MONHOC
                self.cursor.execute(
                    "UPDATE MONHOC SET TENMON = %s, SOTINCHI = %s, ID_GIAOVIEN = %s WHERE ID_MON = %s",
                    (new_name, new_tinchi, new_gv_id, monhoc_id)
                )
                # Cập nhật bảng trung gian LOPHOC_MONHOC
                self.cursor.execute(
                    "UPDATE LOPHOC_MONHOC SET ID_LOP = %s WHERE ID_MON = %s",
                    (new_lop_id, monhoc_id)
                )

                self.db.commit()
                messagebox.showinfo("Thông báo", "Cập nhật môn học thành công!")
                self.load_data()
                popup.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {err}")
                self.db.rollback()

        def delete_monhoc():
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa môn học này?")
            if not confirm:
                return
            try:
                # Xóa dữ liệu khỏi bảng trung gian trước
                self.cursor.execute("DELETE FROM LOPHOC_MONHOC WHERE ID_MON = %s", (monhoc_id,))
                # Sau đó xóa khỏi bảng MONHOC
                self.cursor.execute("DELETE FROM MONHOC WHERE ID_MON = %s", (monhoc_id,))
                self.db.commit()
                messagebox.showinfo("Thông báo", "Xóa môn học thành công!")
                self.load_data()
                popup.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa môn học: {err}")
                self.db.rollback()

        # Nút Sửa (màu vàng)
        edit_btn = tk.Button(btn_frame, text="Sửa", command=update_monhoc, bg="yellow", fg="black", font=("Arial", 10, "bold"))
        edit_btn.pack(side=tk.LEFT, padx=5)
        # Nút Xóa (màu đỏ)
        delete_btn = tk.Button(btn_frame, text="Xóa", command=delete_monhoc, bg="red", fg="white", font=("Arial", 10, "bold"))
        delete_btn.pack(side=tk.LEFT, padx=5)

