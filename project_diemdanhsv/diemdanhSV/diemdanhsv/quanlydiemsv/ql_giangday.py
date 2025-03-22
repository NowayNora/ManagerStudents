import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from tkcalendar import DateEntry
import mysql.connector
from datetime import datetime, timedelta

class QuanLyGiangDay:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.current_week_start = datetime.today() - timedelta(days=datetime.today().weekday())

        self.create_ui()

    def create_ui(self):
        top_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Quản Lý Giảng Dạy", font=("Arial", 16, "bold"), fg="white", bg="blue").pack(pady=10,
                                                                                                              fill=tk.X)

        # Phần lọc (filter_frame)
        filter_frame = tk.Frame(top_frame, bg="lightgray")
        filter_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        tk.Label(filter_frame, text="Lọc theo môn học:", bg="lightgray").pack(side=tk.LEFT, padx=5)
        self.filter_mon_combobox = ttk.Combobox(filter_frame)
        self.filter_mon_combobox.pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Lọc", command=self.filter_data).pack(side=tk.LEFT, padx=5)

        # Phần bottom_frame (chứa tuần, nút điều hướng, form nhập liệu)
        bottom_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        bottom_frame.pack(side=tk.TOP, fill=tk.X)  # Đặt bottom_frame lên trên middle_frame

        self.week_label = tk.Label(bottom_frame, text="", font=("Arial", 12, "bold"), bg="lightgray")
        self.week_label.pack(side=tk.LEFT, padx=5)

        nav_frame = tk.Frame(bottom_frame, bg="lightgray")
        nav_frame.pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="<< Tuần trước", command=self.prev_week).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Tuần sau >>", command=self.next_week).pack(side=tk.LEFT, padx=5)

        form_frame = tk.Frame(bottom_frame, bg="lightgray", padx=10, pady=10)
        form_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(form_frame, text="Ngày Dạy:", bg="lightgray").grid(row=0, column=0, padx=5, pady=5)
        self.cal = DateEntry(form_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.cal.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Tiết bắt đầu:", bg="lightgray").grid(row=0, column=2, padx=5, pady=5)
        self.tiet_entry = tk.Entry(form_frame)
        self.tiet_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Tiết kết thúc:", bg="lightgray").grid(row=0, column=4, padx=5, pady=5)
        self.tietkt_entry = tk.Entry(form_frame)
        self.tietkt_entry.grid(row=0, column=5, padx=5, pady=5)

        tk.Label(form_frame, text="Giáo Viên:", bg="lightgray").grid(row=1, column=0, padx=5, pady=5)
        self.gv_entry = ttk.Entry(form_frame)
        self.gv_entry.grid(row=1, column=1, padx=5, pady=5)
        self.gv_entry.config(state="disabled")  # Khóa ô nhập liệu

        tk.Label(form_frame, text="Môn Học:", bg="lightgray").grid(row=1, column=2, padx=5, pady=5)
        self.mon_combobox = ttk.Combobox(form_frame)
        self.mon_combobox.grid(row=1, column=3, padx=5, pady=5)

        # Phần nút thao tác (thêm, sửa, xóa, tải lại)
        button_frame = tk.Frame(self.parent, bg="white")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Thêm", bg="green", fg="black", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sửa", bg="orange", fg="black", command=self.update_entry).pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Button(button_frame, text="Xóa", bg="red", fg="black", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Tải lại", bg="blue", fg="white", command=self.reload_data).pack(side=tk.LEFT,
                                                                                                      padx=5)

        # Phần bảng lịch học (middle_frame)
        middle_frame = tk.Frame(self.parent, bg="white")
        middle_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.table_frame = tk.Frame(middle_frame, bg="white")
        self.table_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.table_frame, bg="white", width=1800, height=400)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.scrollbar_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.scrollbar_x = ttk.Scrollbar(middle_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Tải dữ liệu ban đầu
        self.load_combobox_data()
        self.update_table_headers()
        self.load_teachers()
        self.load_schedule()

        self.mon_combobox.bind("<<ComboboxSelected>>", self.update_teacher_entry)

    def filter_data(self):
        filter_subject = self.filter_mon_combobox.get()
        query = """
            SELECT giangday.ID_GIANGDAY, giangday.NGAYDAY, giangday.TIETGD, 
                    giaovien.TENGIAOVIEN, monhoc.TENMON
            FROM giangday
            JOIN giaovien ON giangday.ID_GIAOVIEN = giaovien.ID_GIAOVIEN
            JOIN monhoc ON giangday.ID_MON = monhoc.ID_MON
        """
        conditions = []
        params = []

        if filter_subject:
            conditions.append("monhoc.TENMON = %s")
            params.append(filter_subject)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        try:
            self.cursor.execute(query, tuple(params))
            rows = self.cursor.fetchall()
            self.show_filtered_result_on_canvas(rows)
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể lọc dữ liệu: {err}")
            
    def show_filtered_result_on_canvas(self, rows):
        week_dates = [(self.current_week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        schedule_data = {date: {"Sáng": "", "Chiều": "", "Tối": ""} for date in week_dates}

        for row in rows:
            ngay, tiet, gv, mon = row[1], row[2], row[3], row[4]
            ngay_str = ngay.strftime("%Y-%m-%d") if isinstance(ngay, datetime) else str(ngay)
            try:
                tiet_num = int(tiet.replace(" ", "").split('-')[0])
            except ValueError:
                continue
            session = "Sáng" if 1 <= tiet_num <= 6 else ("Chiều" if 7 <= tiet_num <= 11 else "Tối")
            if ngay_str in schedule_data:
                schedule_data[ngay_str][session] += f"{gv} - {mon}\n"

        self.draw_schedule_on_canvas(schedule_data)

    def update_table_headers(self):
        week_dates = [(self.current_week_start + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        self.week_label.config(text=f"Lịch tuần: {week_dates[0]} - {week_dates[-1]}")

    def load_schedule(self):
        week_dates = [(self.current_week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        # search_text = self.search_entry.get().strip().lower()

        try:
            query = """
                SELECT giangday.ID_GIANGDAY, giangday.NGAYDAY, giangday.TIETGD, 
                    giaovien.TENGIAOVIEN, monhoc.TENMON
                FROM giangday
                JOIN giaovien ON giangday.ID_GIAOVIEN = giaovien.ID_GIAOVIEN
                JOIN monhoc ON giangday.ID_MON = monhoc.ID_MON
                WHERE NGAYDAY BETWEEN %s AND %s
            """
            params = (week_dates[0], week_dates[-1])
            # if search_text:
            #     query += " AND (LOWER(giaovien.TENGIAOVIEN) LIKE %s OR LOWER(monhoc.TENMON) LIKE %s)"
            #     params += (f"%{search_text}%", f"%{search_text}%")

            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            print("Dữ liệu từ MySQL:", rows)
        except mysql.connector.Error as err:
            print(f"Lỗi truy vấn MySQL: {err}")
            return

        schedule_data = {date: {"Sáng": "", "Chiều": "", "Tối": ""} for date in week_dates}
        self.cell_mapping = {}
        for row in rows:
            rec_id, ngay, tiet, gv, mon = row
            if isinstance(ngay, datetime):
                ngay_str = ngay.strftime("%Y-%m-%d")
            elif isinstance(ngay, str):
                ngay_str = ngay
            else:
                ngay_str = str(ngay)

            tiet_cleaned = tiet.replace(" ", "")
            tiet_str = tiet_cleaned.split('-')[0]
            try:
                tiet_num = int(tiet_str)
            except ValueError:
                print(f"Lỗi khi chuyển đổi TIETGD: {tiet}")
                continue

            session = "Sáng" if 1 <= tiet_num <= 6 else ("Chiều" if 7 <= tiet_num <= 11 else "Tối")
            if ngay_str in schedule_data:
                schedule_data[ngay_str][session] += f"Tiết {tiet}: {gv} - {mon}\n"
            key = (ngay_str, session)
            if key not in self.cell_mapping:
                self.cell_mapping[key] = []
            self.cell_mapping[key].append({
                "ID": rec_id,
                "NGAYDAY": ngay_str,
                "TIETGD": tiet,
                "TENGIAOVIEN": gv,
                "TENMON": mon
            })
        print("Dữ liệu lịch giảng dạy để vẽ:", schedule_data)
        self.schedule_data = schedule_data
        self.draw_schedule_on_canvas(schedule_data)

    def draw_schedule_on_canvas(self, schedule_data):
        print("Dữ liệu lịch giảng dạy để vẽ:", schedule_data)
        self.canvas.delete("all")

        width = self.canvas.winfo_width() or 1800
        height = self.canvas.winfo_height() or 400

        start_color = (168, 218, 220)
        end_color = (255, 255, 255)
        for i in range(height):
            ratio = i / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color)

        sessions = ["Sáng", "Chiều", "Tối"]
        cell_width = 150
        cell_height = 100
        x_offset = 100
        y_offset = 40
        font_title = ("Helvetica", 10, "bold")
        font_content = ("Helvetica", 9)

        sorted_dates = sorted(schedule_data.keys())
        weekday_mapping = {
            0: "Thứ 2",
            1: "Thứ 3",
            2: "Thứ 4",
            3: "Thứ 5",
            4: "Thứ 6",
            5: "Thứ 7",
            6: "Chủ nhật"
        }

        for i, day_str in enumerate(sorted_dates):
            dt = datetime.strptime(day_str, "%Y-%m-%d")
            day_label = dt.strftime("%d/%m")
            day_name = weekday_mapping.get(dt.weekday(), "")
            header_text = f"{day_name}\n{day_label}"
            self.canvas.create_text(
                x_offset + i * cell_width + cell_width / 2 + 2,
                15 + 2,
                text=header_text,
                font=font_title,
                fill="gray",
                justify="center"
            )
            self.canvas.create_text(
                x_offset + i * cell_width + cell_width / 2,
                15,
                text=header_text,
                font=font_title,
                fill="darkblue",
                justify="center"
            )

        for j, session in enumerate(sessions):
            self.canvas.create_text(
                50 + 2,
                y_offset + j * cell_height + cell_height / 2 + 2,
                text=session,
                font=font_title,
                fill="gray"
            )
            self.canvas.create_text(
                50,
                y_offset + j * cell_height + cell_height / 2,
                text=session,
                font=font_title,
                fill="darkblue"
            )

        for j, session in enumerate(sessions):
            for i, day_str in enumerate(sorted_dates):
                text_in_cell = schedule_data[day_str][session]
                x1 = x_offset + i * cell_width
                y1 = y_offset + j * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                cell_tag = f"cell_{day_str}_{session}"
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="darkred", width=2, tags=(cell_tag,))
                self.canvas.create_text(x1 + 5, y1 + 5, text=text_in_cell, anchor="nw",
                                        font=font_content, fill="black", width=cell_width - 10, tags=(cell_tag,))
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        print(f"{day_str} - {session}: {text_in_cell}")

    def reload_data(self):
        # Xóa toàn bộ dữ liệu trên Canvas
        self.canvas.delete("all")
        self.schedule_data = {}
        self.cell_mapping = {}

        # Reset ô tìm kiếm và lọc
        # self.search_entry.delete(0, tk.END)
        self.filter_mon_combobox.set("")

        # Reset các ô nhập liệu
        self.cal.set_date(datetime.today())
        self.tiet_entry.delete(0, tk.END)
        self.tietkt_entry.delete(0, tk.END)
        self.gv_entry.config(state="normal")
        self.gv_entry.delete(0, tk.END)
        self.gv_entry.config(state="readonly")
        self.mon_combobox.set("")
        self.selected_id_gd = None

        # Tải lại dữ liệu từ database
        self.load_schedule()

    


    import tkinter.simpledialog as simpledialog

    import tkinter.simpledialog as simpledialog

    def on_canvas_click(self, event):
        if not hasattr(self, "schedule_data") or not self.schedule_data:
            messagebox.showerror("Lỗi", "Chưa có dữ liệu lịch, vui lòng tải dữ liệu.")
            return

        x, y = event.x, event.y
        x_offset, y_offset = 100, 40
        cell_width, cell_height = 150, 100
        sessions = ["Sáng", "Chiều", "Tối"]

        if x < x_offset or y < y_offset:
            return

        col = (x - x_offset) // cell_width
        row = (y - y_offset) // cell_height

        sorted_dates = sorted(self.schedule_data.keys())

        try:
            selected_date = sorted_dates[col]
            selected_session = sessions[row]
        except IndexError:
            return

        key = (selected_date, selected_session)
        records = self.cell_mapping.get(key, [])

        if not records:
            messagebox.showinfo("Thông báo", "Ô được chọn không có dữ liệu.")
            return

        # Nếu có nhiều bản ghi, hiển thị hộp thoại chọn với danh sách đánh số
        if len(records) > 1:
            options = [f"{i+1}. {r['TENGIAOVIEN']} - {r['TENMON']} (Tiết {r['TIETGD']})" for i, r in enumerate(records)]
            options_str = "\n".join(options)
            selected_index = simpledialog.askinteger("Chọn tiết dạy", 
                                                    f"Có nhiều bản ghi, chọn một:\n\n{options_str}\n\nNhập số thứ tự (1-{len(records)}):",
                                                    minvalue=1, maxvalue=len(records))
            if selected_index is None:
                return
            record = records[selected_index - 1]  # Chọn bản ghi theo số thứ tự
        else:
            record = records[0]

        # Cập nhật form với dữ liệu đã chọn
        try:
            dt = datetime.strptime(record["NGAYDAY"], "%Y-%m-%d")
            self.cal.set_date(dt)
        except Exception as e:
            print("Lỗi chuyển đổi ngày:", e)

        self.tiet_entry.delete(0, tk.END)
        tiet_bat_dau, tiet_ket_thuc = record["TIETGD"].split('-')
        self.tiet_entry.insert(0, tiet_bat_dau)
        self.tietkt_entry.delete(0, tk.END)
        self.tietkt_entry.insert(0, tiet_ket_thuc)

        self.gv_entry.config(state="normal")
        self.gv_entry.delete(0, tk.END)
        self.gv_entry.insert(0, record["TENGIAOVIEN"])
        self.gv_entry.config(state="readonly")
        self.mon_combobox.set(record["TENMON"])
        self.selected_id_gd = record["ID"]

        print("Ô được chọn:", key, "Record:", record)




    def prev_week(self):
        self.current_week_start -= timedelta(weeks=1)
        self.update_table_headers()
        self.load_schedule()

    def next_week(self):
        self.current_week_start += timedelta(weeks=1)
        self.update_table_headers()
        self.load_schedule()

    def load_teachers(self):
        pass

    def load_combobox_data(self):
        self.cursor.execute("SELECT TENMON FROM monhoc")
        subjects = self.cursor.fetchall()
        self.mon_combobox["values"] = [row[0] for row in subjects]
        self.filter_mon_combobox["values"] = [row[0] for row in subjects]

    def update_teacher_entry(self, event=None):
        selected_subject = self.mon_combobox.get()
        query = """
            SELECT giaovien.TENGIAOVIEN 
            FROM monhoc 
            JOIN giaovien ON monhoc.ID_GIAOVIEN = giaovien.ID_GIAOVIEN 
            WHERE monhoc.TENMON = %s
        """
        self.cursor.execute(query, (selected_subject,))
        result = self.cursor.fetchone()
        if result:
            self.gv_entry.config(state="normal")
            self.gv_entry.delete(0, tk.END)
            self.gv_entry.insert(0, result[0])
            self.gv_entry.config(state="readonly")

    def validate_tiet(self):
        tiet_bat_dau = self.tiet_entry.get().strip()
        tiet_ket_thuc = self.tietkt_entry.get().strip()

        if not tiet_bat_dau or not tiet_ket_thuc:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ tiết bắt đầu và tiết kết thúc!")
            return None

        if not tiet_bat_dau.isdigit() or not tiet_ket_thuc.isdigit():
            messagebox.showerror("Lỗi", "Tiết học phải là số nguyên!")
            return None

        tiet_bat_dau, tiet_ket_thuc = int(tiet_bat_dau), int(tiet_ket_thuc)

        if tiet_bat_dau < 1 or tiet_ket_thuc > 15:
            messagebox.showerror("Lỗi", "Tiết học phải nằm trong khoảng từ 1 đến 15!")
            return None
        if tiet_bat_dau > tiet_ket_thuc:
            messagebox.showerror("Lỗi", "Tiết bắt đầu không thể lớn hơn tiết kết thúc!")
            return None
        if tiet_ket_thuc - tiet_bat_dau + 1 < 1 or tiet_ket_thuc - tiet_bat_dau + 1 > 5:
            messagebox.showerror("Lỗi", "Một buổi học phải từ 1 đến 5 tiết!")
            return None

        return f"{tiet_bat_dau}-{tiet_ket_thuc}"

    def add_entry(self):
        try:
            date_str = self.cal.get()
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            formatted_date = date_obj.strftime('%Y-%m-%d')

            tiet = self.validate_tiet()
            if tiet is None:
                return

            gv, mon = self.gv_entry.get(), self.mon_combobox.get()

            if not all([formatted_date, tiet, gv, mon]):
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
                return

            self.cursor.execute("SELECT ID_GIAOVIEN FROM giaovien WHERE TENGIAOVIEN = %s", (gv,))
            gv_id = self.cursor.fetchone()
            if not gv_id:
                messagebox.showerror("Lỗi", "Giáo viên không tồn tại!")
                return

            self.cursor.execute("SELECT ID_MON FROM monhoc WHERE TENMON = %s", (mon,))
            mon_id = self.cursor.fetchone()
            if not mon_id:
                messagebox.showerror("Lỗi", "Môn học không tồn tại!")
                return

            self.cursor.execute("""
                INSERT INTO giangday (NGAYDAY, TIETGD, ID_GIAOVIEN, ID_MON) 
                VALUES (%s, %s, %s, %s)
            """, (formatted_date, tiet, gv_id[0], mon_id[0]))
            self.db.commit()

            messagebox.showinfo("Thành công", "Thêm lịch giảng dạy thành công!")
            self.load_data()

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm dữ liệu: {err}")
        self.reload_data()

    def update_entry(self):
        if not hasattr(self, 'selected_id_gd') or not self.selected_id_gd:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng trước khi cập nhật!")
            return

        date_str = self.cal.get()
        date_obj = datetime.strptime(date_str, "%m/%d/%y")
        formatted_date = date_obj.strftime('%Y-%m-%d')

        tiet = self.validate_tiet()
        if tiet is None:
            return

        gv, mon = self.gv_entry.get(), self.mon_combobox.get()

        if not all([formatted_date, tiet, gv, mon]):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        self.cursor.execute("SELECT ID_GIAOVIEN FROM giaovien WHERE TENGIAOVIEN = %s", (gv,))
        id_gv = self.cursor.fetchone()
        if not id_gv:
            messagebox.showerror("Lỗi", "Không tìm thấy giáo viên này!")
            return
        id_gv = id_gv[0]

        self.cursor.execute("SELECT ID_MON FROM monhoc WHERE TENMON = %s", (mon,))
        id_mon = self.cursor.fetchone()
        if not id_mon:
            messagebox.showerror("Lỗi", "Không tìm thấy môn học này!")
            return
        id_mon = id_mon[0]

        try:
            self.cursor.execute(""" 
                UPDATE giangday 
                SET NGAYDAY = %s, TIETGD = %s, ID_GIAOVIEN = %s, ID_MON = %s
                WHERE ID_GIANGDAY = %s
            """, (formatted_date, tiet, id_gv, id_mon, self.selected_id_gd))
            self.db.commit()
            messagebox.showinfo("Thành công", "Cập nhật thành công!")
            self.load_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi MySQL: {err}")
        self.reload_data()

    def delete_entry(self):
        if not hasattr(self, 'selected_id_gd') or not self.selected_id_gd:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng trước khi xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giảng dạy này?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM giangday WHERE ID_GIANGDAY = %s", (self.selected_id_gd,))
                self.db.commit()
                messagebox.showinfo("Thành công", "Xóa thành công")
                self.reload_data()
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {err}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khác: {e}")

    def select_entry(self, event=None):
        selected_item = self.canvas.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0], "values")

        if len(item) != 5:
            return

        try:
            ngay = datetime.strptime(item[1], "%Y-%m-%d")
            self.cal.set_date(ngay)
        except ValueError:
            messagebox.showerror("Lỗi", f"Ngày không hợp lệ: {item[1]}")
            return

        self.tiet_entry.delete(0, tk.END)
        self.tiet_entry.insert(0, item[2])

        self.gv_entry.config(state="normal")
        self.gv_entry.delete(0, tk.END)
        self.gv_entry.insert(0, item[3])
        self.gv_entry.config(state="readonly")

        self.mon_combobox.set(item[4])

        try:
            self.cursor.execute("""
                SELECT ID_GIANGDAY FROM giangday
                WHERE NGAYDAY = %s AND TIETGD = %s
                AND ID_GIAOVIEN = (SELECT ID_GIAOVIEN FROM giaovien WHERE TENGIAOVIEN = %s)
                AND ID_MON = (SELECT ID_MON FROM monhoc WHERE TENMON = %s)
            """, (item[1], item[2], item[3], item[4]))

            result = self.cursor.fetchall()

            if result:
                self.selected_id_gd = result[0][0]
            else:
                self.selected_id_gd = None
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi MySQL: {err}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khác: {e}")


