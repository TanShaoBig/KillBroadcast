# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

from .EntityNames import FormatIdentifier, GetEntityDisplayName, ToUnicode


LevelId = clientApi.GetLevelId()


def StripFormatting(value):
    text = ToUnicode(value).strip()
    result = []
    skipNext = False
    for char in text:
        if skipNext:
            skipNext = False
            continue
        if char == u'§':
            skipNext = True
            continue
        result.append(char)
    return u''.join(result).strip()


def IsUsefulDisplayName(value, identifier=''):
    value = StripFormatting(value)
    if not value:
        return False
    lowered = value.lower()
    identifier = ToUnicode(identifier).strip().lower()
    if identifier and lowered in (identifier, identifier.rsplit(':', 1)[-1]):
        return False
    if lowered.startswith('item.') and lowered.endswith('.name'):
        return False
    return True


def GetLocalizedItemName(itemId, auxValue=0):
    if not itemId:
        return u''
    try:
        itemComp = clientApi.GetEngineCompFactory().CreateItem(LevelId)
    except Exception:
        return u''
    try:
        hoverName = itemComp.GetItemHoverName(itemId, int(auxValue or 0), None)
        if IsUsefulDisplayName(hoverName, itemId):
            return StripFormatting(hoverName)
    except Exception:
        pass
    try:
        basicInfo = itemComp.GetItemBasicInfo(itemId, int(auxValue or 0), False)
        basicName = basicInfo.get('itemName') if isinstance(basicInfo, dict) else ''
        if IsUsefulDisplayName(basicName, itemId):
            return StripFormatting(basicName)
    except Exception:
        pass
    return u''


def ResolveWeaponDisplayName(args):
    args = args if isinstance(args, dict) else {}
    itemId = args.get('WeaponId') or args.get('weaponId') or ''
    try:
        auxValue = int(args.get('WeaponAux', args.get('weaponAux', 0)) or 0)
    except Exception:
        auxValue = 0
    explicitName = args.get('WeaponName') or args.get('weaponName') or ''
    customName = args.get('WeaponCustomName') or args.get('weaponCustomName') or ''
    if args.get('WeaponNameProvided') and IsUsefulDisplayName(explicitName, itemId):
        return StripFormatting(explicitName)
    if IsUsefulDisplayName(customName, itemId):
        return StripFormatting(customName)
    if itemId in ('air', 'minecraft:air'):
        return u'徒手'
    localizedName = GetLocalizedItemName(itemId, auxValue)
    if localizedName:
        return localizedName
    if IsUsefulDisplayName(explicitName, itemId):
        return StripFormatting(explicitName)
    return FormatIdentifier(itemId) or u'武器'


def ResolveTargetDisplayName(args):
    args = args if isinstance(args, dict) else {}
    return GetEntityDisplayName(
        args.get('TargetType') or args.get('targetType') or '',
        args.get('TargetName') or args.get('targetName') or '',
        bool(args.get('TargetIsPlayer') or args.get('targetIsPlayer')),
    )
