# ただいま大幅な見直し実施中
# DVD納品等に対応し、シンプルにQGISを日ごろの運用にも利用できる環境の構築を目指します。
[初期システム一式](https://1drv.ms/u/s!Am9UcJ606r_LgrkFLyqZ1NJCikxwWQ?e=pb3Vwa)

# QGISランチャー
 QGIS3.34.4.bat を起動してください。
 /ProjectFiles/ProjectFile.qgs が起動します。

 拡張子はLIZMAP連携のためQGSを利用しています。
 
（フォルダー構成）  
　QGISポータブル版を私の趣味により統一環境として組込済のプラグインを含んでいます。  
　WindowsのDOS.BATです。    
  /QGIS_portable  
　　QGIS3.34.4.BAT -----------------　ランチャー本体   
　　/QGIS3.34.4/qgis --------------- QGIS本体  
　　/QGIS3.34.4/qgisconfig----------　各種共通設定ファイルを含んだコンフィグファイル    
　　/ProjectFiles-------------------　初期設定がされたプロジェクトファイルを保存するフォルダ    
　　/ProjectFiles/OpenData----------　プロジェクトファイルで利用しているオープンデータを保存するフォルダ  
　を/QGIS_portableを英数字のみからなうフォルダに設置してください。   
　日本語を含むフォルダはエラーになります。  
  

**（注意）**  
　　/ProjectFiles/OpenData　の中身は容量の問題でグーグルドライで共有しているので下記からダウンロードしてください。  
　　https://drive.google.com/drive/folders/1CdTkJd-HtvLOeJjtEOjinKCPFkVXYmCr?usp=sharing


# 統一環境として組込済のプラグイン  
## 検索  
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
https://github.com/yamamoto-ryuzo/yr-qgis-easyinstantprint-plugin  
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
