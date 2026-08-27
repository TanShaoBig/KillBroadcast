# -*- coding: utf-8 -*-
import math
import time

import mod.server.extraServerApi as serverApi

from .Compat import IsTsGunsDamageAttributed, IsTsGunsServerLoaded
from .ModConfig import (
    AIM_SNAPSHOT_EVENT,
    AIM_SNAPSHOT_MAX_AGE_SECONDS,
    AIM_SNAPSHOT_MAX_CAMERA_DISTANCE,
    AIM_SNAPSHOT_SERVER_MIN_INTERVAL_SECONDS,
    CLIENT_SYSTEM_NAME,
    CORPSE_KILL_CONTEXT_SECONDS,
    CREATE_KILL_EVENT,
    DAMAGE_CONTEXT_SECONDS,
    DEATH_LOCK_SECONDS,
    PENDING_LETHAL_CONFIRM_TICKS,
    PENDING_LETHAL_EXPIRE_TICKS,
    HEADSHOT_SOUND_EVENT,
    HEADSHOT_SOUND_RADIUS_SQ,
    HIT_MARKER_DEDUP_SECONDS,
    HIT_MARKER_EVENT,
    PLAYER_DEATH_CLEANUP_EVENT,
    HEADSHOT_EYE_HEIGHT,
    HEADSHOT_ENTITY_TOP_RATIO,
    HEADSHOT_PLAYER_BODY_HALF_WIDTH,
    HEADSHOT_PLAYER_BODY_HEIGHT,
    HEADSHOT_PLAYER_SNEAKING_BODY_HEIGHT,
    HEADSHOT_RAY_MAX_DISTANCE,
    HEADSHOT_SNEAK_EYE_OFFSET,
    HEADSHOT_SNEAKING_HEIGHT,
    HEADSHOT_STANDING_HEIGHT,
    KILL_SOURCE_GENERIC,
    KILL_SOURCE_EXTERNAL,
    MOD_NAMESPACE,
    PROJECTILE_CONTEXT_SECONDS,
    SERVER_STATUS_EVENT,
)


ServerSystem = serverApi.GetServerSystemCls()
EngineCompFactory = serverApi.GetEngineCompFactory()
LevelId = serverApi.GetLevelId()

try:
    STRING_TYPES = (basestring,)
except NameError:
    STRING_TYPES = (str,)


class KillBroadcastServerSystem(ServerSystem):
    """Server-side owner of generic kill and hit-marker feedback."""

    def __init__(self, namespace, systemName):
        ServerSystem.__init__(self, namespace, systemName)
        self.compatibilityState = 'unknown'
        self.tsgunsLoaded = False
        self.enabled = False
        self._engineNamespace = serverApi.GetEngineNamespace()
        self._engineSystemName = serverApi.GetEngineSystemName()
        self._deathLocks = {}
        self._pendingLethalHits = {}
        self._hitMarkerTimes = {}
        self._damageContexts = {}
        self._projectileContexts = {}
        self._aimSnapshots = {}
        self._aimSnapshotTimes = {}
        self._registeredWeaponNames = {}
        # Entity type identifier -> owners that explicitly manage its death
        # animation and kill confirmation. This registry is runtime-only and
        # can be populated before the standalone server system is enabled.
        self._externallyManagedEntityTypes = {}
        self._probeTicks = 0
        self._serverTick = 0
        self._playerIdCacheTick = -1
        self._playerIdCache = set()
        self._activated = False
        self._listenLifecycleEvents()

    def _listenLifecycleEvents(self):
        for eventName, callback in (
            ('LoadServerAddonScriptsAfter', self.OnLoadServerAddonScriptsAfter),
            ('OnScriptTickServer', self.OnScriptTickServer),
            ('AddServerPlayerEvent', self.OnAddServerPlayerEvent),
            ('ClientLoadAddonsFinishServerEvent', self.OnClientLoadAddonsFinishServerEvent),
        ):
            try:
                self.ListenForEvent(
                    self._engineNamespace,
                    self._engineSystemName,
                    eventName,
                    self,
                    callback,
                )
            except Exception as error:
                print('[KillBroadcast] listen lifecycle event error:', eventName, error)

    def _listenEngineEvent(self, eventName, callback):
        try:
            self.ListenForEvent(
                self._engineNamespace,
                self._engineSystemName,
                eventName,
                self,
                callback,
            )
            return True
        except Exception as error:
            print('[KillBroadcast] listen engine event error:', eventName, error)
            return False

    def _unlistenEngineEvent(self, eventName, callback):
        try:
            self.UnListenForEvent(
                self._engineNamespace,
                self._engineSystemName,
                eventName,
                self,
                callback,
            )
        except Exception:
            pass

    def OnLoadServerAddonScriptsAfter(self, args=None):
        self.ResolveCompatibility('load_finished')

    def OnScriptTickServer(self, args=None):
        self._serverTick += 1
        if self.compatibilityState == 'unknown':
            self._probeTicks += 1
            if self._probeTicks >= 5:
                self.ResolveCompatibility('tick_fallback')
        self._processPendingLethalHits()
        self._cleanupState(time.time())

    def ResolveCompatibility(self, reason=''):
        if self.compatibilityState != 'unknown':
            return self.enabled
        tsgunsLoaded = IsTsGunsServerLoaded()
        if tsgunsLoaded is None:
            print('[KillBroadcast][Compat] TsGuns query is not ready; keeping server inactive')
            return False
        self.compatibilityState = 'enabled'
        self.tsgunsLoaded = bool(tsgunsLoaded)
        self.enabled = True
        self._activate()
        mode = 'cooperative' if self.tsgunsLoaded else 'standalone'
        print('[KillBroadcast][Compat] standalone server enabled; mode=%s' % mode)
        self._broadcastStatus()
        return True

    def _activate(self):
        if self._activated:
            return
        self._activated = True
        for eventName, callback in (
            ('MobDieEvent', self.OnMobDieEvent),
            ('PlayerDieEvent', self.OnPlayerDieEvent),
            ('EntityRemoveEvent', self.OnTargetEntityRemoveEvent),
            ('PlayerRespawnFinishServerEvent', self.OnTargetPlayerRespawnFinishServerEvent),
            ('ActorHurtServerEvent', self.OnActorHurtServerEvent),
            ('ActuallyHurtServerEvent', self.OnActuallyHurtServerEvent),
            ('SpawnProjectileServerEvent', self.OnSpawnProjectileServerEvent),
            ('ProjectileCritHitEvent', self.OnProjectileCritHitEvent),
            ('ProjectileDoHitEffectEvent', self.OnProjectileDoHitEffectEvent),
        ):
            self._listenEngineEvent(eventName, callback)
        try:
            self.ListenForEvent(
                MOD_NAMESPACE,
                CLIENT_SYSTEM_NAME,
                AIM_SNAPSHOT_EVENT,
                self,
                self.OnAimSnapshot,
            )
        except Exception as error:
            print('[KillBroadcast] listen aim snapshot event error:', error)
        try:
            playerIds = serverApi.GetPlayerList()
        except Exception:
            playerIds = []
        for playerId in playerIds:
            self._enablePlayerCritBox(playerId)

    def _broadcastStatus(self, playerId=None):
        if self.compatibilityState == 'unknown':
            return False
        payload = {
            'Enabled': bool(self.enabled),
            'DisabledByTsGuns': False,
            'TsGunsLoaded': bool(self.tsgunsLoaded),
            'Cooperative': bool(self.tsgunsLoaded),
            'Reason': self.compatibilityState,
        }
        recipients = [playerId] if playerId else []
        if not recipients:
            try:
                recipients = serverApi.GetPlayerList()
            except Exception:
                recipients = []
        sent = False
        for receiverId in recipients:
            try:
                self.NotifyToClient(receiverId, SERVER_STATUS_EVENT, payload)
                sent = True
            except Exception:
                pass
        return sent

    def OnAddServerPlayerEvent(self, args):
        playerId = self._getPlayerId(args)
        if playerId:
            self._playerIdCache = getattr(self, '_playerIdCache', set())
            self._playerIdCache.add(str(playerId))
            if self.enabled:
                self._enablePlayerCritBox(playerId)
            if self.compatibilityState != 'unknown':
                self._broadcastStatus(playerId)
        return True

    def OnClientLoadAddonsFinishServerEvent(self, args):
        playerId = self._getPlayerId(args)
        if playerId:
            if self.enabled:
                self._enablePlayerCritBox(playerId)
            if self.compatibilityState != 'unknown':
                self._broadcastStatus(playerId)
        return True

    def _getPlayerId(self, args):
        if not isinstance(args, dict):
            return None
        return args.get('playerId') or args.get('PlayerId') or args.get('__id__') or args.get('id')

    def _isPlayer(self, entityId):
        if not entityId:
            return False
        serverTick = getattr(self, '_serverTick', 0)
        if getattr(self, '_playerIdCacheTick', -1) != serverTick:
            try:
                players = serverApi.GetPlayerList()
                self._playerIdCache = set(str(playerId) for playerId in players)
                self._playerIdCacheTick = serverTick
            except Exception:
                return False
        return str(entityId) in self._playerIdCache

    def _enablePlayerCritBox(self, playerId):
        if not playerId:
            return False
        try:
            EngineCompFactory.CreatePlayer(playerId).OpenPlayerCritBox()
            return True
        except Exception as error:
            print('[KillBroadcast] enable player headshot box error:', playerId, error)
            return False

    def _getEntityType(self, entityId):
        try:
            return EngineCompFactory.CreateEngineType(entityId).GetEngineTypeStr() or ''
        except Exception:
            return ''

    def _normalizeEntityTypeIdentifier(self, entityType):
        if entityType is None:
            return ''
        try:
            entityType = str(entityType).strip().lower()
        except Exception:
            return ''
        if ':' not in entityType or entityType.startswith(':') or entityType.endswith(':'):
            return ''
        return entityType

    def _normalizeEntityTypeIdentifiers(self, entityTypes):
        if isinstance(entityTypes, STRING_TYPES):
            entityTypes = (entityTypes,)
        elif not isinstance(entityTypes, (list, tuple, set, frozenset)):
            return []
        normalized = []
        seen = set()
        for entityType in entityTypes:
            entityType = self._normalizeEntityTypeIdentifier(entityType)
            if not entityType or entityType in seen:
                continue
            seen.add(entityType)
            normalized.append(entityType)
        return normalized

    def _normalizeExternalOwnerId(self, ownerId):
        if ownerId is None:
            return ''
        try:
            return str(ownerId).strip().lower()
        except Exception:
            return ''

    def _parseManagedEntityTypeArgs(self, args, entityTypes=None):
        if isinstance(args, dict):
            ownerId = (
                args.get('OwnerId') or args.get('ownerId') or
                args.get('ProviderId') or args.get('providerId')
            )
            for key in (
                'EntityTypes', 'entityTypes',
                'EntityIdentifiers', 'entityIdentifiers',
                'Identifiers', 'identifiers',
            ):
                if key in args:
                    entityTypes = args.get(key)
                    break
        else:
            ownerId = args
        return (
            self._normalizeExternalOwnerId(ownerId),
            self._normalizeEntityTypeIdentifiers(entityTypes),
        )

    def _resolveKillTargetType(self, targetId, args=None, recentContext=None):
        args = args if isinstance(args, dict) else {}
        recentContext = recentContext if isinstance(recentContext, dict) else {}
        for key in (
            'TargetType', 'targetType', 'EntityType', 'entityType',
            'Identifier', 'identifier',
        ):
            if args.get(key):
                return args.get(key)
        if recentContext.get('TargetType'):
            return recentContext.get('TargetType')
        candidate = self._pendingLethalHits.get(str(targetId))
        if isinstance(candidate, dict) and candidate.get('TargetType'):
            return candidate.get('TargetType')
        return self._getEntityType(targetId)

    def _isExternallyManagedEntityType(self, entityType):
        entityType = self._normalizeEntityTypeIdentifier(entityType)
        if not entityType:
            return False
        registry = getattr(self, '_externallyManagedEntityTypes', {})
        return bool(registry.get(entityType))

    def _isExternallyManagedTarget(self, targetId, args=None, recentContext=None):
        return self._isExternallyManagedEntityType(
            self._resolveKillTargetType(targetId, args, recentContext)
        )

    def _getEntityName(self, entityId):
        try:
            name = EngineCompFactory.CreateName(entityId).GetName()
            if name:
                return name
        except Exception:
            pass
        entityType = self._getEntityType(entityId)
        if entityType:
            return entityType.rsplit(':', 1)[-1]
        return ''

    def _getFootPos(self, entityId):
        try:
            return EngineCompFactory.CreatePos(entityId).GetFootPos()
        except Exception:
            return None

    def _getDimensionId(self, entityId):
        try:
            return EngineCompFactory.CreateDimension(entityId).GetEntityDimensionId()
        except Exception:
            return None

    def _getDistance(self, attackerId, targetId):
        attackerPos = self._getFootPos(attackerId)
        targetPos = self._getFootPos(targetId)
        if not attackerPos or not targetPos or len(attackerPos) < 3 or len(targetPos) < 3:
            return None
        try:
            return math.sqrt(sum(
                (float(attackerPos[index]) - float(targetPos[index])) ** 2
                for index in range(3)
            ))
        except Exception:
            return None

    def _getHealth(self, entityId):
        try:
            attr = EngineCompFactory.CreateAttr(entityId)
            healthType = serverApi.GetMinecraftEnum().AttrType.HEALTH
            return float(attr.GetAttrValue(healthType))
        except Exception:
            return None

    def _getMaxHealth(self, entityId):
        try:
            attr = EngineCompFactory.CreateAttr(entityId)
            healthType = serverApi.GetMinecraftEnum().AttrType.HEALTH
            return float(attr.GetAttrMaxValue(healthType))
        except Exception:
            return None

    def _getDamageValue(self, args):
        if not isinstance(args, dict):
            return None
        for key in ('damage', 'Damage', 'amount', 'Amount'):
            if args.get(key) is None:
                continue
            try:
                return max(0.0, float(args.get(key)))
            except Exception:
                pass
        return None

    def _predictHealthAfterDamage(self, targetId, damage=None, health=None):
        """Return the predicted health after the current hurt is applied.

        ActuallyHurtServerEvent reports the effective damage while the
        target's health value is still available for the current hit.  Keep
        this calculation in one place so the hit-marker and death paths use
        the same lethal prediction.
        """
        if health is None:
            health = self._getHealth(targetId)
        if damage is None:
            return None
        try:
            health = float(health)
            damage = max(0.0, float(damage))
        except Exception:
            return None
        if health <= 0.0:
            return None
        return health - damage

    def _willDamageKill(self, targetId, damage=None, health=None):
        predictedHealth = self._predictHealthAfterDamage(targetId, damage, health)
        return bool(predictedHealth is not None and predictedHealth <= 0.0001)

    def _getCollisionSize(self, entityId):
        if not entityId:
            return None
        try:
            size = EngineCompFactory.CreateCollisionBox(entityId).GetSize()
            if not size or len(size) < 2:
                return None
            width = float(size[0])
            height = float(size[1])
            if width <= 0.0 or height <= 0.0:
                return None
            return (width, height)
        except Exception:
            return None

    def _isPlayerTarget(self, entityId):
        return bool(
            self._isPlayer(entityId) or
            self._getEntityType(entityId) == 'minecraft:player'
        )

    def _toVec3(self, value):
        if not value or len(value) < 3:
            return None
        try:
            return (float(value[0]), float(value[1]), float(value[2]))
        except Exception:
            return None

    def _getHitPosition(self, args):
        if not isinstance(args, dict):
            return None
        for key in ('hitPos', 'HitPos', 'hitPosition', 'HitPosition', 'damagePos'):
            value = self._toVec3(args.get(key))
            if value:
                return value
        for keys in (
            ('x', 'y', 'z'),
            ('hitX', 'hitY', 'hitZ'),
            ('posX', 'posY', 'posZ'),
        ):
            if all(args.get(key) is not None for key in keys):
                return self._toVec3(tuple(args.get(key) for key in keys))
        return None

    def _hasExplicitHeadshot(self, args):
        return bool(
            isinstance(args, dict) and
            ('HeadShot' in args or 'headshot' in args)
        )

    def _getExplicitHeadshot(self, args):
        if not isinstance(args, dict):
            return False
        if 'HeadShot' in args:
            return bool(args.get('HeadShot'))
        return bool(args.get('headshot'))

    def _isPlayerSneaking(self, playerId):
        try:
            playerComp = EngineCompFactory.CreatePlayer(playerId)
            isSneaking = getattr(playerComp, 'isSneaking', None)
            return bool(isSneaking and isSneaking())
        except Exception:
            return False

    def _getViewRayOrigin(self, playerId):
        footPos = self._toVec3(self._getFootPos(playerId))
        if not footPos:
            return None
        eyeHeight = HEADSHOT_EYE_HEIGHT
        if self._isPlayerSneaking(playerId):
            eyeHeight -= HEADSHOT_SNEAK_EYE_OFFSET
        return (footPos[0], footPos[1] + eyeHeight, footPos[2])

    def _getViewDirection(self, playerId):
        try:
            rotation = EngineCompFactory.CreateRot(playerId).GetRot()
            if not rotation or len(rotation) < 2:
                return None
            return self._toVec3(serverApi.GetDirFromRot((rotation[0], rotation[1])))
        except Exception:
            return None

    def _normalizeVec3(self, value):
        value = self._toVec3(value)
        if not value:
            return None
        length = math.sqrt(sum(axis * axis for axis in value))
        if length <= 0.000001:
            return None
        return tuple(axis / length for axis in value)

    def OnAimSnapshot(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        playerId = args.get('__id__')
        if not playerId or not self._isPlayer(playerId):
            return False
        now = time.time()
        playerKey = str(playerId)
        self._aimSnapshotTimes = getattr(self, '_aimSnapshotTimes', {})
        if now - self._aimSnapshotTimes.get(playerKey, 0.0) < AIM_SNAPSHOT_SERVER_MIN_INTERVAL_SECONDS:
            return False
        self._aimSnapshotTimes[playerKey] = now
        origin = self._toVec3(args.get('Pos') or args.get('position'))
        direction = self._normalizeVec3(args.get('Vec') or args.get('direction'))
        if not origin or not direction:
            return False
        footPos = self._toVec3(self._getFootPos(playerId))
        if footPos:
            cameraDistance = math.sqrt(sum(
                (origin[index] - footPos[index]) ** 2
                for index in range(3)
            ))
            if cameraDistance > AIM_SNAPSHOT_MAX_CAMERA_DISTANCE:
                return False
        self._aimSnapshots[playerKey] = {
            'Origin': origin,
            'Direction': direction,
            'ExpireAt': now + AIM_SNAPSHOT_MAX_AGE_SECONDS,
        }
        return True

    def _getRecentAimSnapshot(self, playerId):
        if not playerId:
            return None
        now = time.time()
        snapshot = self._aimSnapshots.get(str(playerId))
        if not isinstance(snapshot, dict) or snapshot.get('ExpireAt', 0.0) <= now:
            self._aimSnapshots.pop(str(playerId), None)
            return None
        return snapshot

    def _intersectRayAabbDistance(self, origin, direction, boxMin, boxMax, maxDistance):
        origin = self._toVec3(origin)
        direction = self._normalizeVec3(direction)
        boxMin = self._toVec3(boxMin)
        boxMax = self._toVec3(boxMax)
        if not origin or not direction or not boxMin or not boxMax:
            return None
        minDistance = 0.0
        maxDistance = max(float(maxDistance), 0.0)
        for axis in range(3):
            ray = direction[axis]
            start = origin[axis]
            minValue = boxMin[axis]
            maxValue = boxMax[axis]
            if abs(ray) <= 0.000001:
                if start < minValue or start > maxValue:
                    return None
                continue
            nearDistance = (minValue - start) / ray
            farDistance = (maxValue - start) / ray
            if nearDistance > farDistance:
                nearDistance, farDistance = farDistance, nearDistance
            minDistance = max(minDistance, nearDistance)
            maxDistance = min(maxDistance, farDistance)
            if minDistance > maxDistance:
                return None
        return minDistance

    def _getRayTargetHitPosition(self, origin, direction, targetId):
        origin = self._toVec3(origin)
        direction = self._normalizeVec3(direction)
        footPos = self._toVec3(self._getFootPos(targetId))
        if not origin or not direction or not footPos:
            return None
        if self._isPlayerTarget(targetId):
            bodyHeight = (
                HEADSHOT_PLAYER_SNEAKING_BODY_HEIGHT
                if self._isPlayerSneaking(targetId)
                else HEADSHOT_PLAYER_BODY_HEIGHT
            )
            halfWidth = HEADSHOT_PLAYER_BODY_HALF_WIDTH
        else:
            collisionSize = self._getCollisionSize(targetId)
            if not collisionSize:
                collisionSize = (
                    HEADSHOT_PLAYER_BODY_HALF_WIDTH * 2.0,
                    HEADSHOT_PLAYER_BODY_HEIGHT,
                )
            halfWidth = collisionSize[0] * 0.5
            bodyHeight = collisionSize[1]
        hitDistance = self._intersectRayAabbDistance(
            origin,
            direction,
            (
                footPos[0] - halfWidth,
                footPos[1],
                footPos[2] - halfWidth,
            ),
            (
                footPos[0] + halfWidth,
                footPos[1] + bodyHeight,
                footPos[2] + halfWidth,
            ),
            HEADSHOT_RAY_MAX_DISTANCE
        )
        if hitDistance is None:
            return None
        return tuple(
            origin[index] + direction[index] * hitDistance
            for index in range(3)
        )

    def _getPlayerViewRayHitPosition(self, attackerId, targetId):
        return self._getRayTargetHitPosition(
            self._getViewRayOrigin(attackerId),
            self._getViewDirection(attackerId),
            targetId,
        )

    def _getViewRayDistance(self, origin, targetId):
        targetPos = self._toVec3(self._getFootPos(targetId))
        if not origin or not targetPos:
            return HEADSHOT_RAY_MAX_DISTANCE
        distance = math.sqrt(sum(
            (origin[index] - targetPos[index]) ** 2
            for index in range(3)
        )) + 3.0
        return min(HEADSHOT_RAY_MAX_DISTANCE, max(1.0, distance))

    def _getDistanceAlongRay(self, origin, direction, hitPos):
        origin = self._toVec3(origin)
        direction = self._normalizeVec3(direction)
        hitPos = self._toVec3(hitPos)
        if not origin or not direction or not hitPos:
            return None
        return sum(
            (hitPos[index] - origin[index]) * direction[index]
            for index in range(3)
        )

    def _queryViewRayTargetHit(self, attackerId, targetId, args=None):
        origin = self._getViewRayOrigin(attackerId)
        direction = self._normalizeVec3(self._getViewDirection(attackerId))
        if not origin or not direction:
            return None
        targetHitPos = self._getPlayerViewRayHitPosition(attackerId, targetId)
        targetDistance = self._getDistanceAlongRay(origin, direction, targetHitPos)
        if targetDistance is None or targetDistance < 0.0:
            return None
        try:
            dimensionId = EngineCompFactory.CreateDimension(attackerId).GetEntityDimensionId()
            rayResult = serverApi.getEntitiesOrBlockFromRay(
                dimensionId,
                origin,
                direction,
                self._getViewRayDistance(origin, targetId),
                True,
                serverApi.GetMinecraftEnum().RayFilterType.BothEntitiesAndBlock
            )
        except Exception:
            return None
        args = args if isinstance(args, dict) else {}
        ignoredIds = set((str(attackerId),))
        projectileId = args.get('projectileId') or args.get('ProjectileId')
        if projectileId:
            ignoredIds.add(str(projectileId))
        for hitInfo in rayResult or ():
            if not isinstance(hitInfo, dict):
                continue
            hitType = str(hitInfo.get('type') or '').lower()
            if hitType not in ('block', 'entity'):
                continue
            entityId = None
            if hitType == 'entity':
                entityId = hitInfo.get('entityId') or hitInfo.get('id')
                if not entityId or str(entityId) in ignoredIds:
                    continue
                if str(entityId) == str(targetId):
                    continue
            hitDistance = self._getDistanceAlongRay(
                origin,
                direction,
                hitInfo.get('hitPos')
            )
            if hitDistance is None:
                return None
            if hitDistance < targetDistance - 0.0001:
                return None
        return {
            'type': 'Entity',
            'entityId': targetId,
            'hitPos': targetHitPos,
            'distance': targetDistance,
        }

    def _isPlayerHeadshotPosition(self, targetId, hitPos):
        footPos = self._toVec3(self._getFootPos(targetId))
        hitPos = self._toVec3(hitPos)
        if not footPos or not hitPos:
            return False
        if self._isPlayerTarget(targetId):
            minHeight, maxHeight = (
                HEADSHOT_SNEAKING_HEIGHT
                if self._isPlayerSneaking(targetId)
                else HEADSHOT_STANDING_HEIGHT
            )
        else:
            collisionSize = self._getCollisionSize(targetId)
            height = collisionSize[1] if collisionSize else HEADSHOT_PLAYER_BODY_HEIGHT
            minHeight = height * HEADSHOT_ENTITY_TOP_RATIO
            maxHeight = height
        relativeHeight = hitPos[1] - footPos[1]
        epsilon = 0.0001
        return minHeight - epsilon <= relativeHeight <= maxHeight + epsilon

    def _detectViewRayHeadshot(self, attackerId, targetId, args=None):
        if not attackerId or not targetId:
            return False
        snapshot = self._getRecentAimSnapshot(attackerId)
        if snapshot:
            hitPos = self._getRayTargetHitPosition(
                snapshot.get('Origin'),
                snapshot.get('Direction'),
                targetId,
            )
            if hitPos and self._isPlayerHeadshotPosition(targetId, hitPos):
                return True
        hitPos = self._getPlayerViewRayHitPosition(attackerId, targetId)
        return bool(hitPos and self._isPlayerHeadshotPosition(targetId, hitPos))

    def _getItemIdentifier(self, itemDict):
        if not isinstance(itemDict, dict):
            return ''
        for key in ('newItemName', 'itemName', 'identifier', 'itemIdentifier', 'fullName', 'name'):
            value = itemDict.get(key)
            if value:
                return str(value)
        return ''

    def _getItemAux(self, itemDict):
        if not isinstance(itemDict, dict):
            return 0
        for key in ('newAuxValue', 'auxValue', 'aux', 'itemAux'):
            if key not in itemDict:
                continue
            try:
                return int(itemDict.get(key) or 0)
            except Exception:
                pass
        return 0

    def _getCarriedWeaponContext(self, playerId):
        if not playerId:
            return {}
        try:
            itemComp = EngineCompFactory.CreateItem(playerId)
            itemDict = itemComp.GetPlayerItem(
                serverApi.GetMinecraftEnum().ItemPosType.CARRIED,
                0,
                True
            )
        except Exception:
            itemComp = None
            itemDict = None
        itemId = self._getItemIdentifier(itemDict)
        if not itemId or itemId in ('air', 'minecraft:air'):
            return {
                'WeaponId': 'minecraft:air',
                'WeaponAux': 0,
                'WeaponName': u'徒手',
            }
        aux = self._getItemAux(itemDict)
        context = {
            'WeaponId': itemId,
            'WeaponAux': aux,
        }
        if isinstance(itemDict, dict) and itemDict.get('extraId'):
            context['WeaponExtraId'] = str(itemDict.get('extraId'))
        if itemComp:
            try:
                customName = itemComp.GetCustomName(itemDict)
                if customName:
                    context['WeaponCustomName'] = customName
            except Exception:
                pass
            try:
                enchanted = bool(
                    itemDict.get('enchantData') or itemDict.get('modEnchantData')
                ) if isinstance(itemDict, dict) else False
                basicInfo = itemComp.GetItemBasicInfo(itemId, aux, enchanted)
                if isinstance(basicInfo, dict) and basicInfo.get('itemName'):
                    context['WeaponName'] = basicInfo.get('itemName')
            except Exception:
                pass
        registeredName = self._registeredWeaponNames.get(itemId)
        if registeredName:
            context['WeaponName'] = registeredName
            context['WeaponNameProvided'] = True
        return context

    def _copyWeaponContext(self, context):
        if not isinstance(context, dict):
            return {}
        keys = (
            'WeaponId',
            'WeaponAux',
            'WeaponName',
            'WeaponNameProvided',
            'WeaponCustomName',
            'WeaponExtraId',
        )
        return dict((key, context[key]) for key in keys if key in context)

    def _resolvePlayerFromEntity(self, entityId):
        if not entityId:
            return None
        if self._isPlayer(entityId):
            return entityId
        projectileContext = self._projectileContexts.get(str(entityId))
        if isinstance(projectileContext, dict):
            ownerId = projectileContext.get('AttackerId')
            if self._isPlayer(ownerId):
                return ownerId
        try:
            sourceId = EngineCompFactory.CreateBulletAttributes(entityId).GetSourceEntityId()
            if self._isPlayer(sourceId):
                return sourceId
        except Exception:
            pass
        return None

    def _resolveDamageSource(self, args):
        args = args if isinstance(args, dict) else {}
        projectileId = args.get('projectileId') or args.get('ProjectileId')
        if projectileId:
            projectileContext = self._projectileContexts.get(str(projectileId))
            if isinstance(projectileContext, dict):
                attackerId = projectileContext.get('AttackerId')
                if self._isPlayer(attackerId):
                    return attackerId, self._copyWeaponContext(projectileContext)
            attackerId = self._resolvePlayerFromEntity(projectileId)
            if attackerId:
                return attackerId, self._getCarriedWeaponContext(attackerId)
        for key in ('srcId', 'attacker', 'AttackerId', 'attackerId', 'ownerId', 'spawnerId'):
            sourceId = args.get(key)
            attackerId = self._resolvePlayerFromEntity(sourceId)
            if attackerId:
                sourceContext = self._projectileContexts.get(str(sourceId), {})
                weaponContext = self._copyWeaponContext(sourceContext)
                if not weaponContext:
                    weaponContext = self._getCarriedWeaponContext(attackerId)
                return attackerId, weaponContext
        return None, {}

    def _recordDamageContext(self, attackerId, targetId, weaponContext=None, args=None):
        if not attackerId or not targetId or not self._isPlayer(attackerId):
            return False
        args = args if isinstance(args, dict) else {}
        now = time.time()
        self._cleanupState(now)
        key = str(targetId)
        existing = self._damageContexts.get(key, {})
        if not isinstance(existing, dict) or existing.get('ExpireAt', 0.0) <= now:
            existing = {}
        targetType = (
            args.get('TargetType') or args.get('targetType') or
            args.get('EntityType') or args.get('entityType') or
            self._getEntityType(targetId) or existing.get('TargetType') or ''
        )
        targetName = (
            args.get('TargetName') or args.get('targetName') or
            self._getEntityName(targetId) or existing.get('TargetName') or ''
        )
        targetMaxHealth = args.get('TargetMaxHealth')
        if targetMaxHealth is None:
            targetMaxHealth = args.get('targetMaxHealth')
        if targetMaxHealth is None:
            targetMaxHealth = self._getMaxHealth(targetId)
        if targetMaxHealth is None:
            targetMaxHealth = existing.get('TargetMaxHealth')
        targetIsPlayer = bool(
            self._isPlayer(targetId) or
            targetType == 'minecraft:player' or
            existing.get('TargetIsPlayer')
        )
        context = {
            'AttackerId': attackerId,
            'TargetId': targetId,
            'TargetType': targetType,
            'TargetName': targetName,
            'TargetMaxHealth': targetMaxHealth,
            'TargetIsPlayer': targetIsPlayer,
            'RecordedAt': now,
            'ExpireAt': now + DAMAGE_CONTEXT_SECONDS,
        }
        targetPos = self._toVec3(self._getFootPos(targetId))
        if targetPos:
            context['TargetPos'] = targetPos
        elif existing.get('TargetPos'):
            context['TargetPos'] = existing.get('TargetPos')
        targetDimension = self._getDimensionId(targetId)
        if targetDimension is not None:
            context['TargetDimension'] = targetDimension
        elif existing.get('TargetDimension') is not None:
            context['TargetDimension'] = existing.get('TargetDimension')
        context.update(self._copyWeaponContext(weaponContext or self._getCarriedWeaponContext(attackerId)))
        explicitHeadshot = 'HeadShot' in args or 'headshot' in args
        headshotProvided = bool(
            args.get('HeadShotProvided')
            if 'HeadShotProvided' in args
            else explicitHeadshot
        )
        if explicitHeadshot:
            if 'HeadShot' in args:
                context['HeadShot'] = bool(args.get('HeadShot'))
            else:
                context['HeadShot'] = bool(args.get('headshot'))
            context['HeadShotProvided'] = headshotProvided
        elif existing.get('AttackerId') == attackerId:
            context['HeadShot'] = bool(existing.get('HeadShot'))
            context['HeadShotProvided'] = bool(existing.get('HeadShotProvided'))
        else:
            context['HeadShot'] = False
            context['HeadShotProvided'] = False
        projectileId = args.get('projectileId') or args.get('ProjectileId')
        if projectileId:
            context['ProjectileId'] = projectileId
        for sourceKey, targetKey in (
            ('WeaponId', 'WeaponId'),
            ('weaponId', 'WeaponId'),
            ('WeaponAux', 'WeaponAux'),
            ('weaponAux', 'WeaponAux'),
            ('WeaponCustomName', 'WeaponCustomName'),
            ('weaponCustomName', 'WeaponCustomName'),
            ('WeaponExtraId', 'WeaponExtraId'),
            ('weaponExtraId', 'WeaponExtraId'),
        ):
            if args.get(sourceKey) is not None:
                context[targetKey] = args.get(sourceKey)
        explicitWeaponName = args.get('WeaponName') or args.get('weaponName')
        if explicitWeaponName:
            context['WeaponName'] = explicitWeaponName
            context['WeaponNameProvided'] = True
        damage = self._getDamageValue(args)
        if damage is not None:
            context['Damage'] = damage
            sameAttacker = bool(
                existing and
                str(existing.get('AttackerId')) == str(attackerId)
            )
            previousTotal = 0.0
            if sameAttacker:
                try:
                    previousTotal = float(existing.get('TotalDamage', existing.get('Damage', 0.0)) or 0.0)
                except Exception:
                    previousTotal = 0.0
            context['TotalDamage'] = previousTotal + float(damage)
            context['LastDamageAt'] = now
        elif existing and str(existing.get('AttackerId')) == str(attackerId):
            if existing.get('TotalDamage') is not None:
                context['TotalDamage'] = existing.get('TotalDamage')
            if existing.get('Damage') is not None:
                context['Damage'] = existing.get('Damage')
            if existing.get('LastDamageAt') is not None:
                context['LastDamageAt'] = existing.get('LastDamageAt')
        if args.get('LethalDamage'):
            context['LethalDamage'] = True
        if args.get('PredictedHealth') is not None:
            try:
                context['PredictedHealth'] = float(args.get('PredictedHealth'))
            except Exception:
                pass
        distance = self._getDistance(attackerId, targetId)
        if distance is not None:
            context['Distance'] = distance
        self._damageContexts[key] = context
        return True

    def _getRecentDamageContext(self, targetId):
        if not targetId:
            return None
        now = time.time()
        self._cleanupState(now)
        context = self._damageContexts.get(str(targetId))
        if not isinstance(context, dict) or context.get('ExpireAt', 0.0) <= now:
            return None
        return context

    def _cleanupState(self, now):
        for targetId, expireAt in list(self._deathLocks.items()):
            if expireAt <= now:
                self._deathLocks.pop(targetId, None)
        for key, lastAt in list(self._hitMarkerTimes.items()):
            if now - lastAt > HIT_MARKER_DEDUP_SECONDS:
                self._hitMarkerTimes.pop(key, None)
        for targetId, context in list(self._damageContexts.items()):
            if not isinstance(context, dict) or context.get('ExpireAt', 0.0) <= now:
                self._damageContexts.pop(targetId, None)
        for projectileId, context in list(self._projectileContexts.items()):
            if not isinstance(context, dict) or context.get('ExpireAt', 0.0) <= now:
                self._projectileContexts.pop(projectileId, None)
        for playerId, snapshot in list(self._aimSnapshots.items()):
            if not isinstance(snapshot, dict) or snapshot.get('ExpireAt', 0.0) <= now:
                self._aimSnapshots.pop(playerId, None)
        aimSnapshotTimes = getattr(self, '_aimSnapshotTimes', {})
        for playerId, lastAt in list(aimSnapshotTimes.items()):
            if now - lastAt > AIM_SNAPSHOT_MAX_AGE_SECONDS * 4.0:
                aimSnapshotTimes.pop(playerId, None)
        self._aimSnapshotTimes = aimSnapshotTimes

    def _isDeathLocked(self, targetId):
        if not targetId:
            return False
        now = time.time()
        self._cleanupState(now)
        key = str(targetId)
        if self._deathLocks.get(key, 0.0) > now:
            return True
        self._deathLocks[key] = now + DEATH_LOCK_SECONDS
        return False

    def _queuePendingLethalHit(
        self,
        attackerId,
        targetId,
        args,
        health,
        damage,
        eventArgs=None,
    ):
        if not attackerId or not targetId:
            return False
        nowTick = int(self._serverTick)
        self._pendingLethalHits[str(targetId)] = {
            'AttackerId': attackerId,
            'TargetId': targetId,
            'TargetType': self._resolveKillTargetType(targetId, args),
            'Args': dict(args) if isinstance(args, dict) else {},
            # Keep the engine event dict itself. Other listeners can legally
            # change damage after this callback, and the final value is what
            # the next-tick confirmation must evaluate.
            'EventArgs': eventArgs if isinstance(eventArgs, dict) else args,
            'HealthBefore': health,
            'InitialDamage': damage,
            'ReadyTick': nowTick + PENDING_LETHAL_CONFIRM_TICKS,
            'ExpireTick': nowTick + PENDING_LETHAL_EXPIRE_TICKS,
        }
        return True

    def _candidateDamageIsLethal(self, candidate):
        if not isinstance(candidate, dict):
            return False
        eventArgs = candidate.get('EventArgs')
        damage = self._getDamageValue(eventArgs)
        if damage is None:
            damage = candidate.get('InitialDamage')
        healthBefore = candidate.get('HealthBefore')
        if healthBefore is not None:
            try:
                if float(healthBefore) <= 0.0:
                    return True
            except Exception:
                pass
        return self._willDamageKill(
            candidate.get('TargetId'),
            damage,
            healthBefore,
        )

    def _confirmPendingLethalHit(self, targetId, removed=False):
        key = str(targetId)
        candidate = self._pendingLethalHits.get(key)
        if not isinstance(candidate, dict):
            return False
        if not self._candidateDamageIsLethal(candidate):
            self._pendingLethalHits.pop(key, None)
            return False
        healthBefore = candidate.get('HealthBefore')
        healthAfter = None if removed else self._getHealth(targetId)
        healthDropped = bool(removed)
        if healthAfter is not None:
            try:
                healthAfter = float(healthAfter)
                healthDropped = healthAfter <= 0.0
                if healthBefore is not None:
                    healthDropped = bool(
                        healthDropped or
                        healthAfter < float(healthBefore) - 0.0001
                    )
            except Exception:
                healthDropped = False
        if not healthDropped:
            if int(self._serverTick) < int(candidate.get('ExpireTick', 0)):
                return False
            self._pendingLethalHits.pop(key, None)
            return False
        self._pendingLethalHits.pop(key, None)
        confirmArgs = dict(candidate.get('Args') or {})
        confirmArgs['LethalDamage'] = True
        if healthAfter is not None:
            confirmArgs['ConfirmedHealth'] = healthAfter
        return self._handleDeath(
            candidate.get('AttackerId'),
            candidate.get('TargetId'),
            confirmArgs,
        )

    def _processPendingLethalHits(self):
        handled = False
        for targetKey, candidate in list(self._pendingLethalHits.items()):
            if not isinstance(candidate, dict):
                self._pendingLethalHits.pop(targetKey, None)
                continue
            if int(candidate.get('ReadyTick', 0)) > int(self._serverTick):
                continue
            handled = self._confirmPendingLethalHit(
                candidate.get('TargetId') or targetKey
            ) or handled
        return handled

    def OnMobDieEvent(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        return self._handleDeath(args.get('attacker'), args.get('id'), args)

    def OnPlayerDieEvent(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        # The kill HUD belongs to the local attacker, but a player can die
        # while an earlier kill animation is still on screen.  Send a small
        # client-only cleanup signal to the dead player before handling the
        # death as a possible kill for somebody else.
        targetId = args.get('id') or args.get('playerId') or args.get('PlayerId')
        self.NotifyPlayerDeathCleanup(targetId)
        return self._handleDeath(args.get('attacker'), targetId, args)

    def NotifyPlayerDeathCleanup(self, targetId):
        if not targetId:
            return False
        try:
            self.NotifyToClient(targetId, PLAYER_DEATH_CLEANUP_EVENT, {
                'EntityId': targetId,
            })
            return True
        except Exception as error:
            print('[KillBroadcast] notify player death cleanup error:', error)
            return False

    def NotifyHeadshotSoundToNearbyClients(
        self,
        attackerId,
        targetId,
        soundPos=None,
        targetDimension=None,
    ):
        if not targetId:
            return False
        soundPos = self._toVec3(soundPos) or self._toVec3(self._getFootPos(targetId))
        if targetDimension is None:
            targetDimension = self._getDimensionId(targetId)
        try:
            players = serverApi.GetPlayerList() or []
        except Exception:
            players = []
        notified = False
        for receiverId in players:
            if not receiverId or str(receiverId) == str(attackerId):
                continue
            isVictim = str(receiverId) == str(targetId)
            if not isVictim:
                if soundPos is None or targetDimension is None:
                    continue
                if self._getDimensionId(receiverId) != targetDimension:
                    continue
                receiverPos = self._toVec3(self._getFootPos(receiverId))
                if not receiverPos:
                    continue
                distanceSq = sum(
                    (float(receiverPos[index]) - float(soundPos[index])) ** 2
                    for index in range(3)
                )
                if distanceSq > HEADSHOT_SOUND_RADIUS_SQ:
                    continue
            packet = {
                'AttackerId': attackerId,
                'EntityId': targetId,
            }
            if soundPos:
                packet['Pos'] = soundPos
            try:
                self.NotifyToClient(receiverId, HEADSHOT_SOUND_EVENT, packet)
                notified = True
            except Exception as error:
                print('[KillBroadcast] notify nearby headshot sound error:', receiverId, error)
        return notified

    def _handleDeath(self, attackerId, targetId, args):
        if not targetId:
            return False
        args = args if isinstance(args, dict) else {}
        recentContext = self._getRecentDamageContext(targetId)
        resolveTargetType = getattr(self, '_resolveKillTargetType', None)
        targetType = (
            resolveTargetType(targetId, args, recentContext)
            if resolveTargetType else
            (recentContext or {}).get('TargetType') or self._getEntityType(targetId)
        )
        isManagedType = getattr(self, '_isExternallyManagedEntityType', None)
        externalSource = args.get('Source') == 'external'
        externallyManaged = bool(isManagedType and isManagedType(targetType))
        if not externalSource and externallyManaged:
            # The external owner is authoritative for registered entity types.
            # Keep the recent damage context so a later ReportExternalKill call
            # can reuse weapon, target and headshot evidence.
            self._pendingLethalHits.pop(str(targetId), None)
            return False
        resolvedAttackerId, weaponContext = self._resolveDamageSource({
            'srcId': attackerId,
            'projectileId': args.get('projectileId') or args.get('ProjectileId'),
        })
        if recentContext and (
            not resolvedAttackerId or
            str(recentContext.get('AttackerId')) == str(resolvedAttackerId)
        ):
            attackerId = recentContext.get('AttackerId')
            weaponContext = self._copyWeaponContext(recentContext)
        else:
            attackerId = resolvedAttackerId
        if not attackerId or str(attackerId) == str(targetId):
            return False
        if (
            self.tsgunsLoaded and
            IsTsGunsDamageAttributed(attackerId, targetId) and
            not (externalSource and externallyManaged)
        ):
            return False
        if not self._isPlayer(attackerId):
            return False
        if self._isDeathLocked(targetId):
            self._pendingLethalHits.pop(str(targetId), None)
            return False
        self._pendingLethalHits.pop(str(targetId), None)
        if not weaponContext:
            weaponContext = self._getCarriedWeaponContext(attackerId)
        headshotResolved = 'HeadShot' in args or 'headshot' in args
        if 'HeadShot' in args:
            headshot = bool(args.get('HeadShot'))
        else:
            headshot = bool(args.get('headshot')) if headshotResolved else False
        if not headshotResolved and recentContext:
            if recentContext.get('HeadShotProvided'):
                headshot = bool(recentContext.get('HeadShot'))
                headshotResolved = True
            elif recentContext.get('HeadShot'):
                headshot = True
                headshotResolved = True
        if not headshotResolved:
            getHitPosition = getattr(self, '_getHitPosition', None)
            hitPos = getHitPosition(args) if getHitPosition else None
            isHeadshotPosition = getattr(self, '_isPlayerHeadshotPosition', None)
            headshot = bool(
                (isHeadshotPosition and isHeadshotPosition(targetId, hitPos)) or
                self._detectViewRayHeadshot(attackerId, targetId, args)
            )
        targetPos = (recentContext or {}).get('TargetPos') or self._getFootPos(targetId)
        targetDimension = (recentContext or {}).get('TargetDimension')
        payload = {
            'HeadShot': headshot,
            'EntityId': targetId,
            'Source': args.get('Source') or KILL_SOURCE_GENERIC,
            'TargetType': targetType,
            'TargetName': (recentContext or {}).get('TargetName') or self._getEntityName(targetId),
            'TargetIsPlayer': bool(
                (recentContext or {}).get('TargetIsPlayer') or self._isPlayer(targetId)
            ),
        }
        targetMaxHealth = (recentContext or {}).get('TargetMaxHealth')
        if targetMaxHealth is None:
            targetMaxHealth = self._getMaxHealth(targetId)
        if targetMaxHealth is not None:
            payload['TargetMaxHealth'] = targetMaxHealth
        payload.update(self._copyWeaponContext(weaponContext))
        if args.get('WeaponName') or args.get('weaponName'):
            payload['WeaponName'] = args.get('WeaponName') or args.get('weaponName')
            payload['WeaponNameProvided'] = True
        distance = (recentContext or {}).get('Distance')
        if distance is None:
            distance = self._getDistance(attackerId, targetId)
        if distance is not None:
            payload['Distance'] = distance
        totalDamage = (recentContext or {}).get('TotalDamage')
        if totalDamage is None:
            totalDamage = (recentContext or {}).get('Damage')
        if totalDamage is not None:
            payload['Damage'] = totalDamage
        try:
            self.NotifyToClient(attackerId, CREATE_KILL_EVENT, payload)
        except Exception as error:
            # _isDeathLocked reserved this target for the current attempt.
            # Release it on delivery failure so an external owner can retry.
            self._deathLocks.pop(str(targetId), None)
            print('[KillBroadcast] notify kill error:', error)
            return False
        if headshot:
            self.NotifyHeadshotSoundToNearbyClients(
                attackerId,
                targetId,
                targetPos,
                targetDimension,
            )
        self._damageContexts.pop(str(targetId), None)
        return True

    def OnActorHurtServerEvent(self, args):
        """Keep attacker attribution for damage types omitted by ActuallyHurt."""
        if not self.enabled or not isinstance(args, dict):
            return False
        targetId = args.get('entityId')
        attackerId, weaponContext = self._resolveDamageSource(args)
        if not attackerId or not targetId:
            return False
        externallyManaged = self._isExternallyManagedTarget(targetId, args)
        if (
            self.tsgunsLoaded and
            IsTsGunsDamageAttributed(attackerId, targetId) and
            not externallyManaged
        ):
            return False
        contextArgs = dict(args)
        for key in ('damage', 'Damage', 'amount', 'Amount'):
            contextArgs.pop(key, None)
        return self._recordDamageContext(
            attackerId, targetId, weaponContext, contextArgs)

    def OnActuallyHurtServerEvent(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        targetId = args.get('entityId')
        attackerId, weaponContext = self._resolveDamageSource(args)
        if not attackerId or not targetId:
            return False
        externallyManaged = self._isExternallyManagedTarget(targetId, args)
        tsgunsAttributed = bool(
            self.tsgunsLoaded and
            IsTsGunsDamageAttributed(attackerId, targetId)
        )
        if tsgunsAttributed and not externallyManaged:
            return False
        health = self._getHealth(targetId)
        damage = self._getDamageValue(args)
        predictedHealth = self._predictHealthAfterDamage(targetId, damage, health)
        lethalDamage = self._willDamageKill(targetId, damage, health)
        contextArgs = dict(args)
        contextArgs['LethalDamage'] = False
        if predictedHealth is not None:
            contextArgs['PredictedHealth'] = predictedHealth
        recentContext = self._getRecentDamageContext(targetId) or {}
        hasExplicitHeadshot = self._hasExplicitHeadshot(args)
        contextArgs['HeadShotProvided'] = bool(hasExplicitHeadshot)
        hitPos = self._getHitPosition(args)
        if not hasExplicitHeadshot:
            projectileId = args.get('projectileId') or args.get('ProjectileId')
            recentProjectileId = recentContext.get('ProjectileId')
            projectileHeadshot = bool(
                projectileId and
                recentProjectileId and
                str(projectileId) == str(recentProjectileId) and
                recentContext.get('HeadShot')
            )
            detectedHeadshot = bool(
                projectileHeadshot or
                self._isPlayerHeadshotPosition(targetId, hitPos) or
                self._detectViewRayHeadshot(attackerId, targetId, args)
            )
            contextArgs['HeadShot'] = detectedHeadshot
        contextRecorded = self._recordDamageContext(
            attackerId, targetId, weaponContext, contextArgs)
        recentContext = self._getRecentDamageContext(targetId) or {}
        externallyManaged = self._isExternallyManagedTarget(
            targetId, contextArgs, recentContext)
        if tsgunsAttributed:
            # TsGuns owns the ordinary hit marker. For an externally managed
            # target we only retain context for the later authoritative report.
            return contextRecorded
        key = '%s:%s' % (attackerId, targetId)
        now = time.time()
        self._cleanupState(now)
        # Predict a lethal hit from the current health and the effective
        # damage before relying on a separate death event.
        killed = bool(not externallyManaged and (
            (health is not None and health <= 0.0) or
            lethalDamage
        ))
        payload = {
            'EntityId': targetId,
            'HeadShot': bool(recentContext.get('HeadShot')),
            'Killed': killed,
        }
        hitMarkerSent = False
        if now - self._hitMarkerTimes.get(key, 0.0) >= HIT_MARKER_DEDUP_SECONDS:
            self._hitMarkerTimes[key] = now
            try:
                self.NotifyToClient(attackerId, HIT_MARKER_EVENT, payload)
                hitMarkerSent = True
            except Exception as error:
                print('[KillBroadcast] notify hit marker error:', error)
        killQueued = False
        if killed:
            killQueued = self._queuePendingLethalHit(
                attackerId,
                targetId,
                contextArgs,
                health,
                damage,
                args,
            )
        return hitMarkerSent or killQueued

    def OnSpawnProjectileServerEvent(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        projectileId = args.get('projectileId') or args.get('id')
        attackerId = args.get('spawnerId') or args.get('srcId')
        attackerId = self._resolvePlayerFromEntity(attackerId)
        if not projectileId or not attackerId:
            return False
        context = {
            'AttackerId': attackerId,
            'ProjectileId': projectileId,
            'ProjectileType': args.get('projectileIdentifier') or '',
            'ExpireAt': time.time() + PROJECTILE_CONTEXT_SECONDS,
        }
        context.update(self._getCarriedWeaponContext(attackerId))
        self._projectileContexts[str(projectileId)] = context
        return True

    def OnProjectileCritHitEvent(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        projectileId = args.get('id') or args.get('projectileId')
        targetId = args.get('targetId') or args.get('entityId')
        attackerId, weaponContext = self._resolveDamageSource({'projectileId': projectileId})
        if not attackerId or not targetId:
            return False
        if self.tsgunsLoaded and IsTsGunsDamageAttributed(attackerId, targetId):
            return False
        return self._recordDamageContext(
            attackerId,
            targetId,
            weaponContext,
            {
                'HeadShot': True,
                'ProjectileId': projectileId,
            }
        )

    def OnProjectileDoHitEffectEvent(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        if str(args.get('hitTargetType') or '').upper() != 'ENTITY':
            return False
        projectileId = args.get('id') or args.get('projectileId')
        targetId = args.get('targetId') or args.get('entityId')
        attackerId, weaponContext = self._resolveDamageSource({'projectileId': projectileId})
        if not attackerId or not targetId:
            return False
        if self.tsgunsLoaded and IsTsGunsDamageAttributed(attackerId, targetId):
            return False
        hitPos = self._getHitPosition(args)
        contextArgs = {
            'HeadShot': self._isPlayerHeadshotPosition(targetId, hitPos),
            'ProjectileId': projectileId,
        }
        return self._recordDamageContext(attackerId, targetId, weaponContext, contextArgs)

    def RegisterWeaponDisplayName(self, itemId, displayName):
        if not itemId or not displayName:
            return False
        self._registeredWeaponNames[str(itemId)] = displayName
        return True

    def RegisterExternallyManagedEntityTypes(self, args, entityTypes=None):
        """Disable automatic kill confirmation for entity type identifiers.

        This method intentionally works before ``self.enabled`` becomes true,
        allowing another addon to register ownership during server loading.
        Repeated registration by the same owner is idempotent, and an entity
        type stays managed until every owner has unregistered it.
        """
        ownerId, entityTypes = self._parseManagedEntityTypeArgs(args, entityTypes)
        if not ownerId or not entityTypes:
            return False
        registry = getattr(self, '_externallyManagedEntityTypes', {})
        for entityType in entityTypes:
            owners = registry.setdefault(entityType, set())
            owners.add(ownerId)
        self._externallyManagedEntityTypes = registry
        return True

    def UnregisterExternallyManagedEntityTypes(self, args, entityTypes=None):
        ownerId, normalizedTypes = self._parseManagedEntityTypeArgs(args, entityTypes)
        if not ownerId:
            return False
        hasTypeFilter = entityTypes is not None
        if isinstance(args, dict):
            hasTypeFilter = any(key in args for key in (
                'EntityTypes', 'entityTypes',
                'EntityIdentifiers', 'entityIdentifiers',
                'Identifiers', 'identifiers',
            ))
        if hasTypeFilter and not normalizedTypes:
            return False
        registry = getattr(self, '_externallyManagedEntityTypes', {})
        targetTypes = normalizedTypes if hasTypeFilter else list(registry.keys())
        changed = False
        for entityType in targetTypes:
            owners = registry.get(entityType)
            if not owners or ownerId not in owners:
                continue
            owners.discard(ownerId)
            changed = True
            if not owners:
                registry.pop(entityType, None)
        self._externallyManagedEntityTypes = registry
        return changed

    def GetExternallyManagedEntityTypes(self, ownerId=None):
        ownerId = self._normalizeExternalOwnerId(ownerId) if ownerId else ''
        registry = getattr(self, '_externallyManagedEntityTypes', {})
        if not ownerId:
            return sorted(
                entityType for entityType, owners in registry.items() if owners)
        return sorted(
            entityType for entityType, owners in registry.items()
            if ownerId in owners
        )

    def IsExternallyManagedEntityType(self, entityType):
        """Public read-only query for weapon or kill-UI provider addons."""
        return self._isExternallyManagedEntityType(entityType)

    def GetExternalKillApiInfo(self):
        return {
            'Version': 1,
            'ManagedEntityTypes': self.GetExternallyManagedEntityTypes(),
            'SupportsNativeEventArgs': True,
            'SupportsOptionalHeadShot': True,
            'SupportsManagedTypeQuery': True,
        }

    def RecordExternalDamageSource(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        targetId = (
            args.get('TargetId') or args.get('targetId') or
            args.get('EntityId') or args.get('entityId')
        )
        attackerId, weaponContext = self._resolveDamageSource(args)
        if not attackerId or not targetId:
            return False
        recentContext = self._getRecentDamageContext(targetId)
        externallyManaged = self._isExternallyManagedTarget(
            targetId, args, recentContext)
        if (
            self.tsgunsLoaded and
            IsTsGunsDamageAttributed(attackerId, targetId) and
            not externallyManaged
        ):
            return False
        if not weaponContext:
            weaponContext = self._getCarriedWeaponContext(attackerId)
        contextArgs = dict(args)
        if not self._hasExplicitHeadshot(args):
            hitPos = self._getHitPosition(args)
            contextArgs['HeadShot'] = bool(
                self._isPlayerHeadshotPosition(targetId, hitPos) or
                self._detectViewRayHeadshot(attackerId, targetId, args)
            )
            contextArgs['HeadShotProvided'] = False
        else:
            contextArgs['HeadShotProvided'] = True
        return self._recordDamageContext(attackerId, targetId, weaponContext, contextArgs)

    def RecordDamageSource(self, args):
        return self.RecordExternalDamageSource(args)

    def ReportExternalKill(self, args):
        if not self.enabled or not isinstance(args, dict):
            return False
        targetId = (
            args.get('TargetId') or args.get('targetId') or
            args.get('EntityId') or args.get('entityId')
        )
        attackerId, weaponContext = self._resolveDamageSource(args)
        if not attackerId or not targetId or str(attackerId) == str(targetId):
            return False
        recentContext = self._getRecentDamageContext(targetId)
        externallyManaged = self._isExternallyManagedTarget(
            targetId, args, recentContext)
        if (
            self.tsgunsLoaded and
            IsTsGunsDamageAttributed(attackerId, targetId) and
            not externallyManaged
        ):
            return False
        contextArgs = dict(args)
        contextArgs['Source'] = KILL_SOURCE_EXTERNAL
        contextArgs['LethalDamage'] = True
        self._recordDamageContext(attackerId, targetId, weaponContext, contextArgs)
        return self._handleDeath(attackerId, targetId, contextArgs)

    def ConfirmExternalKill(self, args):
        return self.ReportExternalKill(args)

    def OnTargetEntityRemoveEvent(self, args):
        if not isinstance(args, dict):
            return False
        targetId = args.get('id')
        if not targetId:
            return False
        context = self._getRecentDamageContext(targetId)
        if self._isExternallyManagedTarget(targetId, args, context):
            # The live engine type is often unavailable by the time removal is
            # observed. Keep the cached context until its normal TTL so an
            # external owner can still report the confirmed kill afterwards.
            self._pendingLethalHits.pop(str(targetId), None)
            return True
        handled = self._confirmPendingLethalHit(targetId, removed=True)
        if (
            isinstance(context, dict) and
            context.get('LethalDamage') and
            not context.get('TargetIsPlayer') and
            time.time() - float(context.get('RecordedAt', 0.0)) <= CORPSE_KILL_CONTEXT_SECONDS
        ):
            handled = self._handleDeath(
                context.get('AttackerId'),
                targetId,
                {
                    'HeadShot': bool(context.get('HeadShot')),
                    'WeaponName': context.get('WeaponName'),
                },
            )
        self._damageContexts.pop(str(targetId), None)
        return handled or True

    def OnTargetPlayerRespawnFinishServerEvent(self, args):
        if isinstance(args, dict):
            targetId = args.get('playerId') or args.get('id')
            if targetId:
                # Also clean on respawn as a safety net for servers that do
                # not emit PlayerDieEvent for custom death/respawn flows.
                self.NotifyPlayerDeathCleanup(targetId)
                self._deathLocks.pop(str(targetId), None)
                self._pendingLethalHits.pop(str(targetId), None)
                self._damageContexts.pop(str(targetId), None)
                self._enablePlayerCritBox(targetId)
        return True

    def Destroy(self):
        try:
            self.UnListenForEvent(
                MOD_NAMESPACE,
                CLIENT_SYSTEM_NAME,
                AIM_SNAPSHOT_EVENT,
                self,
                self.OnAimSnapshot,
            )
        except Exception:
            pass
        for eventName, callback in (
            ('LoadServerAddonScriptsAfter', self.OnLoadServerAddonScriptsAfter),
            ('OnScriptTickServer', self.OnScriptTickServer),
            ('AddServerPlayerEvent', self.OnAddServerPlayerEvent),
            ('ClientLoadAddonsFinishServerEvent', self.OnClientLoadAddonsFinishServerEvent),
            ('MobDieEvent', self.OnMobDieEvent),
            ('PlayerDieEvent', self.OnPlayerDieEvent),
            ('EntityRemoveEvent', self.OnTargetEntityRemoveEvent),
            ('PlayerRespawnFinishServerEvent', self.OnTargetPlayerRespawnFinishServerEvent),
            ('ActorHurtServerEvent', self.OnActorHurtServerEvent),
            ('ActuallyHurtServerEvent', self.OnActuallyHurtServerEvent),
            ('SpawnProjectileServerEvent', self.OnSpawnProjectileServerEvent),
            ('ProjectileCritHitEvent', self.OnProjectileCritHitEvent),
            ('ProjectileDoHitEffectEvent', self.OnProjectileDoHitEffectEvent),
        ):
            self._unlistenEngineEvent(eventName, callback)
        self._deathLocks = {}
        self._pendingLethalHits = {}
        self._hitMarkerTimes = {}
        self._damageContexts = {}
        self._projectileContexts = {}
        self._aimSnapshots = {}
        self._aimSnapshotTimes = {}
        self._registeredWeaponNames = {}
        self._externallyManagedEntityTypes = {}
        self._playerIdCache = set()
        self._playerIdCacheTick = -1
