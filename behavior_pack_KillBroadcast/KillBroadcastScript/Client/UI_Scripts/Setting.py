# -*- coding: utf-8 -*-
import time

import mod.client.extraClientApi as clientApi

from ...Compat import IsHideKillSettingsProviderLoaded, IsTsGunsClientLoaded
from .Gd656KillEffectUI import Gd656KillEffectUI
from .KillBroadcastSettingManager import KillBroadcastSettingManager


ScreenNode = clientApi.GetScreenNodeCls()
GameComp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())


class Setting(ScreenNode):
    MAX_CELLS = 13
    SETTINGS_SAVE_DEBOUNCE_SECONDS = 0.30
    LAYOUT_EDITOR_PATH = '/UISettingPanel'
    LAYOUT_EDITOR_CSGO_PATH = LAYOUT_EDITOR_PATH + '/KillPanel'
    LAYOUT_EDITOR_ALT_PATH = LAYOUT_EDITOR_PATH + '/KillPanel_DeltaForce'
    LAYOUT_EDITOR_STYLE_BAR_PATH = LAYOUT_EDITOR_PATH + '/KillEffectStyleBar'
    LAYOUT_SHARE_PREFIX = 'TGKE1'
    LAYOUT_SHARE_STYLE_MAP = {
        'csgo': 'c',
        'cf_combo': 'f',
        'pubg': 'p',
        'battlefield1': 'b1',
        'battlefield5': 'b5',
        'delta_force': 'd',
        'old_priest': 'op',
        'valorant': 'v',
        'king_honor': 'kh',
        'cod': 'o',
        'apex': 'a',
        'cupping_cat': 'cc',
        'xiaoxiao_world': 'xw',
        'big_dog_bark': 'bd',
        'qinshou_xiansheng': 'qs',
    }
    LAYOUT_SHARE_STYLE_REVERSE_MAP = dict(
        (shortName, style) for style, shortName in LAYOUT_SHARE_STYLE_MAP.items()
    )
    LAYOUT_SHARE_STYLE_REVERSE_MAP['l'] = 'pubg'

    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.uiNode = None
        self.settingMgr = KillBroadcastSettingManager()
        self.hiddenByProvider = False
        self.scrollPath = ''
        self.updateTick = 0
        self.cellDefinitions = {}
        self.toggleValues = {}
        self.sliderValues = {}
        self.layoutEditing = False
        self.layoutEditorStyle = 'csgo'
        self.layoutDragState = {}
        self.layoutPreviewDefaults = {}
        self.layoutPreviewController = None
        self.layoutPreviewNextTime = 0.0
        self.layoutLastSliderValues = {'alpha': None, 'size': None}
        self.layoutBoundNodeId = None
        self.layoutInfoTimer = None
        self.settingsDirty = False
        self.settingsSaveTimer = None

    def Create(self):
        self.uiNode = clientApi.GetUI('KillBroadcast', 'Setting')
        self.settingMgr.LoadConfig()
        self.hiddenByProvider = bool(
            IsHideKillSettingsProviderLoaded() or IsTsGunsClientLoaded()
        )
        self.SetVisible('/Setting_Panel/Category_Choice', not self.hiddenByProvider)
        self.SetVisible('/Setting_Panel/Setting_Elements', not self.hiddenByProvider)
        self.SetVisible('/Setting_Panel/HiddenNotice', self.hiddenByProvider)
        self.SetVisible(self.LAYOUT_EDITOR_PATH, False)
        self.SetVisible(self.LAYOUT_EDITOR_PATH + '/PastePanel', False)
        self.BindButton('/Setting_Panel/TitleBar/Cancel', self.OnClose)
        if self.hiddenByProvider:
            return
        self.scrollPath = self.GetSettingScrollPath()
        self.ConfigureCells()
        self.RefreshControls()

    def GetSettingScrollPath(self):
        path = '/Setting_Panel/Setting_Elements/elements_scroll'
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        scroll = ctrl.asScrollView() if ctrl else None
        if not scroll:
            return ''
        try:
            return scroll.GetScrollViewContentPath()
        except Exception:
            return ''

    def GetCellPath(self, index):
        if not self.scrollPath:
            return ''
        return self.scrollPath + '/cell_' + str(index)

    def SetVisible(self, path, visible):
        if not path:
            return False
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if not ctrl:
            return False
        ctrl.SetVisible(bool(visible))
        return True

    def SetLabel(self, path, text):
        if not path:
            return False
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        if not ctrl:
            return False
        try:
            label = ctrl.asLabel()
            if not label:
                return False
            label.SetText(self.ToText(text))
            return True
        except Exception:
            return False

    def ToText(self, value):
        if value is None:
            return u''
        try:
            if isinstance(value, unicode):
                return value
        except NameError:
            if isinstance(value, str):
                return value
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except Exception:
                return value.decode('utf-8', 'ignore')
        try:
            return unicode(value)
        except NameError:
            return str(value)

    def BindButton(self, path, callback):
        if not path:
            return False
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        button = ctrl.asButton() if ctrl else None
        if not button:
            return False
        button.AddTouchEventParams({'isSwallow': True})
        button.SetButtonTouchUpCallback(callback)
        return True

    def BuildCellDefinitions(self):
        manager = self.settingMgr
        definitions = [
            {
                'Name': u'启用击杀特效',
                'Introduction': u'| 控制击杀后是否显示击杀反馈',
                'Type': 'Toggle',
                'Key': manager.KILL_EFFECT_ENABLE_SETTING_KEY,
                'Default': True,
            },
            {
                'Name': u'显示击中标记',
                'Introduction': u'| 控制准星中心的四线命中反馈',
                'Type': 'Toggle',
                'Key': manager.HIT_MARKER_ENABLE_SETTING_KEY,
                'Default': True,
            },
            {
                'Name': u'击杀震动反馈',
                'Introduction': u'| 击杀时触发设备短震动',
                'Type': 'Toggle',
                'Key': manager.KILL_VIBRATION_FEEDBACK_SETTING_KEY,
                'Default': False,
            },
            {
                'Name': u'击杀特效风格',
                'Introduction': u'| 切换当前击杀反馈样式及其专属选项',
                'Type': 'Button',
                'Action': 'Style',
                'AboveText': manager.GetKillEffectStyleName(),
            },
            {
                'Name': u'击杀特效UI自定义',
                'Introduction': u'| 拖动预览并独立调整每种风格的大小和透明度',
                'Type': 'Button',
                'Action': 'LayoutEditor',
                'AboveText': u'调整',
            },
            {
                'Name': u'击杀重置时间',
                'Introduction': u'| 控制击杀反馈保持显示的时间',
                'Type': 'Slider',
                'Key': manager.KILL_EFFECT_RESET_TIME_SETTING_KEY,
                'Default': 5.0,
                'Min': 3.0,
                'Max': 15.0,
                'Step': 1.0,
                'Integer': True,
                'ValueFormat': u'%d秒',
            },
        ]
        style = manager.GetKillEffectStyle()
        styleDefinitions = {
            'csgo': [
                {
                    'Name': u'使用CT阵营图标',
                    'Introduction': u'| 关闭显示T阵营，开启显示CT阵营',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_TEAM_CT_SETTING_KEY,
                    'Default': False,
                },
                {
                    'Name': u'击杀拖尾长度',
                    'Introduction': u'| 调整CSGO卡牌特效的拖尾长度',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_TRAIL_LENGTH_SETTING_KEY,
                    'Default': 1.0,
                    'Min': 0.5,
                    'Max': 2.0,
                    'Step': 0.1,
                    'ValueFormat': u'%.1fX',
                },
            ],
            'cf_combo': [
                {
                    'Name': u'最高连杀图标等级',
                    'Introduction': u'| 限制CF连杀图标和语音的最高等级',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_CF_MAX_COMBO_SETTING_KEY,
                    'Default': 6,
                    'Min': 2.0,
                    'Max': 6.0,
                    'Step': 1.0,
                    'Integer': True,
                    'ValueFormat': u'%d级',
                },
                {
                    'Name': u'显示击杀详情',
                    'Introduction': u'| 显示目标、武器、爆头与距离信息',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_CF_SHOW_DETAILS_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'显示击杀距离',
                    'Introduction': u'| 在CF击杀详情中显示距离',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_CF_SHOW_DISTANCE_SETTING_KEY,
                    'Default': True,
                },
            ],
            'pubg': [
                {
                    'Name': u'显示淘汰武器',
                    'Introduction': u'| 在PUBG淘汰字幕中显示武器',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_PUBG_SHOW_WEAPON_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'显示淘汰距离',
                    'Introduction': u'| 在PUBG淘汰字幕中显示距离',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_PUBG_SHOW_DISTANCE_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'显示连续淘汰',
                    'Introduction': u'| 连续击杀时显示累计淘汰数量',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_PUBG_SHOW_COMBO_SETTING_KEY,
                    'Default': True,
                },
            ],
            'apex': [
                {
                    'Name': u'\u662f\u5426\u663e\u793a\u80cc\u666f',
                    'Introduction': u'| \u63a7\u5236APEX\u51fb\u6740\u7279\u6548\u7684\u80cc\u666f\u662f\u5426\u663e\u793a',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_APEX_SHOW_BACKGROUND_SETTING_KEY,
                    'Default': True,
                },
            ],
            'battlefield1': [
                {
                    'Name': u'\u662f\u5426\u663e\u793a\u80cc\u666f',
                    'Introduction': u'| \u63a7\u5236\u6218\u57301\u51fb\u6740\u7279\u6548\u7684\u80cc\u666f\u662f\u5426\u663e\u793a',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_BF1_SHOW_BACKGROUND_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'骷髅队列最大数量',
                    'Introduction': u'| 控制战地1队列最多显示的图标数量',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_BF1_QUEUE_LENGTH_SETTING_KEY,
                    'Default': 7,
                    'Min': 1.0,
                    'Max': 7.0,
                    'Step': 1.0,
                    'Integer': True,
                    'ValueFormat': u'%d个',
                },
            ],
            'battlefield5': [
                {
                    'Name': u'显示奖励与累计得分',
                    'Introduction': u'| 显示爆头奖励、击杀确认和累计得分',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_BF5_SHOW_SCORE_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'显示击杀距离',
                    'Introduction': u'| 在战地5击杀文字中显示距离',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_BF5_SHOW_DISTANCE_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'骷髅队列最大数量',
                    'Introduction': u'| 控制战地5队列最多显示的图标数量',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_BF5_QUEUE_LENGTH_SETTING_KEY,
                    'Default': 7,
                    'Min': 1.0,
                    'Max': 7.0,
                    'Step': 1.0,
                    'Integer': True,
                    'ValueFormat': u'%d个',
                },
            ],
            'delta_force': [
                {
                    'Name': u'骷髅队列最大数量',
                    'Introduction': u'| 控制三角洲队列保留的图标数量',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_DELTA_QUEUE_LENGTH_SETTING_KEY,
                    'Default': 7,
                    'Min': 1.0,
                    'Max': 7.0,
                    'Step': 1.0,
                    'Integer': True,
                    'ValueFormat': u'%d个',
                },
            ],
            'old_priest': [
                {
                    'Name': u'表情队列最大数量',
                    'Introduction': u'| 控制老牧师队列保留的随机表情数量',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_OLD_PRIEST_QUEUE_LENGTH_SETTING_KEY,
                    'Default': 7,
                    'Min': 1.0,
                    'Max': 7.0,
                    'Step': 1.0,
                    'Integer': True,
                    'ValueFormat': u'%d个',
                },
            ],
            'valorant': [
                {
                    'Name': u'显示爆头标记',
                    'Introduction': u'| 爆头时显示无畏契约爆头标记',
                    'Type': 'Toggle',
                    'Key': manager.KILL_EFFECT_VALORANT_SHOW_HEADSHOT_SETTING_KEY,
                    'Default': True,
                },
                {
                    'Name': u'最高进化等级',
                    'Introduction': u'| 限制无畏契约图标的最高进化等级',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_VALORANT_MAX_TIER_SETTING_KEY,
                    'Default': 3,
                    'Min': 1.0,
                    'Max': 3.0,
                    'Step': 1.0,
                    'Integer': True,
                    'ValueFormat': u'%d级',
                },
            ],
            'cod': [
                {
                    'Name': u'嘉豪语录分类',
                    'Introduction': u'| 选择COD击杀嘲讽语录来源',
                    'Type': 'Button',
                    'Action': 'CodTauntSource',
                    'AboveText': manager.GetCodTauntSourceName(),
                },
            ],
            'qinshou_xiansheng': [
                {
                    'Name': u'\u753b\u9762\u505c\u7559\u65f6\u95f4',
                    'Introduction': u'| \u8c03\u6574\u89e6\u53d1\u540e\u5230\u753b\u9762\u5f00\u59cb\u6de1\u51fa\u7684\u65f6\u95f4',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_QINSHOU_HOLD_DURATION_SETTING_KEY,
                    'Default': manager.KILL_EFFECT_QINSHOU_HOLD_DURATION_DEFAULT,
                    'Min': 0.20,
                    'Max': 10.0,
                    'Step': 0.05,
                    'ValueFormat': u'%.2f\u79d2',
                },
                {
                    'Name': u'\u753b\u9762\u6de1\u51fa\u65f6\u95f4',
                    'Introduction': u'| \u8c03\u6574\u56fe\u7247\u4ece\u5b8c\u5168\u663e\u793a\u5230\u6d88\u5931\u6240\u9700\u7684\u65f6\u95f4',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_SETTING_KEY,
                    'Default': manager.KILL_EFFECT_QINSHOU_FADE_OUT_DURATION_DEFAULT,
                    'Min': 0.10,
                    'Max': 5.0,
                    'Step': 0.10,
                    'ValueFormat': u'%.1f\u79d2',
                },
                {
                    'Name': u'\u97f3\u9891\u6700\u4f4e\u500d\u7387',
                    'Introduction': u'| \u8bbe\u7f6e\u968f\u673a\u97f3\u9891\u500d\u7387\u7684\u4e00\u7aef\uff0c\u64ad\u653e\u65f6\u81ea\u52a8\u6309\u5927\u5c0f\u6392\u5e8f',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_QINSHOU_PITCH_MIN_SETTING_KEY,
                    'Default': manager.KILL_EFFECT_QINSHOU_PITCH_MIN_DEFAULT,
                    'Min': 0.10,
                    'Max': 3.0,
                    'Step': 0.10,
                    'ValueFormat': u'%.1fX',
                },
                {
                    'Name': u'\u97f3\u9891\u6700\u9ad8\u500d\u7387',
                    'Introduction': u'| \u8bbe\u7f6e\u968f\u673a\u97f3\u9891\u500d\u7387\u7684\u53e6\u4e00\u7aef\uff0c\u64ad\u653e\u65f6\u81ea\u52a8\u6309\u5927\u5c0f\u6392\u5e8f',
                    'Type': 'Slider',
                    'Key': manager.KILL_EFFECT_QINSHOU_PITCH_MAX_SETTING_KEY,
                    'Default': manager.KILL_EFFECT_QINSHOU_PITCH_MAX_DEFAULT,
                    'Min': 0.10,
                    'Max': 3.0,
                    'Step': 0.10,
                    'ValueFormat': u'%.1fX',
                },
            ],
        }
        return definitions + styleDefinitions.get(style, [])

    def ConfigureCells(self):
        definitions = self.BuildCellDefinitions()
        self.cellDefinitions = {}
        self.toggleValues = {}
        self.sliderValues = {}
        for index in range(1, self.MAX_CELLS + 1):
            cellPath = self.GetCellPath(index)
            if index > len(definitions):
                self.SetVisible(cellPath, False)
                continue
            definition = definitions[index - 1]
            self.cellDefinitions[index] = definition
            controlType = definition.get('Type', '')
            self.SetVisible(cellPath, True)
            self.SetLabel(cellPath + '/Panel/SettingName', definition.get('Name', u'设置'))
            self.SetLabel(cellPath + '/Panel/Introduction', definition.get('Introduction', u''))
            for childType in ('Button', 'Toggle', 'Slider'):
                self.SetVisible(cellPath + '/' + childType, childType == controlType)
            if controlType == 'Button':
                self.SetLabel(cellPath + '/Button/above', definition.get('AboveText', u'调整'))
                action = definition.get('Action')
                if action == 'Style':
                    self.BindButton(cellPath + '/Button', self.OnStyle)
                elif action == 'LayoutEditor':
                    self.BindButton(cellPath + '/Button', self.OnLayoutEditor)
                elif action == 'CodTauntSource':
                    self.BindButton(cellPath + '/Button', self.OnCodTauntSource)

    def GetSwitchToggleControl(self, cellPath):
        for path, togglePath in (
            (cellPath + '/Toggle', '/this_toggle'),
            (cellPath + '/Toggle/this_toggle', ''),
        ):
            ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
            if not ctrl:
                continue
            try:
                toggle = ctrl.asSwitchToggle()
            except Exception:
                toggle = None
            if toggle:
                return toggle, togglePath
        return None

    def SetToggleValue(self, index, value):
        result = self.GetSwitchToggleControl(self.GetCellPath(index))
        if not result:
            return False
        toggle, togglePath = result
        try:
            if togglePath:
                toggle.SetToggleState(bool(value), togglePath)
            else:
                toggle.SetToggleState(bool(value))
            self.toggleValues[index] = bool(value)
            return True
        except Exception:
            return False

    def GetToggleValue(self, index):
        result = self.GetSwitchToggleControl(self.GetCellPath(index))
        if not result:
            return None
        toggle, togglePath = result
        try:
            if togglePath:
                return bool(toggle.GetToggleState(togglePath))
            return bool(toggle.GetToggleState())
        except TypeError:
            try:
                return bool(toggle.GetToggleState())
            except Exception:
                return None
        except Exception:
            return None

    def GetSlider(self, index):
        path = self.GetCellPath(index) + '/Slider/slider'
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode and path else None
        return ctrl.asSlider() if ctrl else None

    def NormalizeSliderValue(self, definition, value):
        minimum = float(definition.get('Min', 0.0))
        maximum = float(definition.get('Max', 1.0))
        step = max(float(definition.get('Step', 1.0)), 0.000001)
        value = min(maximum, max(minimum, float(value)))
        value = minimum + round((value - minimum) / step) * step
        value = min(maximum, max(minimum, value))
        if definition.get('Integer'):
            return int(round(value))
        return round(float(value), 4)

    def FormatSliderValue(self, definition, value):
        valueFormat = definition.get('ValueFormat', u'%s')
        try:
            return valueFormat % value
        except Exception:
            return self.ToText(value)

    def SetSliderControl(self, index, definition, value):
        value = self.NormalizeSliderValue(definition, value)
        minimum = float(definition.get('Min', 0.0))
        maximum = float(definition.get('Max', 1.0))
        ratio = (float(value) - minimum) / max(maximum - minimum, 0.000001)
        slider = self.GetSlider(index)
        if slider:
            try:
                slider.SetSliderValue(min(1.0, max(0.0, ratio)))
            except Exception:
                pass
        self.sliderValues[index] = value
        self.SetLabel(
            self.GetCellPath(index) + '/Slider/label',
            self.FormatSliderValue(definition, value)
        )

    def GetSliderControlValue(self, index, definition):
        slider = self.GetSlider(index)
        if not slider:
            return None
        try:
            ratio = min(1.0, max(0.0, float(slider.GetSliderValue())))
        except Exception:
            return None
        minimum = float(definition.get('Min', 0.0))
        maximum = float(definition.get('Max', 1.0))
        return self.NormalizeSliderValue(definition, minimum + ratio * (maximum - minimum))

    def GetDefinitionValue(self, definition):
        return self.settingMgr.Get(definition.get('Key'), definition.get('Default'))

    def SetDefinitionValue(self, definition, value):
        result = self.settingMgr.Set(definition.get('Key'), value, False)
        self.MarkSettingsDirty()
        return result

    def CancelSettingsSaveTimer(self):
        if self.settingsSaveTimer is None:
            return
        try:
            GameComp.CancelTimer(self.settingsSaveTimer)
        except Exception:
            pass
        self.settingsSaveTimer = None

    def MarkSettingsDirty(self):
        self.settingsDirty = True
        self.CancelSettingsSaveTimer()
        try:
            self.settingsSaveTimer = GameComp.AddTimer(
                self.SETTINGS_SAVE_DEBOUNCE_SECONDS,
                self.FlushSettingsSave,
            )
        except Exception:
            self.settingsSaveTimer = None

    def FlushSettingsSave(self):
        self.CancelSettingsSaveTimer()
        if not self.settingsDirty:
            return True
        if not self.settingMgr.SaveConfig():
            return False
        self.settingsDirty = False
        return True

    def RefreshControls(self):
        for index, definition in self.cellDefinitions.items():
            controlType = definition.get('Type')
            if controlType == 'Toggle':
                self.SetToggleValue(index, bool(self.GetDefinitionValue(definition)))
            elif controlType == 'Slider':
                self.SetSliderControl(index, definition, self.GetDefinitionValue(definition))
            elif definition.get('Action') == 'Style':
                self.SetLabel(
                    self.GetCellPath(index) + '/Button/above',
                    self.settingMgr.GetKillEffectStyleName()
                )
            elif definition.get('Action') == 'CodTauntSource':
                self.SetLabel(
                    self.GetCellPath(index) + '/Button/above',
                    self.settingMgr.GetCodTauntSourceName()
                )

    def ApplySettings(self):
        try:
            system = clientApi.GetSystem('KillBroadcast', 'KillBroadcastClientSystem')
            if system and hasattr(system, 'ApplySharedSettings'):
                values = self.settingMgr.GetValuesSnapshot()
                return system.ApplySharedSettings(values)
        except Exception:
            pass
        return False

    def Update(self):
        if self.hiddenByProvider or not self.scrollPath:
            return
        if self.layoutEditing:
            self.UpdateLayoutEditor()
            return
        self.updateTick += 1
        if self.updateTick < 2:
            return
        self.updateTick = 0
        changed = False
        for index, definition in self.cellDefinitions.items():
            controlType = definition.get('Type')
            if controlType == 'Toggle':
                value = self.GetToggleValue(index)
                if value is None or self.toggleValues.get(index) == value:
                    continue
                self.toggleValues[index] = value
                self.SetDefinitionValue(definition, value)
                changed = True
            elif controlType == 'Slider':
                value = self.GetSliderControlValue(index, definition)
                if value is None:
                    continue
                self.SetLabel(
                    self.GetCellPath(index) + '/Slider/label',
                    self.FormatSliderValue(definition, value)
                )
                if self.sliderValues.get(index) == value:
                    continue
                self.sliderValues[index] = value
                self.SetDefinitionValue(definition, value)
                changed = True
        if changed:
            self.ApplySettings()

    def OnClose(self, args=None):
        self.FlushSettingsSave()
        self.CloseLayoutEditor()
        self.SetTouchMouseSimulation(False)
        try:
            clientApi.PopScreen()
        except Exception:
            pass

    def OnStyle(self, args=None):
        self.settingMgr.CycleKillEffectStyle(False)
        self.MarkSettingsDirty()
        self.ConfigureCells()
        self.RefreshControls()
        self.ApplySettings()

    def OnLayoutEditor(self, args=None):
        return self.OpenLayoutEditor()

    def OnCodTauntSource(self, args=None):
        self.settingMgr.CycleCodTauntSource(False)
        self.MarkSettingsDirty()
        self.ConfigureCells()
        self.RefreshControls()
        self.ApplySettings()
        return True

    def OpenLayoutEditor(self):
        if not self.uiNode:
            return False
        panel = self.uiNode.GetBaseUIControl(self.LAYOUT_EDITOR_PATH)
        if not panel:
            return False
        self.layoutEditing = True
        self.layoutEditorStyle = self.settingMgr.GetKillEffectStyle()
        self.layoutDragState = {}
        self.SetVisible('/Setting_Panel', False)
        self.SetVisible(self.LAYOUT_EDITOR_PATH, True)
        self.SetVisible(self.LAYOUT_EDITOR_PATH + '/PastePanel', False)
        self.SetVisible(self.LAYOUT_EDITOR_STYLE_BAR_PATH, True)
        self.SetTouchMouseSimulation(True)
        self.CaptureLayoutPreviewDefaults()
        self.BindLayoutEditorControls()
        self.SetLayoutEditorStyle(self.layoutEditorStyle, True)
        return True

    def CloseLayoutEditor(self):
        self.layoutEditing = False
        self.layoutDragState = {}
        self.layoutPreviewNextTime = 0.0
        self.CancelLayoutInfoTimer()
        if self.layoutPreviewController:
            try:
                self.layoutPreviewController.Destroy()
            except Exception:
                pass
        self.layoutPreviewController = None
        self.layoutPreviewDefaults = {}
        self.layoutLastSliderValues = {'alpha': None, 'size': None}

    def SetTouchMouseSimulation(self, enable):
        try:
            GameComp.SimulateTouchWithMouse(bool(enable))
        except Exception:
            pass

    def CaptureLayoutPreviewDefaults(self):
        referenceSize = self.GetLayoutReferenceSize()
        if referenceSize[0] > 1.0 and referenceSize[1] > 1.0:
            baseSize = (float(referenceSize[0]), float(referenceSize[1]) * 0.13)
            for path in (self.LAYOUT_EDITOR_CSGO_PATH, self.LAYOUT_EDITOR_ALT_PATH):
                self.layoutPreviewDefaults[path] = baseSize
            return True
        captured = False
        for path in (self.LAYOUT_EDITOR_CSGO_PATH, self.LAYOUT_EDITOR_ALT_PATH):
            ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
            size = self.GetControlSize(ctrl)
            if size[0] > 1.0 and size[1] > 1.0:
                self.layoutPreviewDefaults[path] = size
                captured = True
        return captured

    def BindLayoutEditorControls(self):
        if not self.uiNode:
            return False
        nodeId = id(self.uiNode)
        if self.layoutBoundNodeId == nodeId:
            return True
        self.layoutBoundNodeId = nodeId
        for path, callback in (
            (self.LAYOUT_EDITOR_STYLE_BAR_PATH + '/Previous', self.OnLayoutPreviousStyle),
            (self.LAYOUT_EDITOR_STYLE_BAR_PATH + '/Next', self.OnLayoutNextStyle),
            (self.LAYOUT_EDITOR_PATH + '/SettingChoice/Reset', self.OnLayoutReset),
            (self.LAYOUT_EDITOR_PATH + '/SettingChoice/Import', self.OnLayoutOpenImport),
            (self.LAYOUT_EDITOR_PATH + '/SettingChoice/Share', self.OnLayoutShare),
            (self.LAYOUT_EDITOR_PATH + '/SettingChoice/Save', self.OnLayoutSave),
            (self.LAYOUT_EDITOR_PATH + '/PastePanel/Paste', self.OnLayoutPaste),
            (self.LAYOUT_EDITOR_PATH + '/PastePanel/Use', self.OnLayoutApplyImport),
            (self.LAYOUT_EDITOR_PATH + '/PastePanel/TitleBar/Cancel', self.OnLayoutImportCancel),
        ):
            self.BindButton(path, callback)
        for path in (self.LAYOUT_EDITOR_CSGO_PATH, self.LAYOUT_EDITOR_ALT_PATH):
            ctrl = self.uiNode.GetBaseUIControl(path)
            button = ctrl.asButton() if ctrl else None
            if not button:
                continue
            button.AddTouchEventParams({
                'isSwallow': True,
                'is_handle_button_move_event': True,
            })
            button.SetButtonTouchDownCallback(
                lambda args, controlPath=path: self.OnLayoutDragDown(controlPath, args)
            )
            button.SetButtonTouchMoveCallback(
                lambda args, controlPath=path: self.OnLayoutDragMove(controlPath, args)
            )
            button.SetButtonTouchUpCallback(self.OnLayoutDragEnd)
            button.SetButtonTouchCancelCallback(self.OnLayoutDragEnd)
        return True

    def GetLayoutPreviewPath(self, style=None):
        style = str(style or self.layoutEditorStyle).lower()
        if style == self.settingMgr.STYLE_CSGO:
            return self.LAYOUT_EDITOR_CSGO_PATH
        return self.LAYOUT_EDITOR_ALT_PATH

    def GetStyleDisplayName(self, style):
        style = str(style or '').lower()
        for value, name in self.settingMgr.STYLE_OPTIONS:
            if value == style:
                return name
        return u'CSGO'

    def SetLayoutEditorStyle(self, style, refreshPreview=True):
        styles = [value for value, _ in self.settingMgr.STYLE_OPTIONS]
        style = str(style or '').lower()
        if style not in styles:
            style = self.settingMgr.STYLE_CSGO
        self.layoutEditorStyle = style
        isCsgo = style == self.settingMgr.STYLE_CSGO
        self.SetVisible(self.LAYOUT_EDITOR_CSGO_PATH, isCsgo)
        self.SetVisible(self.LAYOUT_EDITOR_ALT_PATH, not isCsgo)
        self.SetLabel(
            self.LAYOUT_EDITOR_STYLE_BAR_PATH + '/StyleName',
            self.GetStyleDisplayName(style)
        )
        self.SyncLayoutEditorSliders()
        self.ApplyLayoutEditorPreview()
        if refreshPreview:
            self.RefreshLayoutEditorPerformance()
        return True

    def StepLayoutEditorStyle(self, direction):
        styles = [value for value, _ in self.settingMgr.STYLE_OPTIONS]
        try:
            index = styles.index(self.layoutEditorStyle)
        except ValueError:
            index = 0
        return self.SetLayoutEditorStyle(styles[(index + direction) % len(styles)], True)

    def OnLayoutPreviousStyle(self, args=None):
        return self.StepLayoutEditorStyle(-1)

    def OnLayoutNextStyle(self, args=None):
        return self.StepLayoutEditorStyle(1)

    def SetEditorSliderValue(self, path, value):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        slider = ctrl.asSlider() if ctrl else None
        if not slider:
            return False
        slider.SetSliderValue(min(1.0, max(0.0, float(value))))
        return True

    def GetEditorSliderValue(self, path):
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        slider = ctrl.asSlider() if ctrl else None
        if not slider:
            return None
        try:
            return float(slider.GetSliderValue())
        except Exception:
            return None

    def SyncLayoutEditorSliders(self):
        data = self.settingMgr.GetKillEffectLayout(self.layoutEditorStyle)
        sizeRange = 150.0
        sizeValue = (float(data.get('Size', 100)) - 50.0) / sizeRange
        alphaValue = float(data.get('Alpha', 100)) / 100.0
        self.SetEditorSliderValue(
            self.LAYOUT_EDITOR_PATH + '/SettingChoice/Transparency_slider',
            alphaValue
        )
        self.SetEditorSliderValue(
            self.LAYOUT_EDITOR_PATH + '/SettingChoice/Size_slider',
            sizeValue
        )
        self.SetLabel(
            self.LAYOUT_EDITOR_PATH + '/SettingChoice/Transparency_label',
            str(int(data.get('Alpha', 100)))
        )
        self.SetLabel(
            self.LAYOUT_EDITOR_PATH + '/SettingChoice/Size_label',
            str(int(data.get('Size', 100)))
        )
        self.layoutLastSliderValues = {'alpha': alphaValue, 'size': sizeValue}

    def ApplyLayoutEditorPreview(self):
        style = self.layoutEditorStyle
        path = self.GetLayoutPreviewPath(style)
        baseSize = self.layoutPreviewDefaults.get(path)
        if style == 'qinshou_xiansheng':
            referenceSize = self.GetLayoutReferenceSize()
            if referenceSize:
                baseSize = referenceSize
        applied = self.settingMgr.ApplyKillEffectLayoutToControl(
            self.uiNode,
            path,
            style,
            self.LAYOUT_EDITOR_PATH,
            baseSize,
            style == self.settingMgr.STYLE_CSGO,
        )
        if self.layoutPreviewController and style != self.settingMgr.STYLE_CSGO:
            data = self.settingMgr.GetKillEffectLayout(style)
            scale = float(data.get('Size', 100)) / 100.0
            if isinstance(baseSize, (list, tuple)) and len(baseSize) >= 2:
                self.layoutPreviewController.SetLayoutViewportSize((
                    float(baseSize[0]) * scale,
                    float(baseSize[1]) * scale,
                ))
            self.layoutPreviewController.SetLayoutScale(scale)
            self.layoutPreviewController.SetLayoutAlpha(float(data.get('Alpha', 100)) / 100.0)
        return applied

    def GetLayoutPreviewController(self):
        if self.layoutPreviewController is None:
            self.layoutPreviewController = Gd656KillEffectUI(self.LAYOUT_EDITOR_ALT_PATH)
        self.layoutPreviewController.Init(self.uiNode)
        return self.layoutPreviewController

    def RefreshLayoutEditorPerformance(self):
        style = self.layoutEditorStyle
        self.settingMgr.ApplyKillEffectStyleToUi(self.uiNode, self.LAYOUT_EDITOR_CSGO_PATH)
        if style == self.settingMgr.STYLE_CSGO:
            if self.layoutPreviewController:
                self.layoutPreviewController.Clear()
            self.layoutPreviewNextTime = time.time() + 3.0
            return True
        controller = self.GetLayoutPreviewController()
        controller.SetStyle(style)
        controller.SetStyleOptions(self.settingMgr.GetKillEffectStyleOptions(style))
        controller.Clear()
        controller.SetPanelVisible(True)
        count = 6 if style in (controller.KING_HONOR_STYLE, controller.XIAOXIAO_WORLD_STYLE) else (
            5 if style in controller.SCROLL_STYLES or style in (
                controller.CUPPING_CAT_STYLE,
                controller.BIG_DOG_BARK_STYLE,
            ) else (
            3 if style in ('cf_combo', 'pubg', 'valorant', 'cod', 'apex') else 1
            )
        )
        for index in range(count):
            controller.AddKill(
                index == count - 1,
                u'死神猎手',
                u'敌方玩家',
                False,
                18.5 + index * 7.3,
                20,
            )
        self.ApplyLayoutEditorPreview()
        previewInterval = 3.2
        if style == 'qinshou_xiansheng':
            options = self.settingMgr.GetKillEffectStyleOptions(style)
            previewInterval = max(previewInterval, (
                float(options.get('HoldDuration', 0.0)) +
                float(options.get('FadeOutDuration', 0.0)) + 0.1
            ))
        self.layoutPreviewNextTime = time.time() + previewInterval
        return True

    def UpdateLayoutEditor(self):
        alphaPath = self.LAYOUT_EDITOR_PATH + '/SettingChoice/Transparency_slider'
        sizePath = self.LAYOUT_EDITOR_PATH + '/SettingChoice/Size_slider'
        alphaValue = self.GetEditorSliderValue(alphaPath)
        sizeValue = self.GetEditorSliderValue(sizePath)
        data = self.settingMgr.GetKillEffectLayout(self.layoutEditorStyle)
        changed = False
        if alphaValue is not None and alphaValue != self.layoutLastSliderValues.get('alpha'):
            data['Alpha'] = int(round(min(1.0, max(0.0, alphaValue)) * 100))
            self.layoutLastSliderValues['alpha'] = alphaValue
            changed = True
        if sizeValue is not None and sizeValue != self.layoutLastSliderValues.get('size'):
            data['Size'] = int(round(50.0 + min(1.0, max(0.0, sizeValue)) * 150.0))
            self.layoutLastSliderValues['size'] = sizeValue
            changed = True
        if changed:
            data = self.settingMgr.SetKillEffectLayout(self.layoutEditorStyle, data, False)
            self.MarkSettingsDirty()
            self.SetLabel(
                self.LAYOUT_EDITOR_PATH + '/SettingChoice/Transparency_label',
                str(data['Alpha'])
            )
            self.SetLabel(
                self.LAYOUT_EDITOR_PATH + '/SettingChoice/Size_label',
                str(data['Size'])
            )
            self.ApplyLayoutEditorPreview()
            self.ApplySettings()
        if self.layoutPreviewController and self.layoutEditorStyle != self.settingMgr.STYLE_CSGO:
            self.layoutPreviewController.UpdateFrame()
        if time.time() >= self.layoutPreviewNextTime:
            self.RefreshLayoutEditorPerformance()

    def GetControlSize(self, ctrl):
        try:
            size = ctrl.GetSize()
            if size and len(size) >= 2:
                return (float(size[0]), float(size[1]))
        except Exception:
            pass
        return (0.0, 0.0)

    def GetLayoutReferenceSize(self):
        panel = self.uiNode.GetBaseUIControl(self.LAYOUT_EDITOR_PATH) if self.uiNode else None
        size = self.GetControlSize(panel)
        if size[0] > 1.0 and size[1] > 1.0:
            return size
        for getterName in ('GetScreenViewInfo', 'GetScreenSize'):
            getter = getattr(GameComp, getterName, None)
            if not getter:
                continue
            try:
                size = getter()
                if size and len(size) >= 2:
                    width = float(size[0])
                    height = float(size[1])
                    if width > 1.0 and height > 1.0:
                        return (width, height)
            except Exception:
                pass
        return (0.0, 0.0)

    def GetPointerPos(self, args):
        if isinstance(args, dict):
            for xKey, yKey in (
                ('TouchPosX', 'TouchPosY'),
                ('ScreenPosX', 'ScreenPosY'),
            ):
                if xKey not in args or yKey not in args:
                    continue
                try:
                    x = float(args.get(xKey))
                    y = float(args.get(yKey))
                    return (x, y)
                except Exception:
                    pass
        try:
            action = clientApi.GetEngineCompFactory().CreateAction(clientApi.GetLocalPlayerId())
            pos = action.GetMousePosition()
            if pos and len(pos) >= 2:
                return (float(pos[0]), float(pos[1]))
        except Exception:
            pass
        return None

    def OnLayoutDragDown(self, controlPath, args):
        if controlPath != self.GetLayoutPreviewPath():
            self.layoutDragState = {}
            return
        ctrl = self.uiNode.GetBaseUIControl(controlPath) if self.uiNode else None
        pointer = self.GetPointerPos(args)
        if not ctrl or not pointer:
            self.layoutDragState = {}
            return
        data = self.settingMgr.GetKillEffectLayout(self.layoutEditorStyle)
        self.layoutDragState = {
            'Path': controlPath,
            'Pointer': pointer,
            'Center': list(data.get('Center', [0.5, 0.835])),
            'BaseSize': self.layoutPreviewDefaults.get(controlPath),
        }

    def OnLayoutDragMove(self, controlPath, args):
        state = self.layoutDragState
        if not state or state.get('Path') != controlPath:
            return
        pointer = self.GetPointerPos(args)
        if not pointer:
            return
        startPointer = state.get('Pointer', pointer)
        refSize = self.GetLayoutReferenceSize()
        if refSize[0] <= 0.0 or refSize[1] <= 0.0:
            return
        startCenter = state.get('Center', [0.5, 0.835])
        center = [
            min(1.0, max(0.0, float(startCenter[0]) + (pointer[0] - startPointer[0]) / refSize[0])),
            min(1.0, max(0.0, float(startCenter[1]) + (pointer[1] - startPointer[1]) / refSize[1])),
        ]
        data = self.settingMgr.GetKillEffectLayout(self.layoutEditorStyle)
        data['Center'] = center
        self.settingMgr.SetKillEffectLayout(self.layoutEditorStyle, data, False)
        self.MarkSettingsDirty()
        self.ApplyLayoutEditorPreview()

    def OnLayoutDragEnd(self, args=None):
        if not self.layoutDragState:
            return False
        self.layoutDragState = {}
        if not self.FlushSettingsSave():
            self.ShowTip(u'击杀特效布局保存失败，请重试')
            return False
        self.ApplySettings()
        return True

    def OnLayoutReset(self, args=None):
        defaultValue = self.settingMgr.LAYOUT_DEFAULTS.get(self.layoutEditorStyle, {})
        self.settingMgr.SetKillEffectLayout(self.layoutEditorStyle, defaultValue, False)
        self.MarkSettingsDirty()
        if not self.FlushSettingsSave():
            self.ShowTip(u'击杀特效布局保存失败，请重试')
            return False
        self.SyncLayoutEditorSliders()
        self.ApplyLayoutEditorPreview()
        self.RefreshLayoutEditorPerformance()
        self.ApplySettings()
        return True

    def OnLayoutSave(self, args=None):
        if not self.layoutEditing:
            return False
        self.layoutDragState = {}
        if not self.FlushSettingsSave():
            self.ShowTip(u'击杀特效布局保存失败，请重试')
            return False
        self.ApplySettings()
        self.CloseLayoutEditor()
        self.SetTouchMouseSimulation(False)
        try:
            clientApi.PopScreen()
            try:
                GameComp.AddTimer(0.05, self.ApplySettings)
            except Exception:
                pass
        except Exception:
            self.SetVisible(self.LAYOUT_EDITOR_PATH, False)
        return True

    def FormatShareNumber(self, value):
        try:
            value = float(value)
        except Exception:
            value = 0.0
        if abs(value - int(round(value))) < 0.00001:
            return str(int(round(value)))
        text = ('%.4f' % value).rstrip('0').rstrip('.')
        return text if text else '0'

    def ParseShareNumber(self, text, defaultValue=None):
        try:
            value = float(self.ToText(text).strip())
        except Exception:
            return defaultValue
        if value != value or value in (float('inf'), float('-inf')):
            return defaultValue
        if abs(value - int(round(value))) < 0.00001:
            return int(round(value))
        return value

    def BuildLayoutShareCode(self, style=None):
        style = self.ToText(style or self.layoutEditorStyle).strip().lower()
        validStyles = set(value for value, _ in self.settingMgr.STYLE_OPTIONS)
        if style not in validStyles:
            return self.LAYOUT_SHARE_PREFIX
        chunks = [self.LAYOUT_SHARE_PREFIX]
        shortName = self.LAYOUT_SHARE_STYLE_MAP.get(style)
        data = self.settingMgr.GetKillEffectLayout(style)
        center = data.get('Center', [0.5, 0.835])
        if not shortName or not isinstance(center, (list, tuple)) or len(center) < 2:
            return self.LAYOUT_SHARE_PREFIX
        values = (
            self.FormatShareNumber(center[0]),
            self.FormatShareNumber(center[1]),
            self.FormatShareNumber(data.get('Size', 100)),
            self.FormatShareNumber(data.get('Alpha', 100)),
        )
        chunks.append(shortName + ':' + ','.join(values))
        return '|'.join(chunks)

    def ParseLayoutShareCode(self, text):
        text = self.ToText(text).strip()
        if not text.startswith(self.LAYOUT_SHARE_PREFIX):
            return None
        chunks = [chunk for chunk in text.split('|') if chunk]
        if not chunks or chunks[0] != self.LAYOUT_SHARE_PREFIX:
            return None
        layouts = {}
        for chunk in chunks[1:]:
            if ':' not in chunk:
                continue
            styleName, valueText = chunk.split(':', 1)
            styleName = self.ToText(styleName).strip().lower()
            validStyles = set(value for value, _ in self.settingMgr.STYLE_OPTIONS)
            style = self.LAYOUT_SHARE_STYLE_REVERSE_MAP.get(styleName, styleName)
            values = valueText.split(',')
            if style not in validStyles or len(values) != 4:
                continue
            parsedValues = [self.ParseShareNumber(value, None) for value in values]
            if any(value is None for value in parsedValues):
                continue
            centerX, centerY, size, alpha = parsedValues
            if not (
                0.0 <= centerX <= 1.0 and
                0.0 <= centerY <= 1.0 and
                50.0 <= size <= 200.0 and
                0.0 <= alpha <= 100.0
            ):
                continue
            layouts[style] = {
                'Center': [centerX, centerY],
                'Size': size,
                'Alpha': alpha,
            }
        return layouts if layouts else None

    def ApplyLayoutShareData(self, layouts):
        if not isinstance(layouts, dict):
            return False
        validStyles = set(value for value, _ in self.settingMgr.STYLE_OPTIONS)
        changed = False
        previousLayouts = {}
        importedStyles = []
        for style, data in layouts.items():
            style = self.ToText(style).strip().lower()
            if style not in validStyles or style not in self.settingMgr.LAYOUT_DEFAULTS:
                continue
            previousLayouts[style] = self.settingMgr.GetKillEffectLayout(style)
            self.settingMgr.SetKillEffectLayout(style, data, False)
            importedStyles.append(style)
            changed = True
        if not changed:
            return False
        wasDirty = self.settingsDirty
        self.CancelSettingsSaveTimer()
        if not self.settingMgr.SaveConfig():
            for style, data in previousLayouts.items():
                self.settingMgr.SetKillEffectLayout(style, data, False)
            self.settingsDirty = wasDirty
            if wasDirty:
                self.MarkSettingsDirty()
            return False
        self.settingsDirty = False
        previewStyle = self.layoutEditorStyle
        if previewStyle not in importedStyles and len(importedStyles) == 1:
            previewStyle = importedStyles[0]
        if previewStyle != self.layoutEditorStyle:
            self.SetLayoutEditorStyle(previewStyle, True)
        else:
            self.SyncLayoutEditorSliders()
            self.ApplyLayoutEditorPreview()
            self.RefreshLayoutEditorPerformance()
        self.ApplySettings()
        return True

    def GetClipboardText(self):
        for obj in (GameComp, clientApi):
            getter = getattr(obj, 'GetClipboardContent', None)
            if not getter:
                continue
            try:
                return getter()
            except Exception:
                pass
        return None

    def SetClipboardText(self, text):
        text = self.ToText(text)
        if not text:
            return False
        for obj in (GameComp, clientApi):
            setter = getattr(obj, 'SetClipboardContent', None)
            if not setter:
                continue
            try:
                result = setter(text)
                if result is False:
                    continue
                return True
            except Exception:
                pass
        return False

    def SetLayoutEditBoxText(self, text):
        path = self.LAYOUT_EDITOR_PATH + '/PastePanel/edit_box'
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        editBox = ctrl.asTextEditBox() if ctrl else None
        if not editBox:
            return False
        editBox.SetEditText(self.ToText(text))
        return True

    def GetLayoutEditBoxText(self):
        path = self.LAYOUT_EDITOR_PATH + '/PastePanel/edit_box'
        ctrl = self.uiNode.GetBaseUIControl(path) if self.uiNode else None
        editBox = ctrl.asTextEditBox() if ctrl else None
        if not editBox:
            return u''
        text = editBox.GetEditText()
        return text if text is not None else u''

    def CancelLayoutInfoTimer(self):
        if self.layoutInfoTimer is None:
            return
        try:
            GameComp.CancelTimer(self.layoutInfoTimer)
        except Exception:
            pass
        self.layoutInfoTimer = None

    def HideLayoutInfo(self):
        self.layoutInfoTimer = None
        self.SetVisible(self.LAYOUT_EDITOR_PATH + '/PastePanel/InformationText', False)

    def ShowLayoutInfo(self, text):
        path = self.LAYOUT_EDITOR_PATH + '/PastePanel/InformationText'
        self.SetLabel(path, text)
        self.SetVisible(path, True)
        self.CancelLayoutInfoTimer()
        try:
            self.layoutInfoTimer = GameComp.AddTimer(1.0, self.HideLayoutInfo)
        except Exception:
            self.layoutInfoTimer = None

    def ShowTip(self, text):
        try:
            GameComp.SetTipMessage(self.ToText(text))
        except Exception:
            pass

    def OnLayoutShare(self, args=None):
        shareCode = self.BuildLayoutShareCode(self.layoutEditorStyle)
        if self.SetClipboardText(shareCode):
            self.ShowTip(u'击杀特效布局分享码已复制')
            return True
        panelPath = self.LAYOUT_EDITOR_PATH + '/PastePanel'
        if self.SetVisible(panelPath, True) and self.SetLayoutEditBoxText(shareCode):
            self.ShowLayoutInfo(u'自动复制失败，请在文本框中手动复制')
            return True
        self.SetVisible(panelPath, False)
        self.ShowTip(u'击杀特效布局分享码生成失败')
        return False

    def OnLayoutOpenImport(self, args=None):
        self.SetVisible(self.LAYOUT_EDITOR_PATH + '/PastePanel', True)
        self.SetVisible(self.LAYOUT_EDITOR_PATH + '/PastePanel/InformationText', False)

    def OnLayoutImportCancel(self, args=None):
        self.SetVisible(self.LAYOUT_EDITOR_PATH + '/PastePanel', False)

    def OnLayoutPaste(self, args=None):
        text = self.GetClipboardText()
        if text is None:
            self.ShowLayoutInfo(u'读取剪贴板失败')
            return
        self.ShowLayoutInfo(
            u'粘贴成功' if self.SetLayoutEditBoxText(text) else u'粘贴失败'
        )

    def OnLayoutApplyImport(self, args=None):
        layouts = self.ParseLayoutShareCode(self.GetLayoutEditBoxText())
        if not layouts:
            self.ShowLayoutInfo(u'击杀特效分享码无效')
            return False
        applied = self.ApplyLayoutShareData(layouts)
        self.ShowLayoutInfo(u'击杀特效布局已应用' if applied else u'击杀特效布局保存失败')
        return applied

    def Destroy(self):
        self.FlushSettingsSave()
        self.CloseLayoutEditor()
        self.SetTouchMouseSimulation(False)
        self.cellDefinitions = {}
        self.toggleValues = {}
        self.sliderValues = {}
