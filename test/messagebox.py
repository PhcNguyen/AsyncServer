import tkinter as tk
import tkinter.messagebox as messagebox

class CountdownDialog:
    def __init__(self, master, countdown):
        self.master = master
        self.countdown = countdown
        self.dialog = tk.Toplevel(master)
        self.dialog.title("Thông báo")
        self.label = tk.Label(self.dialog, text=f"Bạn có {self.countdown} giây để xác nhận.")
        self.label.pack(pady=20)
        self.update_countdown()

    def update_countdown(self):
        if self.countdown > 0:
            self.label.config(text=f"Bạn có {self.countdown} giây để xác nhận.")
            self.countdown -= 1
            self.master.after(1000, self.update_countdown)
        else:
            self.dialog.destroy()  # Đóng hộp thoại sau khi hết thời gian

# Sử dụng
root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính
CountdownDialog(root, 30)  # Khởi tạo hộp thoại với 30 giây
root.mainloop()
