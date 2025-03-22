import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

class QuanLyLopHoc:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.department_dict = {}
        self.setup_style()
        self.create_ui()

    def setup_style(self):
        # Cấu hình giao diện hiện đại với ttk.Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#F0F0F0")
        self.style.configure("TLabel", background="#F0F0F0", font=("Helvetica", 11))
        self.style.configure("TButton", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 10))

    def create_ui(self):
        # Khung chính
        container = ttk.Frame(self.parent, padding=10)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề ứng dụng
        title = ttk.Label(
            container,
            text="Quản Lý Lớp Học",
            anchor="center",
            background="#1976D2",
            foreground="white",
            font=("Helvetica", 16, "bold")
        )
        title.pack(fill=tk.X, pady=(0, 10))
        
        # --- Form Thêm Lớp Học (luôn hiển thị) ---
        add_frame = ttk.LabelFrame(container, text="Thêm Lớp Học", padding=10)
        add_frame.pack(fill=tk.X, pady=5)
        
        # Hiển thị thông tin theo hàng ngang: Tên Lớp, Khoa và Nút Thêm
        ttk.Label(add_frame, text="Tên Lớp:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_name_entry = ttk.Entry(add_frame)
        self.class_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Khoa:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.department_combobox = ttk.Combobox(add_frame, state="readonly", width=18)
        self.department_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.load_departments()
        
        # Nút Thêm (màu xanh)
        add_btn = tk.Button(add_frame, text="Thêm", bg="blue", fg="white",
                            font=("Helvetica", 10, "bold"), command=self.add_class)
        add_btn.grid(row=0, column=4, padx=5, pady=5)
        
        # --- Treeview hiển thị danh sách lớp học ---
        tree_frame = ttk.Frame(container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        columns = ("ID", "Tên Lớp", "Khoa")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=tk.CENTER, width=150)
        
        # Scrollbar cho Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Gán sự kiện chọn dòng để mở popup Sửa/Xóa
        self.tree.bind("<<TreeviewSelect>>", self.open_edit_popup)
        
        self.load_data()

    def load_departments(self):
        """Nạp danh sách khoa vào Combobox"""
        self.cursor.execute("SELECT ID_KHOA, TENKHOA FROM khoa")
        rows = self.cursor.fetchall()
        self.department_dict = {row[1]: row[0] for row in rows}  # {TENKHOA: ID_KHOA}
        self.department_combobox["values"] = list(self.department_dict.keys())

    def add_class(self):
        class_name = self.class_name_entry.get().strip()
        department = self.department_combobox.get()
        department_id = self.department_dict.get(department)
        
        if not class_name or not department_id:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        query = "INSERT INTO lophoc (TENLOP, ID_KHOA) VALUES (%s, %s)"
        try:
            self.cursor.execute(query, (class_name, department_id))
            self.db.commit()
            messagebox.showinfo("Thành công", "Thêm lớp học thành công!")
            self.load_data()
            # Xóa nội dung form thêm
            self.class_name_entry.delete(0, tk.END)
            self.department_combobox.set("")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm lớp học: {e}")
            self.db.rollback()

    def load_data(self):
        """Tải dữ liệu lớp học vào Treeview"""
        self.tree.delete(*self.tree.get_children())
        query = """
            SELECT lophoc.ID_LOP, lophoc.TENLOP, khoa.TENKHOA 
            FROM lophoc 
            INNER JOIN khoa ON lophoc.ID_KHOA = khoa.ID_KHOA
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)

    def open_edit_popup(self, event):
        """Khi chọn 1 dòng, mở popup chứa form Sửa/Xóa lớp học."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0], "values")
        class_id = item[0]
        current_name = item[1]
        current_department = item[2]

        popup = tk.Toplevel(self.parent)
        popup.title("Sửa / Xóa Lớp Học")
        popup.grab_set()
        popup.geometry("350x200")
        
        # Form sửa lớp học
        form_frame = ttk.LabelFrame(popup, text="Thông Tin Lớp Học", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tên lớp
        ttk.Label(form_frame, text="Tên Lớp:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_entry = ttk.Entry(form_frame)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.insert(0, current_name)
        
        # Khoa
        ttk.Label(form_frame, text="Khoa:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        dept_combobox = ttk.Combobox(form_frame, state="readonly", width=18)
        dept_combobox.grid(row=1, column=1, padx=5, pady=5)
        dept_combobox["values"] = list(self.department_dict.keys())
        dept_combobox.set(current_department)
        
        # Frame chứa các nút Sửa và Xóa
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        
        def update_class():
            new_name = name_entry.get().strip()
            new_dept = dept_combobox.get()
            new_dept_id = self.department_dict.get(new_dept)
            
            if not new_name or not new_dept_id:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return
            
            query = "UPDATE lophoc SET TENLOP=%s, ID_KHOA=%s WHERE ID_LOP=%s"
            try:
                self.cursor.execute(query, (new_name, new_dept_id, class_id))
                self.db.commit()
                messagebox.showinfo("Thành công", "Sửa thông tin lớp học thành công!")
                self.load_data()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể sửa lớp học: {e}")
                self.db.rollback()
        
        def delete_class():
            confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa lớp học này?")
            if confirm:
                query = "DELETE FROM lophoc WHERE ID_LOP=%s"
                try:
                    self.cursor.execute(query, (class_id,))
                    self.db.commit()
                    messagebox.showinfo("Thành công", "Xóa lớp học thành công!")
                    self.load_data()
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể xóa lớp học: {e}")
                    self.db.rollback()
        
        # Nút Sửa (màu vàng) và Nút Xóa (màu đỏ)
        update_btn = tk.Button(btn_frame, text="Sửa", bg="yellow", fg="black",
                               font=("Helvetica", 10, "bold"), command=update_class)
        update_btn.pack(side=tk.LEFT, padx=5)
        delete_btn = tk.Button(btn_frame, text="Xóa", bg="red", fg="white",
                               font=("Helvetica", 10, "bold"), command=delete_class)
        delete_btn.pack(side=tk.LEFT, padx=5)


