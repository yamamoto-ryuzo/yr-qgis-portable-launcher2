import tkinter as tk
from tkinter import messagebox
import configparser
import sys
import os

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ログインフォーム")
        self.center_window(300, 150)

        self.login_attempts = 0
        self.max_attempts = 10
        self.logged_in_user = None

        tk.Label(self.master, text="ユーザー名:").pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()
        self.username_entry.bind('<Return>', self.focus_password)

        tk.Label(self.master, text="パスワード:").pack()
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()
        self.password_entry.bind('<Return>', self.focus_login_button)

        self.login_button = tk.Button(self.master, text="ログイン", command=self.validate_login)
        self.login_button.pack(pady=10)
        self.login_button.bind('<Return>', self.validate_login)

        self.username_entry.focus()

    def center_window(self, width, height):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def focus_password(self, event):
        self.password_entry.focus()

    def focus_login_button(self, event):
        self.login_button.focus()

    def validate_login(self, event=None):
        entered_username = self.username_entry.get()
        entered_password = self.password_entry.get()
        
        config = configparser.ConfigParser()
        config.read('auth.config')
        
        if 'credentials' in config:
            credentials = config['credentials']
            if entered_username in credentials and credentials[entered_username] == entered_password:
                messagebox.showinfo("ログイン成功", f"ようこそ、{entered_username}さん!")
                self.logged_in_user = entered_username
                self.master.quit()
            else:
                self.login_attempts += 1
                remaining_attempts = self.max_attempts - self.login_attempts
                if remaining_attempts > 0:
                    messagebox.showerror("ログイン失敗", f"ユーザー名またはパスワードが無効です。\n残り試行回数: {remaining_attempts}")
                    self.clear_entries()
                else:
                    messagebox.showerror("ログイン失敗", "試行回数の上限に達しました。プログラムを終了します。")
                    self.master.quit()
                    sys.exit()
        else:
            messagebox.showerror("設定エラー", "設定ファイルに認証情報セクションが見つかりません")
            self.clear_entries()

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()

    def get_logged_in_user(self):
        return self.logged_in_user

def run_login():
    if not os.path.exists('auth.config'):
        return "default_user"  # ファイルが存在しない場合のデフォルトユーザー名
    
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
    return app.get_logged_in_user()

# メイン処理
if __name__ == "__main__":
    logged_in_user = run_login()
    if logged_in_user:
        print(f"ログインに成功しました。ユーザー名: {logged_in_user}")
    else:
        print("ログインに失敗しました。")