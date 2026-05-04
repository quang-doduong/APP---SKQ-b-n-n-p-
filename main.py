import customtkinter as ctk
import tkintermapview
import threading
import os
from tkinter import messagebox
from PIL import Image
import logic_module

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_A = os.path.join(BASE_DIR, "A.png")
PATH_C = os.path.join(BASE_DIR, "C.png")

# Sử dụng Segoe UI để ổn định Telex/VNI
FONT_V = ("Segoe UI", 15)

class TaxiApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("App Đặt Xe Thông Minh")
        self.geometry("1200x800")
        self.latest_res = None

        # Tiền tải ảnh vào bộ nhớ để tránh lag khi mở popup
        self.img_c_data = None
        if os.path.exists(PATH_C):
            self.img_c_data = ctk.CTkImage(Image.open(PATH_C), size=(350, 225))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL TRÁI ---
        self.left_frame = ctk.CTkFrame(self, width=380, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_frame.grid_propagate(False)

        if os.path.exists(PATH_A):
            img_a = ctk.CTkImage(Image.open(PATH_A), size=(380, 160))
            ctk.CTkLabel(self.left_frame, text="", image=img_a).pack(fill="x", pady=(0, 20))

        # Nhập liệu - Fix trễ nhịp tiếng Việt triệt để
        self.entry_don = ctk.CTkEntry(self.left_frame, placeholder_text="📍 Điểm đón...", font=FONT_V, height=45)
        self.entry_don.pack(fill="x", padx=25, pady=10)
        self.entry_don._entry.config(font=FONT_V)
        self.entry_don.bind("<KeyRelease>", self.reset_button) # Reset nút khi sửa text

        self.entry_den = ctk.CTkEntry(self.left_frame, placeholder_text="🏁 Điểm đến...", font=FONT_V, height=45)
        self.entry_den.pack(fill="x", padx=25, pady=10)
        self.entry_den._entry.config(font=FONT_V)
        self.entry_den.bind("<KeyRelease>", self.reset_button) # Reset nút khi sửa text

        # Emojis khu vực
        self.xe_emoji_lbl = ctk.CTkLabel(self.left_frame, text="🚗", font=("Segoe UI", 80))
        self.xe_emoji_lbl.pack(pady=10)

        self.combo_xe = ctk.CTkComboBox(self.left_frame, values=["1 - Xe hai bánh", "2 - Xe taxi 4 chỗ", "3 - Xe taxi 7 chỗ"],
                                        font=FONT_V, command=self.update_xe_emoji, height=40)
        self.combo_xe.pack(fill="x", padx=25, pady=5)
        self.combo_xe.set("2 - Xe taxi 4 chỗ")

        self.time_emoji_lbl = ctk.CTkLabel(self.left_frame, text="🕒", font=("Segoe UI", 40))
        self.time_emoji_lbl.pack(pady=(15, 0))

        self.combo_doi = ctk.CTkComboBox(self.left_frame, values=["1 - Đợi lâu", "2 - Bình thường", "3 - Cần gấp"],
                                         font=FONT_V, command=self.update_time_emoji, height=40)
        self.combo_doi.pack(fill="x", padx=25, pady=5)
        self.combo_doi.set("2 - Bình thường")

        # NÚT ĐA NĂNG: Khởi tạo mặc định là nút Tìm chuyến
        self.btn_main = ctk.CTkButton(self.left_frame, text="🔍 TÌM CHUYẾN", font=("Segoe UI", 16, "bold"), height=55, command=self.start_calc)
        self.btn_main.pack(fill="x", padx=25, pady=30)

        # --- PANEL PHẢI (MAP) ---
        self.map_widget = tkintermapview.TkinterMapView(self, corner_radius=15)
        self.map_widget.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.map_widget.set_position(10.7626, 106.6601)
        self.map_widget.set_zoom(13)
        self.path_obj = None

    def update_xe_emoji(self, val):
        mapping = {"1": "      🏍️", "2": "🚗", "3": "🚙"}
        self.xe_emoji_lbl.configure(text=mapping.get(val[0], "🚗"))
        self.reset_button()

    def update_time_emoji(self, val):
        mapping = {"1": "☕", "2": "🕒", "3": "⚡"}
        self.time_emoji_lbl.configure(text=mapping.get(val[0], "🕒"))
        self.reset_button()

    def reset_button(self, event=None):
        # Hàm trả nút về trạng thái TÌM CHUYẾN khi có dữ liệu đầu vào bị thay đổi
        self.btn_main.configure(state="normal", text="🔍 TÌM CHUYẾN", fg_color=["#3a7ebf", "#1f538d"], command=self.start_calc)

    def start_calc(self):
        self.btn_main.configure(state="disabled", text="Đang tính...")
        threading.Thread(target=self.work, daemon=True).start()

    def work(self):
        try:
            xe = int(self.combo_xe.get()[0])
            doi = int(self.combo_doi.get()[0])
            res = logic_module.calculate_trip(self.entry_don.get(), self.entry_den.get(), xe, doi)
            self.after(0, self.done, res)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Lỗi", str(e)))
            self.after(0, lambda: self.btn_main.configure(state="normal", text="🔍 TÌM CHUYẾN"))

    def done(self, res):
        self.latest_res = res
        t, km, x, p, loc_a, loc_b, coords, mid = res
        self.map_widget.set_position(mid[0], mid[1])
        if self.path_obj: self.path_obj.delete()
        self.map_widget.set_marker(loc_a[0], loc_a[1], text="Đón")
        self.map_widget.set_marker(loc_b[0], loc_b[1], text="Đến")
        self.path_obj = self.map_widget.set_path(coords, width=6)
        
        # ĐỔI NÚT thành XÁC NHẬN CHUYẾN với lệnh confirm
        self.btn_main.configure(state="normal", text="✅ XÁC NHẬN CHUYẾN", fg_color="#2FA572", command=self.confirm)

    def confirm(self):
        if not self.latest_res: return
        t, km, x, p, loc_a, loc_b, coords, mid = self.latest_res
        
        pop = ctk.CTkToplevel(self)
        pop.title("Hóa đơn")
        pop.geometry("500x620")
        pop.attributes("-topmost", True)
        pop.grab_set()

        # Hiện ảnh C.png đã tải sẵn
        if self.img_c_data:
            ctk.CTkLabel(pop, image=self.img_c_data, text="").pack(pady=20)

        ctk.CTkLabel(pop, text="ĐẶT XE THÀNH CÔNG!", font=("Segoe UI", 22, "bold"), text_color="#2FA572").pack()
        
        box = ctk.CTkFrame(pop, fg_color="#f5f5f5")
        box.pack(fill="x", padx=40, pady=15)

        data = [("🕒 Giờ giấc:", t), ("📏 Quãng đường:", f"{km:.2f} km"), 
                ("📈 Hệ số nhân:", f"{x:.2f}x"), ("💰 TỔNG CƯỚC:", f"{p:,.0f} VND")]

        for lb, vl in data:
            f = ctk.CTkFrame(box, fg_color="transparent")
            f.pack(fill="x", padx=15, pady=6)
            ctk.CTkLabel(f, text=lb, font=("Segoe UI", 14), text_color="black").pack(side="left")
            ctk.CTkLabel(f, text=vl, font=("Segoe UI", 14, "bold"), text_color="#1f6aa5").pack(side="right")
        
        # Sau khi hoàn thành hóa đơn, ta reset nút về lại tìm chuyến để người dùng có thể dùng tiếp
        self.reset_button()

        ctk.CTkButton(pop, text="ĐÓNG", font=("Segoe UI", 14, "bold"), height=45, command=pop.destroy).pack(pady=20)

if __name__ == "__main__":
    TaxiApp().mainloop()