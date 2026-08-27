# -*- coding: utf-8 -*-
"""Compatibility provider for another addon that owns kill-effect settings.

Copy this file into the other addon's script package and call
RegisterHideKillEffectSettings() from its InitClient hook.  The provider uses
a shared system name, so KillBroadcast can discover it without scanning files.
"""
import mod.client.extraClientApi as clientApi

COMPAT_NAMESPACE = 'KillBroadcastCompat'
HIDE_KILL_SETTINGS_SYSTEM = 'HideKillEffectSettings'


CompatClientSystem = clientApi.GetClientSystemCls()


class HideKillEffectSettingsSystem(CompatClientSystem):
    def __init__(self, namespace, systemName):
        CompatClientSystem.__init__(self, namespace, systemName)


def RegisterHideKillEffectSettings():
    return clientApi.RegisterSystem(
        COMPAT_NAMESPACE,
        HIDE_KILL_SETTINGS_SYSTEM,
        __name__ + '.HideKillEffectSettingsSystem'
    )
