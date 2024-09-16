import tkinter as tk
from tkinter import messagebox
import configparser
import sys
import os
import json

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ログインフォーム")
        self.center_window(300, 150)

        self.login_attempts = 0
        self.max_attempts = 10
        self.logged_in_user = None
        self.user_role = None

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
        
        with open('auth.config', 'r') as config_file:
            config = json.load(config_file)
        
        users = config.get('users', [])
        valid_user = False
        for user in users:
            if user['username'] == entered_username and user['password'] == entered_password:
                messagebox.showinfo("ログイン成功", f"ようこそ、{entered_username}さん!\n あなたの権限は {user['userrole']}です。")
                self.logged_in_user = entered_username
                self.user_role = user['userrole']
                valid_user = True
                self.master.quit()
                break
        
        if not valid_user:
            self.login_attempts += 1
            remaining_attempts = self.max_attempts - self.login_attempts
            if remaining_attempts > 0:
                messagebox.showerror("ログイン失敗", f"ユーザー名またはパスワードが無効です。\n残り試行回数: {remaining_attempts}")
                self.clear_entries()
            else:
                messagebox.showerror("ログイン失敗", "試行回数の上限に達しました。プログラムを終了します。")
                self.master.quit()
                sys.exit()

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()

    def get_logged_in_user(self):
        return self.logged_in_user

    def get_user_role(self):
        return self.user_role

def run_login():
    if not os.path.exists('auth.config'):
        return "free", "Administrator"  # ファイルが存在しない場合のデフォルトユーザー名と役割
    
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
    return app.get_logged_in_user(), app.get_user_role()

# メイン処理
if __name__ == "__main__":
    logged_in_user, user_role = run_login()
    if logged_in_user:
        print(f"ログインに成功しました。ユーザー名: {logged_in_user}, 権限は {user_role}です。")
    else:
        print("ログインに失敗しました。")