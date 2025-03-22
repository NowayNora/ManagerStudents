import tkinter as tk
from tkinter import messagebox, Canvas, Scrollbar, Frame
import mysql.connector
from datetime import datetime, timedelta

# Chuyển đổi thứ sang tiếng Việt
WEEKDAYS_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

class LichHoc:
    def __init__(self, parent, db, auth_info):
        self.parent = parent
        self.db = db
        self.cursor = db.cursor()
        self.auth_info = auth_info
        
        self.current_week_start = datetime.today() - timedelta(days=datetime.today().weekday())
        self.schedule_data = {}
        self.times_of_day = ["Sáng", "Chiều", "Tối"]
        
        self.parent.configure(bg="white")
        header_frame = tk.Frame(self.parent, bg="white")
        header_frame.pack(pady=10)

        self.week_label = tk.Label(header_frame, font=("Arial", 14, "bold"), bg="white", fg="#007acc")
        self.week_label.pack(side=tk.LEFT, padx=10)
        
        prev_button = tk.Button(header_frame, text="← Tuần trước", font=("Arial", 12), command=self.prev_week)
        prev_button.pack(side=tk.LEFT, padx=5)
        
        today_button = tk.Button(header_frame, text="Hôm nay", font=("Arial", 12), command=self.go_to_today)
        today_button.pack(side=tk.LEFT, padx=5)
        
        next_button = tk.Button(header_frame, text="Tuần tiếp theo →", font=("Arial", 12), command=self.next_week)
        next_button.pack(side=tk.LEFT, padx=5)
        
        self.canvas = Canvas(self.parent, bg="#f0f0f0")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = Scrollbar(self.parent, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.schedule_frame = Frame(self.canvas, bg="#f0f0f0")
        self.canvas.create_window((0, 0), window=self.schedule_frame, anchor="nw")
        
        self.schedule_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.update_schedule()
    
    def update_schedule(self):
        self.schedule_data.clear()
        start_date = self.current_week_start
        end_date = start_date + timedelta(days=6)
        self.week_label.config(text=f"Lịch học: {start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}")
        self.load_data_from_db(start_date, end_date)
        self.create_schedule_grid()
    
    def load_data_from_db(self, start_date, end_date):
        student_id = self.auth_info[2]
        try:
            query = """
                SELECT g.NGAYDAY, g.TIETGD, m.TENMON, gv.TENGIAOVIEN
                FROM giangday g
                JOIN monhoc m ON g.ID_MON = m.ID_MON
                JOIN giaovien gv ON g.ID_GIAOVIEN = gv.ID_GIAOVIEN
                JOIN dangky d ON d.ID_MON = g.ID_MON
                WHERE d.ID_SINHVIEN = %s AND g.NGAYDAY BETWEEN %s AND %s
                ORDER BY g.NGAYDAY, g.TIETGD
            """
            self.cursor.execute(query, (student_id, start_date, end_date))
            rows = self.cursor.fetchall()

            for r in rows:
                ngayday, tietgd, tenmon, tengv = r
                weekday_vi = WEEKDAYS_VI[ngayday.weekday()]
                day_str = f"{weekday_vi}, {ngayday.strftime('%d/%m/%Y')}"
                ca = self.parse_ca(tietgd)
                if day_str not in self.schedule_data:
                    self.schedule_data[day_str] = {"Sáng": [], "Chiều": [], "Tối": []}
                self.schedule_data[day_str][ca].append({"tenmon": tenmon, "tengv": tengv, "tiet": tietgd})
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {err}")
    
    def parse_ca(self, tietgd_str):
        first_tiet = int(tietgd_str.split('-')[0])
        if first_tiet <= 4:
            return "Sáng"
        elif first_tiet <= 9:
            return "Chiều"
        else:
            return "Tối"
    
    def create_schedule_grid(self):
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        days = [(self.current_week_start + timedelta(days=i)) for i in range(7)]
        days_str = [f"{WEEKDAYS_VI[d.weekday()]}, {d.strftime('%d/%m/%Y')}" for d in days]
        
        for col_index, day_str in enumerate(days_str, start=1):
            tk.Label(self.schedule_frame, text=day_str, font=("Arial", 12, "bold"), bg="#e1ecf4", width=16, height=2, relief=tk.RIDGE).grid(row=0, column=col_index)
        
        for row_index, ca in enumerate(self.times_of_day, start=1):
            tk.Label(self.schedule_frame, text=ca, font=("Arial", 12, "bold"), bg="#e1ecf4", width=12, height=2, relief=tk.RIDGE).grid(row=row_index, column=0)
            for col_index, day_str in enumerate(days_str, start=1):
                cell_frame = tk.Frame(self.schedule_frame, bg="white", bd=2, relief=tk.RIDGE, width=200, height=80)
                cell_frame.grid(row=row_index, column=col_index, sticky="nsew", padx=2, pady=2)
                buoi_list = self.schedule_data.get(day_str, {}).get(ca, [])
                if buoi_list:
                    for item in buoi_list:
                        lbl = tk.Label(cell_frame, text=f"{item['tenmon']}\nTiết {item['tiet']} | GV: {item['tengv']}", bg="#3498db", fg="white", wraplength=180, font=("Arial", 10, "bold"))
                        lbl.pack(expand=True, fill=tk.BOTH)
                else:
                    tk.Label(cell_frame, text="-", bg="white", font=("Arial", 10, "bold")).pack(expand=True, fill=tk.BOTH)
    
    def prev_week(self):
        self.current_week_start -= timedelta(days=7)
        self.update_schedule()
    
    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.update_schedule()
    
    def go_to_today(self):
        self.current_week_start = datetime.today() - timedelta(days=datetime.today().weekday())
        self.update_schedule()