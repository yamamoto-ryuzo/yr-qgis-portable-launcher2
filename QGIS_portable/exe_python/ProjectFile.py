import set_drive

import os
import sys
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

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

# exe.config にQGISの実行ディレクトリの存在するフォルダを指定  
# ./QGIS3.34.4
def read_qgis_install_dir_from_config():
    try:
        with open("exe.config", "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("QGIS_INSTALL_DIR"):
                    return line.split("=")[1].strip()
    except Exception as e:
        print("設定ファイルの読み込み中にエラーが発生しました:", e)
        return None

def read_qgis_project_file_from_config(file_name):
    try:
        with open(file_name+".config", "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("ProjectFile"):
                    qgis_project_file = line.split("=")[1].strip()
                elif line.startswith("qgisconfig_folder"):
                    qgisconfig_folder = line.split("=")[1].strip()
            return qgis_project_file, qgisconfig_folder
    except Exception as e:
        print("設定ファイルの読み込み中にエラーが発生しました:", e)
        return None


def main():

    set_drive.change_drive()

    # 実行ファイルのパスを取得
    exe_path = sys.executable

    # ファイル名を取得し、拡張子を除去
    file_name = os.path.splitext(os.path.basename(exe_path))[0]

    # QGISのインストールディレクトリを設定ファイルから読み込む
    qgis_install_dir = read_qgis_install_dir_from_config()
    if qgis_install_dir is None:
        error_message = "QGISのインストールディレクトリが【exe.config】から読み込めませんでした。"
        messagebox.showerror("エラー", error_message)
        return
    
    # QGISのプロジェクトファイルを設定ファイルから読み込む
    qgis_project_file, qgisconfig_folder = read_qgis_project_file_from_config(file_name)
    
    if qgis_project_file is None:
        error_message = "QGISのプロジェクトファイル【"+file_name+".config】が設定されていません。"
        messagebox.showerror("エラー", error_message)
        return
    
    # カレントディレクトリをQGISのインストールディレクトリに設定
    os.chdir(qgis_install_dir)

    # カレントディレクトリの内容を新しいウィンドウで表示
    # show_directory_contents()

    # QGISをバックグラウンドで起動し、指定されたプロジェクトファイルを開く
    # subprocess.Popen(["start", "", "/b", "qgis-ltr-grass.bat", qgis_project_file], shell=True)

    ########################################
    # ポータブル版のBATをpythonに修正した起動 #
    ########################################
    # 現在の作業ディレクトリを取得
    DRV_LTR = os.getcwd()
    # QGISのインストールパスを設定
    OSGEO4W_ROOT = os.path.join(DRV_LTR, 'qgis')
    # システムパスにQGIS関連のディレクトリを追加
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps', 'qgis-ltr', 'bin')
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps')
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'bin')
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps', 'grass')
    # コマンドライン引数をチェックしてQGISを起動
    if qgis_project_file  is None:
        # 引数がない場合は新しい空のプロジェクトでQGISを起動
        subprocess.Popen([os.path.join(OSGEO4W_ROOT, 'bin', 'qgis-ltr.bat'), '--profiles-path', qgisconfig_folder])
    else:
        # 引数がある場合は指定されたプロジェクトファイルを開く
        subprocess.Popen([os.path.join(OSGEO4W_ROOT, 'bin', 'qgis-ltr.bat'), '--profiles-path', qgisconfig_folder , '--project', qgis_project_file])








if __name__ == "__main__":
    main()