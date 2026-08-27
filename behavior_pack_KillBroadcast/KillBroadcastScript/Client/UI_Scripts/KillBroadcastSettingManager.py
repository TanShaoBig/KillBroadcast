# -*- coding: utf-8 -*-
import copy
import math

import mod.client.extraClientApi as clientApi

from ...Compat import GetTsGunsClientSystem
from .CodTaunts import (
    COD_TAUNT_SOURCE_JIAHAO_CHARCOAL,
    COD_TAUNT_SOURCE_OPTIONS,
    GetCodTauntSourceName as ResolveCodTauntSourceName,
    NormalizeCodTauntSource,
)


LevelId = clientApi.GetLevelId()
GameComp = clientApi.GetEngineCompFactory().CreateGame(LevelId)
_SHARED_MISSING = object()


class KillBroadcastSettingManager(object):
    CONFIG_NAME = 'KillBroadcast_Setting_Config'
    LEGACY_CONFIG_NAME = 'TsGuns_Setting_Config'
    CONFIG_VERSION = 5

    KILL_EFFECT_ENABLE_SETTING_KEY = 'kill_effect.enable'
    KILL_EFFECT_STYLE_SETTING_KEY = 'kill_effect.style'
    KILL_EFFECT_LAYOUT_SETTING_KEY = 'kill_effect.layouts'
    KILL_EFFECT_ONLY_TSGUNS_SETTING_KEY = 'kill_effect.only_tsguns'
    KILL_EFFECT_TEAM_CT_SETTING_KEY = 'kill_effect.team_ct'
    KILL_VIBRATION_FEEDBACK_SETTING_KEY = 'kill_effect.vibration_feedback'
    KILL_EFFECT_RESET_TIME_SETTING_KEY = 'kill_effect.reset_time'
    KILL_EFFECT_TRAIL_LENGTH_SETTING_KEY = 'kill_effect.trail_length'
    KILL_EFFECT_CF_MAX_COMBO_SETTING_KEY = 'kill_effect.cf.max_combo'
    KILL_EFFECT_CF_SHOW_DETAILS_SETTING_KEY = 'kill_effect.cf.show_details'
    KILL_EFFECT_CF_SHOW_DISTANCE_SETTING_KEY = 'kill_effect.cf.show_distance'
    KILL_EFFECT_PUBG_SHOW_WEAPON_SETTING_KEY = 'kill_effect.pubg.show_weapon'
    KILL_EFFECT_PUBG_SHOW_DISTANCE_SETTING_KEY = 'kill_effect.pubg.show_distance'
    KILL_EFFECT_PUBG_SHOW_COMBO_SETTING_KEY = 'kill_effect.pubg.show_combo'
    KILL_EFFECT_APEX_SHOW_BACKGROUND_SETTING_KEY = 'kill_effect.apex.show_background'
    KILL_EFFECT_BF1_SHOW_BACKGROUND_SETTING_KEY = 'kill_effect.battlefield1.show_background'
    KILL_EFFECT_BF1_SHOW_TEXT_SETTING_KEY = 'kill_effect.battlefield1.show_text'
    KILL_EFFECT_BF1_SHOW_DISTANCE_SETTING_KEY = 'kill_effect.battlefield1.show_distance'
    KILL_EFFECT_BF1_QUEUE_LENGTH_SETTING_KEY = 'kill_effect.battlefield1.queue_length'
    KILL_EFFECT_BF5_SHOW_SCORE_SETTING_KEY = 'kill_effect.battlefield5.show_score'
    KILL_EFFECT_BF5_SHOW_DISTANCE_SETTING_KEY = 'kill_effect.battlefield5.show_distance'
    KILL_EFFECT_BF5_QUEUE_LENGTH_SETTING_KEY = 'kill_effect.battlefield5.queue_length'
    KILL_EFFECT_DELTA_QUEUE_LENGTH_SETTING_KEY = 'kill_effect.delta_force.queue_length'
    KILL_EFFECT_OLD_PRIEST_QUEUE_LENGTH_SETTING_KEY = 'kill_effect.old_priest.queue_length'
    KILL_EFFECT_VALORANT_SHOW_HEADSHOT_SETTING_KEY = 'kill_effect.valorant.show_headshot'
    KILL_EFFECT_VALORANT_MAX_TIER_SETTING_KEY = 'kill_effect.valorant.max_tier'
    KILL_EFFECT_COD_TAUNT_SOURCE_SETTING_KEY = 'kill_effect.cod.taunt_source'
    KILL_EFFECT_QINSHOU_HOLD_DURATION_SETTING_KEY = 'kill_effect.qinshou_xiansheng.hold_duration'
    KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_SETTING_KEY = 'kill_effect.qinshou_xiansheng.fade_out_duration'
    KILL_EFFECT_QINSHOU_PITCH_MIN_SETTING_KEY = 'kill_effect.qinshou_xiansheng.pitch_min'
    KILL_EFFECT_QINSHOU_PITCH_MAX_SETTING_KEY = 'kill_effect.qinshou_xiansheng.pitch_max'
    KILL_EFFECT_QINSHOU_HOLD_DURATION_DEFAULT = 2.05
    KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_DEFAULT = 0.50
    KILL_EFFECT_QINSHOU_PITCH_MIN_DEFAULT = 0.50
    KILL_EFFECT_QINSHOU_PITCH_MAX_DEFAULT = 2.00
    HIT_MARKER_ENABLE_SETTING_KEY = 'hit_marker.enable'

    STYLE_CSGO = 'csgo'
    STYLE_OPTIONS = (
        ('csgo', u'CSGO'),
        ('cod', u'COD'),
        ('apex', u'APEX'),
        ('cf_combo', u'CF连杀'),
        ('pubg', u'PUBG淘汰'),
        ('battlefield1', u'战地1'),
        ('battlefield5', u'战地5'),
        ('delta_force', u'三角洲'),
        ('old_priest', u'老牧师'),
        ('valorant', u'无畏契约'),
        ('king_honor', u'王者荣耀'),
        ('cupping_cat', u'拔罐猫'),
        ('xiaoxiao_world', u'小小世界'),
        ('big_dog_bark', u'大狗叫'),
        ('qinshou_xiansheng', u'秦兽先生'),
    )
    LAYOUT_DEFAULTS = {
        'csgo': {'Center': [0.5, 0.835], 'Size': 100, 'Alpha': 100},
        'cf_combo': {'Center': [0.3625, 0.6448], 'Size': 100, 'Alpha': 100},
        'pubg': {'Center': [0.5138, 0.7583], 'Size': 100, 'Alpha': 100},
        'battlefield1': {'Center': [0.5109, 0.6891], 'Size': 100, 'Alpha': 100},
        'battlefield5': {'Center': [0.5109, 0.655], 'Size': 100, 'Alpha': 100},
        'delta_force': {'Center': [0.5143, 0.6584], 'Size': 100, 'Alpha': 100},
        'old_priest': {'Center': [0.5143, 0.6584], 'Size': 100, 'Alpha': 100},
        'valorant': {'Center': [0.5177, 0.7752], 'Size': 103, 'Alpha': 100},
        'king_honor': {'Center': [0.5000, 0.4000], 'Size': 100, 'Alpha': 100},
        'cod': {'Center': [0.6100, 0.4000], 'Size': 100, 'Alpha': 100},
        'apex': {'Center': [0.5000, 0.5800], 'Size': 100, 'Alpha': 100},
        'cupping_cat': {'Center': [0.5000, 0.4750], 'Size': 183, 'Alpha': 100},
        'xiaoxiao_world': {'Center': [0.5000, 0.0450], 'Size': 100, 'Alpha': 100},
        'big_dog_bark': {'Center': [0.5000, 0.6250], 'Size': 100, 'Alpha': 100},
        'qinshou_xiansheng': {'Center': [0.5000, 0.5000], 'Size': 100, 'Alpha': 100},
    }
    LAYOUT_V4_DEFAULTS = {
        'cupping_cat': {'Center': [0.5000, 0.6600], 'Size': 100, 'Alpha': 100},
        'xiaoxiao_world': {'Center': [0.5000, 0.6650], 'Size': 100, 'Alpha': 100},
        'big_dog_bark': {'Center': [0.5000, 0.6400], 'Size': 100, 'Alpha': 100},
    }
    TEAM_T_TEXTURE = 'textures/ui/killbroadcast_csgo_map_ui/Game_UI/teamT'
    TEAM_CT_TEXTURE = 'textures/ui/killbroadcast_csgo_map_ui/Game_UI/teamCT'
    TEAM_T_COLOR = (0.7686274509803922, 0.7372549019607844, 0.4235294117647059)
    TEAM_CT_COLOR = (0.7490196078431373, 0.8941176470588236, 0.9921568627450981)
    TEAM_T_ACCENT_COLOR = (1.0, 1.0, 1.0)
    TEAM_CT_ACCENT_COLOR = (0.18, 0.34, 0.48)

    def __init__(self):
        self.SettingValues = {}
        self._loaded = False
        self._configComp = None
        self._revision = 0
        self._sharedDirty = False

    @staticmethod
    def _finiteFloat(value, defaultValue):
        try:
            result = float(value)
        except (TypeError, ValueError, OverflowError):
            result = float(defaultValue)
        if math.isnan(result) or math.isinf(result):
            return float(defaultValue)
        return result

    @classmethod
    def _boundedFloat(cls, value, defaultValue, minimum, maximum):
        return min(float(maximum), max(float(minimum), cls._finiteFloat(value, defaultValue)))

    @classmethod
    def _boundedInt(cls, value, defaultValue, minimum, maximum):
        result = int(round(cls._finiteFloat(value, defaultValue)))
        return min(int(maximum), max(int(minimum), result))

    def _getConfigComp(self):
        if self._configComp is None:
            try:
                self._configComp = clientApi.GetEngineCompFactory().CreateConfigClient(LevelId)
            except Exception as error:
                print('[KillBroadcast] create config client error:', error)
                self._configComp = False
        return self._configComp

    def _readConfig(self, name, isGlobal):
        config = self._getConfigComp()
        if not config:
            return None
        try:
            return config.GetConfigData(name, isGlobal)
        except Exception:
            return None

    def _selectData(self, globalData, localData):
        values = []
        for data in (globalData, localData):
            if isinstance(data, dict):
                values.append(data)
        if not values:
            return None
        values.sort(key=lambda value: int(value.get('Revision', 0) or 0))
        return values[-1]

    def _extractValues(self, data):
        if not isinstance(data, dict):
            return {}
        values = data.get('Values', data)
        return dict(values) if isinstance(values, dict) else {}

    def _migrateLegacyValues(self, values):
        if values:
            return values
        legacy = self._selectData(
            self._readConfig(self.LEGACY_CONFIG_NAME, True),
            self._readConfig(self.LEGACY_CONFIG_NAME, False),
        )
        legacyValues = self._extractValues(legacy)
        migrated = {}
        for key, value in legacyValues.items():
            if str(key).startswith('kill_effect.') or str(key).startswith('hit_marker.'):
                migrated[key] = copy.deepcopy(value)
        # The old option means "only TsGuns kills".  This standalone package
        # must remain useful without TsGuns, so its first-run default is false.
        migrated[self.KILL_EFFECT_ONLY_TSGUNS_SETTING_KEY] = False
        return migrated

    def LoadConfig(self, force=False):
        if self._loaded and not force:
            return
        data = self._selectData(
            self._readConfig(self.CONFIG_NAME, True),
            self._readConfig(self.CONFIG_NAME, False),
        )
        configVersion = 0
        if isinstance(data, dict):
            try:
                self._revision = max(self._revision, int(data.get('Revision', 0) or 0))
            except Exception:
                pass
            try:
                configVersion = int(data.get('Version', 0) or 0)
            except Exception:
                configVersion = 0
        self.SettingValues = self._migrateLegacyValues(self._extractValues(data))
        migrationChanged = self._applyKillEffectLayoutsV4Migration(configVersion)
        migrationChanged = self._applyKillEffectLayoutsV5Migration(configVersion) or migrationChanged
        self._ensureDefaults()
        self._loaded = True
        if migrationChanged:
            self.SaveConfig()

    def _applyKillEffectLayoutsV4Migration(self, configVersion):
        if configVersion >= 4:
            return False
        # V4 only bumped the stored schema version.  Older builds replaced the
        # complete layout map here, which also erased every player adjustment.
        # _ensureDefaults already fills missing styles without touching valid
        # custom entries, so migration only needs to persist the version bump.
        return True

    def _layoutMatchesDefault(self, value, expected):
        if not isinstance(value, dict) or not isinstance(expected, dict):
            return False
        center = value.get('Center')
        expectedCenter = expected.get('Center')
        if not isinstance(center, (list, tuple)) or len(center) < 2:
            return False
        try:
            return (
                abs(float(center[0]) - float(expectedCenter[0])) <= 0.0001 and
                abs(float(center[1]) - float(expectedCenter[1])) <= 0.0001 and
                int(round(float(value.get('Size', 100)))) ==
                int(expected.get('Size', 100)) and
                int(round(float(value.get('Alpha', 100)))) ==
                int(expected.get('Alpha', 100))
            )
        except (TypeError, ValueError):
            return False

    def _applyKillEffectLayoutsV5Migration(self, configVersion):
        if configVersion >= 5:
            return False
        layouts = self.SettingValues.get(self.KILL_EFFECT_LAYOUT_SETTING_KEY)
        if isinstance(layouts, dict):
            for style, oldDefault in self.LAYOUT_V4_DEFAULTS.items():
                if self._layoutMatchesDefault(layouts.get(style), oldDefault):
                    layouts[style] = copy.deepcopy(self.LAYOUT_DEFAULTS[style])
        # Returning true also persists the version bump when all three layouts
        # were already customized and therefore intentionally preserved.
        return True

    def _ensureDefaults(self):
        defaults = {
            self.KILL_EFFECT_ENABLE_SETTING_KEY: True,
            self.KILL_EFFECT_STYLE_SETTING_KEY: self.STYLE_CSGO,
            self.KILL_EFFECT_ONLY_TSGUNS_SETTING_KEY: False,
            self.KILL_EFFECT_TEAM_CT_SETTING_KEY: False,
            self.KILL_VIBRATION_FEEDBACK_SETTING_KEY: False,
            self.KILL_EFFECT_RESET_TIME_SETTING_KEY: 5.0,
            self.KILL_EFFECT_TRAIL_LENGTH_SETTING_KEY: 1.0,
            self.KILL_EFFECT_CF_MAX_COMBO_SETTING_KEY: 6,
            self.KILL_EFFECT_CF_SHOW_DETAILS_SETTING_KEY: True,
            self.KILL_EFFECT_CF_SHOW_DISTANCE_SETTING_KEY: True,
            self.KILL_EFFECT_PUBG_SHOW_WEAPON_SETTING_KEY: True,
            self.KILL_EFFECT_PUBG_SHOW_DISTANCE_SETTING_KEY: True,
            self.KILL_EFFECT_PUBG_SHOW_COMBO_SETTING_KEY: True,
            self.KILL_EFFECT_APEX_SHOW_BACKGROUND_SETTING_KEY: True,
            self.KILL_EFFECT_BF1_SHOW_BACKGROUND_SETTING_KEY: True,
            self.KILL_EFFECT_BF1_SHOW_TEXT_SETTING_KEY: True,
            self.KILL_EFFECT_BF1_SHOW_DISTANCE_SETTING_KEY: True,
            self.KILL_EFFECT_BF1_QUEUE_LENGTH_SETTING_KEY: 7,
            self.KILL_EFFECT_BF5_SHOW_SCORE_SETTING_KEY: True,
            self.KILL_EFFECT_BF5_SHOW_DISTANCE_SETTING_KEY: True,
            self.KILL_EFFECT_BF5_QUEUE_LENGTH_SETTING_KEY: 7,
            self.KILL_EFFECT_DELTA_QUEUE_LENGTH_SETTING_KEY: 7,
            self.KILL_EFFECT_OLD_PRIEST_QUEUE_LENGTH_SETTING_KEY: 7,
            self.KILL_EFFECT_VALORANT_SHOW_HEADSHOT_SETTING_KEY: True,
            self.KILL_EFFECT_VALORANT_MAX_TIER_SETTING_KEY: 3,
            self.KILL_EFFECT_COD_TAUNT_SOURCE_SETTING_KEY: COD_TAUNT_SOURCE_JIAHAO_CHARCOAL,
            self.KILL_EFFECT_QINSHOU_HOLD_DURATION_SETTING_KEY: self.KILL_EFFECT_QINSHOU_HOLD_DURATION_DEFAULT,
            self.KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_SETTING_KEY: self.KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_DEFAULT,
            self.KILL_EFFECT_QINSHOU_PITCH_MIN_SETTING_KEY: self.KILL_EFFECT_QINSHOU_PITCH_MIN_DEFAULT,
            self.KILL_EFFECT_QINSHOU_PITCH_MAX_SETTING_KEY: self.KILL_EFFECT_QINSHOU_PITCH_MAX_DEFAULT,
            self.HIT_MARKER_ENABLE_SETTING_KEY: True,
        }
        for key, value in defaults.items():
            if key not in self.SettingValues:
                self.SettingValues[key] = copy.deepcopy(value)
        layouts = self.SettingValues.get(self.KILL_EFFECT_LAYOUT_SETTING_KEY)
        if not isinstance(layouts, dict):
            layouts = {}
        for style, value in self.LAYOUT_DEFAULTS.items():
            if not isinstance(layouts.get(style), dict):
                layouts[style] = copy.deepcopy(value)
        apexLayout = layouts.get('apex')
        if isinstance(apexLayout, dict):
            center = apexLayout.get('Center')
            try:
                usesOldDefault = (
                    isinstance(center, (list, tuple)) and len(center) >= 2 and
                    abs(float(center[0]) - 0.5) <= 0.0001 and
                    abs(float(center[1]) - 0.69) <= 0.0001
                )
            except (TypeError, ValueError):
                usesOldDefault = False
            if usesOldDefault:
                apexLayout['Center'] = copy.deepcopy(self.LAYOUT_DEFAULTS['apex']['Center'])
        self.SettingValues[self.KILL_EFFECT_LAYOUT_SETTING_KEY] = layouts

    def SaveConfig(self):
        self.LoadConfig()
        sharedOk = False
        system = GetTsGunsClientSystem()
        sharedManager = getattr(system, 'settingMgr', None) if system else None
        if self._sharedDirty and sharedManager and hasattr(sharedManager, 'SaveConfig'):
            try:
                sharedOk = bool(sharedManager.SaveConfig())
                if sharedOk:
                    self._sharedDirty = False
            except Exception as error:
                print('[KillBroadcast] save TsGuns shared config error:', error)
        config = self._getConfigComp()
        if not config:
            return sharedOk
        self._revision += 1
        data = {
            'Version': self.CONFIG_VERSION,
            'Revision': self._revision,
            'Values': copy.deepcopy(self.SettingValues),
        }
        ok = False
        for isGlobal in (True, False):
            try:
                ok = bool(config.SetConfigData(self.CONFIG_NAME, data, isGlobal)) or ok
            except Exception as error:
                print('[KillBroadcast] save config error:', error)
        return ok or sharedOk

    def GetValuesSnapshot(self):
        self.LoadConfig()
        return copy.deepcopy(self.SettingValues)

    def ApplyValuesSnapshot(self, values):
        if not isinstance(values, dict):
            return False
        self.SettingValues = copy.deepcopy(values)
        self._ensureDefaults()
        self._loaded = True
        return True

    def Get(self, key, default=None):
        self.LoadConfig()
        system = GetTsGunsClientSystem()
        if system and hasattr(system, 'GetKillBroadcastSettingValue'):
            try:
                value = system.GetKillBroadcastSettingValue(key, _SHARED_MISSING)
                if value is not _SHARED_MISSING:
                    return value
            except Exception as error:
                print('[KillBroadcast] get TsGuns shared setting error:', key, error)
        return self.SettingValues.get(key, default)

    def Set(self, key, value, save=True):
        self.LoadConfig()
        self.SettingValues[key] = copy.deepcopy(value)
        system = GetTsGunsClientSystem()
        if system and hasattr(system, 'SetKillBroadcastSettingValue'):
            try:
                sharedManager = getattr(system, 'settingMgr', None)
                if not save and sharedManager and hasattr(sharedManager, 'SetValue'):
                    sharedManager.SetValue(key, value, False, False)
                    self._sharedDirty = True
                    if hasattr(sharedManager, 'GetSettingValueByKey'):
                        current = sharedManager.GetSettingValueByKey(key)
                        if current is not None:
                            self.SettingValues[key] = copy.deepcopy(current)
                            return current
                    return value
                result = system.SetKillBroadcastSettingValue(key, value)
                if self._sharedDirty and sharedManager and hasattr(sharedManager, 'SaveConfig'):
                    if sharedManager.SaveConfig():
                        self._sharedDirty = False
                return result
            except Exception as error:
                print('[KillBroadcast] set TsGuns shared setting error:', key, error)
        if save:
            self.SaveConfig()
        return value

    def IsKillEffectEnabled(self):
        return bool(self.Get(self.KILL_EFFECT_ENABLE_SETTING_KEY, True))

    def IsHitMarkerEnabled(self):
        return bool(self.Get(self.HIT_MARKER_ENABLE_SETTING_KEY, True))

    def IsKillVibrationFeedbackEnabled(self):
        return bool(self.Get(self.KILL_VIBRATION_FEEDBACK_SETTING_KEY, False))

    def GetKillEffectStyle(self):
        value = str(self.Get(self.KILL_EFFECT_STYLE_SETTING_KEY, self.STYLE_CSGO) or '').lower()
        for style, _ in self.STYLE_OPTIONS:
            if style == value:
                return style
        return self.STYLE_CSGO

    def CycleKillEffectStyle(self, save=True):
        styles = [style for style, _ in self.STYLE_OPTIONS]
        current = self.GetKillEffectStyle()
        index = styles.index(current) if current in styles else 0
        return self.Set(
            self.KILL_EFFECT_STYLE_SETTING_KEY,
            styles[(index + 1) % len(styles)],
            save,
        )

    def GetKillEffectStyleName(self):
        style = self.GetKillEffectStyle()
        for value, name in self.STYLE_OPTIONS:
            if value == style:
                return name
        return u'CSGO'

    def GetCodTauntSource(self):
        return NormalizeCodTauntSource(self.Get(
            self.KILL_EFFECT_COD_TAUNT_SOURCE_SETTING_KEY,
            COD_TAUNT_SOURCE_JIAHAO_CHARCOAL,
        ))

    def GetCodTauntSourceName(self):
        return ResolveCodTauntSourceName(self.GetCodTauntSource())

    def CycleCodTauntSource(self, save=True):
        sources = [value for value, _ in COD_TAUNT_SOURCE_OPTIONS]
        current = self.GetCodTauntSource()
        index = sources.index(current) if current in sources else 0
        return self.Set(
            self.KILL_EFFECT_COD_TAUNT_SOURCE_SETTING_KEY,
            sources[(index + 1) % len(sources)],
            save,
        )

    def GetKillEffectResetTime(self):
        value = self._boundedFloat(
            self.Get(self.KILL_EFFECT_RESET_TIME_SETTING_KEY, 5.0), 5.0, 3.0, 15.0)
        if self.GetKillEffectStyle() == 'qinshou_xiansheng':
            options = self.GetKillEffectStyleOptions('qinshou_xiansheng')
            value = max(value, (
                float(options.get('HoldDuration', 0.0)) +
                float(options.get('FadeOutDuration', 0.0))
            ))
        return value

    def StepKillEffectResetTime(self, delta):
        return self.Set(
            self.KILL_EFFECT_RESET_TIME_SETTING_KEY,
            self.GetKillEffectResetTime() + float(delta),
        )

    def GetKillEffectTrailLength(self):
        return self._boundedFloat(
            self.Get(self.KILL_EFFECT_TRAIL_LENGTH_SETTING_KEY, 1.0), 1.0, 0.5, 2.0)

    def GetKillEffectTeamStyle(self):
        if bool(self.Get(self.KILL_EFFECT_TEAM_CT_SETTING_KEY, False)):
            return self.TEAM_CT_TEXTURE, self.TEAM_CT_COLOR, self.TEAM_CT_ACCENT_COLOR
        return self.TEAM_T_TEXTURE, self.TEAM_T_COLOR, self.TEAM_T_ACCENT_COLOR

    def _setControlColor(self, uiNode, path, color):
        ctrl = uiNode.GetBaseUIControl(path) if uiNode else None
        if not ctrl:
            return False
        applied = False
        try:
            image = ctrl.asImage()
            if image:
                image.SetSpriteColor(tuple(color))
                applied = True
        except Exception:
            pass
        try:
            ctrl.SetColor(tuple(color))
            applied = True
        except Exception:
            pass
        return applied

    def ApplyKillEffectStyleToUi(self, uiNode, panelPath):
        if not uiNode or not panelPath:
            return False
        texture, color, accentColor = self.GetKillEffectTeamStyle()
        teamPath = panelPath + '/Team'
        applied = False
        teamControl = uiNode.GetBaseUIControl(teamPath)
        try:
            image = teamControl.asImage() if teamControl else None
            if image:
                image.SetSprite(texture)
                applied = True
        except Exception:
            pass
        applied = self._setControlColor(uiNode, teamPath, accentColor) or applied
        applied = self._setControlColor(uiNode, teamPath + '/circle', color) or applied
        for index in range(1, 6):
            cardPath = teamPath + '/circle/poker_kill_bar/' + str(index)
            for suffix, cardColor in (
                ('', accentColor),
                ('/bone_1', accentColor),
                ('/count', accentColor),
                ('/bone_2', accentColor),
                ('/bg', color),
                ('/effect', accentColor),
            ):
                applied = self._setControlColor(uiNode, cardPath + suffix, cardColor) or applied
        countPath = teamPath + '/circle/poker_kill_bar/1/count_label'
        countControl = uiNode.GetBaseUIControl(countPath)
        try:
            label = countControl.asLabel() if countControl else None
            if label:
                label.SetTextColor(tuple(accentColor))
                applied = True
        except Exception:
            pass
        return applied

    def GetKillEffectLayout(self, style=None):
        style = style or self.GetKillEffectStyle()
        defaultValue = self.LAYOUT_DEFAULTS.get(style, self.LAYOUT_DEFAULTS[self.STYLE_CSGO])
        layouts = self.Get(self.KILL_EFFECT_LAYOUT_SETTING_KEY, {})
        if not isinstance(layouts, dict):
            layouts = {}
        value = layouts.get(style, defaultValue)
        result = copy.deepcopy(defaultValue)
        if isinstance(value, dict):
            result.update(value)
        center = result.get('Center', defaultValue['Center'])
        if not isinstance(center, (list, tuple)) or len(center) < 2:
            center = defaultValue['Center']
        result['Center'] = [
            self._boundedFloat(center[0], defaultValue['Center'][0], 0.0, 1.0),
            self._boundedFloat(center[1], defaultValue['Center'][1], 0.0, 1.0),
        ]
        result['Size'] = self._boundedInt(
            result.get('Size', defaultValue['Size']), defaultValue['Size'], 50, 200)
        result['Alpha'] = self._boundedInt(
            result.get('Alpha', defaultValue['Alpha']), defaultValue['Alpha'], 0, 100)
        return result

    def ResetCurrentLayout(self):
        style = self.GetKillEffectStyle()
        layouts = copy.deepcopy(self.Get(self.KILL_EFFECT_LAYOUT_SETTING_KEY, {}))
        layouts[style] = copy.deepcopy(self.LAYOUT_DEFAULTS[style])
        return self.Set(self.KILL_EFFECT_LAYOUT_SETTING_KEY, layouts)

    def SetKillEffectLayout(self, style, value, save=True):
        style = str(style or self.GetKillEffectStyle()).lower()
        if style not in self.LAYOUT_DEFAULTS:
            style = self.STYLE_CSGO
        current = self.GetKillEffectLayout(style)
        if isinstance(value, dict):
            current.update(copy.deepcopy(value))
        center = current.get('Center', self.LAYOUT_DEFAULTS[style]['Center'])
        if not isinstance(center, (list, tuple)) or len(center) < 2:
            center = self.LAYOUT_DEFAULTS[style]['Center']
        current['Center'] = [
            self._boundedFloat(center[0], self.LAYOUT_DEFAULTS[style]['Center'][0], 0.0, 1.0),
            self._boundedFloat(center[1], self.LAYOUT_DEFAULTS[style]['Center'][1], 0.0, 1.0),
        ]
        current['Size'] = self._boundedInt(
            current.get('Size', self.LAYOUT_DEFAULTS[style]['Size']),
            self.LAYOUT_DEFAULTS[style]['Size'], 50, 200)
        current['Alpha'] = self._boundedInt(
            current.get('Alpha', self.LAYOUT_DEFAULTS[style]['Alpha']),
            self.LAYOUT_DEFAULTS[style]['Alpha'], 0, 100)
        layouts = copy.deepcopy(self.Get(self.KILL_EFFECT_LAYOUT_SETTING_KEY, {}))
        layouts[style] = current
        self.Set(self.KILL_EFFECT_LAYOUT_SETTING_KEY, layouts, save)
        return copy.deepcopy(current)

    def GetKillEffectStyleOptions(self, style=None):
        style = style or self.GetKillEffectStyle()
        if style == 'cf_combo':
            return {
                'MaxCombo': self._boundedInt(
                    self.Get(self.KILL_EFFECT_CF_MAX_COMBO_SETTING_KEY, 6), 6, 2, 6),
                'ShowDetails': bool(self.Get(self.KILL_EFFECT_CF_SHOW_DETAILS_SETTING_KEY, True)),
                'ShowDistance': bool(self.Get(self.KILL_EFFECT_CF_SHOW_DISTANCE_SETTING_KEY, True)),
            }
        if style == 'pubg':
            return {
                'ShowWeapon': bool(self.Get(self.KILL_EFFECT_PUBG_SHOW_WEAPON_SETTING_KEY, True)),
                'ShowDistance': bool(self.Get(self.KILL_EFFECT_PUBG_SHOW_DISTANCE_SETTING_KEY, True)),
                'ShowCombo': bool(self.Get(self.KILL_EFFECT_PUBG_SHOW_COMBO_SETTING_KEY, True)),
            }
        if style == 'apex':
            return {
                'ShowBackground': bool(self.Get(self.KILL_EFFECT_APEX_SHOW_BACKGROUND_SETTING_KEY, True)),
            }
        if style == 'battlefield1':
            return {
                'ShowBackground': bool(self.Get(self.KILL_EFFECT_BF1_SHOW_BACKGROUND_SETTING_KEY, True)),
                'QueueLength': self._boundedInt(
                    self.Get(self.KILL_EFFECT_BF1_QUEUE_LENGTH_SETTING_KEY, 7), 7, 1, 7),
            }
        if style == 'battlefield5':
            return {
                'ShowScoreDetails': bool(self.Get(self.KILL_EFFECT_BF5_SHOW_SCORE_SETTING_KEY, True)),
                'ShowDistance': bool(self.Get(self.KILL_EFFECT_BF5_SHOW_DISTANCE_SETTING_KEY, True)),
                'QueueLength': self._boundedInt(
                    self.Get(self.KILL_EFFECT_BF5_QUEUE_LENGTH_SETTING_KEY, 7), 7, 1, 7),
            }
        if style == 'delta_force':
            return {
                'QueueLength': self._boundedInt(
                    self.Get(self.KILL_EFFECT_DELTA_QUEUE_LENGTH_SETTING_KEY, 7), 7, 1, 7)
            }
        if style == 'old_priest':
            return {
                'QueueLength': self._boundedInt(
                    self.Get(self.KILL_EFFECT_OLD_PRIEST_QUEUE_LENGTH_SETTING_KEY, 7), 7, 1, 7)
            }
        if style == 'valorant':
            return {
                'ShowHeadshot': bool(self.Get(self.KILL_EFFECT_VALORANT_SHOW_HEADSHOT_SETTING_KEY, True)),
                'MaxTier': self._boundedInt(
                    self.Get(self.KILL_EFFECT_VALORANT_MAX_TIER_SETTING_KEY, 3), 3, 1, 3),
            }
        if style == 'cod':
            return {
                'TauntSource': self.GetCodTauntSource(),
            }
        if style == 'qinshou_xiansheng':
            values = (
                (self.KILL_EFFECT_QINSHOU_HOLD_DURATION_SETTING_KEY,
                 self.KILL_EFFECT_QINSHOU_HOLD_DURATION_DEFAULT, 0.20, 10.0),
                (self.KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_SETTING_KEY,
                 self.KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_DEFAULT, 0.10, 5.0),
                (self.KILL_EFFECT_QINSHOU_PITCH_MIN_SETTING_KEY,
                 self.KILL_EFFECT_QINSHOU_PITCH_MIN_DEFAULT, 0.10, 3.0),
                (self.KILL_EFFECT_QINSHOU_PITCH_MAX_SETTING_KEY,
                 self.KILL_EFFECT_QINSHOU_PITCH_MAX_DEFAULT, 0.10, 3.0),
            )
            normalized = []
            for key, defaultValue, minimum, maximum in values:
                normalized.append(self._boundedFloat(
                    self.Get(key, defaultValue), defaultValue, minimum, maximum))
            pitchMin, pitchMax = min(normalized[2:]), max(normalized[2:])
            return {
                'HoldDuration': normalized[0],
                'FadeOutDuration': normalized[1],
                'PitchMin': pitchMin,
                'PitchMax': pitchMax,
            }
        return {}

    def GetControlSize(self, ctrl):
        try:
            size = ctrl.GetSize()
            if size and len(size) >= 2:
                return (float(size[0]), float(size[1]))
        except Exception:
            pass
        return (0.0, 0.0)

    def GetUiReferenceSize(self, uiNode=None, panelPath=''):
        if uiNode and panelPath:
            panel = uiNode.GetBaseUIControl(panelPath)
            size = self.GetControlSize(panel) if panel else (0.0, 0.0)
            if size[0] > 1.0 and size[1] > 1.0:
                return size
        for getterName in ('GetScreenViewInfo', 'GetScreenSize'):
            getter = getattr(GameComp, getterName, None)
            if not getter:
                continue
            try:
                size = getter()
                if size and len(size) >= 2 and float(size[0]) > 1.0 and float(size[1]) > 1.0:
                    return (float(size[0]), float(size[1]))
            except Exception:
                pass
        return (0.0, 0.0)

    def ApplyKillEffectLayoutToControl(
        self, uiNode, path, style, referencePath='', baseSize=None, applyAlpha=True
    ):
        if not uiNode or not path:
            return False
        ctrl = uiNode.GetBaseUIControl(path)
        if not ctrl:
            return False
        referenceSize = self.GetUiReferenceSize(uiNode, referencePath)
        if not isinstance(baseSize, (list, tuple)) or len(baseSize) < 2:
            baseSize = self.GetControlSize(ctrl)
        if not baseSize or len(baseSize) < 2 or baseSize[0] <= 0.0 or baseSize[1] <= 0.0:
            return False
        data = self.GetKillEffectLayout(style)
        scale = float(data['Size']) / 100.0
        size = (float(baseSize[0]) * scale, float(baseSize[1]) * scale)
        try:
            ctrl.SetAnchorFrom('top_left')
            ctrl.SetAnchorTo('center')
        except Exception:
            pass
        try:
            resultX = ctrl.SetFullSize('x', {
                'followType': 'none',
                'relativeValue': 0.0,
                'absoluteValue': float(size[0]),
            })
            resultY = ctrl.SetFullSize('y', {
                'followType': 'none',
                'relativeValue': 0.0,
                'absoluteValue': float(size[1]),
            })
            if resultX is False or resultY is False:
                raise ValueError('SetFullSize failed')
        except Exception:
            try:
                ctrl.SetSize(size, False)
            except TypeError:
                ctrl.SetSize(size)
            except Exception:
                return False
        center = data['Center']
        try:
            resultX = ctrl.SetFullPosition('x', {
                'followType': 'parent',
                'relativeValue': float(center[0]),
                'absoluteValue': 0.0,
            })
            resultY = ctrl.SetFullPosition('y', {
                'followType': 'parent',
                'relativeValue': float(center[1]),
                'absoluteValue': 0.0,
            })
            if resultX is False or resultY is False:
                raise ValueError('SetFullPosition failed')
        except Exception:
            try:
                if not referenceSize or referenceSize[0] <= 0.0 or referenceSize[1] <= 0.0:
                    return False
                ctrl.SetPosition((
                    float(center[0]) * float(referenceSize[0]),
                    float(center[1]) * float(referenceSize[1]),
                ))
            except Exception:
                return False
        try:
            ctrl.SetAlpha(float(data['Alpha']) / 100.0 if applyAlpha else 1.0)
            return True
        except Exception as error:
            print('[KillBroadcast] apply kill layout error:', path, error)
            return False
