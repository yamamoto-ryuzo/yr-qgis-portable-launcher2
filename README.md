# 初めての人でも扱いやすいポータブルQGIS環境の構築
## 2024/04/27　起動のためのコンフィグが必要になりました。そのうち説明は更新予定。
　https://github.com/yamamoto-ryuzo/yr-qgis-portable-launcher2/issues/2
## ただいま大幅な見直し実施中  
## DVD納品等に対応し、シンプルにQGISを日ごろの運用にも利用できる環境の構築を目指します。 
[システム一式 ver3.38.1](https://1drv.ms/u/c/cbbfeab49e70546f/EYyJqLhVbXNFufPDmemiWhABSOS7PdZqyGN_K_YfKuRKIg?e=N0973F)  
[システム一式 LTR ver3.34.8](https://1drv.ms/u/c/cbbfeab49e70546f/EUBx0GqMvbNBgcDbWhdHy4cBjpGuXLGYzPh1cE952tUFeg?e=QgoXg9)  

## QGISランチャー  
 ProjectFile.exe を起動してください。  
 /ProjectFiles/ProjectFile.qgs が起動します。  
 'shift'キーを押しながら起動すると、プロファイルをリセットできます。

EXEはファイル名を変えることで、同じ名称のqgsファイルを起動します。  
 例）test.exe　に　変更すると　test.qgs が起動します  

 ※拡張子はLIZMAP連携のためQGSを利用しています。
 
（フォルダー構成）  
　QGISポータブル版を私の趣味により統一環境として組込済のプラグインを含んでいます。  
　WindowsのProjectFile.exeです。    
  /QGIS_portable  
　　ProjectFile.exe ----------------　ランチャー本体   
　　/QGIS各バージョン/qgis --------------- QGIS本体  
　　/QGIS各バージョン/qgisconfig----------　各種共通設定ファイルを含んだコンフィグファイル    
　　/ProjectFiles-------------------　初期設定がされたプロジェクトファイルを保存するフォルダ    
　　/ProjectFiles/OpenData----------　プロジェクトファイルで利用しているオープンデータを保存するフォルダ  

　を/QGIS_portableを英数字のみからなるフォルダに解凍してください。   
　日本語を含むフォルダはエラーになります。  
![image](https://github.com/yamamoto-ryuzo/yr-qgis-portable-launcher2/assets/86514652/177ffbe3-654d-4d22-9f70-add09bcf0323)
  
## 統一環境として組込済のプラグイン  
### MMQGIS
[https://plugins.qgis.org/plugins/mmqgis/#plugin-about ](https://michaelminn.com/linux/mmqgis/)   
### 検索  
### Search Layers  
https://github.com/NationalSecurityAgency/qgis-searchlayers-plugin  
### GEO_search  
https://github.com/yamamoto-ryuzo/GEO-search-plugin  
## 印刷  
### Instant Print  
https://github.com/sourcepole/qgis-instantprint-plugin  
### 簡易印刷  
公開予定  
### (保留中)  
公式プラグインでは日本語対応していません、下記リポジトリからダウンロードください。  
https://github.com/sourcepole/qgis-instantprint-plugin  
### (保留中)  
https://github.com/Orbitalnet-incs/meshprint  
## レイヤー管理   
### Layers menu from project  
https://github.com/xcaeag/MenuFromProject-Qgis-Plugin  
## 画面  
### ZoomView  
https://bitbucket.org/janzandr/zoomview/src/master/
## WEB連携  
### Street View  
リポジトリなし  
### Lizmap  
https://github.com/3liz/lizmap-plugin  
### qgis2web  
https://github.com/qgis2web/qgis2web  
### Qgis2threejs  
https://github.com/minorua/Qgis2threejs  
## データ連携  
### PLATEAU QGIS Plugin  
https://github.com/Project-PLATEAU/plateau-qgis-plugin  
### ExcelSync  
https://github.com/opengisch/qgis_excel_sync  
### Spreadsheet Layers  
https://github.com/camptocamp/QGIS-SpreadSheetLayers  
### MOJXML Loader  
https://github.com/MIERUNE/qgis-mojxml-plugin  
## その他  
### Select Themes  
https://github.com/Amphibitus/selectThemes  
### QGIS-legendView  
https://github.com/yamamoto-ryuzo/QGIS-legendView
### EasyAttributeFilter  
https://github.com/Orbitalnet-incs/EasyAttributeFilter  
### (保留中)  
https://github.com/Orbitalnet-incs/SearchZmap  
　　
#### ・補足事項  
    .BATの改行コードをWindows用にするため　.gitattributes　を設置 

