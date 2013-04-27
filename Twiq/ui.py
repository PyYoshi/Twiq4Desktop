# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

import os

from PySide import QtGui, QtCore
from tweepy.error import TweepError

from Twiq import _, APP_CONFIG_DIR_PATH
from Twiq.tw import Twit, Token
from Twiq.resources.ui_main import Ui_MainWindow
from Twiq.resources.ui_auth import Ui_AuthorizeWindow
from Twiq.resources.ui_confirm import Ui_ConfirmDialog
from Twiq.resources import resource_rc # リソースファイルを読み込む。使用していないわけではない。
from Twiq.conf import read_app_config, get_accounts_list, \
    read_account_config, AppConfig, AccountConfig, \
    save_account_config, delete_account_config, save_app_config

class ConfirmDialog(QtGui.QMainWindow, Ui_ConfirmDialog):
    def __init__(self, parent=None):
        super(ConfirmDialog, self).__init__(parent)
        self.setupUi(self)

    @QtCore.Slot()
    def accept(self):
        pass

    @QtCore.Slot()
    def reject(self):
        pass

class DeleteConfirmDialog(ConfirmDialog):
    def __init__(self, account_name, parent=None):
        super(DeleteConfirmDialog, self).__init__(parent)
        self.account_name = account_name

    @QtCore.Slot()
    def accept(self):
        try:
            delete_account_config(self.account_name)
        except Exception as e:
            # TODO: エラー出力
            pass
        finally:
            self.close()

    @QtCore.Slot()
    def reject(self):
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
        self.app_config = read_app_config()
        if self.app_config == None: self.app_config = AppConfig()
        # APP_CONFIG_DIR_PATHの監視
        self.watcher = QtCore.QFileSystemWatcher([APP_CONFIG_DIR_PATH], parent=self)
        self.connect(self.watcher, QtCore.SIGNAL('directoryChanged(const QString &)'), self.onAppConfDirChanged)
        # 前回使用時のアカウントを選択 & 初期化段階でのアカウント情報の読み込みとcomboboxへの追加
        last_account_name = self.app_config.selected_account
        self.tw = None
        self.reloadAccountsConfig()
        last_account_index = self.accountComboBox.findText(last_account_name)
        self.accountComboBox.setCurrentIndex(last_account_index)
        # TODO: 投稿モードプラグインの読み込みとcomboboxへの追加

    def reloadAccountsConfig(self):
        cur_account = self.accountComboBox.currentText()
        self.accountComboBox.clear()
        for account_name in get_accounts_list():
            account_config = read_account_config(account_name)
            self.addAccountToComboBox(account_config)
        index = self.accountComboBox.findText(cur_account)
        if cur_account != None and index != -1:
            self.accountComboBox.setCurrentIndex(index)
            self.tw = self.accountComboBox.itemData(self.accountComboBox.currentIndex())['tw']

    def onAppConfDirChanged(self, path):
        self.reloadAccountsConfig()

    def addAccountToComboBox(self, account_config):
        tw = Twit(
            Token(self.app_config.consumer_key, self.app_config.consumer_secret_key),
            Token(account_config.access_key, account_config.access_secret_key)
        )
        account_obj = {
            'tw':tw,
            'config':account_config
        }
        self.accountComboBox.addItem(account_config.screen_name, account_obj)

    @QtCore.Slot()
    def msgTextChanged(self):
        v = Twit.validate_msg(self.msgTextEdit.toPlainText())
        template = """<html><head/><body><p><span style=\" color:#585858;\">%s</span></p></body></html>"""
        if not v[0] and v[1] != 140:
            template = """<html><head/><body><p><span style=" color:#ff0000;">%s</span></p></body></html>"""
        self.msgCountLabel.setText(template % v[1])

    @QtCore.Slot()
    def accountStrIndexChanged(self):
        account = self.accountComboBox.itemData(self.accountComboBox.currentIndex())
        if account != None: self.tw = account['tw']
        self.app_config.selected_account = self.accountComboBox.currentText()

    @QtCore.Slot()
    def modeStrIndexChanged(self):
        pass

    @QtCore.Slot()
    def addAccount(self):
        self.auth_window = AuthorizeWindow(self)
        self.auth_window.show()

    @QtCore.Slot()
    def delAccount(self):
        account_name = self.accountComboBox.currentText()
        self.confirm_dialog = DeleteConfirmDialog(account_name,self)
        self.confirm_dialog.msgLabel.setText('Delete %s account?' % account_name)
        self.confirm_dialog.show()

    def keyPressEvent(self, event):
        screen_name = self.accountComboBox.currentText()
        # Undo
        ctrl_u = event.modifiers() & QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_U)
        # Post
        ctrl_enter = event.modifiers() & QtCore.Qt.ControlModifier and (event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter)
        # TODO: ボスが来た機能を実装!
        # TODO: Ctrl+矢印キーでアカウントやモードの切り替え
        msg = self.msgTextEdit.toPlainText()
        v = Twit.validate_msg(msg)
        if ctrl_enter and v[0]:
            try:
                self.tw.post(msg)
                self.msgTextEdit.clear()
            except Exception as e:
                # TODO: エラー処理
                pass
        elif ctrl_u:
            try:
                self.msgTextEdit.clear()
                latest = self.tw.get_user_timeline(screen_name, count=1)[0]
                self.msgTextEdit.setPlainText(latest.text)
                self.tw.destroy_status(latest.id)
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