# このpythonが動作するタイミングは
# QGISが起動を開始し、基本的な初期化が完了した後に実行されます
# ユーザーインターフェースが表示される前に実行されます
# QGISのフルAPIとPythonへのアクセスが可能な状態で実行されま
# QGISは起動時にそのファイルを自動的に検出して実行します

from qgis.core import QgsProject, QgsEditorWidgetSetup
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsExpressionContextUtils
import os

def on_project_read():
    # プロジェクトファイルの読み込み開始
    pass

def on_render_complete():
    # マップキャンバスの描画完了
    # プロジェクトが本当に読み込まれていない場合があるため、時間稼ぎが必要であり以下のメッセージ表示は削除しないこと
    # QGISの変数はすべて小文字であることに注意
    UserRole_value = QgsExpressionContextUtils.globalScope().variable('userrole')
    QMessageBox.information(None, "startup.py", "プロジェクトの読み込みが完了しました。\n初期設定を開始します。")
    print (f"変数　UserRole：{UserRole_value}")
    if UserRole_value == 'Viewer':
        set_all_layers_readonly()
    #QMessageBox.information(None, "startup.py", "プロジェクトの読み込みと初期化が完全に終了しました。")
    print("プロジェクトの読み込みと初期化が完全に終了しました")
    pass

def on_all_tasks_finished():
    # すべてのバックグラウンドタスクの完了
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
QgsProject.instance().readProject.connect(on_project_read)
iface.mapCanvas().renderComplete.connect(on_render_complete)
QgsApplication.taskManager().allTasksFinished.connect(on_all_tasks_finished)



