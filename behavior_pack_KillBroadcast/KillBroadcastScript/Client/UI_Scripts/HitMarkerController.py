# -*- coding: utf-8 -*-
import math
import random
import time
import mod.client.extraClientApi as clientApi


HIT_MARKER_PARENT_PATH = '/GamePanel'
HIT_MARKER_PANEL_PATH = HIT_MARKER_PARENT_PATH + '/HitMarkerPanel'
HIT_MARKER_CENTER_PATHS = (
    '/GamePanel/CrosshairPanel/Middle',
    '/GamePanel/CrosshairPanel',
)
HIT_MARKER_LINE_SPECS = (
    ('TopLeft', -1.0, -1.0, 45.0),
    ('TopRight', 1.0, -1.0, -45.0),
    ('BottomLeft', -1.0, 1.0, -45.0),
    ('BottomRight', 1.0, 1.0, 45.0),
)
HIT_MARKER_ENTRY_DISTANCE_RATIO = 17.0 / 48.0
HIT_MARKER_IMPACT_DISTANCE_RATIO = 8.5 / 48.0
HIT_MARKER_PULSE_DISTANCE_RATIO = 7.0 / 48.0
HIT_MARKER_SETTLE_DISTANCE_RATIO = 9.5 / 48.0
HIT_MARKER_ENTRY_DURATION = 0.055
HIT_MARKER_PULSE_DURATION = 0.060
HIT_MARKER_REBOUND_DURATION = 0.070
HIT_MARKER_COMBO_KICK_DURATION = 0.035
HIT_MARKER_COMBO_IMPACT_DURATION = 0.050
HIT_MARKER_COMBO_SETTLE_DURATION = 0.065
HIT_MARKER_HOLD_DURATION = 0.055
HIT_MARKER_FADE_DURATION = 0.300
HIT_MARKER_ENTRY_SIZE_RATIOS = (1.0 / 7.0, 7.0 / 48.0)
HIT_MARKER_IMPACT_SIZE_RATIOS = (1.45 / 8.0, 8.0 / 48.0)
HIT_MARKER_PULSE_SIZE_RATIOS = (1.6 / 7.0, 7.0 / 48.0)
HIT_MARKER_SETTLE_SIZE_RATIOS = (1.15 / 6.5, 6.5 / 48.0)
HIT_MARKER_COMBO_KICK_DISTANCE_RATIO = 11.5 / 48.0
HIT_MARKER_COMBO_KICK_SIZE_RATIOS = (1.35 / 7.5, 7.5 / 48.0)
HIT_MARKER_EXIT_DISTANCE_RATIO = 19.0 / 48.0
HIT_MARKER_EXIT_SIZE_RATIOS = (0.075, 14.0 / 48.0)
HIT_MARKER_ROTATION_ANGLES = (-18.0, -12.0, -6.0, 0.0, 6.0, 12.0, 18.0)
HIT_MARKER_ROTATION_MIN_CHANGE = 8.0
HIT_MARKER_ROTATION_MAX_CHANGE = 18.0
HIT_MARKER_NORMAL_COLOR = (1.0, 1.0, 1.0)
HIT_MARKER_HEADSHOT_COLOR = (1.0, 0.22, 0.16)


class HitMarkerController(object):
    def __init__(self, settingMgr):
        self.settingMgr = settingMgr
        self.uiNode = None
        self.hitMarkerStartTime = 0.0
        self.hitMarkerRotationAngle = 0.0
        self.hitMarkerRotationStartAngle = 0.0
        self.hitMarkerLastRotationAngle = None
        self.hitMarkerComboStartState = None
        self.hitMarkerFrameState = {}
        self.hitMarkerHeadshot = False
        self.hitMarkerControls = []
        self.hitMarkerFrameListening = False

    def SetControlVisible(self, path, visible):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if ctrl:
            ctrl.SetVisible(bool(visible))

    def SetControlAlpha(self, path, alpha):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if ctrl:
            ctrl.SetAlpha(float(alpha))

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

    def Clamp(self, value, minimum, maximum):
        return max(minimum, min(maximum, value))

    def EaseOutCubic(self, value):
        value = self.Clamp(float(value), 0.0, 1.0)
        return 1.0 - (1.0 - value) * (1.0 - value) * (1.0 - value)

    def LerpFloat(self, start, end, progress):
        return float(start) + (float(end) - float(start)) * float(progress)

    def Update(self, args=None):
        if self.hitMarkerStartTime <= 0.0:
            return False
        return self.OnHitMarkerFrame(args)

    def InitHitMarker(self):
        self.StopHitMarkerFrameListener()
        self.hitMarkerStartTime = 0.0
        self.hitMarkerRotationAngle = 0.0
        self.hitMarkerRotationStartAngle = 0.0
        self.hitMarkerLastRotationAngle = None
        self.hitMarkerComboStartState = None
        self.hitMarkerFrameState = {}
        self.hitMarkerControls = []
        self.SetControlVisible(HIT_MARKER_PANEL_PATH, False)
        if not self.uiNode:
            return False
        for name, directionX, directionY, angle in HIT_MARKER_LINE_SPECS:
            path = HIT_MARKER_PANEL_PATH + '/' + name
            ctrl = self.uiNode.GetBaseUIControl(path)
            image = ctrl.asImage() if ctrl else None
            if not ctrl or not image:
                self.hitMarkerControls = []
                return False
            try:
                image.SetRotatePivot((0.5, 0.5))
                image.Rotate(float(angle))
            except Exception as e:
                print('KillBroadcast init hit marker line error:', path, e)
                self.hitMarkerControls = []
                return False
            self.hitMarkerControls.append((ctrl, image, directionX, directionY, angle))
        return True

    def StartHitMarkerFrameListener(self):
        if self.hitMarkerFrameListening:
            return
        self.hitMarkerFrameListening = True

    def StopHitMarkerFrameListener(self):
        self.hitMarkerFrameListening = False

    def ShowHitMarker(self, args=None):
        if not self.settingMgr.IsHitMarkerEnabled():
            if self.hitMarkerStartTime > 0.0:
                self.HideHitMarker()
            return False
        if not self.uiNode:
            self.uiNode = clientApi.GetUI('KillBroadcast', 'Game')
        if not self.uiNode:
            return False
        if len(self.hitMarkerControls) != len(HIT_MARKER_LINE_SPECS) and not self.InitHitMarker():
            return False
        isCombo = self.hitMarkerStartTime > 0.0 and bool(self.hitMarkerFrameState)
        comboStartState = dict(self.hitMarkerFrameState) if isCombo else None
        headshot = bool(isinstance(args, dict) and (args.get('HeadShot') or args.get('headshot')))
        self.hitMarkerHeadshot = headshot
        self.hitMarkerComboStartState = comboStartState
        if isCombo:
            self.hitMarkerRotationStartAngle = float(comboStartState.get(
                'RotationAngle',
                self.hitMarkerRotationAngle
            ))
            self.hitMarkerRotationAngle = self.SelectNextHitMarkerRotation()
        else:
            self.hitMarkerRotationAngle = 0.0
            self.hitMarkerRotationStartAngle = 0.0
            self.hitMarkerLastRotationAngle = 0.0
        color = HIT_MARKER_HEADSHOT_COLOR if headshot else HIT_MARKER_NORMAL_COLOR
        for _, image, _, _, _ in self.hitMarkerControls:
            try:
                image.SetSpriteColor(color)
            except Exception:
                pass
        self.hitMarkerStartTime = time.time()
        if not self.AlignHitMarkerToCrosshair():
            return False
        self.SetControlVisible(HIT_MARKER_PANEL_PATH, True)
        self.SetControlAlpha(HIT_MARKER_PANEL_PATH, 1.0)
        self.ApplyHitMarkerFrame(0.0)
        self.StartHitMarkerFrameListener()
        return True

    def SelectNextHitMarkerRotation(self):
        candidates = list(HIT_MARKER_ROTATION_ANGLES)
        lastAngle = self.hitMarkerFrameState.get(
            'RotationAngle',
            self.hitMarkerLastRotationAngle
        )
        if lastAngle is not None:
            changedCandidates = [
                angle for angle in candidates
                if HIT_MARKER_ROTATION_MIN_CHANGE
                <= abs(float(angle) - float(lastAngle))
                <= HIT_MARKER_ROTATION_MAX_CHANGE
            ]
            if changedCandidates:
                candidates = changedCandidates
        angle = float(random.choice(candidates)) if candidates else 0.0
        self.hitMarkerLastRotationAngle = angle
        return angle

    def ApplyHitMarkerRotation(self):
        rotationCenter = self.GetHitMarkerRotationCenter()
        if not rotationCenter:
            return False
        groupAngle = float(self.hitMarkerFrameState.get(
            'RotationAngle',
            self.hitMarkerRotationAngle
        ))
        for _, image, _, _, baseAngle in self.hitMarkerControls:
            try:
                image.Rotate(float(baseAngle))
                image.RotateAround(rotationCenter, groupAngle)
            except Exception as e:
                print('KillBroadcast rotate hit marker line error:', e)
                return False
        return True

    def OnHitMarkerFrame(self, args=None):
        if self.hitMarkerStartTime <= 0.0:
            self.HideHitMarker()
            return
        elapsed = max(0.0, time.time() - self.hitMarkerStartTime)
        totalDuration = self.GetHitMarkerTotalDuration()
        if elapsed >= totalDuration:
            self.HideHitMarker()
            return
        self.ApplyHitMarkerFrame(elapsed)

    def ApplyHitMarkerFrame(self, elapsed):
        self.AlignHitMarkerToCrosshair()
        diagonalScale = 0.7071067811865476
        frameState = self.GetHitMarkerFrameState(elapsed)
        distance = frameState['Distance']
        widthRatio = frameState['WidthRatio']
        heightRatio = frameState['HeightRatio']
        alpha = frameState['Alpha']
        self.hitMarkerFrameState = frameState
        for ctrl, image, directionX, directionY, baseAngle in self.hitMarkerControls:
            try:
                baseX = float(directionX) * diagonalScale
                baseY = float(directionY) * diagonalScale
                ctrl.SetFullPosition('x', {
                    'followType': 'parent',
                    'relativeValue': baseX * distance,
                })
                ctrl.SetFullPosition('y', {
                    'followType': 'parent',
                    'relativeValue': baseY * distance,
                })
                ctrl.SetFullSize('y', {
                    'followType': 'parent',
                    'relativeValue': heightRatio,
                })
                ctrl.SetFullSize('x', {
                    'followType': 'y',
                    'relativeValue': widthRatio,
                })
                ctrl.SetAlpha(alpha)
            except Exception as e:
                print('KillBroadcast update hit marker line error:', e)
                self.HideHitMarker()
                return False
        if not self.ApplyHitMarkerRotation():
            self.HideHitMarker()
            return False
        return True

    def GetHitMarkerTotalDuration(self):
        if self.hitMarkerComboStartState:
            coreDuration = (
                HIT_MARKER_COMBO_KICK_DURATION
                + HIT_MARKER_COMBO_IMPACT_DURATION
                + HIT_MARKER_COMBO_SETTLE_DURATION
            )
        else:
            coreDuration = (
                HIT_MARKER_ENTRY_DURATION
                + HIT_MARKER_PULSE_DURATION
                + HIT_MARKER_REBOUND_DURATION
            )
        return coreDuration + HIT_MARKER_HOLD_DURATION + HIT_MARKER_FADE_DURATION

    def GetHitMarkerFrameState(self, elapsed):
        lineElapsed = max(0.0, float(elapsed))
        headshotScale = 1.08 if self.hitMarkerHeadshot else 1.0
        comboState = self.hitMarkerComboStartState
        if comboState:
            kickEnd = HIT_MARKER_COMBO_KICK_DURATION
            impactEnd = kickEnd + HIT_MARKER_COMBO_IMPACT_DURATION
            coreEnd = impactEnd + HIT_MARKER_COMBO_SETTLE_DURATION
            startDistance = float(comboState.get('Distance', HIT_MARKER_SETTLE_DISTANCE_RATIO))
            startWidth = float(comboState.get('WidthRatio', HIT_MARKER_SETTLE_SIZE_RATIOS[0]))
            startHeight = float(comboState.get('HeightRatio', HIT_MARKER_SETTLE_SIZE_RATIOS[1]))
            startAlpha = float(comboState.get('Alpha', 1.0))
            kickDistance = max(startDistance, HIT_MARKER_COMBO_KICK_DISTANCE_RATIO * headshotScale)
            kickWidth = HIT_MARKER_COMBO_KICK_SIZE_RATIOS[0]
            kickHeight = max(startHeight, HIT_MARKER_COMBO_KICK_SIZE_RATIOS[1] * headshotScale)
            if lineElapsed < kickEnd:
                progress = self.EaseOutCubic(lineElapsed / HIT_MARKER_COMBO_KICK_DURATION)
                distance = self.LerpFloat(startDistance, kickDistance, progress)
                widthRatio = self.LerpFloat(startWidth, kickWidth, progress)
                heightRatio = self.LerpFloat(startHeight, kickHeight, progress)
                alpha = self.LerpFloat(startAlpha, 1.0, progress)
            elif lineElapsed < impactEnd:
                progress = self.EaseOutCubic(
                    (lineElapsed - kickEnd) / HIT_MARKER_COMBO_IMPACT_DURATION
                )
                distance = self.LerpFloat(kickDistance, HIT_MARKER_PULSE_DISTANCE_RATIO * headshotScale, progress)
                widthRatio = self.LerpFloat(kickWidth, HIT_MARKER_PULSE_SIZE_RATIOS[0], progress)
                heightRatio = self.LerpFloat(kickHeight, HIT_MARKER_PULSE_SIZE_RATIOS[1] * headshotScale, progress)
                alpha = 1.0
            elif lineElapsed < coreEnd:
                progress = self.EaseOutCubic(
                    (lineElapsed - impactEnd) / HIT_MARKER_COMBO_SETTLE_DURATION
                )
                distance = self.LerpFloat(
                    HIT_MARKER_PULSE_DISTANCE_RATIO * headshotScale,
                    HIT_MARKER_SETTLE_DISTANCE_RATIO * headshotScale,
                    progress
                )
                widthRatio = self.LerpFloat(
                    HIT_MARKER_PULSE_SIZE_RATIOS[0],
                    HIT_MARKER_SETTLE_SIZE_RATIOS[0],
                    progress
                )
                heightRatio = self.LerpFloat(
                    HIT_MARKER_PULSE_SIZE_RATIOS[1] * headshotScale,
                    HIT_MARKER_SETTLE_SIZE_RATIOS[1] * headshotScale,
                    progress
                )
                alpha = 1.0
            else:
                distance = HIT_MARKER_SETTLE_DISTANCE_RATIO * headshotScale
                widthRatio = HIT_MARKER_SETTLE_SIZE_RATIOS[0]
                heightRatio = HIT_MARKER_SETTLE_SIZE_RATIOS[1] * headshotScale
                alpha = 1.0
            rotationDuration = HIT_MARKER_COMBO_KICK_DURATION + HIT_MARKER_COMBO_IMPACT_DURATION
            rotationProgress = self.Clamp(lineElapsed / rotationDuration, 0.0, 1.0)
            rotationProgress = rotationProgress * rotationProgress * (3.0 - 2.0 * rotationProgress)
            rotationAngle = self.LerpFloat(
                self.hitMarkerRotationStartAngle,
                self.hitMarkerRotationAngle,
                rotationProgress
            )
        else:
            entryEnd = HIT_MARKER_ENTRY_DURATION
            pulseEnd = entryEnd + HIT_MARKER_PULSE_DURATION
            coreEnd = pulseEnd + HIT_MARKER_REBOUND_DURATION
            if lineElapsed < entryEnd:
                progress = self.EaseOutCubic(lineElapsed / HIT_MARKER_ENTRY_DURATION)
                distance = self.LerpFloat(HIT_MARKER_ENTRY_DISTANCE_RATIO, HIT_MARKER_IMPACT_DISTANCE_RATIO, progress)
                widthRatio = self.LerpFloat(HIT_MARKER_ENTRY_SIZE_RATIOS[0], HIT_MARKER_IMPACT_SIZE_RATIOS[0], progress)
                heightRatio = self.LerpFloat(HIT_MARKER_ENTRY_SIZE_RATIOS[1], HIT_MARKER_IMPACT_SIZE_RATIOS[1], progress)
                alpha = self.Clamp(lineElapsed / 0.035, 0.0, 1.0)
            elif lineElapsed < pulseEnd:
                progress = self.EaseOutCubic((lineElapsed - entryEnd) / HIT_MARKER_PULSE_DURATION)
                distance = self.LerpFloat(HIT_MARKER_IMPACT_DISTANCE_RATIO, HIT_MARKER_PULSE_DISTANCE_RATIO, progress)
                widthRatio = self.LerpFloat(HIT_MARKER_IMPACT_SIZE_RATIOS[0], HIT_MARKER_PULSE_SIZE_RATIOS[0], progress)
                heightRatio = self.LerpFloat(HIT_MARKER_IMPACT_SIZE_RATIOS[1], HIT_MARKER_PULSE_SIZE_RATIOS[1], progress)
                alpha = 1.0
            elif lineElapsed < coreEnd:
                progress = self.EaseOutCubic((lineElapsed - pulseEnd) / HIT_MARKER_REBOUND_DURATION)
                distance = self.LerpFloat(HIT_MARKER_PULSE_DISTANCE_RATIO, HIT_MARKER_SETTLE_DISTANCE_RATIO, progress)
                widthRatio = self.LerpFloat(HIT_MARKER_PULSE_SIZE_RATIOS[0], HIT_MARKER_SETTLE_SIZE_RATIOS[0], progress)
                heightRatio = self.LerpFloat(HIT_MARKER_PULSE_SIZE_RATIOS[1], HIT_MARKER_SETTLE_SIZE_RATIOS[1], progress)
                alpha = 1.0
            else:
                distance = HIT_MARKER_SETTLE_DISTANCE_RATIO
                widthRatio = HIT_MARKER_SETTLE_SIZE_RATIOS[0]
                heightRatio = HIT_MARKER_SETTLE_SIZE_RATIOS[1]
                alpha = 1.0
            distance *= headshotScale
            heightRatio *= headshotScale
            rotationAngle = self.hitMarkerRotationAngle

        fadeStart = coreEnd + HIT_MARKER_HOLD_DURATION
        if lineElapsed > fadeStart:
            exitProgress = self.Clamp((lineElapsed - fadeStart) / HIT_MARKER_FADE_DURATION, 0.0, 1.0)
            moveProgress = exitProgress * exitProgress * (3.0 - 2.0 * exitProgress)
            distance = self.LerpFloat(
                HIT_MARKER_SETTLE_DISTANCE_RATIO * headshotScale,
                HIT_MARKER_EXIT_DISTANCE_RATIO * headshotScale,
                moveProgress
            )
            widthRatio = self.LerpFloat(
                HIT_MARKER_SETTLE_SIZE_RATIOS[0],
                HIT_MARKER_EXIT_SIZE_RATIOS[0],
                moveProgress
            )
            heightRatio = self.LerpFloat(
                HIT_MARKER_SETTLE_SIZE_RATIOS[1] * headshotScale,
                HIT_MARKER_EXIT_SIZE_RATIOS[1] * headshotScale,
                moveProgress
            )
            alpha = math.pow(max(0.0, 1.0 - exitProgress), 0.85)
        return {
            'Distance': distance,
            'WidthRatio': widthRatio,
            'HeightRatio': heightRatio,
            'Alpha': alpha,
            'RotationAngle': rotationAngle,
        }

    def GetHitMarkerRotationCenter(self):
        if not self.uiNode:
            return None
        for path in HIT_MARKER_CENTER_PATHS:
            center = self.GetControlGlobalCenter(path)
            if center:
                return (float(center[0]), float(center[1]))
        return None

    def AlignHitMarkerToCrosshair(self):
        if not self.uiNode:
            return False
        targetCenter = self.GetHitMarkerRotationCenter()
        marker = self.uiNode.GetBaseUIControl(HIT_MARKER_PANEL_PATH)
        parentRect = self.GetControlGlobalRect(HIT_MARKER_PARENT_PATH)
        if not targetCenter or not marker or not parentRect:
            return False
        try:
            parentX, parentY, parentWidth, parentHeight = parentRect
            if parentWidth <= 1.0 or parentHeight <= 1.0:
                return False
            marker.SetFullPosition('x', {
                'followType': 'parent',
                'relativeValue': (float(targetCenter[0]) - parentX) / parentWidth - 0.5,
            })
            marker.SetFullPosition('y', {
                'followType': 'parent',
                'relativeValue': (float(targetCenter[1]) - parentY) / parentHeight - 0.5,
            })
            return True
        except Exception as e:
            print('KillBroadcast align hit marker to crosshair error:', e)
            return False

    def HideHitMarker(self):
        self.hitMarkerStartTime = 0.0
        self.hitMarkerRotationAngle = 0.0
        self.hitMarkerRotationStartAngle = 0.0
        self.hitMarkerLastRotationAngle = None
        self.hitMarkerComboStartState = None
        self.hitMarkerFrameState = {}
        self.SetControlVisible(HIT_MARKER_PANEL_PATH, False)
        self.StopHitMarkerFrameListener()
        return True
