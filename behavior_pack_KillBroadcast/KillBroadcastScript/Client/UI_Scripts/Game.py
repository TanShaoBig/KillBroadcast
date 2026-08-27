# -*- coding: utf-8 -*-
import time

import mod.client.extraClientApi as clientApi

from .Gd656KillEffectUI import Gd656KillEffectUI
from .DisplayNameResolver import ResolveTargetDisplayName, ResolveWeaponDisplayName
from .HitMarkerController import HitMarkerController
from .KillPokerUI import KillPokerUI
from .KillBroadcastSettingManager import KillBroadcastSettingManager


ScreenNode = clientApi.GetScreenNodeCls()
LocalPlayerId = clientApi.GetLocalPlayerId()
GameComp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
AudioComp = clientApi.GetEngineCompFactory().CreateCustomAudio(clientApi.GetLevelId())
KILL_EFFECT_LAYOUT_REFERENCE_PATH = '/GamePanel'


class Game(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.uiNode = None
        self.settingMgr = KillBroadcastSettingManager()
        self.killPoker = KillPokerUI('KillBroadcast', 'Game')
        self.gd656KillEffect = Gd656KillEffectUI()
        self.hitMarker = HitMarkerController(self.settingMgr)
        self.killEffectStyle = None
        self.killEffectBaseSizes = {}
        self.killEffectBaseScreenSize = None
        self.killEffectTimeoutGeneration = 0
        self.killPokerTimer = None
        self.killVibrationTimer = None

    def Create(self):
        self.uiNode = clientApi.GetUI('KillBroadcast', 'Game')
        self.hitMarker.uiNode = self.uiNode
        self.settingMgr.LoadConfig()
        self.SetControlVisible('/KillPanel', False)
        self.SetControlVisible('/KillPanel_DeltaForce', False)
        self.hitMarker.InitHitMarker()
        self.killPoker.Init()
        self.killPoker.Clear()
        self.gd656KillEffect.Init(self.uiNode)
        self.gd656KillEffect.Clear()
        self.ApplyKillEffectSettings()

    def OnActive(self):
        return self.ApplyKillEffectSettings(True, True)

    def IsKillEffectFeedbackEnabled(self):
        return self.settingMgr.IsKillEffectEnabled()

    def IsHitMarkerFeedbackEnabled(self):
        return self.settingMgr.IsHitMarkerEnabled()

    def RebindAfterDimensionChange(self):
        try:
            uiNode = clientApi.GetUI('KillBroadcast', 'Game')
        except Exception:
            uiNode = None
        if not uiNode:
            return False
        self.CancelKillEffectTimeout()
        self.CancelKillVibrationTimer()
        self.uiNode = uiNode
        self.hitMarker.uiNode = uiNode
        self.killEffectBaseSizes = {}
        self.killEffectBaseScreenSize = None
        self.SetControlVisible('/KillPanel', False)
        self.SetControlVisible('/KillPanel_DeltaForce', False)
        hitMarkerReady = self.hitMarker.InitHitMarker()
        killPokerReady = self.killPoker.Init()
        gd656Ready = self.gd656KillEffect.RebindControls(uiNode)
        if not hitMarkerReady or not killPokerReady or not gd656Ready:
            return False
        self.killPoker.Clear()
        self.gd656KillEffect.Clear()
        self.ApplyKillEffectSettings(True, True)
        return True

    def SetControlVisible(self, path, visible):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if ctrl:
            ctrl.SetVisible(bool(visible))

    def SetControlAlpha(self, path, alpha):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if not ctrl:
            return False
        try:
            ctrl.SetAlpha(float(alpha))
            return True
        except Exception:
            return False

    def GetControlGlobalCenter(self, path):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if not ctrl:
            return None
        try:
            pos = ctrl.GetGlobalPosition()
            size = ctrl.GetSize()
            return (float(pos[0]) + float(size[0]) * 0.5, float(pos[1]) + float(size[1]) * 0.5)
        except Exception:
            return None

    def GetControlGlobalRect(self, path):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if not ctrl:
            return None
        try:
            pos = ctrl.GetGlobalPosition()
            size = ctrl.GetSize()
            return (float(pos[0]), float(pos[1]), float(size[0]), float(size[1]))
        except Exception:
            return None

    def CaptureKillEffectBaseSizes(self):
        if not self.uiNode:
            return False
        screenSize = self.GetKillEffectScreenSize()
        if not screenSize:
            return False
        self.killEffectBaseScreenSize = screenSize
        baseSize = (float(screenSize[0]), float(screenSize[1]) * 0.13)
        for path in ('/KillPanel', '/KillPanel_DeltaForce'):
            self.killEffectBaseSizes[path] = baseSize
        return True

    def GetKillEffectScreenSize(self):
        for uiNode, path in (
            (self.uiNode, KILL_EFFECT_LAYOUT_REFERENCE_PATH),
            (None, ''),
        ):
            try:
                size = self.settingMgr.GetUiReferenceSize(uiNode, path)
                if size and len(size) >= 2:
                    width = float(size[0])
                    height = float(size[1])
                    if width > 1.0 and height > 1.0:
                        return (width, height)
            except Exception:
                pass
        return None

    def ApplyKillEffectLayout(self, style=None):
        if not self.uiNode:
            return False
        style = style or self.settingMgr.GetKillEffectStyle()
        path = '/KillPanel' if style == self.settingMgr.STYLE_CSGO else '/KillPanel_DeltaForce'
        if not self.CaptureKillEffectBaseSizes():
            return False
        baseSize = self.killEffectBaseSizes.get(path)
        applied = self.settingMgr.ApplyKillEffectLayoutToControl(
            self.uiNode,
            path,
            style,
            KILL_EFFECT_LAYOUT_REFERENCE_PATH,
            baseSize,
            style == self.settingMgr.STYLE_CSGO,
        )
        if style != self.settingMgr.STYLE_CSGO:
            layout = self.settingMgr.GetKillEffectLayout(style)
            scale = float(layout.get('Size', 100)) / 100.0
            self.gd656KillEffect.SetLayoutViewportSize((
                float(baseSize[0]) * scale,
                float(baseSize[1]) * scale,
            ))
            self.gd656KillEffect.SetLayoutScale(scale)
            self.gd656KillEffect.SetLayoutAlpha(float(layout.get('Alpha', 100)) / 100.0)
        return applied

    def NeedsPostShowLayoutRefresh(self, style):
        return style != self.gd656KillEffect.QINSHOU_XIANSHENG_STYLE

    def ApplyKillEffectSettings(self, hideWhenDisabled=True, applyLayout=True,
                                settingValues=None, reloadConfig=True):
        if not self.uiNode:
            return False
        if isinstance(settingValues, dict):
            self.settingMgr.ApplyValuesSnapshot(settingValues)
        else:
            self.settingMgr.LoadConfig(bool(reloadConfig))
        style = self.settingMgr.GetKillEffectStyle()
        self.killEffectStyle = style
        self.killPoker.SetTrailLength(self.settingMgr.GetKillEffectTrailLength())
        self.gd656KillEffect.SetStyle(style)
        self.gd656KillEffect.SetStyleOptions(self.settingMgr.GetKillEffectStyleOptions(style))
        self.settingMgr.ApplyKillEffectStyleToUi(self.uiNode, '/KillPanel')
        if not self.settingMgr.IsHitMarkerEnabled():
            self.hitMarker.HideHitMarker()
        if applyLayout:
            self.ApplyKillEffectLayout(style)
        if hideWhenDisabled and not self.settingMgr.IsKillEffectEnabled():
            self.HideKillPanel(True)
        return True

    def RefreshKillEffectUiNode(self):
        uiNode = clientApi.GetUI('KillBroadcast', 'Game')
        if not uiNode:
            return False
        if self.uiNode is not uiNode:
            return self.RebindAfterDimensionChange()
        self.uiNode = uiNode
        self.hitMarker.uiNode = uiNode
        return self.gd656KillEffect.RebindControls(uiNode)

    def CreateKill(self, args):
        if not self.settingMgr.IsKillEffectEnabled():
            self.HideKillPanel(True)
            return False
        if not self.RefreshKillEffectUiNode():
            return False
        headshot = bool(isinstance(args, dict) and (args.get('HeadShot') or args.get('headshot')))
        self.TriggerKillVibration(headshot)
        self.ApplyKillEffectSettings(False, False, None, False)
        style = self.settingMgr.GetKillEffectStyle()
        if style == self.settingMgr.STYLE_CSGO:
            self.SetControlVisible('/KillPanel_DeltaForce', False)
            self.SetControlVisible('/KillPanel', True)
            self.ApplyKillEffectLayout(style)
            self.killPoker.Init()
            self.killPoker.AddKill(headshot)
            soundName = 'killbroadcast.kill.csgo.headshot' if headshot else 'killbroadcast.kill.csgo'
            try:
                AudioComp.PlayCustomUIMusic(soundName, 1, 1, False)
            except Exception:
                pass
        else:
            self.SetControlVisible('/KillPanel', False)
            self.SetControlVisible('/KillPanel_DeltaForce', True)
            self.ApplyKillEffectLayout(style)
            weaponName, targetName, distance, targetMaxHealth, damage = self.GetKillEffectPerformanceData(args)
            targetEntityId = args.get('EntityId') if isinstance(args, dict) else None
            targetIdentifier = args.get('TargetType') if isinstance(args, dict) else None
            targetIsPlayer = bool(args.get('TargetIsPlayer')) if isinstance(args, dict) else False
            if self.gd656KillEffect.AddKill(
                headshot,
                weaponName,
                targetName,
                True,
                distance,
                targetMaxHealth,
                damage,
                targetEntityId,
                targetIdentifier,
                targetIsPlayer,
            ):
                self.gd656KillEffect.UpdateFrame(None)
        if self.NeedsPostShowLayoutRefresh(style):
            self.ApplyKillEffectLayout(style)
            try:
                GameComp.AddTimer(0.0, lambda: self.ApplyKillEffectLayout(style))
            except Exception:
                pass
        if style == 'battlefield1':
            self.CancelKillEffectTimeout()
        else:
            self.ScheduleKillEffectTimeout()
        return True

    def GetKillEffectPerformanceData(self, args):
        args = args if isinstance(args, dict) else {}
        weaponName = ResolveWeaponDisplayName(args)
        targetName = ResolveTargetDisplayName(args)
        distance = args.get('Distance')
        targetMaxHealth = args.get('TargetMaxHealth')
        damage = args.get('Damage')
        if damage is None:
            damage = args.get('TotalDamage')
        try:
            distance = float(distance) if distance is not None else None
        except Exception:
            distance = None
        try:
            targetMaxHealth = float(targetMaxHealth) if targetMaxHealth is not None else None
        except Exception:
            targetMaxHealth = None
        try:
            damage = max(0.0, float(damage)) if damage is not None else None
        except Exception:
            damage = None
        return weaponName, targetName, distance, targetMaxHealth, damage

    def TriggerKillVibration(self, headshot=False):
        if not self.settingMgr.IsKillVibrationFeedbackEnabled():
            return False
        self.CancelKillVibrationTimer()
        try:
            device = clientApi.GetEngineCompFactory().CreateDevice(LocalPlayerId)
            device.SetDeviceVibrate(35 if headshot else 55)
            return True
        except Exception:
            return False

    def CancelKillVibrationTimer(self):
        if self.killVibrationTimer is not None:
            try:
                GameComp.CancelTimer(self.killVibrationTimer)
            except Exception:
                pass
            self.killVibrationTimer = None

    def HideKillEffectControls(self):
        self.SetControlVisible('/KillPanel', False)
        self.SetControlVisible('/KillPanel_DeltaForce', False)
        return True

    def HideKillPanel(self, clear=True):
        self.CancelKillEffectTimeout()
        self.HideKillEffectControls()
        if clear:
            try:
                self.killPoker.Clear()
                self.gd656KillEffect.Clear()
            except Exception:
                pass

    def ClearFeedbackOnLocalDeath(self):
        """Clear every local feedback layer when the player dies."""
        self.HideKillPanel(True)
        try:
            self.hitMarker.HideHitMarker()
        except Exception:
            pass
        self.CancelKillVibrationTimer()
        return True

    def CancelKillEffectTimeout(self):
        self.killEffectTimeoutGeneration += 1
        if self.killPokerTimer is not None:
            try:
                GameComp.CancelTimer(self.killPokerTimer)
            except Exception:
                pass
            self.killPokerTimer = None

    def ScheduleKillEffectTimeout(self):
        self.CancelKillEffectTimeout()
        generation = self.killEffectTimeoutGeneration
        duration = self.settingMgr.GetKillEffectResetTime()
        if self.settingMgr.GetKillEffectStyle() == self.gd656KillEffect.CUPPING_CAT_STYLE:
            duration = max(duration, self.gd656KillEffect.GetCuppingCatAnimationDuration() + 0.05)
        try:
            self.killPokerTimer = GameComp.AddTimer(
                duration,
                lambda: self.OnKillEffectTimeout(generation),
            )
            return True
        except Exception:
            self.killPokerTimer = None
            return False

    def OnKillEffectTimeout(self, generation=None):
        if generation is not None and generation != self.killEffectTimeoutGeneration:
            return False
        self.killPokerTimer = None
        style = self.settingMgr.GetKillEffectStyle()
        if style in self.gd656KillEffect.SCROLL_STYLES:
            if self.gd656KillEffect.BeginScrollingDismiss():
                return True
        if style == 'pubg' and self.gd656KillEffect.BeginPubgNaturalDismiss():
            return True
        self.HideKillPanel(True)
        return False

    def ShowHitMarker(self, args=None):
        try:
            uiNode = clientApi.GetUI('KillBroadcast', 'Game')
        except Exception:
            uiNode = None
        if not uiNode:
            return False
        if self.uiNode is not uiNode and not self.RebindAfterDimensionChange():
            return False
        self.uiNode = uiNode
        self.hitMarker.uiNode = uiNode
        return self.hitMarker.ShowHitMarker(args)

    def UpdateKillEffectAnimation(self, args=None):
        if not self.gd656KillEffect.animationActive:
            return False
        style = self.gd656KillEffect.style
        active = bool(self.gd656KillEffect.UpdateFrame(args))
        if (
            style == self.gd656KillEffect.QINSHOU_XIANSHENG_STYLE and
            not active
        ):
            self.HideKillEffectControls()
        return active

    def Update(self):
        self.UpdateKillEffectAnimation(None)
        return True

    def UpdateFrame(self, args=None):
        self.hitMarker.Update(args)
        self.UpdateKillEffectAnimation(args)
        return True

    def Destroy(self):
        self.HideKillPanel(True)
        self.hitMarker.HideHitMarker()
        self.CancelKillVibrationTimer()
        try:
            self.gd656KillEffect.Destroy()
        except Exception:
            pass
        self.hitMarker.uiNode = None
        self.uiNode = None
        self.killEffectBaseSizes = {}
        self.killEffectBaseScreenSize = None
