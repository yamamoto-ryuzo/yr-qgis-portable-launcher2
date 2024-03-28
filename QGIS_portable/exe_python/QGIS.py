import os
import sys
import subprocess
import tkinter as tk
from tkinter import scrolledtext

def list_current_directory_contents():
    try:
        # カレントディレクトリのファイルとディレクトリのリストを取得
        contents = os.listdir()
        return "\n".join(contents)
    except PermissionError:
        return "カレントディレクトリへのアクセス権限がありません。"
    except Exception as e:
        return "エラーが発生しました: {}".format(e)

def show_directory_contents():
    # 新しいウィンドウを作成
    window = tk.Tk()
    window.title("ディレクトリの内容")

    # スクロール可能なテキストボックスを作成
    text_area = scrolledtext.ScrolledText(window, width=40, height=10)
    text_area.pack(expand=True, fill="both")

    # カレントディレクトリの内容をテキストボックスに表示
    directory_contents = list_current_directory_contents()
    text_area.insert(tk.END, directory_contents)

    # ウィンドウを表示
    window.mainloop()

def main():

    # 実行ファイルのパスを取得
    exe_path = sys.executable

    # ファイル名を取得し、拡張子を除去
    file_name = os.path.splitext(os.path.basename(exe_path))[0]

    # QGISのインストールディレクトリへ移動
    qgis_install_dir = "./QGIS3.34.4"
    os.chdir(qgis_install_dir)

    # カレントディレクトリの内容を新しいウィンドウで表示
    # show_directory_contents()

    # QGISをバックグラウンドで起動し、指定されたプロジェクトファイルを開く
    import subprocess
    project_file = "../ProjectFiles/"+file_name+".qgs"
    subprocess.Popen(["start", "", "/b", "qgis-ltr-grass.bat", project_file], shell=True)

if __name__ == "__main__":
    main()