# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi

from ..ModConfig import MOD_NAMESPACE, SERVER_SYSTEM_NAME


def GetKillBroadcastServerSystem():
    try:
        return serverApi.GetSystem(MOD_NAMESPACE, SERVER_SYSTEM_NAME)
    except Exception:
        return None


def RegisterWeaponDisplayName(itemId, displayName):
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'RegisterWeaponDisplayName'):
        return False
    return bool(system.RegisterWeaponDisplayName(itemId, displayName))


def RegisterManagedEntityTypes(ownerId, entityTypes):
    """Let an external addon own kill confirmation for entity identifiers."""
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'RegisterExternallyManagedEntityTypes'):
        return False
    return bool(system.RegisterExternallyManagedEntityTypes({
        'OwnerId': ownerId,
        'EntityTypes': entityTypes,
    }))


def UnregisterManagedEntityTypes(ownerId, entityTypes=None):
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'UnregisterExternallyManagedEntityTypes'):
        return False
    payload = {'OwnerId': ownerId}
    if entityTypes is not None:
        payload['EntityTypes'] = entityTypes
    return bool(system.UnregisterExternallyManagedEntityTypes(payload))


def GetManagedEntityTypes(ownerId=None):
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'GetExternallyManagedEntityTypes'):
        return []
    return list(system.GetExternallyManagedEntityTypes(ownerId))


def RecordDamageSource(
    attackerId,
    targetId,
    weaponId='',
    weaponName='',
    headshot=None,
    weaponAux=0,
    hitPos=None
):
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'RecordExternalDamageSource'):
        return False
    payload = {
        'AttackerId': attackerId,
        'TargetId': targetId,
    }
    if headshot is not None:
        payload['HeadShot'] = bool(headshot)
    if hitPos is not None:
        payload['hitPos'] = hitPos
    if weaponId:
        payload['WeaponId'] = weaponId
        payload['WeaponAux'] = weaponAux
    if weaponName:
        payload['WeaponName'] = weaponName
    return bool(system.RecordExternalDamageSource(payload))


def ReportKill(
    attackerId,
    targetId,
    weaponId='',
    weaponName='',
    headshot=None,
    weaponAux=0,
    hitPos=None,
    targetType='',
    targetName='',
    damage=None
):
    """Confirm a kill handled by a custom death-animation pipeline."""
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'ReportExternalKill'):
        return False
    payload = {
        'AttackerId': attackerId,
        'TargetId': targetId,
    }
    if headshot is not None:
        payload['HeadShot'] = bool(headshot)
    if hitPos is not None:
        payload['hitPos'] = hitPos
    if weaponId:
        payload['WeaponId'] = weaponId
        payload['WeaponAux'] = weaponAux
    if weaponName:
        payload['WeaponName'] = weaponName
    if targetType:
        payload['TargetType'] = targetType
    if targetName:
        payload['TargetName'] = targetName
    if damage is not None:
        payload['Damage'] = damage
    return bool(system.ReportExternalKill(payload))


ConfirmKill = ReportKill


def ReportKillInfo(killInfo):
    """Forward a complete kill-info dictionary to the public server API."""
    system = GetKillBroadcastServerSystem()
    if not system or not hasattr(system, 'ReportExternalKill'):
        return False
    if not isinstance(killInfo, dict):
        return False
    return bool(system.ReportExternalKill(dict(killInfo)))


ConfirmKillInfo = ReportKillInfo
