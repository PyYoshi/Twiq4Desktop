#!/bin/bash
pyside-uic Twiq/resources/ui_main.ui -o Twiq/resources/ui_main.py
pyside-uic Twiq/resources/ui_auth.ui -o Twiq/resources/ui_auth.py
pyside-rcc Twiq/resources/resource.qrc -o Twiq/resources/resource_rc.py