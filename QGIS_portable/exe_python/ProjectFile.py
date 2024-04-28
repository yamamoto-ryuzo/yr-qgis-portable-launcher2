import set_drive

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

def list_current_directory_contents():
    try:
        # カレントフォルダのファイルとフォルダのリストを取得
        contents = os.listdir()
        return "\n".join(contents)
    except PermissionError:
        return "カレントフォルダへのアクセス権限がありません。"
    except Exception as e:
        return "エラーが発生しました: {}".format(e)

def show_directory_contents():
    # 新しいウィンドウを作成
    window = tk.Tk()
    window.title("フォルダの内容")

    # スクロール可能なテキストボックスを作成
    text_area = scrolledtext.ScrolledText(window, width=40, height=10)
    text_area.pack(expand=True, fill="both")

    # カレントフォルダの内容をテキストボックスに表示
    directory_contents = list_current_directory_contents()
    text_area.insert(tk.END, directory_contents)

    # ウィンドウを表示
    window.mainloop()

# exe.config にQGISの実行フォルダの存在するフォルダを指定  
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
        with open(file_name+".config", "r", encoding="utf-8") as f:
            lines = f.readlines()
            qgis_project_file = None
            qgisconfig_folder = None
            for line in lines:
                # コメント行を無視する
                if line.startswith("#"):
                    continue
                if line.startswith("ProjectFile"):
                    # プロジェクトファイルのパスを取得
                    qgis_project_file = line.split("=")[1].strip()
                elif line.startswith("qgisconfig_folder"):
                    # QGIS 設定フォルダーのパスを取得
                    qgisconfig_folder = line.split("=")[1].strip()
            return qgis_project_file, qgisconfig_folder
    except Exception as e:
        print("設定ファイルの読み込み中にエラーが発生しました:", e)
        return None

def main():
    set_drive.change_drive()

    # 実行ファイルのパスを取得
    exe_path = sys.executable
    # messagebox.showerror("実行ファイル", exe_path)

    # ファイル名を取得し、拡張子を除去
    file_name = os.path.splitext(os.path.basename(exe_path))[0]

    # QGISのインストールフォルダを設定ファイルから読み込む
    qgis_install_dir = read_qgis_install_dir_from_config()
    if qgis_install_dir is None:
        error_message = "QGISのインストールフォルダが【exe.config】から読み込めませんでした。"
        # messagebox.showerror("エラー", error_message)
        return
    
    # QGISのプロジェクトファイルを設定ファイルから読み込む
    qgis_project_file, qgisconfig_folder = read_qgis_project_file_from_config(file_name)
    
    # カレントフォルダをQGISのインストールフォルダに設定
    os.chdir(qgis_install_dir)

    # 予定のユーザープロファイルにportableフォルダーが存在しない場合は標準のqgisconfigを複写する
    # 実行で使いたいportableフォルダのパス
    # 環境変数を含むことを前提とする
    # 環境変数 %APPDATA%を含むフォルダのパス
    # 環境変数を展開して実際のパスに変換する
    portable_profile_path = os.path.expandvars(qgisconfig_folder)
    # messagebox.showerror("実行・ポータブルprofilesフォルダ", portable_profile_path)  

    source_path = os.path.abspath('./qgisconfig')
    # messagebox.showerror("配布用・ポータブルprofilesフォルダ", source_path)        
    # ポータブルプロファイルが存在しない場合にコピーする
    if not os.path.exists(os.path.join(portable_profile_path,'profiles','portable')):
        # 上書き許可
        shutil.copytree(source_path, portable_profile_path, dirs_exist_ok=True)
        # messagebox.showerror("profilesフォルダを複写しました", portable_profile_path)

    ########################################
    # ポータブル版のBATをpythonに修正した起動 #
    ########################################
    # 現在の作業フォルダを取得
    DRV_LTR = os.getcwd()
    # messagebox.showerror("現在の作業フォルダのパス", DRV_LTR)  
    # QGISのインストールパスを設定
    OSGEO4W_ROOT = os.path.join(DRV_LTR, 'qgis')
    # messagebox.showerror("QGISフォルダのパス", OSGEO4W_ROOT) 
    # システムパスにQGIS関連のフォルダを追加
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps', 'qgis-ltr', 'bin')
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps')
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'bin')
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps', 'grass')
    # コマンドライン引数をチェックしてQGISを起動
    # messagebox.showerror("プロジェクトファイルのパス", qgis_project_file)  
    # messagebox.showerror("profilesフォルダ", portable_profile_path)  

    # 9.6.1. コマンドラインと環境変数
    # https://docs.qgis.org/3.34/ja/docs/user_manual/introduction/qgis_configuration.html#command-line-and-environment-variables  
    # 標準のプロファイルは「portable」   
    if qgis_project_file is None:
        # 引数がない場合は新しい空のプロジェクトでQGISを起動
        subprocess.Popen([os.path.join(OSGEO4W_ROOT, 'bin', 'qgis-ltr.bat'), '--profiles-path', portable_profile_path , '--profile', 'portable'])
    else:
        # 引数がある場合は指定されたプロジェクトファイルを開く
        subprocess.Popen([os.path.join(OSGEO4W_ROOT, 'bin', 'qgis-ltr.bat'), '--profiles-path', portable_profile_path , '--profile', 'portable' ,'--project', qgis_project_file])

if __name__ == "__main__":
    main()