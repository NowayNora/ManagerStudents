import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import face_recognition
import numpy as np
import mysql.connector
import time
import pickle  # Nếu cần dùng pickle để mã hóa dữ liệu khuôn mặt
from PIL import Image, ImageTk

class ThemGuongMat:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = self.db.cursor()
        # Danh sách khuôn mặt (dành cho chức năng tìm kiếm)
        self.known_face_encodings = []
        self.known_face_names = []
        self.create_gui()
        self.load_students()

    def create_gui(self):
        style = ttk.Style()
        style.theme_use("clam")
        default_font = ("Segoe UI", 12)
        
        self.parent.configure(bg="#f0f0f0")
        
        # --- Header ---
        header = tk.Frame(self.parent, bg="#007acc")
        header.pack(fill=tk.X, padx=20, pady=(20,10))
        title = tk.Label(header, text="Thêm/Cập nhật Khuôn Mặt Cho Sinh Viên", 
                         font=("Segoe UI", 20, "bold"), bg="#007acc", fg="white", pady=10)
        title.pack()
        
        # --- Main Frame: chia 2 cột ---
        main_frame = tk.Frame(self.parent, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # --- Frame bên trái: Thông tin sinh viên & chức năng bổ sung ---
        left_frame = tk.LabelFrame(main_frame, text="Thông tin sinh viên", 
                                   font=default_font, bg="white", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=10)
        left_frame.columnconfigure(0, weight=1)

        # --- Thêm Combobox chọn lớp ---
        lbl_class = tk.Label(left_frame, text="Chọn lớp:", font=default_font, bg="white")
        lbl_class.pack(anchor="w", padx=10, pady=(5, 5))
        self.combobox_class = ttk.Combobox(left_frame, font=default_font, state="readonly")
        self.combobox_class.pack(fill="x", padx=10, pady=(0, 10))
        self.combobox_class.bind("<<ComboboxSelected>>", self.on_class_selected)  # Gọi khi chọn lớp

        lbl_student = tk.Label(left_frame, text="Chọn sinh viên:", font=default_font, bg="white")
        lbl_student.pack(anchor="w", padx=10, pady=(5,5))
        self.combobox_student = ttk.Combobox(left_frame, font=default_font, state="readonly")
        self.combobox_student.pack(fill="x", padx=10, pady=(0,10))
        
        # Các nút chức năng bổ sung
        func_frame = tk.Frame(left_frame, bg="white")
        func_frame.pack(fill="x", padx=10, pady=10)
        self.btn_delete_face = tk.Button(func_frame, text="Xóa khuôn mặt", font=default_font, bg="#d9534f", fg="white", command=self.delete_face)
        self.btn_delete_face.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        # self.btn_search_face = tk.Button(func_frame, text="Tìm kiếm", font=default_font, bg="#f0ad4e", fg="white", command=self.search_face)
        # self.btn_search_face.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.btn_stats = tk.Button(func_frame, text="Thống kê", font=default_font, bg="#5bc0de", fg="white", command=self.show_statistics)
        self.btn_stats.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        func_frame.columnconfigure((0,1,2), weight=1)
        
        # --- Frame bên phải: Chia làm 2 phần ---
        right_frame = tk.Frame(main_frame, bg="white", bd=2, relief=tk.RIDGE)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10,0), pady=10)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        
        # Phần quét/cập nhật khuôn mặt: khung nhỏ cố định 300x300
        scan_frame = tk.LabelFrame(right_frame, text="Quét/Cập nhật khuôn mặt", 
                                   font=default_font, bg="white", padx=10, pady=10)
        scan_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scan_frame.rowconfigure(2, weight=1)
        scan_frame.columnconfigure(0, weight=1)
        
        instr_label = tk.Label(scan_frame, 
                               text="Nhấn nút bên dưới để quét (hoặc cập nhật) khuôn mặt.\nHãy nhìn vào camera trong vài giây.",
                               font=default_font, bg="white", justify="center")
        instr_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.btn_scan_face = tk.Button(scan_frame, text="Quét/Cập nhật", font=default_font, bg="#007acc", fg="white", command=self.scan_face)
        self.btn_scan_face.grid(row=1, column=0, padx=10, pady=5)
        
        # Khung xem trước webcam với kích thước cố định 300x300
        cam_frame = tk.Frame(scan_frame, bg="black", width=1000, height=1000)
        cam_frame.grid(row=2, column=0, padx=10, pady=10)
        cam_frame.grid_propagate(False)
        self.camera_label = tk.Label(cam_frame, bg="black")
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Lưu ý: Phiên bản này đã loại bỏ danh sách snapshot (Listbox) để tối giản giao diện.

    def load_classes(self):
        try:
            self.cursor.execute("SELECT ID_LOP, TENLOP FROM LOPHOC")
            classes = self.cursor.fetchall()
            self.class_dict = {c[1]: c[0] for c in classes}  # Map tên lớp -> ID lớp
            self.combobox_class['values'] = list(self.class_dict.keys())  # Đổ dữ liệu vào combobox
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách lớp: {e}")

    def load_students_by_class(self, class_id):
        try:
            self.cursor.execute("SELECT ID_SINHVIEN, TENSINHVIEN FROM SINHVIEN WHERE ID_LOP = %s", (class_id,))
            students = self.cursor.fetchall()
            self.students_dict = {s[1]: s[0] for s in students}  # Map tên sinh viên -> ID
            self.combobox_student['values'] = list(self.students_dict.keys())  # Đổ dữ liệu vào combobox
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên: {e}")

    def on_class_selected(self, event):
        selected_class = self.combobox_class.get()  # Lấy tên lớp đã chọn
        if selected_class in self.class_dict:
            class_id = self.class_dict[selected_class]  # Lấy ID lớp từ dictionary
            self.load_students_by_class(class_id)  # Load danh sách sinh viên theo lớp
            self.combobox_student.set('')  # Xóa lựa chọn cũ trong combobox sinh viên

    def load_students(self):
        self.load_classes()  # Gọi trước để tải danh sách lớp

    # def load_students(self):
    #     try:
    #         self.cursor.execute("SELECT ID_SINHVIEN, TENSINHVIEN FROM SINHVIEN")
    #         students = self.cursor.fetchall()
    #         self.students_dict = {s[1]: s[0] for s in students}
    #         self.combobox_student['values'] = list(self.students_dict.keys())
    #         # Cập nhật danh sách khuôn mặt cho chức năng tìm kiếm
    #         self.known_face_encodings = []
    #         self.known_face_names = []
    #         for s in students:
    #             self.cursor.execute("SELECT KHUONMAT FROM SINHVIEN WHERE ID_SINHVIEN = %s", (s[0],))
    #             data = self.cursor.fetchone()
    #             if data and data[0]:
    #                 encoding = np.frombuffer(data[0], dtype=np.float64)
    #                 self.known_face_encodings.append(encoding)
    #                 self.known_face_names.append(s[1])
    #     except Exception as e:
    #         messagebox.showerror("Lỗi", f"Không thể tải danh sách sinh viên: {e}")
    #
    # def scan_face(self):
    #     selected_student = self.combobox_student.get()
    #     if not selected_student:
    #         messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên trước khi quét khuôn mặt.")
    #         return
    #
    #     messagebox.showinfo("Hướng dẫn", "Hãy nhìn vào camera trong vài giây để quét khuôn mặt.")
    #     cap = cv2.VideoCapture(0)
    #     if not cap.isOpened():
    #         messagebox.showerror("Lỗi", "Không thể mở webcam.")
    #         return
    #     face_encodings_list = []
    #     start_time = time.time()
    #     while time.time() - start_time < 5:
    #         ret, frame = cap.read()
    #         if not ret:
    #             break
    #         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         face_locations = face_recognition.face_locations(rgb_frame)
    #         encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    #         if encodings:
    #             face_encodings_list.append(encodings[0])
    #             for (top, right, bottom, left) in face_locations:
    #                 cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
    #         cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    #         img = Image.fromarray(cv2image).resize((300,300))
    #         imgtk = ImageTk.PhotoImage(image=img)
    #         self.camera_label.imgtk = imgtk
    #         self.camera_label.configure(image=imgtk)
    #         cv2.waitKey(1)
    #     cap.release()
    #     cv2.destroyAllWindows()
    #     if face_encodings_list:
    #         avg_encoding = np.mean(face_encodings_list, axis=0)
    #         self.save_face_encoding(selected_student, avg_encoding)
    #     else:
    #         messagebox.showwarning("Lỗi", "Không nhận diện được khuôn mặt. Hãy thử lại!")
    #
    # def save_face_encoding(self, student_name, face_encoding):
    #     student_id = self.students_dict.get(student_name)
    #     try:
    #         encoding_bytes = face_encoding.astype(np.float64).tobytes()
    #         self.cursor.execute("UPDATE SINHVIEN SET KHUONMAT = %s WHERE ID_SINHVIEN = %s",
    #                             (encoding_bytes, student_id))
    #         self.db.commit()
    #         messagebox.showinfo("Thành công", "Đã lưu khuôn mặt thành công!")
    #         self.load_students()
    #     except Exception as e:
    #         messagebox.showerror("Lỗi", f"Không thể lưu khuôn mặt: {e}")

    def scan_face(self):
        selected_student = self.combobox_student.get()
        if not selected_student:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên trước khi quét khuôn mặt.")
            return

        messagebox.showinfo("Hướng dẫn", "Hãy nhìn vào camera trong vài giây để quét khuôn mặt.")

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Lỗi", "Không thể mở webcam.")
            return

        self.face_encodings_list = []
        self.start_time = time.time()
        self.update_frame()  # Bắt đầu cập nhật khung hình

    def update_frame(self):
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if encodings:
            self.face_encodings_list.append(encodings[0])
            for (top, right, bottom, left) in face_locations:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Cập nhật hình ảnh lên giao diện
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image).resize((300, 300))
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.imgtk = imgtk
        self.camera_label.configure(image=imgtk)

        # Tiếp tục quét trong 5 giây
        if time.time() - self.start_time < 5:
            self.parent.after(10, self.update_frame)  # Gọi lại sau 10ms
        else:
            self.cap.release()
            cv2.destroyAllWindows()
            self.process_face_encodings()  # Xử lý khuôn mặt sau khi hoàn tất

    def process_face_encodings(self):
        if self.face_encodings_list:
            avg_encoding = np.mean(self.face_encodings_list, axis=0)
            selected_student = self.combobox_student.get()
            self.save_face_encoding(selected_student, avg_encoding)
        else:
            messagebox.showwarning("Lỗi", "Không nhận diện được khuôn mặt. Hãy thử lại!")

    def save_face_encoding(self, student_name, face_encoding):
        student_id = self.students_dict.get(student_name)
        try:
            encoding_bytes = face_encoding.astype(np.float64).tobytes()
            self.cursor.execute("UPDATE SINHVIEN SET KHUONMAT = %s WHERE ID_SINHVIEN = %s",
                                (encoding_bytes, student_id))
            self.db.commit()
            messagebox.showinfo("Thành công", "Đã lưu khuôn mặt thành công!")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu khuôn mặt: {e}")
    
    def delete_face(self):
        selected_student = self.combobox_student.get()
        if not selected_student:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần xóa khuôn mặt.")
            return
        student_id = self.students_dict.get(selected_student)
        try:
            self.cursor.execute("UPDATE SINHVIEN SET KHUONMAT = NULL WHERE ID_SINHVIEN = %s", (student_id,))
            self.db.commit()
            messagebox.showinfo("Thành công", "Đã xóa dữ liệu khuôn mặt.")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa khuôn mặt: {e}")
    
    # def search_face(self):
    #     file_path = filedialog.askopenfilename(title="Chọn ảnh khuôn mặt",
    #                                            filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    #     if not file_path:
    #         return
    #     try:
    #         image = face_recognition.load_image_file(file_path)
    #         face_locations = face_recognition.face_locations(image)
    #         if not face_locations:
    #             messagebox.showwarning("Cảnh báo", "Không nhận diện được khuôn mặt trong ảnh.")
    #             return
    #         face_encodings = face_recognition.face_encodings(image, face_locations)
    #         query_encoding = face_encodings[0]
    #     except Exception as e:
    #         messagebox.showerror("Lỗi", f"Lỗi khi xử lý ảnh: {e}")
    #         return
    #     if not self.known_face_encodings:
    #         messagebox.showwarning("Cảnh báo", "Chưa có dữ liệu khuôn mặt được lưu.")
    #         return
    #     matches = face_recognition.compare_faces(self.known_face_encodings, query_encoding)
    #     face_distances = face_recognition.face_distance(self.known_face_encodings, query_encoding)
    #     if any(matches):
    #         best_match_index = np.argmin(face_distances)
    #         student_name = self.known_face_names[best_match_index]
    #         messagebox.showinfo("Kết quả", f"Ảnh khuôn mặt khớp với: {student_name}")
    #     else:
    #         messagebox.showinfo("Kết quả", "Không tìm thấy sinh viên khớp với ảnh khuôn mặt.")
    #
    # def show_statistics(self):
    #     try:
    #         self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN")
    #         total = self.cursor.fetchone()[0]
    #         self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN WHERE KHUONMAT IS NOT NULL")
    #         have_face = self.cursor.fetchone()[0]
    #         no_face = total - have_face
    #         stats = f"Tổng số sinh viên: {total}\nSinh viên có khuôn mặt: {have_face}\nSinh viên chưa có khuôn mặt: {no_face}"
    #         messagebox.showinfo("Thống kê", stats)
    #     except Exception as e:
    #         messagebox.showerror("Lỗi", f"Không thể tải thống kê: {e}")
    #
    def show_statistics(self):
        try:
            selected_class = self.combobox_class.get()  # Lấy lớp đang chọn
            if not selected_class:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn lớp trước khi xem thống kê!")
                return

            class_id = self.class_dict.get(selected_class)  # Lấy ID lớp từ dictionary

            # Thống kê số lượng sinh viên trong lớp được chọn
            self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN WHERE ID_LOP = %s", (class_id,))
            total = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT COUNT(*) FROM SINHVIEN WHERE ID_LOP = %s AND KHUONMAT IS NOT NULL", (class_id,))
            have_face = self.cursor.fetchone()[0]

            no_face = total - have_face

            stats = f"Lớp: {selected_class}\nTổng số sinh viên: {total}\nSinh viên có khuôn mặt: {have_face}\nSinh viên chưa có khuôn mặt: {no_face}"
            messagebox.showinfo("Thống kê", stats)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải thống kê: {e}")
