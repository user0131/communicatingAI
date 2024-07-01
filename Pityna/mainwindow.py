import os
import datetime
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import qt_pitynaui
import pityna

class MainWindow(QtWidgets.QMainWindow):
    """QtWidgets.QMainWindowを継承したサブクラス
    UI画面の構築を行う

    Attributes:
        Pityna (obj): Pitynaオブジェクトを保持
        action (bool): ラジオボタンの状態を保持
        ui (obj): Ui_MainWindowオブジェクトを保持
    """
    def __init__(self):
        super().__init__()
        self.pityna = pityna.Pityna('pityna')
        self.action = True #ラジオボタン
        self.ui = qt_pitynaui.Ui_MainWindow()
        self.log = [] #ログ用のリストを用意
        self.ui.setupUi(self) #setupUiで画面を構築、MainWindow自身を引数にすることが必要

    
    def putlog(self, str): 
        """QListWidgetクラスのaddItem()でログをリストに追加する

        Args:
            str (str): ユーザーの入力または応答メッセージをログ用に整形した文字列
        """
        self.ui.ListWidgetLog.addItem(str) #QListWidgetクラスのaddItem()でログをリストに追加する
        self.log.append(str + '\n') # ユーザーの発現、ピティナの応答のそれぞれに改行を付けてself.logに追加

    def prompt(self): #ピティナの応答メッセージの先頭に、プロンプト用のテキストを追加する
        p = self.pityna.get_name()
        if self.action == True:
            p += ':' + self.pityna.get_responder_name()
        return p + '> '
    
    def change_looks(self):
        """機嫌値によってピティナの表情を切り替えるメソッド
        """
        em = self.pityna.emotion.mood
        if -5 <= em <= 5:
            self.ui.LabelShowImg.setPixmap(QtGui.QPixmap(":/re/img//talk.gif"))
        elif -10 <= em < -5:
            self.ui.LabelShowImg.setPixmap(QtGui.QPixmap(":/re/img/empty.gif"))
        elif -15 <= em < -10:
            self.ui.LabelShowImg.setPixmap(QtGui.QPixmap(":/re/img/angry.gif"))
        elif 5 < em <= 15:
            self.ui.LabelShowImg.setPixmap(QtGui.QPixmap(":/re/img/happy.gif"))

    def writeLog(self):
        """ログを更新日時と共にログファイルに書き込む

        """
        #ログタイトルと更新日時のテキストを作成
        #日時は2023-01-01 00:00:00の書式にする
        now = 'Pityna System Dialogue Log: '\
                + datetime.datetime.now().strftime('%Y-%m-%d %H:%m::%S') + '\n'#「\」は行継続文字
        # リストlogの先頭要素として更新日時を追加
        self.log.insert(0, now)
        # logの全ての要素をログファイルに書き込む
        path = os.path.join(os.path.dirname(__file__), 'dics', 'log.txt')
        with open(path, 'a', encoding = 'utf_8') as f:  #'a'は追加書き込みモード
            f.writelines(self.log)
        
    def button_talk_slot(self):
        """「話す」ボタンがクリックされたときにコールバックされるイベントハンドラー

        ・Pitynaクラスのdialogue()を実行して応答メッセージを取得
        ・入力文字列および応答メッセージをログに出力
        """
        value = self.ui.LineEdit.text() #ラインエディットからユーザーの発現を取得
        if not value:
            self.ui.LabelResponce.setText('なに？')
        else:
            response = self.pityna.dialogue(value)
            self.ui.LabelResponce.setText(response)
            self.putlog('> ' + value)
            self.putlog(self.prompt() + response)
            self.ui.LineEdit.clear()

        # ピティナのイメージを現在の機嫌値に合わせる
        self.change_looks()

    def closeEvent(self, event):
        """ウィジェットを閉じるclose()メソッド実行時にQCloseEventによって呼ばれる

        Overrides:
            ・メッセージボックスを表示する
            ・[Yes]がクリックされたら辞書ファイルとログファイルを更新してい画面を閉じる
            ・[No]がクリックされたら即座に画面を閉じる

        Args:
            event (QCloseEvent): 閉じるイベント発生時に渡されるQCloseEventオブジェクト
        """
        # Yes|No ボタンを配置したメッセージボックスを表示
        reply = QtWidgets.QMessageBox.question(
            self,'質問ですー','辞書を更新してもいい？',
            buttons = QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
        # [Yes]クリックで辞書ファイルの更新とログファイルへの記録を行う
        if reply == QtWidgets.QMessageBox.Yes:
            self.pityna.save()   # 記憶メソッド実行
            self.writeLog(     ) # 対話の一部始終をログファイルに保存
            event.accept()       # イベントを続行し画面を閉じる
        else:
            # [No]クリックで即座に画面を閉じる
            event.accept()

    def show_responder_name(self):
        """RadioButton_1がオンの時に呼ばれるイベントハンドラー

        """
        self.action = True

    def hidden_responder_name(self):
        """RadioButton_2がオンの時に呼ばれるイベントハンドラー
        """
        self.action = False