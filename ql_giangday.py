import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector
from datetime import datetime, timedelta
from tkinter import Canvas
class QuanLyGiangDay:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.current_week_start = datetime.today() - timedelta(days=datetime.today().weekday())

        # Để vẽ lịch, ta sẽ cần một Canvas thay vì Treeview
        self.canvas = None
        self.scrollbar_y = None
        self.schedule_data = {}
        self.cell_mapping = {}
        self.selected_id_gd = None
        self.create_ui()

    def create_ui(self):
        top_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)  # Trên cùng, giãn ngang

    # Tiêu đề
        tk.Label(top_frame, text="Quản Lý Giảng Dạy", font=("Arial", 16, "bold"),
             fg="white", bg="blue").pack(pady=10, fill=tk.X)

    # Khung tìm kiếm
        search_frame = tk.Frame(top_frame, bg="lightgray")
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        tk.Label(search_frame, text="Tìm kiếm: ").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Tìm", command=self.load_schedule).pack(side=tk.LEFT, padx=5)

    # Khung lọc
        filter_frame = tk.Frame(top_frame, bg="lightgray")
        filter_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        # tk.Label(filter_frame, text="Lọc theo môn học:", bg="lightgray").pack(side=tk.LEFT, padx=5)
        self.filter_mon_combobox = ttk.Combobox(filter_frame)
        # self.filter_mon_combobox.pack(side=tk.LEFT, padx=5)
        # tk.Button(filter_frame, text="Lọc", command=self.filter_data).pack(side=tk.LEFT, padx=5)


    # ========== 2. MIDDLE FRAME (chứa lịch) ==========
        middle_frame = tk.Frame(self.parent, bg="white")
        middle_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)  
    # Ở đây ta cho phép frame này giãn (expand) và lấp đầy (fill) không gian trống

    # Tạo frame để chứa Canvas + Scrollbar
        self.table_frame = tk.Frame(middle_frame, bg="white")
        self.table_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    # Canvas hiển thị lịch
        self.canvas = tk.Canvas(self.table_frame, bg="white", width=1800, height=400)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
    # Bind sự kiện click cho canvas (để chọn ô lịch)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # Scrollbar dọc
        self.scrollbar_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    # Scrollbar ngang (có thể để dưới cùng table_frame hoặc middle_frame, tùy ý)
        self.scrollbar_x = ttk.Scrollbar(middle_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

    # Gắn scrollbar cho canvas
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.canvas.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
    # ========== 3. BOTTOM FRAME ==========
        bottom_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        bottom_frame.pack(side=tk.TOP, fill=tk.X)

    # Nhãn hiển thị tuần
        self.week_label = tk.Label(bottom_frame, text="", font=("Arial", 12, "bold"), bg="lightgray")
        self.week_label.pack(side=tk.LEFT, padx=5)

    # Nút chuyển tuần
        nav_frame = tk.Frame(bottom_frame, bg="lightgray")
        nav_frame.pack(side=tk.LEFT, padx=10)
        tk.Button(nav_frame, text="<< Tuần trước", command=self.prev_week).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Tuần sau >>", command=self.next_week).pack(side=tk.LEFT, padx=5)

    # Frame chứa form nhập liệu (ngày, tiết, GV, môn)
        form_frame = tk.Frame(bottom_frame, bg="lightgray", padx=10, pady=10)
        form_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(form_frame, text="Ngày Dạy:", bg="lightgray").grid(row=0, column=0, padx=5, pady=5)
        self.cal = DateEntry(form_frame, width=12, background='darkblue',
                         foreground='white', borderwidth=2)
        self.cal.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Tiết Giảng Dạy:", bg="lightgray").grid(row=0, column=2, padx=5, pady=5)
        self.tiet_entry = tk.Entry(form_frame)
        self.tiet_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Giáo Viên:", bg="lightgray").grid(row=1, column=0, padx=5, pady=5)
        self.gv_entry = ttk.Entry(form_frame)
        self.gv_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Môn Học:", bg="lightgray").grid(row=1, column=2, padx=5, pady=5)
        self.mon_combobox = ttk.Combobox(form_frame)
        self.mon_combobox.grid(row=1, column=3, padx=5, pady=5)

        # Nút thêm, sửa, xóa
        button_frame = tk.Frame(self.parent, bg="white")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Thêm", bg="green", fg="black", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sửa", bg="orange", fg="black", command=self.update_entry).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Xóa", bg="red", fg="black", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        # Nút tải lại
        tk.Button(button_frame, text="Tải lại", bg="blue", fg="white", 
                  command=self.reload_data).pack(side=tk.LEFT, padx=5)

        # # Khung lọc dữ liệu
        # filter_frame = tk.Frame(self.parent, bg="lightgray", padx=10, pady=10)
        # filter_frame.pack(pady=5, fill=tk.X)

        # tk.Label(filter_frame, text="Lọc theo môn học:", bg="lightgray").grid(row=0, column=2, padx=5, pady=5)
        # self.filter_mon_combobox = ttk.Combobox(filter_frame)
        # self.filter_mon_combobox.grid(row=0, column=3, padx=5, pady=5)
        # tk.Button(filter_frame, text="Lọc", command=self.filter_data).grid(row=0, column=5, padx=9, pady=9)

        # Tải dữ liệu ban đầu
        # self.load_data()
        self.load_combobox_data()
        self.update_table_headers()
        self.load_teachers()
        self.load_schedule()

        # Sự kiện chọn môn học -> Tự động hiện giáo viên
        self.mon_combobox.bind("<<ComboboxSelected>>", self.update_teacher_entry)

    def filter_data(self):
        """Lọc dữ liệu theo môn học"""
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
        """Hiển thị dữ liệu đã lọc (theo môn) trên Canvas, theo kiểu sáng/chiều/tối"""
        # Xác định tuần hiện tại
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
        # Vẽ lại Canvas
        self.draw_schedule_on_canvas(schedule_data)

    def update_table_headers(self):
        """Cập nhật nhãn hiển thị tuần (không còn Treeview columns)"""
        week_dates = [(self.current_week_start + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
        self.week_label.config(text=f"Lịch tuần: {week_dates[0]} - {week_dates[-1]}")

    def load_schedule(self):
        """Lấy dữ liệu từ DB, nhóm theo sáng/chiều/tối, rồi vẽ lên Canvas"""
        week_dates = [(self.current_week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        search_text = self.search_entry.get().strip().lower()

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
            if search_text:
                query += " AND (LOWER(giaovien.TENGIAOVIEN) LIKE %s OR LOWER(monhoc.TENMON) LIKE %s)"
                params += (f"%{search_text}%", f"%{search_text}%")

            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            print("Dữ liệu từ MySQL:", rows)
        except mysql.connector.Error as err:
            print(f"Lỗi truy vấn MySQL: {err}")
            return

        # Tạo cấu trúc dữ liệu cho lịch
        schedule_data = {date: {"Sáng": "", "Chiều": "", "Tối": ""} for date in week_dates}
        self.cell_mapping = {}
        for row in rows:
                rec_id,ngay, tiet, gv, mon = row
                if isinstance(ngay, datetime):
                    ngay_str = ngay.strftime("%Y-%m-%d")
                elif isinstance(ngay, (str)):
                    ngay_str = ngay
                else:
                    ngay_str = str(ngay)

            # Xử lý cột TIETGD, ví dụ "1-2" → lấy số tiết đầu tiên
                tiet_cleaned = tiet.replace(" ", "")
                tiet_str = tiet_cleaned.split('-')[0]
                try:
                    tiet_num = int(tiet_str)
                except ValueError:
                    print(f"Lỗi khi chuyển đổi TIETGD: {tiet}")
                    continue
        
            # Phân loại buổi học dựa vào số tiết
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
            # Sau khi thêm xong, sắp xếp record trong mỗi ô theo tiết tăng dần
        for k, records_list in self.cell_mapping.items():
            records_list.sort(key=lambda r: int(r["TIETGD"].split('-')[0]))
        print("Dữ liệu lịch giảng dạy để vẽ:", schedule_data)
        self.schedule_data = schedule_data
        self.draw_schedule_on_canvas(schedule_data)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_schedule_on_canvas(self, schedule_data):
        print("Dữ liệu lịch giảng dạy để vẽ:", schedule_data)
        self.canvas.delete("all")
    
    # Lấy kích thước canvas
        width = self.canvas.winfo_width() or 1800
        height = self.canvas.winfo_height() or 400

    # Vẽ nền gradient từ màu xanh nhạt (#a8dadc) đến trắng (#ffffff)
        start_color = (168, 218, 220)  # rgb của #a8dadc
        end_color = (255, 255, 255)
        for i in range(height):
            ratio = i / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, width, i, fill=color)

    # Các thông số giao diện
        sessions = ["Sáng", "Chiều", "Tối"]
        cell_width = 150
        cell_height = 100
        x_offset = 100  # Dành cho cột tiêu đề ngày
        y_offset = 40   # Dành cho hàng tiêu đề buổi
        font_title = ("Helvetica", 10, "bold")
        font_content = ("Helvetica", 9)

        inner_margin = 4

        font_title = ("Helvetica", 10, "bold")
        font_content = ("Helvetica", 9)
    # Danh sách ngày trong tuần (keys của schedule_data là dạng "YYYY-mm-dd")
        sorted_dates = sorted(schedule_data.keys())
    # Bản đồ chuyển weekday thành tên thứ tiếng Việt
        weekday_mapping = {
            0: "Thứ 2",
            1: "Thứ 3",
            2: "Thứ 4",
            3: "Thứ 5",
            4: "Thứ 6",
            5: "Thứ 7",
            6: "Chủ nhật"
        }

    # Vẽ tiêu đề cột: Hiển thị tên thứ và ngày (vd: "Thứ 2\n15/02")
        for i, day_str in enumerate(sorted_dates):
            dt = datetime.strptime(day_str, "%Y-%m-%d")
            day_label = dt.strftime("%d/%m")
            day_name = weekday_mapping.get(dt.weekday(), "")
            header_text = f"{day_name}\n{day_label}"
        # Vẽ bóng mờ cho header (offset 2 pixel)
            self.canvas.create_text(
                x_offset + i * cell_width + cell_width / 2 + 2,
                15 + 2,
                text=header_text,
                font=font_title,
                fill="gray",
                justify="center"
        )
        # Vẽ tiêu đề chính
            self.canvas.create_text(
                x_offset + i * cell_width + cell_width / 2,
                15,
                text=header_text,
                font=font_title,
                fill="darkblue",
                justify="center"
        )

    # Vẽ tiêu đề hàng (buổi)
        for j, session in enumerate(sessions):
        # Vẽ tên buổi với hiệu ứng bóng mờ
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
            # Tọa độ của ô
                x1 = x_offset + i * cell_width
                y1 = y_offset + j * cell_height
                x2 = x1 + cell_width
                y2 = y1 + cell_height
                cell_tag = f"cell_{day_str}_{session}"
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="darkred", width=2, tags=(cell_tag,))
            
            # Lấy danh sách các record của ô (day_str, session)
                records = self.cell_mapping.get((day_str, session), [])
                n_records = len(records)
                if n_records == 0:
                    continue
            
            # Giới hạn số record hiển thị
                max_records_display = 3
                display_count = min(n_records, max_records_display)
                sub_box_height = (cell_height - 2 * inner_margin) // display_count
            
            # Vẽ từng record
                for idx in range(display_count):
                    record = records[idx]
                    rec_x1 = x1 + inner_margin
                    rec_y1 = y1 + inner_margin + idx * sub_box_height
                    rec_x2 = x2 - inner_margin
                    rec_y2 = rec_y1 + sub_box_height - inner_margin
                    record_tag = f"record_{day_str}_{session}_{idx}"
                    self.canvas.create_rectangle(
                        rec_x1, rec_y1, rec_x2, rec_y2,
                        fill="#5cb85c",
                        outline="gray",
                        width=1,
                        tags=(cell_tag, record_tag)
                    )
                    text_line = f"Tiết {record['TIETGD']}: {record['TENGIAOVIEN']} - {record['TENMON']}"
                    self.canvas.create_text(
                        rec_x1 + 3, rec_y1 + 3,
                        text=text_line,
                        anchor="nw",
                        font=font_content,
                        fill="black",
                        width=(rec_x2 - rec_x1 - 6),
                        tags=(cell_tag, record_tag)
                    )
            
            # Nếu còn nhiều record hơn số hiển thị, vẽ ô "..." ở dưới cùng
                if n_records > max_records_display:
                    rec_x1 = x1 + inner_margin
                    rec_y1 = y1 + inner_margin + display_count * sub_box_height
                    rec_x2 = x2 - inner_margin
                    rec_y2 = y2 - inner_margin
                    ellipsis_tag = f"record_{day_str}_{session}_ellipsis"
                    self.canvas.create_rectangle(
                        rec_x1, rec_y1, rec_x2, rec_y2,
                        fill="#ffcc00",  # màu nền khác để nổi bật
                        outline="gray",
                        width=1,
                        tags=(cell_tag, ellipsis_tag)
                    )
                    self.canvas.create_text(
                        (rec_x1 + rec_x2) / 2, (rec_y1 + rec_y2) / 2,
                    text="...",
                    anchor="center",
                    font=font_content,
                    fill="black",
                    tags=(cell_tag, ellipsis_tag)
                    )
            
            print(f"{day_str} - {session}: {schedule_data[day_str][session]}")
        # Bind sự kiện click cho tag này
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
       

    def on_canvas_click(self, event):
        if not hasattr(self, "schedule_data"):
            messagebox.showerror("Lỗi", "Chưa có dữ liệu lịch, vui lòng tải dữ liệu.")
            return
        sorted_dates = sorted(self.schedule_data.keys())
    # Các thông số được sử dụng trong việc vẽ Canvas (nên lưu chúng làm thuộc tính nếu cần)
        x_offset = 100
        y_offset = 40
        cell_width = 150
        cell_height = 100
        sessions = ["Sáng", "Chiều", "Tối"]

    # Tọa độ click trên Canvas
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

    # Nếu click bên ngoài vùng lưới, bỏ qua
        if x < x_offset or y < y_offset:
            return

    # Tính chỉ số cột và hàng (dựa trên tọa độ)
        col = (x - x_offset) // cell_width
        row = (y - y_offset) // cell_height

    # Lấy danh sách ngày (theo thứ tự sắp xếp)
        sorted_dates = sorted(self.schedule_data.keys())  # Giả sử self.schedule_data đã được lưu khi load_schedule

        try:
            selected_date = sorted_dates[int(col)]
            selected_session = sessions[int(row)]
        except IndexError:
            return

        key = (selected_date, selected_session)
        records = self.cell_mapping.get(key, [])
        if not records:
            messagebox.showinfo("Thông báo", "Ô được chọn không có dữ liệu.")
            return

    # Nếu có nhiều bản ghi, chọn bản ghi đầu tiên (hoặc mở hộp thoại để người dùng chọn)
        # Lấy danh sách các item được click
        clicked_items = self.canvas.find_withtag("current")
        selected_record_tag = None
        if clicked_items:
            tags = self.canvas.gettags(clicked_items[0])
        # Tìm tag có định dạng "record_..."
            for tag in tags:
                if tag.startswith("record_"):
                    selected_record_tag = tag
                    break

    # Nếu tìm được tag chứa index, dùng nó; nếu không thì mặc định idx = 0
        if selected_record_tag:
            parts = selected_record_tag.split("_")
            if len(parts) >= 4:
                try:
                    idx = int(parts[3])
                except ValueError:
                    idx = 0
            else:
                idx = 0
        else:
            idx = 0

    # Đảm bảo idx không vượt quá số lượng record trong ô
        if idx < 0 or idx >= len(records):
            idx = 0

        record = records[idx]
        try:
            dt = datetime.strptime(record["NGAYDAY"], "%Y-%m-%d")
            self.cal.set_date(dt)
        except Exception as e:
            print("Lỗi chuyển đổi ngày:", e)
        self.tiet_entry.delete(0, tk.END)
        self.tiet_entry.insert(0, record["TIETGD"])
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

    # Hàm load_teachers() nếu bạn muốn lấy danh sách GV ở đâu đó
    def load_teachers(self):
        pass

    def load_combobox_data(self):
        """Tải danh sách môn học vào combobox"""
        self.cursor.execute("SELECT TENMON FROM monhoc")
        subjects = self.cursor.fetchall()
        self.mon_combobox["values"] = [row[0] for row in subjects]
        self.filter_mon_combobox["values"] = [row[0] for row in subjects]

    def update_teacher_entry(self, event=None):
        """Tự động hiển thị giáo viên khi chọn môn học"""
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

    def reload_data(self):
        """Tải lại dữ liệu và xóa thông tin nhập"""
        self.load_data()
        self.cal.set_date(datetime.today())
        self.tiet_entry.delete(0, tk.END)
        self.gv_entry.config(state="normal")
        self.gv_entry.delete(0, tk.END)
        self.gv_entry.config(state="readonly")
        self.mon_combobox.set("")
        self.selected_id_gd = None
    def load_data(self):
        try:
        # Tạo danh sách các ngày trong tuần hiện tại (dạng "YYYY-MM-DD")
            week_dates = [(self.current_week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        # Định nghĩa truy vấn với placeholder
            query = """
                SELECT giangday.ID_GIANGDAY, giangday.NGAYDAY, giangday.TIETGD, 
                    giaovien.TENGIAOVIEN, monhoc.TENMON
                FROM giangday
                JOIN giaovien ON giangday.ID_GIAOVIEN = giaovien.ID_GIAOVIEN
                JOIN monhoc ON giangday.ID_MON = monhoc.ID_MON
                WHERE NGAYDAY BETWEEN %s AND %s
            """
            params = (week_dates[0], week_dates[-1])
        
        # Thực hiện truy vấn
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            print("Dữ liệu lịch học:", rows)
        
            if not rows:
                messagebox.showinfo("Thông báo", "Không có dữ liệu lịch học.")
                return

        # Xóa nội dung cũ trên Canvas
            self.canvas.delete("all")
        
        # Tạo cấu trúc dữ liệu cho lịch (week_dates đã là các chuỗi)
            schedule_data = {date: {"Sáng": "", "Chiều": "", "Tối": ""} for date in week_dates}
        
            for row in rows:
                rec_id,ngay, tiet, gv, mon = row
            # Chuyển ngày thành chuỗi "YYYY-MM-DD"
                if isinstance(ngay, datetime):
                    ngay_str = ngay.strftime("%Y-%m-%d")
                else:
                    ngay_str = str(ngay)
            
            # Xử lý cột TIETGD, ví dụ "1-2" -> lấy số tiết đầu tiên để phân loại buổi,
            # nhưng dùng giá trị gốc để hiển thị.
                tiet_cleaned = tiet.replace(" ", "")
                tiet_str = tiet_cleaned.split('-')[0]
                try:
                    tiet_num = int(tiet_str)
                except ValueError:
                    print(f"Lỗi khi chuyển đổi TIETGD: {tiet}")
                    continue

                session = "Sáng" if 1 <= tiet_num <= 6 else ("Chiều" if 7 <= tiet_num <= 11 else "Tối")
                if ngay_str in schedule_data:
                # Hiển thị số tiết (tiet) kèm theo thông tin giáo viên và môn học
                    schedule_data[ngay_str][session] += f"Tiết {tiet}: {gv} - {mon}\n"
        
            print("Dữ liệu lịch giảng dạy để vẽ:", schedule_data)
            self.draw_schedule_on_canvas(schedule_data)

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi truy vấn dữ liệu: {err}")



    def add_entry(self):
        try:
            date_str = self.cal.get()
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            formatted_date = date_obj.strftime('%Y-%m-%d')

            tiet, gv, mon = self.tiet_entry.get(), self.gv_entry.get(), self.mon_combobox.get()

            if not all([formatted_date, tiet, gv, mon]):
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
                return

        # Lấy ID giáo viên
            self.cursor.execute("SELECT ID_GIAOVIEN FROM giaovien WHERE TENGIAOVIEN = %s", (gv,))
            gv_id = self.cursor.fetchone()
            if not gv_id:
                messagebox.showerror("Lỗi", "Giáo viên không tồn tại!")
                return

        # Lấy ID môn học
            self.cursor.execute("SELECT ID_MON FROM monhoc WHERE TENMON = %s", (mon,))
            mon_id = self.cursor.fetchone()
            if not mon_id:
                messagebox.showerror("Lỗi", "Môn học không tồn tại!")
                return

        # Thêm dữ liệu vào bảng giảng dạy
            self.cursor.execute("INSERT INTO giangday (NGAYDAY, TIETGD, ID_GIAOVIEN, ID_MON) VALUES (%s, %s, %s, %s)",
                            (formatted_date, tiet, gv_id[0], mon_id[0]))
            self.db.commit()

            messagebox.showinfo("Thành công", "Thêm lịch giảng dạy thành công!")

        # Cập nhật giao diện
            self.load_schedule()

        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm dữ liệu: {err}")


    def update_entry(self):
        """Cập nhật dữ liệu vào cơ sở dữ liệu"""
        if not hasattr(self, 'selected_id_gd') or not self.selected_id_gd:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng trước khi cập nhật!")
            return

        date_str = self.cal.get()
        date_obj = datetime.strptime(date_str, "%m/%d/%y")
        formatted_date_time = f"{date_obj.strftime('%Y-%m-%d')}"
        ngay, tiet, gv, mon = formatted_date_time, self.tiet_entry.get(), self.gv_entry.get(), self.mon_combobox.get()

        if not all([ngay, tiet, gv, mon]):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Lấy ID_GIAOVIEN và ID_MON
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
            """, (ngay, tiet, id_gv, id_mon, self.selected_id_gd))
            self.db.commit()
            messagebox.showinfo("Thành công", "Cập nhật thành công!")
            self.load_schedule()  # Refresh lại danh sách
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi MySQL: {err}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khác: {e}")

    def delete_entry(self):
        """Xóa dữ liệu khỏi cơ sở dữ liệu"""
        if not hasattr(self, 'selected_id_gd') or not self.selected_id_gd:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng trước khi xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giảng dạy này?")
        if confirm:
            try:
                self.cursor.execute("DELETE FROM giangday WHERE ID_GIANGDAY = %s", (self.selected_id_gd,))
                self.db.commit()
                messagebox.showinfo("Thành công", "Xóa thành công")
                self.load_schedule()  # Cập nhật lại danh sách hiển thị
            except mysql.connector.Error as err:
                messagebox.showerror("Lỗi", f"Lỗi khi xóa: {err}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khác: {e}")

    def select_entry(self, event=None):
        selected_item = self.canvas.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0], "values")
        
        if len(item) != 5:  # Kiểm tra nếu số cột không đúng
            return

        try:
            # Xử lý ngày (cột 1)
            ngay = datetime.strptime(item[1], "%Y-%m-%d")
            self.cal.set_date(ngay)
        except ValueError:
            messagebox.showerror("Lỗi", f"Ngày không hợp lệ: {item[1]}")
            return

        # Điền dữ liệu vào các trường nhập liệu
        self.tiet_entry.delete(0, tk.END)
        self.tiet_entry.insert(0, item[2])  # Tiết dạy

        self.gv_entry.config(state="normal")
        self.gv_entry.delete(0, tk.END)
        self.gv_entry.insert(0, item[3])  # Tên giáo viên
        self.gv_entry.config(state="readonly")

        self.mon_combobox.set(item[4])  # Môn học

        # Lưu ID_GIANGDAY cho mục đích sửa và xóa
        try:
            # Truy vấn ID_GIANGDAY từ cơ sở dữ liệu
            self.cursor.execute("""
                SELECT ID_GIANGDAY FROM giangday
                WHERE NGAYDAY = %s AND TIETGD = %s
                AND ID_GIAOVIEN = (SELECT ID_GIAOVIEN FROM giaovien WHERE TENGIAOVIEN = %s)
                AND ID_MON = (SELECT ID_MON FROM monhoc WHERE TENMON = %s)
            """, (item[1], item[2], item[3], item[4]))

            # Đảm bảo xử lý kết quả của truy vấn trước khi tiếp tục
            result = self.cursor.fetchall()

            if result:
                self.selected_id_gd = result[0][0]  # Lưu ID_GIANGDAY
            else:
                self.selected_id_gd = None
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Lỗi MySQL: {err}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khác: {e}")


