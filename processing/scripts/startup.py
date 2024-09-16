# このpythonが動作するタイミングは
# QGISが起動を開始し、基本的な初期化が完了した後に実行されます
# ユーザーインターフェースが表示される前に実行されます
# QGISのフルAPIとPythonへのアクセスが可能な状態で実行されま
# QGISは起動時にそのファイルを自動的に検出して実行します

from qgis.core import QgsProject, QgsEditorWidgetSetup
from qgis.utils import iface
import os

def on_project_open():
    # プロジェクトが開かれた後に実行したいコード
    set_all_layers_readonly()
    pass

def set_all_layers_readonly():
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    
    success_count = 0
    error_count = 0

    for layer in layers:
        if isinstance(layer, QgsVectorLayer):
            try:
                # レイヤーを読み取り専用に設定
                layer.setReadOnly(True)
                
                # 編集を無効化（全フィールドに適用）
                edit_form_config = layer.editFormConfig()
                for field_index in range(layer.fields().count()):
                    edit_form_config.setReadOnly(field_index, True)
                layer.setEditFormConfig(edit_form_config)
                
                success_count += 1
                print(f"{layer.name()} を読み取り専用に設定しました")
            except Exception as e:
                error_count += 1
                print(f"{layer.name()} の設定中にエラーが発生しました: {str(e)}")
        else:
            print(f"{layer.name()} はベクターレイヤーではないためスキップします")

    # 結果をメッセージバーに表示
    message = f"{success_count}個のレイヤーを読み取り専用に設定しました。"
    if error_count > 0:
        message += f" {error_count}個のレイヤーでエラーが発生しました。"
    
    iface.messageBar().pushMessage("情報", message, level=Qgis.Info, duration=5)

# 関数を実行する場合は以下のように呼び出します
# set_all_layers_readonly()

#######################メイン########################
# プロジェクト読み込み後に実行するpythonはこちらで実行 #
####################################################
iface.messageBar().pushMessage("情報", 'startup.pyを実行開始しました。', level=Qgis.Info, duration=5)
# QgsProject.instance().readProject シグナルを使用して、プロジェクトが読み込まれた後にスクリプトを実行
QgsProject.instance().readProject.connect(on_project_open)
print("startup.py が読み込まれました。プロジェクトが開かれるのを待機しています。")