import set_drive

import os
import sys
import keyboard
import shutil
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

# グローバル変数の定義
# portable_profileを複写する場合は　profile = 1　にイベントで変更
profile = 0

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

# プロジェクトファイルの起動用コンフィグ読込設定
def read_qgis_project_file_from_config(file_name):
    try:
        with open(file_name+".config", "r", encoding="utf-8") as f:
            lines = f.readlines()
            qgis_project_file = None
            qgisconfig_folder = None
            # 仮想ドライブの標準設定は　Q:ドライブ　とする。
            VirtualDrive = "q:"
            # QGISの実行フォルダの上書き
            qgis_install_dir_ow = None

            for line in lines:
                # コメント行を無視する
                if line.startswith("#"):
                    continue
                if line.startswith("ProjectFile"):
                    # プロジェクトファイルのパスを取得
                    qgis_project_file = line.split("=")[1].strip()
                    # messagebox.showerror("プロジェクトファイルのパス情報", qgis_project_file)
                elif line.startswith("qgisconfig_folder"):
                    # QGIS 設定フォルダーのパスを取得
                    qgisconfig_folder = line.split("=")[1].strip()
                    # messagebox.showerror("QGIS 設定フォルダーのパス情報", qgisconfig_folder)
                # カスタム仮想ドライブの読込
                elif line.startswith("VirtualDrive"):
                    # 稼働ドライブを取得
                    VirtualDrive = line.split("=")[1].strip()
                    # messagebox.showerror("仮想ドライブの設定情報", VirtualDrive)
                elif line.startswith("qgis_install_dir_ow"):
                    # QGISの実行フォルダの上書き
                    qgis_install_dir_ow = line.split("=")[1].strip()
                    # messagebox.showerror("仮想ドライブの設定情報の上書き", qgis_install_dir_ow)
            return qgis_project_file, qgisconfig_folder ,VirtualDrive , qgis_install_dir_ow
    except Exception as e:
        print("設定ファイルの読み込み中にエラーが発生しました:", e)
        return None

# フォルダが存在するかどうかの確認
def check_folder_exists(folder_path):
    if os.path.exists(folder_path):
        if os.path.isdir(folder_path):
            return True
        else:
            # messagebox.showerror("エラー", f"'{folder_path}' は存在しますが、フォルダではありません。")
            return False
    else:
        # messagebox.showerror("エラー", f"フォルダ '{folder_path}' は存在しません。")
        return False

# 特定のキーが押されたイベントで実行
def on_key_press(event):
    # グローバル変数を使用するために宣言
    global profile  
    profile = 1


####################
#  MAINプログラム  #
###################
def main():
    # グローバル変数を使用するために宣言
    global profile  
    # "shift"キーが押されたときにon_key_press関数を呼び出す
    keyboard.on_press_key("shift", on_key_press)
    # "r"キーが押されたときにon_key_press関数を呼び出す
    keyboard.on_press_key("r", on_key_press)
    # "crtl"キーが押されたときにon_key_press関数を呼び出す
    keyboard.on_press_key("crtl", on_key_press)
    ############################
    #   設定ファイルの読み込み   #
    ############################
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
    qgis_project_file, qgisconfig_folder , VirtualDrive , qgis_install_dir_ow = read_qgis_project_file_from_config(file_name)
    if qgis_install_dir_ow != None:
        qgis_install_dir = qgis_install_dir_ow


    ############################
    #   仮想ドライブ環境の設定   #
    ############################
    # 一度仮想ドライブを削除
    subprocess.run(["subst", "/d" , VirtualDrive])
    # 現在の作業ディレクトリを VirtualDrive ドライブに指定
    # set_drive.change_drive() 
    # 現在のフォルダを取得する
    current_folder = os.getcwd()
    # messagebox.showerror("現在のフォルダを取得する", current_folder)
    # "/persistent:yes" オプションは、再起動後もドライブの割り当てを保持するためのものです
    subprocess.run(["subst",VirtualDrive, current_folder])
    # ドライブの設定をユーザーに通知する
    # messagebox.showerror("仮想ドライブの設定", VirtualDrive&"ライブを設定しました。")
    # カレントディレクトリを VirtualDriveドライブに変更します。
    os.chdir( VirtualDrive + "\\" )

    DRV_LTR = os.getcwd()  
    # messagebox.showerror("現在の作業フォルダのパス", DRV_LTR)  

    ################
    #   QGIS実行   #
    ################

    # カレントフォルダをQGISのインストールフォルダに設定
    os.chdir(qgis_install_dir)

    #############################
    # portableプロファイルを設定 #
    ############################
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
    # profile == 1(キーボード[r]が押されていれば)コピー
    if not os.path.exists(os.path.join(portable_profile_path, 'profiles', 'portable')) or (profile == 1):
        # 上書き許可
        shutil.copytree(source_path, portable_profile_path, dirs_exist_ok=True)
        # messagebox.showerror("profilesフォルダを複写しました", portable_profile_path)

    #####################
    # ポータブル版の起動 #
    ####################
    # 現在の作業フォルダを取得
    DRV_LTR = os.getcwd()
    # messagebox.showerror("現在の作業フォルダのパス", DRV_LTR)  
    # QGISのインストールパスを設定
    OSGEO4W_ROOT = os.path.join(DRV_LTR, 'qgis')
    # QGISのタイプとして最新版とLTRを自動判定
    folder_path = os.path.join(OSGEO4W_ROOT, 'apps', 'qgis-ltr')
    if check_folder_exists(folder_path):
        QGIS_Type='qgis-ltr'
    else:
        QGIS_Type='qgis'
    # messagebox.showerror("QGISフォルダのパス", OSGEO4W_ROOT) 
    # システムパスにQGIS関連のフォルダを追加
    os.environ['PATH'] += os.pathsep + os.path.join(OSGEO4W_ROOT, 'apps', QGIS_Type, 'bin')
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
        subprocess.Popen([os.path.join(OSGEO4W_ROOT, 'bin', QGIS_Type+'.bat'), '--profiles-path', portable_profile_path , '--profile', 'portable'])
    else:
        # 引数がある場合は指定されたプロジェクトファイルを開く
        subprocess.Popen([os.path.join(OSGEO4W_ROOT, 'bin', QGIS_Type+'.bat'), '--profiles-path', portable_profile_path , '--profile', 'portable' ,'--project', qgis_project_file])

if __name__ == "__main__":
    main()