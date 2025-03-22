import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import pandas as pd
from PIL import Image, ImageTk
import face_recognition
import numpy as np
import mysql.connector
import time
import threading

class ScrollableFrame(tk.Frame):
    def __init__(self, container, bg="white", *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.configure(bg=bg)
        canvas = tk.Canvas(self, bg=bg, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=bg)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class QuanLyGuongMat:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = self.db.cursor()
        self.known_face_encodings = []
        self.known_face_names = []
        self.running = False
        self.create_gui()
        # self.load_known_faces()  # Nếu cần load sẵn khuôn mặt

    def create_gui(self):
        style = ttk.Style()
        style.theme_use('clam')
        default_font = ("Segoe UI", 11)
        self.parent.configure(bg="#f0f0f0")
        
        title = tk.Label(self.parent, text="Hệ Thống Điểm Danh Bằng Khuôn Mặt", 
                         font=("Segoe UI", 18, "bold"), fg="white", bg="#007acc", pady=10)
        title.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10,5))
        
        self.parent.columnconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=2)
        self.parent.rowconfigure(1, weight=3)
        self.parent.rowconfigure(2, weight=1)

        # --- Frame bên trái: Chứa danh sách lớp, môn, giáo viên ---
        self.frame_left_container = ScrollableFrame(self.parent, bg="white")
        self.frame_left_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.frame_left = self.frame_left_container.scrollable_frame  # Frame thực tế chứa nội dung

        # Cấu hình cột
        self.frame_left.columnconfigure(0, weight=1)  # Cột Label
        self.frame_left.columnconfigure(1, weight=2)  # Cột nhập liệu

        # Chọn lớp
        lbl_lop = tk.Label(self.frame_left, text="Chọn lớp:", font=default_font, bg="white")
        lbl_lop.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.combobox_lop = ttk.Combobox(self.frame_left, font=default_font, state="readonly")
        self.combobox_lop.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.combobox_lop.bind("<<ComboboxSelected>>", self.on_lop_selected)

        # Danh sách sinh viên
        lbl_sv = tk.Label(self.frame_left, text="Danh sách Sinh Viên:", font=default_font, bg="white")
        lbl_sv.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.listbox_sinhvien = tk.Listbox(self.frame_left, font=default_font, height=5)
        self.listbox_sinhvien.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Chọn môn
        lbl_mon = tk.Label(self.frame_left, text="Chọn môn:", font=default_font, bg="white")
        lbl_mon.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.combobox_monhoc = ttk.Combobox(self.frame_left, font=default_font, state="readonly")
        self.combobox_monhoc.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.combobox_monhoc.bind("<<ComboboxSelected>>", self.on_monhoc_selected)

        # Giáo viên dạy môn
        lbl_gv = tk.Label(self.frame_left, text="Giáo viên dạy môn:", font=default_font, bg="white")
        lbl_gv.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_giaovien = tk.Entry(self.frame_left, font=default_font, state="readonly")
        self.entry_giaovien.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Chọn giảng dạy
        lbl_gd = tk.Label(self.frame_left, text="Chọn giảng dạy:", font=default_font, bg="white")
        lbl_gd.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.combobox_giangday = ttk.Combobox(self.frame_left, font=default_font, state="readonly")
        self.combobox_giangday.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Nút xác nhận
        self.btn_confirm_selection = tk.Button(self.frame_left, text="Xác nhận lớp & môn", font=default_font,
                                               bg="#4CAF50", fg="white", command=self.confirm_selection)
        self.btn_confirm_selection.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Frame bên phải: Camera ---
        self.frame_right = tk.Frame(self.parent, bg="black", bd=2, relief=tk.RIDGE)
        self.frame_right.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.frame_right.rowconfigure(0, weight=1)
        self.frame_right.columnconfigure(0, weight=1)
        self.label_cam = tk.Label(self.frame_right, bg="black")
        self.label_cam.grid(row=0, column=0, sticky="nsew")
        
        # --- Frame phía dưới: Bảng điểm danh và nút thao tác ---
        self.frame_bottom = tk.Frame(self.parent, bg="white", bd=2, relief=tk.RIDGE)
        self.frame_bottom.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.frame_bottom.rowconfigure(0, weight=1)
        self.frame_bottom.columnconfigure(0, weight=1)
        
        self.tree_diemdanh = ttk.Treeview(self.frame_bottom,
                                          columns=("Tên SV", "Tên môn", "Tên GV", "Ngày điểm danh"),
                                          show="headings")
        self.tree_diemdanh.heading("Tên SV", text="Tên Sinh Viên")
        self.tree_diemdanh.heading("Tên môn", text="Tên Môn")
        self.tree_diemdanh.heading("Tên GV", text="Tên Giáo Viên")
        self.tree_diemdanh.heading("Ngày điểm danh", text="Ngày Điểm Danh")
        self.tree_diemdanh.column("Tên SV", anchor="center", width=150)
        self.tree_diemdanh.column("Tên môn", anchor="center", width=150)
        self.tree_diemdanh.column("Tên GV", anchor="center", width=150)
        self.tree_diemdanh.column("Ngày điểm danh", anchor="center", width=150)
        self.tree_diemdanh.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Thêm scrollbar cho Treeview
        scrollbar_tree = ttk.Scrollbar(self.frame_bottom, orient="vertical", command=self.tree_diemdanh.yview)
        scrollbar_tree.grid(row=0, column=1, sticky="ns", pady=10)
        self.tree_diemdanh.configure(yscrollcommand=scrollbar_tree.set)
        
        self.frame_buttons = tk.Frame(self.frame_bottom, bg="white")
        self.frame_buttons.grid(row=1, column=0, pady=5)
        self.btn_ket_thuc = tk.Button(self.frame_buttons, text="Kết thúc điểm danh", font=default_font,
                                      bg="#d9534f", fg="white", command=self.ket_thuc_diem_danh)
        self.btn_ket_thuc.pack(side=tk.LEFT, padx=5)
        self.btn_start = tk.Button(self.frame_buttons, text="Bắt đầu điểm danh", font=default_font,
                                   bg="#007acc", fg="white", command=self.start_diem_danh, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=5)
        self.btn_confirm = tk.Button(self.frame_buttons, text="Xác nhận điểm danh", font=default_font,
                                     bg="#ffa500", fg="white", command=self.confirm_diem_danh, state=tk.DISABLED)
        self.btn_confirm.pack(side=tk.LEFT, padx=5)
        self.btn_export_excel = tk.Button(self.frame_buttons, text="Xuất Excel", font=default_font,
                                          bg="#28a745", fg="white", command=self.export_diemdanh_to_excel)
        self.btn_export_excel.pack(side=tk.LEFT, padx=5)
        
        self.load_lop()

    # --------------------- Các hàm xử lý dữ liệu ---------------------
    def load_lop(self):
        try:
            self.cursor.execute("SELECT ID_LOP, TENLOP FROM LOPHOC")
            lop_list = self.cursor.fetchall()
            self.combobox_lop["values"] = [lop[1] for lop in lop_list]
            self.lop_dict = {lop[1]: lop[0] for lop in lop_list}
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp: {e}")

    def on_lop_selected(self, event):
        selected_lop = self.combobox_lop.get()
        lop_id = self.lop_dict.get(selected_lop)
        if lop_id:
            self.load_known_faces(lop_id)
        self.cursor.execute("SELECT TENSINHVIEN FROM SINHVIEN WHERE ID_LOP = %s", (lop_id,))
        sinhvien_list = self.cursor.fetchall()
        self.listbox_sinhvien.delete(0, tk.END)
        for sv in sinhvien_list:
            self.listbox_sinhvien.insert(tk.END, sv[0])
        self.cursor.execute("""
            SELECT MONHOC.TENMON FROM MONHOC 
            JOIN LOPHOC_MONHOC ON MONHOC.ID_MON = LOPHOC_MONHOC.ID_MON
            WHERE LOPHOC_MONHOC.ID_LOP = %s
        """, (lop_id,))
        monhoc_list = self.cursor.fetchall()
        self.combobox_monhoc["values"] = [mh[0] for mh in monhoc_list]

    def on_monhoc_selected(self, event):
        selected_mon = self.combobox_monhoc.get()
        self.cursor.execute("SELECT ID_MON, ID_GIAOVIEN FROM MONHOC WHERE TENMON = %s", (selected_mon,))
        mon_data = self.cursor.fetchone()
        if mon_data:
            mon_id, giaovien_id = mon_data
            self.cursor.execute("SELECT TENGIAOVIEN FROM GIAOVIEN WHERE ID_GIAOVIEN = %s", (giaovien_id,))
            gv_data = self.cursor.fetchone()
            self.entry_giaovien.config(state=tk.NORMAL)
            self.entry_giaovien.delete(0, tk.END)
            self.entry_giaovien.insert(0, gv_data[0] if gv_data else "Không xác định")
            self.entry_giaovien.config(state="readonly")
            self.cursor.execute("SELECT ID_GIANGDAY, NGAYDAY FROM GIANGDAY WHERE ID_MON = %s", (mon_id,))
            giangday_list = self.cursor.fetchall()
            self.combobox_giangday["values"] = [f"{gd[1]} (ID: {gd[0]})" for gd in giangday_list]
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy môn học")

    def confirm_selection(self):
        selected_lop = self.combobox_lop.get()
        selected_mon = self.combobox_monhoc.get()
        selected_giangday_text = self.combobox_giangday.get()
        if not selected_lop or not selected_mon or not selected_giangday_text:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đầy đủ lớp, môn học và giảng dạy.")
            return
        try:
            id_giangday = int(selected_giangday_text.split("(ID: ")[-1].strip(")"))
        except ValueError:
            messagebox.showerror("Lỗi", "Không thể xác định ID Giảng Dạy.")
            return
        self.selected_lop = selected_lop
        self.selected_monhoc = selected_mon
        self.selected_giangday = id_giangday
        messagebox.showinfo("Xác nhận", f"Đã chọn:\nLớp: {selected_lop}\nMôn: {selected_mon}\nGiảng dạy ID: {id_giangday}")
        self.btn_start.config(state=tk.NORMAL)
        self.show_ds_diemdanh()

    def check_giangday(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM GIANGDAY")
            result = self.cursor.fetchone()
            if result[0] == 0:
                self.btn_start.config(state=tk.DISABLED)
            else:
                self.btn_start.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kiểm tra bảng giảng dạy: {e}")
            self.btn_start.config(state=tk.DISABLED)

    def load_known_faces(self, lop_id):
        try:
            query = "SELECT TENSINHVIEN, KHUONMAT FROM SINHVIEN WHERE ID_LOP = %s"
            self.cursor.execute(query, (lop_id,))
            sinhvien_list = self.cursor.fetchall()
            self.known_face_encodings.clear()
            self.known_face_names.clear()
            for tensinhvien, khuonmat in sinhvien_list:
                if khuonmat:
                    face_encoding = np.frombuffer(khuonmat, dtype=np.float64)
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(tensinhvien)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu khuôn mặt: {e}")

    def start_diem_danh(self):
        if not hasattr(self, 'selected_monhoc'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học trước khi điểm danh.")
            return
        if hasattr(self, 'cap') and self.cap is not None and self.cap.isOpened():
            messagebox.showwarning("Cảnh báo", "Webcam đã mở.")
            return
        self.running = True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở webcam.")
            return
        self.parent.after(2000, self.show_webcam)

    def show_webcam(self):
        if not getattr(self, "running", False):
            return
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            if not hasattr(self, "frame_count"):
                self.frame_count = 0
            self.frame_count += 1
            if self.frame_count % 3 == 0 and not getattr(self, "detecting", False):
                self.detecting = True
                threading.Thread(target=self.recognize_faces, args=(rgb_frame, face_locations)).start()
            detected_names = self.detected_names if hasattr(self, "detected_names") else []
            for (top, right, bottom, left), name in zip(face_locations, detected_names or ["Unknown"] * len(face_locations)):
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.label_cam.imgtk = imgtk
            self.label_cam.configure(image=imgtk)
            self.label_cam.after(30, self.show_webcam)
        else:
            messagebox.showerror("Lỗi", "Không thể khởi động webcam.")

    def confirm_diem_danh(self):
        if not hasattr(self, "selected_giangday"):
            messagebox.showwarning("Cảnh báo", "Vui lòng xác nhận lớp, môn và giảng dạy.")
            return
        if hasattr(self, "detected_name") and self.detected_name:
            self.update_diem_danh(self.detected_name, self.selected_giangday)
            self.btn_confirm.config(state=tk.DISABLED)
        else:
            messagebox.showwarning("Cảnh báo", "Không có sinh viên nào để xác nhận điểm danh.")

    def recognize_faces(self, rgb_frame, face_locations):
        try:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            detected_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                name = "Unknown"
                if any(matches):
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                detected_names.append(name)
            print(f"Danh sách nhận diện: {detected_names}")
            if not hasattr(self, "last_detected_names"):
                self.last_detected_names = []
            if detected_names != self.last_detected_names:
                self.last_detected_names = detected_names
                self.detected_names = detected_names
                print(f"Cập nhật danh sách: {self.detected_names}")
                if any(name != "Unknown" for name in detected_names):
                    self.btn_confirm.config(state=tk.NORMAL)
                    self.detected_name = detected_names[0]
                else:
                    self.btn_confirm.config(state=tk.DISABLED)
                    self.detected_name = None
        except Exception as e:
            print(f"Lỗi nhận diện khuôn mặt: {e}")
        finally:
            self.detecting = False

    def update_diem_danh(self, sinhvien_name, id_giangday):
        try:
            self.cursor.execute("SELECT ID_SINHVIEN FROM SINHVIEN WHERE TENSINHVIEN = %s", (sinhvien_name,))
            result = self.cursor.fetchone()
            if not result:
                messagebox.showerror("Lỗi", f"Không tìm thấy sinh viên: {sinhvien_name}")
                return
            id_sinhvien = result[0]
            self.cursor.execute("SELECT COUNT(*) FROM DIEMDANH WHERE ID_SINHVIEN = %s AND ID_GIANGDAY = %s",
                                (id_sinhvien, id_giangday))
            count = self.cursor.fetchone()[0]
            if count > 0:
                messagebox.showwarning("Cảnh báo", f"Sinh viên {sinhvien_name} đã điểm danh trước đó.")
                return
            ngay_diem_danh = time.strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("INSERT INTO DIEMDANH (ID_SINHVIEN, ID_GIANGDAY, NGAYDIEMDANH) VALUES (%s, %s, %s)",
                                (id_sinhvien, id_giangday, ngay_diem_danh))
            self.db.commit()
            messagebox.showinfo("Thành công", f"Điểm danh thành công cho {sinhvien_name} (ID Giảng Dạy: {id_giangday})")
            self.tree_diemdanh.insert("", "end", values=(sinhvien_name, self.selected_monhoc, self.entry_giaovien.get(), ngay_diem_danh))
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Lỗi", f"Lỗi khi lưu điểm danh: {e}")

    def show_ds_diemdanh(self):
        if not hasattr(self, 'selected_monhoc'):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn môn học trước khi xem danh sách điểm danh.")
            return
        try:
            self.cursor.execute("SELECT ID_MON FROM MONHOC WHERE TENMON = %s", (self.selected_monhoc,))
            id_mon = self.cursor.fetchone()[0]
            self.cursor.execute("""
                SELECT S.TENSINHVIEN, M.TENMON, G.TENGIAOVIEN, D.NGAYDIEMDANH
                FROM DIEMDANH D
                JOIN SINHVIEN S ON D.ID_SINHVIEN = S.ID_SINHVIEN
                JOIN GIANGDAY GD ON D.ID_GIANGDAY = GD.ID_GIANGDAY
                JOIN MONHOC M ON GD.ID_MON = M.ID_MON
                JOIN GIAOVIEN G ON GD.ID_GIAOVIEN = G.ID_GIAOVIEN
                WHERE M.ID_MON = %s AND DATE(D.NGAYDIEMDANH) = CURDATE()
            """, (id_mon,))
            ds_diemdanh = self.cursor.fetchall()
            for row in self.tree_diemdanh.get_children():
                self.tree_diemdanh.delete(row)
            for row in ds_diemdanh:
                self.tree_diemdanh.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách điểm danh: {e}")

    def export_diemdanh_to_excel(self):
        if not self.tree_diemdanh.get_children():
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để xuất!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All Files", "*.*")]
        )

        if not file_path:
            return  # Người dùng hủy lưu

        try:
            # Thu thập dữ liệu từ Treeview
            data = []
            for item in self.tree_diemdanh.get_children():
                row = self.tree_diemdanh.item(item, "values")
                data.append(row)

            # Chuyển dữ liệu thành DataFrame của pandas
            df = pd.DataFrame(data, columns=["Tên SV", "Tên môn", "Tên GV", "Ngày điểm danh"])

            # Xuất ra file Excel
            df.to_excel(file_path, index=False)

            messagebox.showinfo("Thành công", f"Dữ liệu đã được xuất ra {file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất dữ liệu: {e}")

    def ket_thuc_diem_danh(self):
        self.running = False
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        self.label_cam.config(image="")
        self.combobox_lop.set("")
        self.combobox_monhoc.set("")
        self.combobox_giangday.set("")
        self.entry_giaovien.config(state=tk.NORMAL)
        self.entry_giaovien.delete(0, tk.END)
        self.entry_giaovien.config(state="readonly")
        self.listbox_sinhvien.delete(0, tk.END)
        self.btn_start.config(state=tk.DISABLED)
        self.btn_confirm.config(state=tk.DISABLED)
        self.load_lop()
        messagebox.showinfo("Hoàn tất", "Điểm danh đã kết thúc và hệ thống đã được làm mới.")

    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()
