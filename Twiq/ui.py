# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

import os

from PySide import QtGui, QtCore
from tweepy.error import TweepError

from Twiq import _, APP_CONFIG_DIR_PATH
from Twiq.tw import Twit, Token
from Twiq.resources.ui_main import Ui_MainWindow
from Twiq.resources.ui_auth import Ui_AuthorizeWindow
from Twiq.resources.ui_del_manage import Ui_DelManageDialog
from Twiq.resources import resource_rc # リソースファイルを読み込む。使用していないわけではない。
from Twiq.conf import read_app_config, get_accounts_list, \
    read_account_config, AppConfig, AccountConfig, \
    save_account_config, delete_account_config, save_app_config

class DeleteManageDialog(QtGui.QMainWindow, Ui_DelManageDialog):
    def __init__(self, parent=None):
        super(DeleteManageDialog, self).__init__(parent)
        self.setupUi(self)
        for k,v in parent.accounts.items():
            self.accountComboBox.addItem(k)

    @QtCore.Slot()
    def delAccount(self):
        if self.accountComboBox.currentText():
            reply = QtGui.QMessageBox.question(self, 'Message',
                "Are you sure to delete %s?"%self.accountComboBox.currentText(), QtGui.QMessageBox.Yes |
                QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                delete_account_config(self.accountComboBox.currentText())
                self.close()

class AuthorizeWindow(QtGui.QMainWindow, Ui_AuthorizeWindow):
    def __init__(self, parent=None):
        super(AuthorizeWindow, self).__init__(parent)
        self.setupUi(self)
        self.tw = Twit(Token(parent.app_config.consumer_key, parent.app_config.consumer_secret_key))
        self.webView.setUrl(self.tw.get_auth_url())

    @QtCore.Slot()
    def authOkButton(self):
        pin = self.pinLineEdit.text()
        if 0 < len(pin):
            try:
                token = self.tw.get_access_token(pin)
                user = self.tw.verify_credentials()
                account_config = AccountConfig(user.screen_name, user.id, token.key, token.secret)
                save_account_config(user.screen_name, account_config)
                self.close()
            except TweepError as e:
                _.error(msg=e, extra={'position': 'ui.AuthorizeWindow.authOkButton'})
                if e.reason == 'HTTP Error 401: Unauthorized':
                    # Oops, Did you sign in to Twitter?
                    msg = """<html><head/><body><p><span style=" color:#ff0000;">Oops, Did you sign in to Twitter?</span></p></body></html>"""
                    self.errLabel.setText(msg)
            except Exception as e:
                # Oops, something went wrong...
                _.error(msg=e, extra={'position': 'ui.AuthorizeWindow.authOkButton'})
                msg = """<html><head/><body><p><span style=" color:#ff0000;">Oops, something went wrong...</span></p></body></html>"""
                self.errLabel.setText(msg)

    @QtCore.Slot()
    def authCancelButton(self):
        self.close()

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.accounts_group = QtGui.QActionGroup(self)
        self.accounts_group.triggered.connect(self.onCheckedAccount)
        # menuModeを無効化
        self.menuMode.setEnabled(False)
        # App Configのロード
        self.app_config = read_app_config()
        if self.app_config == None: self.app_config = AppConfig()
        # APP_CONFIG_DIR_PATHの監視
        self.watcher = QtCore.QFileSystemWatcher([APP_CONFIG_DIR_PATH], parent=self)
        self.connect(self.watcher, QtCore.SIGNAL('directoryChanged(const QString &)'), self.onAppConfDirChanged)
        # 前回使用時のアカウントを選択 & 初期化段階でのアカウント情報の読み込みとcomboboxへの追加
        self.accounts = dict()
        self.tw = None
        last_account_name = self.app_config.selected_account
        self.reloadAccountsConfig()
        if last_account_name:
            self.accounts[last_account_name]['action'].setChecked(True)
            self.tw = self.accounts[last_account_name]['tw']
        # TODO: 投稿モードプラグインの読み込みとmenuModeへの追加

    def resizeEvent(self, event):
        # ウィンドウサイズにmsgTextEditのサイズもフィットさせる
        msgTextEdit_width = self.width()
        msgTextEdit_height = self.height() - self.menuBar.height()
        self.msgTextEdit.setGeometry(0,0,msgTextEdit_width,msgTextEdit_height)
        self.msgCountLabel.setGeometry(msgTextEdit_width-64,msgTextEdit_height-32,self.msgCountLabel.width(),self.msgCountLabel.height())
        self.msgCountLabel.raise_()

    def reloadAccountsConfig(self):
        # 選択済みアカウントのチェック
        checked_account_name = None
        if self.accounts_group.checkedAction():
            checked_account_name = self.accounts_group.checkedAction().text()
        # 初期化 & アカウント追加削除アクションの追加
        self.menuAccount.clear()
        self.accounts = dict()
        self.tw = None
        add_action = QtGui.QAction('Add', self)
        add_action.setStatusTip('Add Twitter Account')
        add_action.triggered.connect(self.addAccount)
        delete_action = QtGui.QAction('Delete', self)
        delete_action.setStatusTip('Delete Twitter Account')
        delete_action.triggered.connect(self.delAccount)
        self.menuAccount.addActions([add_action,delete_action])
        self.menuAccount.addSeparator()
        # アカウントをmenuAccountへ追加
        actions = []
        for account_name in get_accounts_list():
            account_config = read_account_config(account_name)
            tw = Twit(
                Token(self.app_config.consumer_key, self.app_config.consumer_secret_key),
                Token(account_config.access_key, account_config.access_secret_key)
            )
            account_action = QtGui.QAction(account_name, self)
            account_action.setCheckable(True)
            account_action.setActionGroup(self.accounts_group)
            actions.append(account_action)
            self.accounts[account_name] = {'tw':tw,'config':account_config,'action':account_action}
        self.menuAccount.addActions(actions)
        if checked_account_name:
            self.accounts[checked_account_name]['action'].setChecked(True)
            self.tw = self.accounts[checked_account_name]['tw']

    def onAppConfDirChanged(self, path):
        self.reloadAccountsConfig()

    def onCheckedAccount(self, action):
        if action:
            self.tw = self.accounts[action.text()]['tw']

    @QtCore.Slot()
    def msgTextChanged(self):
        v = Twit.validate_msg(self.msgTextEdit.toPlainText())
        template = """<html><head/><body><p><span style=\" color:#585858;\">%s</span></p></body></html>"""
        if not v[0] and v[1] != 140:
            template = """<html><head/><body><p><span style=" color:#ff0000;">%s</span></p></body></html>"""
        self.msgCountLabel.setText(template % v[1])

    @QtCore.Slot()
    def addAccount(self):
        self.auth_window = AuthorizeWindow(self)
        self.auth_window.show()

    @QtCore.Slot()
    def delAccount(self):
        self.del_manage_dialog = DeleteManageDialog(self)
        self.del_manage_dialog.show()

    def post_status(self, msg):
        self.tw.post(msg)
        self.msgTextEdit.clear()

    def undo_post(self, screen_name):
        self.msgTextEdit.clear()
        latest = self.tw.get_user_timeline(screen_name, count=1)[0]
        self.msgTextEdit.setPlainText(latest.text)
        self.tw.destroy_status(latest.id)

    def keyPressEvent(self, event):
        screen_name = None
        if self.accounts_group.checkedAction():
            screen_name = self.accounts_group.checkedAction().text()
        # Undo
        ctrl_u = event.modifiers() & QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_U)
        # Post
        ctrl_enter = event.modifiers() & QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)
        # TODO: ボスが来た機能を実装!
        # TODO: Ctrl+矢印キーでアカウントやモードの切り替え
        msg = self.msgTextEdit.toPlainText()
        v = Twit.validate_msg(msg)
        if ctrl_enter and v[0] and screen_name and self.tw:
            try:
                self.post_status(msg)
            except Exception as e:
                # TODO: エラー処理
                pass
        elif ctrl_u and screen_name and self.tw:
            try:
                self.undo_post(screen_name)
            except Exception as e:
                # TODO: エラー処理
                pass

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            save_app_config(self.app_config)
            event.accept()
        else:
            event.ignore()
