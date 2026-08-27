# -*- coding: utf-8 -*-
import time

import mod.client.extraClientApi as clientApi

from ..Compat import IsHideKillSettingsProviderLoaded, IsTsGunsClientLoaded
from ..ModConfig import (
    AIM_SNAPSHOT_EVENT,
    AIM_SNAPSHOT_DIRECTION_DOT_THRESHOLD,
    AIM_SNAPSHOT_HEARTBEAT_SECONDS,
    AIM_SNAPSHOT_INTERVAL_SECONDS,
    AIM_SNAPSHOT_POSITION_EPSILON_SQ,
    CLIENT_SYSTEM_NAME,
    CREATE_KILL_EVENT,
    HEADSHOT_SOUND_EVENT,
    HIT_MARKER_EVENT,
    PLAYER_DEATH_CLEANUP_EVENT,
    MOD_NAMESPACE,
    MOD_RESOURCE_ID,
    SERVER_STATUS_EVENT,
    SERVER_SYSTEM_NAME,
)


ClientSystem = clientApi.GetClientSystemCls()
LocalPlayerId = clientApi.GetLocalPlayerId()
LevelId = clientApi.GetLevelId()
EngineCompFactory = clientApi.GetEngineCompFactory()
GameComp = EngineCompFactory.CreateGame(LevelId)
CameraComp = EngineCompFactory.CreateCamera(LevelId)
UI_RECOVERY_TICKS = 120
UI_RECOVERY_RETRY_INTERVAL_TICKS = 4
LOCAL_DEATH_CHECK_INTERVAL_TICKS = 2
PENDING_FEEDBACK_SECONDS = 2.0
PENDING_FEEDBACK_MAX_COUNT = 16
NATIVE_SETTING_TITLE = u'\u51fb\u6740\u53cd\u9988'
NATIVE_SETTING_ICON = 'textures/ui/killbroadcast_kill_effect/killicon_scrolling_default'
NATIVE_SETTING_BUTTON_ID = 'TpButton'
CSGO_HEADSHOT_SOUND_NAME = 'killbroadcast.kill.csgo.headshot'


class KillBroadcastClientSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.compatibilityState = 'unknown'
        self.serverCompatibilityState = 'unknown'
        self.serverTsGunsLoaded = None
        self.tsgunsLoaded = False
        self.disabledByTsGuns = False
        self.hideKillSettings = False
        self.uiDefinitionsRegistered = False
        self.uiInitialized = False
        self.uiInitFinished = False
        self.nativeSettingRegistered = False
        self._neteaseWindowComp = None
        self._nativeSettingInst = None
        self._headshotAudioComp = None
        self._uiRecoveryTicks = 0
        self._uiRecoveryRetryTicks = 0
        self._pendingFeedback = []
        self._probeTicks = 0
        self._localPlayerDeathCheckTicks = 0
        self._localPlayerDead = False
        self._engineNamespace = clientApi.GetEngineNamespace()
        self._engineSystemName = clientApi.GetEngineSystemName()
        self._nextAimSnapshotTime = 0.0
        self._lastAimSnapshot = None
        self._lastAimSnapshotTime = 0.0
        self._listenLifecycleEvents()
        self.ListenForEvent(
            MOD_NAMESPACE,
            SERVER_SYSTEM_NAME,
            SERVER_STATUS_EVENT,
            self,
            self.OnCompatibilityStatus,
        )

    def _listenLifecycleEvents(self):
        for eventName, callback in (
            ('UiInitFinished', self.OnUiInitFinished),
            ('LoadClientAddonScriptsAfter', self.OnLoadClientAddonScriptsAfter),
            ('DimensionChangeFinishClientEvent', self.OnDimensionChangeFinishClientEvent),
            ('OnScriptTickClient', self.OnScriptTickClient),
            ('OnScriptTickNonChaseFrameClient', self.OnScriptTickNonChaseFrameClient),
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
                print('[KillBroadcast] listen client event error:', eventName, error)

    def _listenFeedbackEvents(self):
        if self.compatibilityState != 'enabled':
            return
        for eventName, callback in (
            (CREATE_KILL_EVENT, self.OnCreateKill),
            (HIT_MARKER_EVENT, self.OnHitMarker),
            (HEADSHOT_SOUND_EVENT, self.OnHeadshotSound),
            (PLAYER_DEATH_CLEANUP_EVENT, self.OnPlayerDeathCleanup),
        ):
            try:
                self.ListenForEvent(
                    MOD_NAMESPACE,
                    SERVER_SYSTEM_NAME,
                    eventName,
                    self,
                    callback,
                )
            except Exception as error:
                print('[KillBroadcast] listen feedback event error:', eventName, error)

    def _unlistenFeedbackEvents(self):
        for eventName, callback in (
            (CREATE_KILL_EVENT, self.OnCreateKill),
            (HIT_MARKER_EVENT, self.OnHitMarker),
            (HEADSHOT_SOUND_EVENT, self.OnHeadshotSound),
            (PLAYER_DEATH_CLEANUP_EVENT, self.OnPlayerDeathCleanup),
        ):
            try:
                self.UnListenForEvent(
                    MOD_NAMESPACE,
                    SERVER_SYSTEM_NAME,
                    eventName,
                    self,
                    callback,
                )
            except Exception:
                pass

    def OnLoadClientAddonScriptsAfter(self, args=None):
        self.ResolveCompatibility('load_finished')

    def OnScriptTickClient(self, args=None):
        if self.compatibilityState == 'unknown':
            self._probeTicks += 1
            if self._probeTicks >= 5:
                self.ResolveCompatibility('tick_fallback')
        if self.compatibilityState == 'enabled':
            self.CheckLocalPlayerDeath()
            self.SendAimSnapshot()
            if self.uiInitialized and not self._getGameUi(False):
                self._startUiRecovery()
            if self._uiRecoveryTicks > 0:
                self._uiRecoveryTicks -= 1
                if self._uiRecoveryRetryTicks > 0:
                    self._uiRecoveryRetryTicks -= 1
                else:
                    if self._recoverUiAfterDimensionChange():
                        self._uiRecoveryTicks = 0
                    else:
                        self._uiRecoveryRetryTicks = UI_RECOVERY_RETRY_INTERVAL_TICKS
        uiNode = self._getGameUi(False) if self.uiInitialized else None
        if uiNode:
            try:
                if hasattr(uiNode, 'Update'):
                    uiNode.Update()
            except Exception as error:
                print('[KillBroadcast] update feedback ui error:', error)

    def OnScriptTickNonChaseFrameClient(self, args=None):
        if not self.uiInitialized:
            return False
        try:
            uiNode = self._getGameUi(False)
            if uiNode and hasattr(uiNode, 'UpdateFrame'):
                return uiNode.UpdateFrame(args)
        except Exception as error:
            print('[KillBroadcast] update feedback frame error:', error)
        return False

    def CheckLocalPlayerDeath(self):
        """Clear the current-life kill count even if a server death event is missed."""
        self._localPlayerDeathCheckTicks += 1
        if self._localPlayerDeathCheckTicks < LOCAL_DEATH_CHECK_INTERVAL_TICKS:
            return False
        self._localPlayerDeathCheckTicks = 0
        try:
            if not GameComp.HasEntity(LocalPlayerId):
                return False
            attrComp = EngineCompFactory.CreateAttr(LocalPlayerId)
            healthType = clientApi.GetMinecraftEnum().AttrType.HEALTH
            health = attrComp.GetAttrValue(healthType)
            if health is None:
                return False
            isDead = float(health) <= 0.0
        except Exception:
            return False
        if not isDead:
            self._localPlayerDead = False
            return False
        if self._localPlayerDead:
            return False
        self._localPlayerDead = True
        return self.OnPlayerDeathCleanup({'Source': 'local_health'})

    def ResolveCompatibility(self, reason=''):
        if self.compatibilityState != 'unknown':
            return self.compatibilityState == 'enabled'
        if self.serverCompatibilityState == 'unknown':
            return False
        tsgunsLoaded = IsTsGunsClientLoaded()
        if tsgunsLoaded is None:
            print('[KillBroadcast][Compat] TsGuns query is not ready; keeping client inactive')
            return False
        providerLoaded = IsHideKillSettingsProviderLoaded()
        self.tsgunsLoaded = bool(tsgunsLoaded or self.serverTsGunsLoaded)
        self.hideKillSettings = self.tsgunsLoaded or providerLoaded is True
        self.compatibilityState = 'enabled'
        self.disabledByTsGuns = False
        self._listenFeedbackEvents()
        mode = 'cooperative' if self.tsgunsLoaded else 'standalone'
        print('[KillBroadcast][Compat] standalone client enabled; mode=%s hide_settings=%s' % (
            mode,
            self.hideKillSettings,
        ))
        if self.uiInitFinished:
            self.RegisterNativeSettingEntry()
        self._createUiIfReady()
        return True

    def OnCompatibilityStatus(self, args):
        if not isinstance(args, dict):
            return False
        self.serverTsGunsLoaded = bool(args.get('TsGunsLoaded') or args.get('Cooperative'))
        if not args.get('Enabled'):
            self.serverCompatibilityState = 'disabled'
            return False
        self.serverCompatibilityState = 'enabled'
        if self.compatibilityState == 'unknown':
            self.ResolveCompatibility('server_status')
        return True

    def OnUiInitFinished(self, args=None):
        self.uiInitFinished = True
        self._registerUiDefinitions()
        self.RegisterNativeSettingEntry()
        self._createUiIfReady()

    def _registerUiDefinitions(self):
        if self.uiDefinitionsRegistered:
            return True
        try:
            clientApi.RegisterUI(
                MOD_NAMESPACE,
                'Game',
                'KillBroadcastScript.Client.UI_Scripts.Game.Game',
                'KillBroadcastGame.Game',
            )
            clientApi.RegisterUI(
                MOD_NAMESPACE,
                'Setting',
                'KillBroadcastScript.Client.UI_Scripts.Setting.Setting',
                'KillBroadcastSetting.Setting',
            )
            self.uiDefinitionsRegistered = True
            return True
        except Exception as error:
            print('[KillBroadcast] register ui error:', error)
            return False

    def _getGameUi(self, recover=False):
        try:
            uiNode = clientApi.GetUI(MOD_NAMESPACE, 'Game')
        except Exception:
            uiNode = None
        if uiNode:
            self.uiInitialized = True
            return uiNode
        self.uiInitialized = False
        if recover:
            return self._createUiIfReady()
        return None

    def _createUiIfReady(self):
        if self.compatibilityState != 'enabled' or not self.uiInitFinished:
            return False
        try:
            uiNode = clientApi.GetUI(MOD_NAMESPACE, 'Game')
        except Exception:
            uiNode = None
        if uiNode:
            self.uiInitialized = True
            return uiNode
        if not self._registerUiDefinitions():
            return False
        try:
            uiNode = clientApi.CreateUI(MOD_NAMESPACE, 'Game', {'isHud': 1})
            if not uiNode:
                uiNode = clientApi.GetUI(MOD_NAMESPACE, 'Game')
            self.uiInitialized = bool(uiNode)
            if not uiNode:
                # A failed create can mean the dimension just rebuilt the UI
                # registry. Allow the next recovery attempt to register the
                # screen definitions again.
                self.uiDefinitionsRegistered = False
            return uiNode or False
        except Exception as error:
            print('[KillBroadcast] create ui error:', error)
            self.uiInitialized = False
            self.uiDefinitionsRegistered = False
            return False

    def _startUiRecovery(self):
        self.uiInitialized = False
        self.uiDefinitionsRegistered = False
        self._uiRecoveryTicks = max(self._uiRecoveryTicks, UI_RECOVERY_TICKS)
        self._uiRecoveryRetryTicks = 0
        return True

    def OnDimensionChangeFinishClientEvent(self, args=None):
        self._nextAimSnapshotTime = 0.0
        self._lastAimSnapshot = None
        self._lastAimSnapshotTime = 0.0
        # The client UI registry can be rebuilt during a dimension change.
        # Force the screen definitions to be registered again before CreateUI.
        self.uiDefinitionsRegistered = False
        self._startUiRecovery()
        if self._recoverUiAfterDimensionChange():
            self._uiRecoveryTicks = 0
            return True
        self._uiRecoveryRetryTicks = UI_RECOVERY_RETRY_INTERVAL_TICKS
        return False

    def _recoverUiAfterDimensionChange(self):
        if self.compatibilityState != 'enabled' or not self.uiInitFinished:
            return False
        uiNode = self._getGameUi(True)
        if not uiNode:
            return False
        try:
            if hasattr(uiNode, 'RebindAfterDimensionChange'):
                if uiNode.RebindAfterDimensionChange() is False:
                    return False
            elif hasattr(uiNode, 'OnActive'):
                uiNode.OnActive()
        except Exception as error:
            print('[KillBroadcast] recover dimension ui error:', error)
            return False
        self.uiInitialized = True
        self._flushPendingFeedback(uiNode)
        return True

    def _queueFeedback(self, eventName, args):
        payload = dict(args) if isinstance(args, dict) else args
        self._pendingFeedback.append((
            eventName,
            payload,
            time.time() + PENDING_FEEDBACK_SECONDS,
        ))
        if len(self._pendingFeedback) > PENDING_FEEDBACK_MAX_COUNT:
            self._pendingFeedback = self._pendingFeedback[-PENDING_FEEDBACK_MAX_COUNT:]
        self._startUiRecovery()
        return True

    def _dispatchFeedbackToUi(self, uiNode, eventName, args):
        if not uiNode:
            return False
        try:
            if eventName == CREATE_KILL_EVENT and hasattr(uiNode, 'CreateKill'):
                return bool(uiNode.CreateKill(args))
            if eventName == HIT_MARKER_EVENT and hasattr(uiNode, 'ShowHitMarker'):
                return bool(uiNode.ShowHitMarker(args))
        except Exception as error:
            print('[KillBroadcast] dispatch feedback ui error:', eventName, error)
        return False

    def _isFeedbackEnabled(self, uiNode, eventName):
        if not uiNode:
            return True
        checkerName = None
        if eventName == CREATE_KILL_EVENT:
            checkerName = 'IsKillEffectFeedbackEnabled'
        elif eventName == HIT_MARKER_EVENT:
            checkerName = 'IsHitMarkerFeedbackEnabled'
        if not checkerName or not hasattr(uiNode, checkerName):
            return True
        try:
            return bool(getattr(uiNode, checkerName)())
        except Exception:
            return True

    def _flushPendingFeedback(self, uiNode=None):
        if not self._pendingFeedback:
            return True
        uiNode = uiNode or self._getGameUi(False)
        if not uiNode:
            return False
        now = time.time()
        pending = self._pendingFeedback
        self._pendingFeedback = []
        sent = False
        for eventName, args, expireAt in pending:
            if expireAt < now:
                continue
            sent = self._dispatchFeedbackToUi(uiNode, eventName, args) or sent
        return sent

    def GetNeteaseWindowComp(self):
        if self._neteaseWindowComp:
            return self._neteaseWindowComp
        try:
            self._neteaseWindowComp = EngineCompFactory.CreateNeteaseWindow(LocalPlayerId)
        except Exception as error:
            print('[KillBroadcast] create netease window comp error:', error)
            self._neteaseWindowComp = None
        return self._neteaseWindowComp

    def RegisterNativeSettingEntry(self):
        if self.nativeSettingRegistered:
            return True
        if not self.uiInitFinished or not self._registerUiDefinitions():
            return False
        comp = self.GetNeteaseWindowComp()
        register = getattr(comp, 'RegisterSettingInst', None) if comp else None
        if not register:
            print('[KillBroadcast] native mod setting entry is not supported')
            return False
        try:
            settingInst = register(
                MOD_RESOURCE_ID,
                NATIVE_SETTING_TITLE,
                NATIVE_SETTING_ICON,
            )
            if not settingInst:
                return False
            settingInst.AddButton(
                NATIVE_SETTING_BUTTON_ID,
                u'\u51fb\u6740\u53cd\u9988\u8bbe\u7f6e',
                u'\u70b9\u51fb\u8fdb\u5165\u51fb\u6740\u53cd\u9988\u4e0e\u547d\u4e2d\u6807\u8bb0\u8bbe\u7f6e',
                self.OpenSettingFromNative,
                1,
            )
            self._nativeSettingInst = settingInst
            self.nativeSettingRegistered = True
            return True
        except Exception as error:
            print('[KillBroadcast] register native mod setting entry error:', error)
            return False

    def CloseNeteaseSettingUi(self):
        comp = self.GetNeteaseWindowComp()
        if not comp:
            return False
        try:
            comp.CloseSettingUI()
            return True
        except Exception as error:
            print('[KillBroadcast] close native mod setting ui error:', error)
            return False

    def OpenSettingFromNative(self, *args):
        self.CloseNeteaseSettingUi()
        return self.OpenSetting()

    def OpenSetting(self):
        if not self.uiInitFinished or not self._registerUiDefinitions():
            return False
        try:
            system = clientApi.GetSystem('TsGuns', 'TsGunsClientSystem')
            if system and hasattr(system, 'OpenSettingFromPause'):
                return system.OpenSettingFromPause()
        except Exception:
            pass
        try:
            return bool(clientApi.PushScreen(MOD_NAMESPACE, 'Setting'))
        except Exception as error:
            print('[KillBroadcast] open setting error:', error)
            return False

    def SendAimSnapshot(self):
        now = time.time()
        if now < self._nextAimSnapshotTime:
            return False
        try:
            position = CameraComp.GetPosition()
            direction = CameraComp.GetForward()
            if not position or not direction or len(position) < 3 or len(direction) < 3:
                return False
            position = (
                float(position[0]), float(position[1]), float(position[2]))
            direction = (
                float(direction[0]), float(direction[1]), float(direction[2]))
            directionLengthSq = sum(value * value for value in direction)
            if directionLengthSq <= 0.000001:
                return False
            directionLength = directionLengthSq ** 0.5
            direction = tuple(value / directionLength for value in direction)
            self._nextAimSnapshotTime = now + AIM_SNAPSHOT_INTERVAL_SECONDS
            previous = self._lastAimSnapshot
            if previous is not None:
                oldPosition, oldDirection = previous
                positionDeltaSq = sum(
                    (position[index] - oldPosition[index]) ** 2
                    for index in range(3)
                )
                directionDot = sum(
                    direction[index] * oldDirection[index]
                    for index in range(3)
                )
                unchanged = (
                    positionDeltaSq <= AIM_SNAPSHOT_POSITION_EPSILON_SQ and
                    directionDot >= AIM_SNAPSHOT_DIRECTION_DOT_THRESHOLD
                )
                if unchanged and now - self._lastAimSnapshotTime < AIM_SNAPSHOT_HEARTBEAT_SECONDS:
                    return False
            self.NotifyToServer(AIM_SNAPSHOT_EVENT, {
                'Pos': position,
                'Vec': direction,
            })
            self._lastAimSnapshot = (position, direction)
            self._lastAimSnapshotTime = now
            return True
        except Exception as error:
            print('[KillBroadcast] send aim snapshot error:', error)
            return False

    def OnCreateKill(self, args):
        if self.compatibilityState != 'enabled':
            return False
        uiNode = self._getGameUi(True)
        if uiNode:
            if self._dispatchFeedbackToUi(uiNode, CREATE_KILL_EVENT, args):
                return True
            if not self._isFeedbackEnabled(uiNode, CREATE_KILL_EVENT):
                return False
        return self._queueFeedback(CREATE_KILL_EVENT, args)

    def OnHitMarker(self, args):
        if self.compatibilityState != 'enabled':
            return False
        uiNode = self._getGameUi(True)
        if uiNode:
            if self._dispatchFeedbackToUi(uiNode, HIT_MARKER_EVENT, args):
                return True
            if not self._isFeedbackEnabled(uiNode, HIT_MARKER_EVENT):
                return False
        return self._queueFeedback(HIT_MARKER_EVENT, args)

    def OnHeadshotSound(self, args):
        if self.compatibilityState != 'enabled' or not isinstance(args, dict):
            return False
        attackerId = args.get('AttackerId') or args.get('attackerId')
        if attackerId and str(attackerId) == str(LocalPlayerId):
            return False
        try:
            if self._headshotAudioComp is None:
                self._headshotAudioComp = EngineCompFactory.CreateCustomAudio(LevelId)
            if not self._headshotAudioComp:
                return False
            pos = args.get('Pos') or args.get('pos')
            if isinstance(pos, (tuple, list)) and len(pos) >= 3:
                soundPos = (float(pos[0]), float(pos[1]), float(pos[2]))
                self._headshotAudioComp.PlayCustomMusic(
                    CSGO_HEADSHOT_SOUND_NAME,
                    soundPos,
                    1.0,
                    1.0,
                    False,
                )
            else:
                self._headshotAudioComp.PlayCustomUIMusic(
                    CSGO_HEADSHOT_SOUND_NAME,
                    1.0,
                    1.0,
                    False,
                )
            return True
        except Exception as error:
            print('[KillBroadcast] play nearby headshot sound error:', error)
            return False

    def OnPlayerDeathCleanup(self, args=None):
        """Immediately remove feedback that was visible when the local player died."""
        if self.compatibilityState != 'enabled':
            return False
        # A death can arrive while the HUD is being rebuilt (for example after
        # a dimension transition).  Do not let a queued pre-death event bring
        # the old CF/APEX/COD feedback back on the next UI recovery.
        self._pendingFeedback = []
        uiNode = self._getGameUi(False)
        if not uiNode:
            return True
        try:
            if hasattr(uiNode, 'ClearFeedbackOnLocalDeath'):
                return bool(uiNode.ClearFeedbackOnLocalDeath())
            if hasattr(uiNode, 'HideKillPanel'):
                uiNode.HideKillPanel(True)
            if hasattr(uiNode, 'hitMarker') and uiNode.hitMarker:
                uiNode.hitMarker.HideHitMarker()
            return True
        except Exception as error:
            print('[KillBroadcast] clear feedback on player death error:', error)
            return False

    def ApplySharedSettings(self, settingValues=None):
        if not self.uiInitialized:
            return False
        try:
            uiNode = self._getGameUi(True)
            if uiNode and hasattr(uiNode, 'ApplyKillEffectSettings'):
                return uiNode.ApplyKillEffectSettings(True, True, settingValues)
        except Exception as error:
            print('[KillBroadcast] apply shared settings error:', error)
        return False

    def _destroyUi(self):
        try:
            uiNode = clientApi.GetUI(MOD_NAMESPACE, 'Game')
            if uiNode and hasattr(uiNode, 'Destroy'):
                uiNode.Destroy()
        except Exception:
            pass
        self.uiInitialized = False

    def Destroy(self):
        self._unlistenFeedbackEvents()
        self._destroyUi()
        self._nativeSettingInst = None
        self._neteaseWindowComp = None
        self._headshotAudioComp = None
        self.nativeSettingRegistered = False
        self._uiRecoveryTicks = 0
        self._uiRecoveryRetryTicks = 0
        self._pendingFeedback = []
        for eventName, callback in (
            ('UiInitFinished', self.OnUiInitFinished),
            ('LoadClientAddonScriptsAfter', self.OnLoadClientAddonScriptsAfter),
            ('DimensionChangeFinishClientEvent', self.OnDimensionChangeFinishClientEvent),
            ('OnScriptTickClient', self.OnScriptTickClient),
            ('OnScriptTickNonChaseFrameClient', self.OnScriptTickNonChaseFrameClient),
        ):
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
        try:
            self.UnListenForEvent(
                MOD_NAMESPACE,
                SERVER_SYSTEM_NAME,
                SERVER_STATUS_EVENT,
                self,
                self.OnCompatibilityStatus,
            )
        except Exception:
            pass
