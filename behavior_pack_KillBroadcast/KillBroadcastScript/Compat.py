# -*- coding: utf-8 -*-
from .ModConfig import (
    COMPAT_NAMESPACE,
    HIDE_KILL_SETTINGS_SYSTEM,
    TSGUNS_CLIENT_SYSTEM,
    TSGUNS_NAMESPACE,
    TSGUNS_SERVER_SYSTEM,
)


def GetTsGunsServerSystem():
    import mod.server.extraServerApi as serverApi
    try:
        return serverApi.GetSystem(TSGUNS_NAMESPACE, TSGUNS_SERVER_SYSTEM)
    except Exception:
        return None


def IsTsGunsServerLoaded():
    return GetTsGunsServerSystem() is not None


def GetTsGunsClientSystem():
    import mod.client.extraClientApi as clientApi
    try:
        return clientApi.GetSystem(TSGUNS_NAMESPACE, TSGUNS_CLIENT_SYSTEM)
    except Exception:
        return None


def IsTsGunsClientLoaded():
    return GetTsGunsClientSystem() is not None


def IsTsGunsDamageAttributed(attackerId, targetId):
    system = GetTsGunsServerSystem()
    if not system:
        return False
    try:
        checker = getattr(system, 'IsKillBroadcastTsGunsDamage', None)
        if checker:
            return bool(checker(attackerId, targetId))
        pendingChecker = getattr(system, 'IsPendingTsGunKill', None)
        return bool(pendingChecker and pendingChecker(targetId))
    except Exception:
        return False


def IsHideKillSettingsProviderLoaded():
    import mod.client.extraClientApi as clientApi
    try:
        return clientApi.GetSystem(COMPAT_NAMESPACE, HIDE_KILL_SETTINGS_SYSTEM) is not None
    except Exception:
        return None
