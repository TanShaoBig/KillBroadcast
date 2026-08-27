# -*- coding: utf-8 -*-
import math
import random
import time
import mod.client.extraClientApi as clientApi

from .CodTaunts import COD_TAUNT_SOURCE_JIAHAO_CHARCOAL, GetCodTauntPool


AudioComp = clientApi.GetEngineCompFactory().CreateCustomAudio(clientApi.GetLevelId())


class Gd656KillEffectUI(object):
    DEFAULT_PANEL_PATH = '/KillPanel_DeltaForce'
    CUPPING_CAT_STYLE = 'cupping_cat'
    XIAOXIAO_WORLD_STYLE = 'xiaoxiao_world'
    KING_HONOR_STYLE = 'king_honor'
    BIG_DOG_BARK_STYLE = 'big_dog_bark'
    QINSHOU_XIANSHENG_STYLE = 'qinshou_xiansheng'
    OLD_PRIEST_STYLE = 'old_priest'
    CUPPING_CAT_FRAME_RATE = 12.0
    CUPPING_CAT_FRAME_SIZE = 192.0
    CUPPING_CAT_ATLASES = {
        1: ('textures/ui/killbroadcast_kill_effect/cupping_cat/cupping_cat_1', 13, 4),
        2: ('textures/ui/killbroadcast_kill_effect/cupping_cat/cupping_cat_2', 18, 5),
        3: ('textures/ui/killbroadcast_kill_effect/cupping_cat/cupping_cat_3', 19, 5),
        4: ('textures/ui/killbroadcast_kill_effect/cupping_cat/cupping_cat_4', 16, 4),
        5: ('textures/ui/killbroadcast_kill_effect/cupping_cat/cupping_cat_5', 42, 7),
    }
    XIAOXIAO_WORLD_BASE_WIDTH = 385.0
    XIAOXIAO_WORLD_BASE_HEIGHT = 65.0
    XIAOXIAO_WORLD_ASPECT = XIAOXIAO_WORLD_BASE_WIDTH / XIAOXIAO_WORLD_BASE_HEIGHT
    XIAOXIAO_WORLD_HEAD_SIZE = 51.0
    XIAOXIAO_WORLD_LEFT_HEAD_OFFSET = (7.0, 7.0)
    XIAOXIAO_WORLD_RIGHT_HEAD_OFFSET = (327.0, 7.0)
    XIAOXIAO_WORLD_TEXTURES = {
        1: 'textures/ui/killbroadcast_kill_effect/xiaoxiao_world/xiaoxiao_world_1',
        2: 'textures/ui/killbroadcast_kill_effect/xiaoxiao_world/xiaoxiao_world_2',
        3: 'textures/ui/killbroadcast_kill_effect/xiaoxiao_world/xiaoxiao_world_3',
        4: 'textures/ui/killbroadcast_kill_effect/xiaoxiao_world/xiaoxiao_world_4',
        5: 'textures/ui/killbroadcast_kill_effect/xiaoxiao_world/xiaoxiao_world_5',
        6: 'textures/ui/killbroadcast_kill_effect/xiaoxiao_world/xiaoxiao_world_6',
    }
    VICTIM_PREVIEW_IDENTIFIER = 'minecraft:zombie'
    VICTIM_PAPER_DOLL_MOLANG_DEFAULTS = {
        'variable.gliding_speed_value': 1.0,
        'variable.tcos0': 0.0,
        'variable.is_holding_left': 0.0,
        'variable.is_holding_right': 0.0,
        'variable.is_holding_spyglass': 0.0,
        'variable.is_brandishing_spear': 0.0,
        'variable.attack_time': -1.0,
        'variable.damage_nearby_mobs': 0.0,
        'variable.use_item_interval_progress': 0.0,
        'variable.use_item_startup_progress': 0.0,
        'variable.charge_amount': 0.0,
        'variable.is_sneaking': 0.0,
        'variable.swim_amount': 0.0,
        'variable.leftarmswim_amount': 0.0,
        'variable.rightarmswim_amount': 0.0,
        'variable.wing_flap': 0.0,
    }
    PLAYER_PAPER_DOLL_MOLANG_DEFAULTS = {
        'variable.liedownamount': 1.0,
    }
    VICTIM_PAPER_DOLL_IDENTIFIER_ALIASES = {
        'minecraft:armadillo': 'killbroadcast:paper_doll_armadillo',
        'minecraft:chicken': 'killbroadcast:paper_doll_chicken',
        'minecraft:copper_golem': 'killbroadcast:paper_doll_copper_golem',
        'minecraft:cow': 'killbroadcast:paper_doll_cow',
        'minecraft:creaking': 'killbroadcast:paper_doll_creaking',
        'minecraft:horse': 'killbroadcast:paper_doll_horse',
        'minecraft:pig': 'killbroadcast:paper_doll_pig',
    }
    # Entity rendering scale follows the model's native dimensions, so the
    # player and small mobs cannot share one value.  Keep the official player
    # framing baseline and enlarge the victim side independently.
    XIAOXIAO_WORLD_PLAYER_SCALE = 0.5
    XIAOXIAO_WORLD_VICTIM_SCALE = 2.4
    PAPER_DOLL_VIEWPORT_SCALE = 2.0
    PAPER_DOLL_OFFSCREEN_POSITION = (-4096.0, -4096.0)
    KING_HONOR_BASE_WIDTH = 260.0
    KING_HONOR_BASE_HEIGHT = 64.0
    KING_HONOR_ASPECT = KING_HONOR_BASE_WIDTH / KING_HONOR_BASE_HEIGHT
    KING_HONOR_HEAD_SIZE = 36.0
    KING_HONOR_LEFT_HEAD_OFFSET = (14.0, 14.0)
    KING_HONOR_RIGHT_HEAD_OFFSET = (210.0, 14.0)
    KING_HONOR_PLAYER_SCALE = 0.5
    KING_HONOR_VICTIM_SCALE = 2.4
    KING_HONOR_TEXTURES = {
        1: 'textures/ui/killbroadcast_kill_effect/king_honor/king_honor_1',
        2: 'textures/ui/killbroadcast_kill_effect/king_honor/king_honor_2',
        3: 'textures/ui/killbroadcast_kill_effect/king_honor/king_honor_3',
        4: 'textures/ui/killbroadcast_kill_effect/king_honor/king_honor_4',
        5: 'textures/ui/killbroadcast_kill_effect/king_honor/king_honor_5',
        6: 'textures/ui/killbroadcast_kill_effect/king_honor/king_honor_6',
    }
    KING_HONOR_ENTRY_DURATION = 0.34
    KING_HONOR_FADE_OUT_DURATION = 0.28
    KING_HONOR_SLIDE_DISTANCE = 12.0
    KING_HONOR_DISPLAY_DURATION = 3.10
    BIG_DOG_BARK_BASE_SIZE = 300.0
    QINSHOU_XIANSHENG_TEXTURE = 'textures/ui/killbroadcast_kill_effect/qinshou_xiansheng/wolf'
    QINSHOU_XIANSHENG_BASE_SIZE = (320.0, 180.0)
    QINSHOU_XIANSHENG_LAYER = 2000
    DEFAULT_PANEL_LAYER = 20
    GAME_HUD_PANEL_HEIGHT_RATIO = 0.13
    QINSHOU_XIANSHENG_ENTRY_DURATION = 0.20
    QINSHOU_XIANSHENG_DISPLAY_DURATION = 2.05
    QINSHOU_XIANSHENG_FADE_OUT_DURATION = 0.50
    QINSHOU_XIANSHENG_PITCH_MIN = 0.50
    QINSHOU_XIANSHENG_PITCH_MAX = 2.00
    BIG_DOG_BARK_TEXTURES = {
        1: 'textures/ui/killbroadcast_kill_effect/big_dog_bark/big_dog_bark_1',
        2: 'textures/ui/killbroadcast_kill_effect/big_dog_bark/big_dog_bark_2',
        3: 'textures/ui/killbroadcast_kill_effect/big_dog_bark/big_dog_bark_3',
        4: 'textures/ui/killbroadcast_kill_effect/big_dog_bark/big_dog_bark_4',
        5: 'textures/ui/killbroadcast_kill_effect/big_dog_bark/big_dog_bark_5',
    }
    BIG_DOG_BARK_ENTRY_DURATION = 0.22
    BIG_DOG_BARK_DISPLAY_DURATION = 2.75
    BIG_DOG_BARK_FADE_OUT_DURATION = 0.30
    BIG_DOG_BARK_SHAKE_DURATION = 0.58
    BIG_DOG_BARK_SHAKE_DISTANCE = 4.0
    OLD_PRIEST_TEXTURES = (
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_01',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_02',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_03',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_04',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_05',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_06',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_07',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_08',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_09',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_10',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_11',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_12',
        'textures/ui/killbroadcast_kill_effect/old_priest/old_priest_13',
    )
    OLD_PRIEST_ICONS_PER_KILL = 1
    OLD_PRIEST_SOUND_COUNT = 9
    ENTRY_DURATION = 0.24
    SCROLL_ANIMATION_DURATION = 0.30
    SCROLL_ICON_SIZE = 24.0
    SCROLL_ICON_SPACING = 2.0
    SCROLL_START_SCALE = 4.0
    SCROLL_MAX_VISIBLE = 7
    SCROLL_MAX_ACTIVE = SCROLL_MAX_VISIBLE + 1
    SCROLL_DISMISS_INTERVAL = 0.10
    TEXT_BASE_HEIGHT = 52.0
    TEXT_LINE_LAYOUTS = {
        'Main': (0.0, 16.0, 1.05),
        'Detail': (17.0, 14.0, 0.82),
        'Score': (33.0, 16.0, 0.95),
    }
    TEXT_LINE_ORDER = ('Main', 'Detail', 'Score')
    TEXT_LINE_ENTRY_OFFSETS = {
        'Main': (18.0, 4.0),
        'Detail': (-14.0, 3.0),
        'Score': (10.0, 2.0),
    }
    TEXT_LINE_EXIT_OFFSETS = {
        'Main': (-10.0, -3.0),
        'Detail': (12.0, -2.0),
        'Score': (-8.0, -2.0),
    }
    CF_COMBO_TEXT_HEIGHT = 68.0
    CF_COMBO_SCORE_HEIGHT = 30.0
    TEXT_MOVE_IN_DURATION = 0.30
    TEXT_LINE_STAGGER = 0.045
    TEXT_FADE_IN_DURATION = 0.20
    TEXT_HOLD_DURATION = 2.50
    TEXT_FADE_OUT_DURATION = 0.30
    TEXT_SCORE_ROLL_DURATION = 0.45
    KILL_SCORE_MIN = 80
    KILL_SCORE_MAX = 120
    HEADSHOT_SCORE_MULTIPLIER = 3
    ICON_HOLD_DURATION = 3.25
    PUBG_FEED_MAX_LINES = 5
    PUBG_FEED_LINE_SPACING = 12.0
    PUBG_FEED_LINE_HEIGHT = 12.0
    PUBG_FEED_DURATION = 5.0
    PUBG_FEED_FADE_IN_DURATION = 0.20
    PUBG_FEED_FADE_OUT_DURATION = 0.30
    PUBG_FEED_MOVE_DURATION = 0.24
    PUBG_FEED_FONT_SCALE = 0.82
    PUBG_COMBO_FONT_SCALE = 1.35
    APEX_FEED_MAX_LINES = 3
    APEX_ENTRY_DURATION = 0.24
    APEX_MOVE_DURATION = 0.20
    APEX_HOLD_DURATION = 2.60
    APEX_FADE_OUT_DURATION = 0.32
    APEX_LINE_SPACING = 20.0
    APEX_LINE_HEIGHT = 19.0
    APEX_START_SCALE = 1.55
    APEX_MAIN_FONT_SCALE = 0.78
    APEX_DAMAGE_FONT_SCALE = 0.62
    APEX_REWARD_MIN = 140
    APEX_REWARD_MAX = 160
    APEX_HEADSHOT_MULTIPLIER = 2
    APEX_HEADSHOT_BONUS_MIN = 5
    APEX_HEADSHOT_BONUS_MAX = 25
    APEX_TARGET_COLOR = (0.93, 0.10, 0.10)
    APEX_TEXT_COLOR = (0.97, 0.97, 0.97)
    APEX_BADGE_COLOR = (0.78, 0.80, 0.82)
    APEX_BACKGROUND_ALPHA = 0.30
    BATTLEFIELD1_ANIMATION_DURATION = 0.20
    BATTLEFIELD1_DISPLAY_DURATION = 4.50
    BATTLEFIELD1_MAX_QUEUE_SIZE = 7
    BATTLEFIELD1_ICON_SIZE = 25.0
    BATTLEFIELD1_BORDER_SIZE = 3.0
    BATTLEFIELD1_FONT_HEIGHT = 9.0
    BATTLEFIELD1_ICON_BOX_ALPHA = 0.20
    BATTLEFIELD1_TEXT_BOX_ALPHA = 0.10
    BATTLEFIELD1_WEAPON_SCALE = 1.0
    BATTLEFIELD1_VICTIM_SCALE = 1.2
    BATTLEFIELD1_HEALTH_SCALE = 1.5
    COD_XP_MIN = 90
    COD_XP_MAX = 110
    COD_HEADSHOT_MULTIPLIER = 2
    COD_HEADSHOT_BONUS_MIN = 5
    COD_HEADSHOT_BONUS_MAX = 25
    COD_PANEL_WIDTH = 300.0
    COD_PANEL_HEIGHT = 48.0
    COD_XP_WIDTH = 78.0
    COD_TEXT_GAP = 8.0
    COD_DETAIL_FONT_SIZE = 0.88
    COD_DETAIL_MIN_FONT_SIZE = 0.68
    COD_DETAIL_REFERENCE_LENGTH = 25.0
    COD_ENTRY_DURATION = 0.16
    COD_LINE_STAGGER = 0.04
    COD_COLOR = (0.92, 0.95, 0.21)
    COD_KILL_TEXTS = (
        u'\u51fb\u6740\u654c\u4eba',
        u'\u76ee\u6807\u5df2\u6e05\u9664',
        u'\u5a01\u80c1\u89e3\u9664',
        u'\u5e72\u51c0\u5229\u843d',
        u'\u4e00\u67aa\u6536\u5de5',
        u'\u51fb\u6740\u786e\u8ba4',
        u'\u4e0b\u4e00\u4e2a\u76ee\u6807',
        u'\u5b8c\u7f8e\u89e3\u51b3',
    )
    COD_HEADSHOT_TEXTS = (
        u'\u7206\u5934\u51fb\u6740',
        u'\u4e00\u67aa\u7206\u5934',
        u'\u6b63\u4e2d\u7709\u5fc3',
        u'\u7cbe\u51c6\u5904\u51b3',
        u'\u5934\u76d4\u4e5f\u6551\u4e0d\u4e86\u4f60',
        u'\u51c6\u661f\u4ece\u4e0d\u8bf4\u8c0e',
        u'\u4e00\u53d1\u5165\u9b42',
        u'\u62ac\u67aa\uff0c\u7ed3\u675f',
    )
    COD_REWARD_TEXTS = (
        u'\u5956\u52b1\u5df2\u5230\u8d26',
        u'\u7ee7\u7eed\u63a8\u8fdb',
        u'\u706b\u529b\u4f18\u52bf',
        u'\u8282\u594f\u62c9\u6ee1',
        u'\u72b6\u6001\u6b63\u70ed',
        u'\u51fb\u6740\u5f97\u5206',
    )
    COD_COMBO_TEXTS = {
        2: (u'\u53cc\u6740', u'\u4e00\u77f3\u4e8c\u9e1f', u'\u53cc\u4efd\u5feb\u4e50', u'\u4e24\u4e2a\u4e00\u8d77\u9001\u8d70'),
        3: (u'\u4e09\u6740', u'\u4e09\u8fde\u6536\u5272', u'\u706b\u529b\u5168\u5f00', u'\u5f00\u59cb\u70ed\u8eab'),
        4: (u'\u56db\u6740', u'\u65e0\u4eba\u80fd\u6321', u'\u63a5\u7ba1\u6218\u573a', u'\u6392\u597d\u961f\uff0c\u4e00\u4e2a\u4e2a\u6765'),
        5: (u'\u4e94\u6740', u'\u4e3b\u5bb0\u6218\u573a', u'\u6740\u75af\u4e86', u'\u8fd8\u6709\u8c01\uff1f'),
    }
    COD_HIGH_COMBO_TEXTS = (
        u'\u8fde\u7eed\u51fb\u6740 x%d',
        u'\u7edf\u6cbb\u6218\u573a x%d',
        u'\u6536\u5272\u7ee7\u7eed x%d',
        u'\u6839\u672c\u505c\u4e0d\u4e0b\u6765 x%d',
    )
    SCROLL_STYLES = ('battlefield5', 'delta_force', 'old_priest')

    STYLE_TEXTURES = {
        'classic': {
            'normal': 'textures/ui/killbroadcast_kill_effect/killicon_scrolling_default',
            'headshot': 'textures/ui/killbroadcast_kill_effect/killicon_scrolling_headshot',
        },
        'battlefield1': {
            'normal': 'textures/ui/killbroadcast_kill_effect/killicon_battlefield1_default',
            'headshot': 'textures/ui/killbroadcast_kill_effect/killicon_battlefield1_headshot',
        },
        'battlefield5': {
            'normal': 'textures/ui/killbroadcast_kill_effect/killicon_battlefield5_default',
            'headshot': 'textures/ui/killbroadcast_kill_effect/killicon_battlefield5_headshot',
        },
        'delta_force': {
            'normal': 'textures/ui/killbroadcast_kill_effect/killicon_df_default',
            'headshot': 'textures/ui/killbroadcast_kill_effect/killicon_df_headshot',
        },
    }

    def __init__(self, panelPath=None):
        self.isGameplayHud = panelPath is None
        self.PANEL_PATH = panelPath or self.DEFAULT_PANEL_PATH
        self.CANVAS_PATH = self.PANEL_PATH + '/Canvas'
        self.uiNode = None
        self.touchDisabledUiNode = None
        self.style = 'pubg'
        self.styleOptions = {}
        self.totalKills = 0
        self.totalScore = 0
        self.lastKillScore = 0
        self.lastHeadshot = False
        self.weaponName = u'\u6b66\u5668'
        self.targetName = u'\u76ee\u6807'
        self.targetMaxHealth = u'?'
        self.killDistance = None
        self.killDamage = None
        self.layoutScale = 1.0
        self.layoutAlpha = 1.0
        self.layoutViewportSize = None
        self.canvasAnimationAlpha = 1.0
        self.entryAnimationStartTime = None
        self.iconHoldUntil = None
        self.textAnimationStartTime = None
        self.textScoreStart = 0
        self.textScoreTarget = 0
        self.animationActive = False
        self.controls = {}
        self.queueControls = []
        self.pubgLineControls = []
        self.queueIcons = []
        self.queueDismissing = False
        self.nextQueueDismissTime = None
        self.pubgFeedItems = []
        self.pubgComboBirthTime = None
        self.apexFeedItems = []
        self.battlefield1Queue = []
        self.battlefield1Current = None
        self.battlefield1StartTime = None
        self.battlefield1LastSwitchTime = None
        self.codTextLines = ()
        self.cuppingCatAnimationStartTime = None
        self.cuppingCatFrameIndex = -1
        self.cuppingCatStage = 0
        self.kingHonorAnimationStartTime = None
        self.kingHonorBasePosition = None
        self.paperDollTargetIdentifier = self.VICTIM_PREVIEW_IDENTIFIER
        self.paperDollTargetIsPlayer = False
        self.bigDogBarkAnimationStartTime = None
        self.bigDogBarkBaseSize = self.BIG_DOG_BARK_BASE_SIZE
        self.bigDogBarkBasePosition = (0.0, 0.0)
        self.qinshouXianshengAnimationStartTime = None
        self.qinshouXianshengBaseSize = self.QINSHOU_XIANSHENG_BASE_SIZE
        self.qinshouXianshengBasePosition = (0.0, 0.0)
        self.qinshouXianshengCanvasBaseSize = None

    def RebindControls(self, uiNode=None):
        uiNode = uiNode or self.uiNode or clientApi.GetUI('KillBroadcast', 'Game')
        if not uiNode:
            self.controls = {}
            self.queueControls = []
            self.pubgLineControls = []
            self.touchDisabledUiNode = None
            return False
        self.uiNode = uiNode
        controls = {}
        directNames = (
            'Bar', 'Ring', 'Frame', 'Primary', 'Emblem', 'Headshot', 'Count',
            'TextPerformance', 'PubgFeed', 'PubgCombo', 'Battlefield1', 'CuppingCat',
            'XiaoXiaoWorld', 'KingHonor', 'BigDogBark', 'QinshouXiansheng'
        )
        for name in directNames:
            path = self.CANVAS_PATH + '/' + name
            controls[name] = self.uiNode.GetBaseUIControl(path)
        for name in ('Main', 'Detail', 'Score'):
            controls[name] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH + '/TextPerformance/' + name)
        battlefield1Paths = {
            'Battlefield1IconBox': '/Battlefield1/IconBox',
            'Battlefield1TextBox': '/Battlefield1/TextBox',
            'Battlefield1Icon': '/Battlefield1/Icon',
            'Battlefield1Victim': '/Battlefield1/Victim',
            'Battlefield1Weapon': '/Battlefield1/Weapon',
            'Battlefield1Health': '/Battlefield1/Health',
        }
        for name, suffix in battlefield1Paths.items():
            controls[name] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH + suffix)
        xiaoXiaoWorldPaths = {
            'XiaoXiaoWorldBanner': '/XiaoXiaoWorld/Banner',
        }
        for name, suffix in xiaoXiaoWorldPaths.items():
            controls[name] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH + suffix)
        kingHonorPaths = {
            'KingHonorBanner': '/KingHonor/Banner',
        }
        for name, suffix in kingHonorPaths.items():
            controls[name] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH + suffix)
        paperDollPaths = {
            'XiaoXiaoWorldLeftDoll': '/XiaoXiaoWorldLeftDoll',
            'XiaoXiaoWorldRightDoll': '/XiaoXiaoWorldRightDoll',
            'KingHonorLeftDoll': '/KingHonorLeftDoll',
            'KingHonorRightDoll': '/KingHonorRightDoll',
        }
        for name, suffix in paperDollPaths.items():
            controls[name] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH + suffix)
        playerIconPaths = {
            'XiaoXiaoWorldRightPlayerIcon': (
                '/XiaoXiaoWorld/XiaoXiaoWorldRightPlayerIcon'
            ),
            'KingHonorRightPlayerIcon': '/KingHonor/KingHonorRightPlayerIcon',
        }
        for name, suffix in playerIconPaths.items():
            controls[name] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH + suffix)
        controls['Canvas'] = self.uiNode.GetBaseUIControl(self.CANVAS_PATH)
        canvas = controls.get('Canvas')
        if canvas:
            try:
                canvasSize = canvas.GetSize()
                if (
                    isinstance(canvasSize, (list, tuple)) and
                    len(canvasSize) >= 2 and
                    float(canvasSize[0]) > 0.0 and
                    float(canvasSize[1]) > 0.0
                ):
                    self.qinshouXianshengCanvasBaseSize = (
                        float(canvasSize[0]), float(canvasSize[1]))
            except Exception:
                pass
        queueControls = []
        for index in range(1, self.SCROLL_MAX_ACTIVE + 1):
            queueControls.append(self.uiNode.GetBaseUIControl(self.CANVAS_PATH + '/Queue%d' % index))
        pubgLineControls = []
        for index in range(1, self.PUBG_FEED_MAX_LINES + 1):
            linePath = self.CANVAS_PATH + '/PubgFeed/Line%d' % index
            pubgLineControls.append({
                'Panel': self.uiNode.GetBaseUIControl(linePath),
                'Background': self.uiNode.GetBaseUIControl(linePath + '/Background'),
                'Prefix': self.uiNode.GetBaseUIControl(linePath + '/Prefix'),
                'Emphasis': self.uiNode.GetBaseUIControl(linePath + '/Emphasis'),
                'Suffix': self.uiNode.GetBaseUIControl(linePath + '/Suffix'),
                'Badge': self.uiNode.GetBaseUIControl(linePath + '/Badge'),
                'Damage': self.uiNode.GetBaseUIControl(linePath + '/Damage'),
            })
        self.controls = controls
        self.queueControls = queueControls
        self.pubgLineControls = pubgLineControls
        self.DisableGameplayHudTouch()
        return bool(self.controls.get('Canvas'))

    def Init(self, uiNode=None, force=False):
        uiNode = uiNode or self.uiNode or clientApi.GetUI('KillBroadcast', 'Game')
        if not uiNode:
            self.controls = {}
            self.queueControls = []
            self.pubgLineControls = []
            return False
        if not force and self.uiNode is uiNode and self.controls.get('Canvas'):
            return True
        if not self.RebindControls(uiNode):
            return False
        self.SetPanelVisible(False)
        return True

    def SetStyle(self, style):
        style = str(style or 'pubg').strip().lower()
        if style == 'csgo':
            style = 'pubg'
        previousStyle = self.style
        changed = style != self.style
        if changed and previousStyle == self.QINSHOU_XIANSHENG_STYLE:
            self.StopQinshouXianshengSound()
        self.style = style
        if changed:
            self.Clear()
            self.ApplyPanelLayer()
        return changed

    def ApplyPanelLayer(self):
        if not self.uiNode:
            return False
        if self.isGameplayHud:
            # The gameplay HUD layer is fixed in JSON.  Calling SetLayer while
            # a kill is shown refreshes the native UI tree and can cancel a
            # touch already held on another add-on's HUD.
            return True
        panel = self.uiNode.GetBaseUIControl(self.PANEL_PATH)
        if not panel:
            return False
        layer = self.DEFAULT_PANEL_LAYER
        if self.style == self.QINSHOU_XIANSHENG_STYLE:
            layer = self.QINSHOU_XIANSHENG_LAYER
        try:
            panel.SetLayer(layer)
            return True
        except Exception:
            return False

    def DisableGameplayHudTouch(self):
        if not self.isGameplayHud or not self.uiNode:
            return False
        if self.touchDisabledUiNode is self.uiNode:
            return True
        found = False
        allDisabled = True
        for path in (
            self.PANEL_PATH,
            self.CANVAS_PATH,
            self.CANVAS_PATH + '/QinshouXiansheng',
        ):
            control = self.uiNode.GetBaseUIControl(path)
            if not control:
                allDisabled = False
                continue
            found = True
            try:
                control.SetTouchEnable(False)
            except Exception:
                allDisabled = False
        if found and allDisabled:
            self.touchDisabledUiNode = self.uiNode
        return bool(found and allDisabled)

    def SetStyleOptions(self, options=None):
        options = dict(options) if isinstance(options, dict) else {}
        changed = options != self.styleOptions
        self.styleOptions = options
        if not changed or self.totalKills <= 0:
            return changed
        if self.style == 'battlefield1':
            maxVisible = self.GetBattlefield1QueueLength()
            if len(self.battlefield1Queue) > maxVisible:
                self.battlefield1Queue = self.battlefield1Queue[-maxVisible:]
            if self.battlefield1Current:
                self.RenderBattlefield1(time.time())
        elif self.style == 'apex':
            if self.apexFeedItems:
                now = time.time()
                self.UpdateApexFeedTargets(now)
                self.RenderApexFeed(now)
        elif self.style in self.SCROLL_STYLES:
            maxVisible = self.GetScrollMaxVisible()
            if len(self.queueIcons) > maxVisible:
                self.queueIcons = self.queueIcons[-maxVisible:]
            now = time.time()
            self.UpdateScrollingTargets(now)
            self.RenderScrollingQueue(now)
        else:
            if self.style == 'cod':
                self.codTextLines = self.BuildCodTextLines(self.totalKills, self.lastHeadshot)
            self.Refresh()
        if self.textAnimationStartTime is not None:
            self.RefreshTextPerformance(self.textScoreTarget)
        self.ApplyStyleLayout()
        return changed

    def GetStyleOption(self, key, defaultValue=None):
        return self.styleOptions.get(key, defaultValue)

    def GetBoundedStyleOption(self, key, defaultValue, minimum, maximum):
        try:
            value = float(self.GetStyleOption(key, defaultValue))
        except Exception:
            value = float(defaultValue)
        return min(max(value, float(minimum)), float(maximum))

    def GetQinshouXianshengTiming(self):
        holdDuration = self.GetBoundedStyleOption(
            'HoldDuration', self.QINSHOU_XIANSHENG_DISPLAY_DURATION,
            0.20, 10.0)
        fadeOutDuration = self.GetBoundedStyleOption(
            'FadeOutDuration', self.QINSHOU_XIANSHENG_FADE_OUT_DURATION,
            0.10, 5.0)
        return holdDuration, fadeOutDuration

    def GetQinshouXianshengPitchRange(self):
        minimum = self.GetBoundedStyleOption(
            'PitchMin', self.QINSHOU_XIANSHENG_PITCH_MIN, 0.10, 3.0)
        maximum = self.GetBoundedStyleOption(
            'PitchMax', self.QINSHOU_XIANSHENG_PITCH_MAX, 0.10, 3.0)
        return (minimum, maximum) if minimum <= maximum else (maximum, minimum)

    def GetScrollMaxVisible(self):
        try:
            value = int(round(float(self.GetStyleOption('QueueLength', self.SCROLL_MAX_VISIBLE))))
        except Exception:
            value = self.SCROLL_MAX_VISIBLE
        return min(max(value, 1), self.SCROLL_MAX_VISIBLE)

    def SetLayoutScale(self, scale):
        try:
            scale = float(scale)
        except Exception:
            scale = 1.0
        self.layoutScale = min(max(scale, 0.1), 4.0)
        if self.queueIcons:
            now = time.time()
            self.UpdateScrollingTargets(now)
            self.RenderScrollingQueue(now)
        if self.pubgFeedItems:
            now = time.time()
            self.UpdatePubgFeedTargets(now)
            self.RenderPubgFeed(now)
        if self.apexFeedItems:
            now = time.time()
            self.UpdateApexFeedTargets(now)
            self.RenderApexFeed(now)
        if self.battlefield1Current:
            self.RenderBattlefield1(time.time())
        self.ApplyStyleLayout()
        # Netease paper dolls render through a native viewport.  Any layout
        # change after RenderEntity invalidates that viewport, so bind it
        # again only after the final control rectangles have been applied.
        self.RefreshPaperDollAvatars()
        return self.layoutScale

    def SetLayoutViewportSize(self, size):
        if not isinstance(size, (list, tuple)) or len(size) < 2:
            self.layoutViewportSize = None
            return False
        try:
            width = float(size[0])
            height = float(size[1])
        except Exception:
            self.layoutViewportSize = None
            return False
        if width <= 0.0 or height <= 0.0:
            self.layoutViewportSize = None
            return False
        self.layoutViewportSize = (width, height)
        return True

    def SetLayoutAlpha(self, alpha):
        try:
            alpha = float(alpha)
        except Exception:
            alpha = 1.0
        self.layoutAlpha = min(max(alpha, 0.0), 1.0)
        return self.ApplyCanvasAlpha()

    def ApplyCanvasAlpha(self):
        canvas = self.controls.get('Canvas')
        if not canvas:
            return False
        try:
            canvas.SetAlpha(float(self.canvasAnimationAlpha) * self.layoutAlpha)
            return True
        except Exception:
            return False

    def GetLayoutCanvasSize(self):
        if self.layoutViewportSize:
            return self.layoutViewportSize
        canvas = self.controls.get('Canvas')
        try:
            size = canvas.GetSize() if canvas else None
        except Exception:
            size = None
        if not isinstance(size, (list, tuple)) or len(size) < 2:
            return None
        try:
            width = float(size[0])
            height = float(size[1])
        except Exception:
            return None
        return (width, height) if width > 0.0 and height > 0.0 else None

    def SetPanelVisible(self, visible):
        if not self.uiNode:
            return False
        ctrl = self.uiNode.GetBaseUIControl(self.PANEL_PATH)
        if not ctrl:
            return False
        ctrl.SetVisible(bool(visible))
        return True

    def SyncPanelLayout(self, sourcePath):
        if not self.uiNode or not sourcePath:
            return False
        source = self.uiNode.GetBaseUIControl(sourcePath)
        target = self.uiNode.GetBaseUIControl(self.PANEL_PATH)
        if not source or not target:
            return False
        applied = False
        try:
            position = source.GetPosition()
            if isinstance(position, (list, tuple)) and len(position) >= 2:
                target.SetPosition((float(position[0]), float(position[1])))
                applied = True
        except Exception:
            pass
        try:
            size = source.GetSize()
            if isinstance(size, (list, tuple)) and len(size) >= 2:
                target.SetSize((float(size[0]), float(size[1])))
                applied = True
        except Exception:
            pass
        return applied

    def AddKill(
        self,
        headshot=False,
        weaponName='',
        targetName='',
        playSound=True,
        distance=None,
        targetMaxHealth=None,
        damage=None,
        targetEntityId=None,
        targetIdentifier='',
        targetIsPlayer=False,
    ):
        if not self.RebindControls():
            return False
        weaponText = self.ToText(weaponName) or u'\u672a\u77e5\u6b66\u5668'
        targetText = self.ToText(targetName) or u'\u672a\u77e5\u76ee\u6807'
        healthText = self.GetBattlefield1HealthText(targetMaxHealth)
        try:
            distanceValue = max(0.0, float(distance)) if distance is not None else None
        except Exception:
            distanceValue = None
        try:
            damageValue = max(0.0, float(damage)) if damage is not None else None
        except Exception:
            damageValue = None
        if self.style == self.KING_HONOR_STYLE:
            return self.AddKingHonorKill(
                bool(headshot), bool(playSound), targetIdentifier, bool(targetIsPlayer)
            )
        if self.style == self.XIAOXIAO_WORLD_STYLE:
            return self.AddXiaoXiaoWorldKill(
                bool(headshot), bool(playSound), targetIdentifier, bool(targetIsPlayer)
            )
        if self.style == self.CUPPING_CAT_STYLE:
            return self.AddCuppingCatKill(bool(headshot), bool(playSound))
        if self.style == self.BIG_DOG_BARK_STYLE:
            return self.AddBigDogBarkKill(bool(headshot), bool(playSound))
        if self.style == self.QINSHOU_XIANSHENG_STYLE:
            return self.AddQinshouXianshengKill(bool(headshot), bool(playSound))
        if self.style == 'battlefield1':
            return self.AddBattlefield1Kill(
                bool(headshot),
                weaponText,
                targetText,
                healthText,
                bool(playSound),
            )
        previousScore = self.totalScore
        self.totalKills += 1
        self.lastHeadshot = bool(headshot)
        self.lastKillScore = (
            self.RollCodKillXp(self.lastHeadshot)
            if self.style == 'cod'
            else (
                self.RollApexKillScore(self.lastHeadshot)
                if self.style == 'apex'
                else self.RollKillScore(self.lastHeadshot)
            )
        )
        self.totalScore += self.lastKillScore
        self.weaponName = weaponText
        self.targetName = targetText
        self.targetMaxHealth = healthText
        self.killDistance = distanceValue
        self.killDamage = damageValue
        if self.style == 'cod':
            self.codTextLines = self.BuildCodTextLines(self.totalKills, self.lastHeadshot)
            self.HideLayers()
        elif self.style in self.SCROLL_STYLES:
            self.AddScrollingKill(self.lastHeadshot)
        elif self.style == 'apex':
            self.HideLayers()
            self.HideTextPerformance()
            self.AddApexKill()
        elif self.style == 'pubg':
            self.HideLayers()
            self.HideTextPerformance()
            self.AddPubgKill()
        else:
            self.Refresh()
            self.PlayEntryAnimation()
            self.iconHoldUntil = time.time() + self.ICON_HOLD_DURATION
        if self.style not in ('pubg', 'apex'):
            if self.style == 'cod':
                self.PlayTextPerformance(self.lastKillScore, self.lastKillScore)
            else:
                self.PlayTextPerformance(previousScore, self.totalScore)
        if playSound:
            self.PlaySound()
        return True

    def AddKingHonorKill(
        self, headshot=False, playSound=True, targetIdentifier='', targetIsPlayer=False
    ):
        panel = self.controls.get('KingHonor')
        if not panel or not self.controls.get('KingHonorBanner'):
            return False
        self.totalKills += 1
        self.lastHeadshot = bool(headshot)
        self.HideLayers()
        self.HideTextPerformance()
        stage = min(max(int(self.totalKills), 1), 6)
        if not self.SetImage('KingHonorBanner', self.KING_HONOR_TEXTURES.get(stage)):
            return False
        self.ResetCanvas()
        self.SetPanelVisible(True)
        self.SetVisible('KingHonor', True)
        self.ApplyStyleLayout()
        self.ApplyKingHonorAvatars(targetIdentifier, targetIsPlayer)
        self.PlayKingHonorAnimation()
        if playSound:
            self.PlaySound()
        return True

    def ApplyKingHonorAvatars(
        self, targetIdentifier='', targetIsPlayer=False
    ):
        return self.ApplyDuelAvatars(
            'KingHonorLeftDoll',
            'KingHonorRightDoll',
            'KingHonorRightPlayerIcon',
            targetIdentifier,
            targetIsPlayer,
            self.KING_HONOR_PLAYER_SCALE,
            self.KING_HONOR_VICTIM_SCALE,
        )

    def PlayKingHonorAnimation(self):
        now = time.time()
        self.kingHonorAnimationStartTime = now
        self.textAnimationStartTime = None
        self.entryAnimationStartTime = None
        self.iconHoldUntil = now + self.KING_HONOR_DISPLAY_DURATION
        self.animationActive = True
        panel = self.controls.get('KingHonor')
        if panel:
            try:
                # Netease paper dolls own a native 3D viewport. Keep their
                # ancestor transform stable after RenderEntity has run.
                panel.SetAlpha(1.0)
                panel.SetVisible(True)
            except Exception:
                pass
        return True

    def AddXiaoXiaoWorldKill(
        self, headshot=False, playSound=True, targetIdentifier='', targetIsPlayer=False
    ):
        panel = self.controls.get('XiaoXiaoWorld')
        if not panel or not self.controls.get('XiaoXiaoWorldBanner'):
            return False
        self.totalKills += 1
        self.lastHeadshot = bool(headshot)
        self.HideLayers()
        self.HideTextPerformance()
        count = min(max(int(self.totalKills), 1), 6)
        if not self.SetImage('XiaoXiaoWorldBanner', self.XIAOXIAO_WORLD_TEXTURES.get(count)):
            return False
        self.ResetCanvas()
        self.SetPanelVisible(True)
        self.SetVisible('XiaoXiaoWorld', True)
        self.ApplyStyleLayout()
        self.ApplyXiaoXiaoWorldAvatars(targetIdentifier, targetIsPlayer)
        self.PlayXiaoXiaoWorldAnimation()
        if playSound:
            self.PlaySound()
        return True

    def ApplyXiaoXiaoWorldAvatars(
        self, targetIdentifier='', targetIsPlayer=False
    ):
        return self.ApplyDuelAvatars(
            'XiaoXiaoWorldLeftDoll',
            'XiaoXiaoWorldRightDoll',
            'XiaoXiaoWorldRightPlayerIcon',
            targetIdentifier,
            targetIsPlayer,
            self.XIAOXIAO_WORLD_PLAYER_SCALE,
            self.XIAOXIAO_WORLD_VICTIM_SCALE,
        )

    def ApplyDuelAvatars(
        self, leftDollName, rightDollName, playerIconName,
        targetIdentifier='', targetIsPlayer=False,
        playerScale=1.0, victimScale=1.0
    ):
        self.paperDollTargetIdentifier = self.GetStableVictimIdentifier(
            targetIdentifier, targetIsPlayer
        )
        self.paperDollTargetIsPlayer = bool(targetIsPlayer)
        iconApplied = self.SetVisible(playerIconName, self.paperDollTargetIsPlayer)
        if self.paperDollTargetIsPlayer:
            self.MovePaperDollControlsOffscreen((rightDollName,))

        # The renderer owns a native viewport. Recalculate the complete UI
        # tree only after the final theme rectangle and visibility are set;
        # otherwise RenderEntity keeps the custom control's creation-time
        # rectangle (the top-left viewport seen in game).
        self.FlushPaperDollLayout()
        leftApplied = self.RenderLocalPlayerPaperDoll(
            leftDollName, playerScale
        )
        victimApplied = iconApplied if self.paperDollTargetIsPlayer else (
            self.RenderVictimPaperDoll(
                rightDollName, self.paperDollTargetIdentifier, victimScale
            )
        )
        return leftApplied or victimApplied

    def FlushPaperDollLayout(self):
        if not self.uiNode:
            return False
        try:
            self.uiNode.UpdateScreen(True)
            return True
        except Exception:
            return False

    def MovePaperDollControlsOffscreen(self, controlNames=None):
        controlNames = controlNames or (
            'XiaoXiaoWorldLeftDoll', 'XiaoXiaoWorldRightDoll',
            'KingHonorLeftDoll', 'KingHonorRightDoll',
        )
        moved = False
        for name in controlNames:
            control = self.controls.get(name)
            if not control:
                continue
            try:
                control.SetPosition(self.PAPER_DOLL_OFFSCREEN_POSITION)
                moved = True
            except Exception:
                pass
        return moved

    def GetStableVictimIdentifier(self, targetIdentifier='', targetIsPlayer=False):
        identifier = self.ToText(targetIdentifier).strip() if targetIdentifier else ''
        if identifier:
            return identifier
        return 'minecraft:player' if targetIsPlayer else self.VICTIM_PREVIEW_IDENTIFIER

    def ResolveVictimPaperDollIdentifier(self, targetIdentifier=''):
        identifier = self.ToText(targetIdentifier).strip() if targetIdentifier else ''
        if not identifier:
            return ''
        return self.VICTIM_PAPER_DOLL_IDENTIFIER_ALIASES.get(
            identifier.lower(), identifier
        )

    def RefreshPaperDollAvatars(self):
        if self.totalKills <= 0:
            return False
        if self.style == self.KING_HONOR_STYLE:
            return self.ApplyKingHonorAvatars(
                self.paperDollTargetIdentifier,
                self.paperDollTargetIsPlayer,
            )
        if self.style == self.XIAOXIAO_WORLD_STYLE:
            return self.ApplyXiaoXiaoWorldAvatars(
                self.paperDollTargetIdentifier,
                self.paperDollTargetIsPlayer,
            )
        return False

    def RenderLocalPlayerPaperDoll(self, controlName, scale=0.7):
        control = self.controls.get(controlName)
        try:
            doll = control.asNeteasePaperDoll() if control else None
        except Exception:
            doll = None
        if not doll:
            return False
        playerId = clientApi.GetLocalPlayerId()
        if not playerId:
            return False
        params = {
            # GetLocalPlayerId already returns the engine-owned entity ID in
            # the exact type accepted by RenderEntity.  Converting it through
            # ToText turns a Python 2 str into unicode and breaks player lookup
            # on some NetEase runtimes.
            'entity_id': playerId,
            'scale': float(scale),
            'render_depth': -50,
            'init_rot_y': -35.0,
            'rotation_axis': (0, 1, 0),
            'molang_dict': dict(self.PLAYER_PAPER_DOLL_MOLANG_DEFAULTS),
        }
        try:
            return bool(doll.RenderEntity(params))
        except Exception:
            return False

    def RenderVictimPaperDoll(
        self, controlName, targetIdentifier='', scale=0.7
    ):
        control = self.controls.get(controlName)
        try:
            doll = control.asNeteasePaperDoll() if control else None
        except Exception:
            doll = None
        if not doll:
            return False
        identifier = self.ResolveVictimPaperDollIdentifier(targetIdentifier)
        if not identifier:
            return False
        renderParams = {
            'entity_identifier': identifier,
            'scale': float(scale),
            'render_depth': -15,
            'init_rot_y': 35.0,
            'molang_dict': dict(self.VICTIM_PAPER_DOLL_MOLANG_DEFAULTS),
        }
        try:
            return bool(doll.RenderEntity(renderParams))
        except Exception:
            return False

    def PlayXiaoXiaoWorldAnimation(self):
        # Scaling the Canvas after RenderEntity invalidates the native paper
        # doll viewport, so this style uses a stable hold instead.
        self.entryAnimationStartTime = None
        self.textAnimationStartTime = None
        self.iconHoldUntil = time.time() + self.ICON_HOLD_DURATION
        self.animationActive = True
        return True

    def AddCuppingCatKill(self, headshot=False, playSound=True):
        if not self.controls.get('CuppingCat'):
            return False
        self.totalKills += 1
        self.lastHeadshot = bool(headshot)
        self.HideLayers()
        self.HideTextPerformance()
        if not self.PlayCuppingCatAnimation(min(self.totalKills, 5)):
            return False
        if playSound:
            self.PlaySound()
        return True

    def PlayCuppingCatAnimation(self, stage):
        atlas = self.CUPPING_CAT_ATLASES.get(int(stage))
        ctrl = self.controls.get('CuppingCat')
        image = ctrl.asImage() if ctrl else None
        if not atlas or not image:
            return False
        texture, _, _ = atlas
        try:
            image.SetSprite(texture)
            image.SetSpriteUVSize((self.CUPPING_CAT_FRAME_SIZE, self.CUPPING_CAT_FRAME_SIZE))
            image.SetSpriteUV((0.0, 0.0))
            ctrl.SetAlpha(1.0)
            ctrl.SetVisible(True)
        except Exception:
            return False
        self.cuppingCatStage = int(stage)
        self.cuppingCatFrameIndex = 0
        self.cuppingCatAnimationStartTime = time.time()
        self.entryAnimationStartTime = None
        self.textAnimationStartTime = None
        self.iconHoldUntil = None
        self.animationActive = True
        self.SetPanelVisible(True)
        self.ResetCanvas()
        self.ApplyStyleLayout()
        return True

    def UpdateCuppingCatAnimation(self, now):
        atlas = self.CUPPING_CAT_ATLASES.get(self.cuppingCatStage)
        if not atlas or self.cuppingCatAnimationStartTime is None:
            return False
        _, frameCount, columns = atlas
        elapsed = max(0.0, float(now) - float(self.cuppingCatAnimationStartTime))
        frameIndex = min(int(elapsed * self.CUPPING_CAT_FRAME_RATE), frameCount - 1)
        if frameIndex != self.cuppingCatFrameIndex:
            ctrl = self.controls.get('CuppingCat')
            image = ctrl.asImage() if ctrl else None
            if not image:
                return False
            try:
                image.SetSpriteUV((
                    float(frameIndex % columns) * self.CUPPING_CAT_FRAME_SIZE,
                    float(frameIndex // columns) * self.CUPPING_CAT_FRAME_SIZE,
                ))
            except Exception:
                return False
            self.cuppingCatFrameIndex = frameIndex
        if elapsed < float(frameCount) / self.CUPPING_CAT_FRAME_RATE:
            return True
        self.cuppingCatAnimationStartTime = None
        return False

    def GetCuppingCatAnimationDuration(self):
        atlas = self.CUPPING_CAT_ATLASES.get(self.cuppingCatStage)
        if not atlas:
            return 0.0
        return float(atlas[1]) / self.CUPPING_CAT_FRAME_RATE

    def AddBigDogBarkKill(self, headshot=False, playSound=True):
        if not self.controls.get('BigDogBark'):
            return False
        self.totalKills += 1
        self.lastHeadshot = bool(headshot)
        self.HideLayers()
        self.HideTextPerformance()
        stage = min(max(int(self.totalKills), 1), 5)
        if not self.SetImage('BigDogBark', self.BIG_DOG_BARK_TEXTURES.get(stage)):
            return False
        self.ResetCanvas()
        self.SetPanelVisible(True)
        self.SetVisible('BigDogBark', True)
        self.ApplyStyleLayout()
        self.PlayBigDogBarkAnimation()
        if playSound:
            self.PlaySound()
        return True

    def PlayBigDogBarkAnimation(self):
        now = time.time()
        self.bigDogBarkAnimationStartTime = now
        self.entryAnimationStartTime = None
        self.textAnimationStartTime = None
        self.iconHoldUntil = None
        self.animationActive = True
        ctrl = self.controls.get('BigDogBark')
        if ctrl:
            try:
                ctrl.SetAlpha(0.0)
                ctrl.SetVisible(True)
            except Exception:
                pass
        return True

    def UpdateBigDogBarkAnimation(self, now):
        ctrl = self.controls.get('BigDogBark')
        start = self.bigDogBarkAnimationStartTime
        if not ctrl or start is None:
            return False
        elapsed = max(0.0, float(now) - float(start))
        fadeStart = self.BIG_DOG_BARK_DISPLAY_DURATION
        totalDuration = fadeStart + self.BIG_DOG_BARK_FADE_OUT_DURATION
        if elapsed >= totalDuration:
            self.bigDogBarkAnimationStartTime = None
            try:
                ctrl.SetVisible(False)
                ctrl.SetAlpha(1.0)
                ctrl.SetPosition(self.bigDogBarkBasePosition)
                ctrl.SetSize((self.bigDogBarkBaseSize, self.bigDogBarkBaseSize))
            except Exception:
                pass
            return False
        entryProgress = min(elapsed / self.BIG_DOG_BARK_ENTRY_DURATION, 1.0)
        entryEased = 1.0 - (1.0 - entryProgress) * (1.0 - entryProgress)
        if entryProgress < 0.70:
            firstPhase = entryProgress / 0.70
            firstEased = 1.0 - (1.0 - firstPhase) * (1.0 - firstPhase)
            scale = 0.68 + 0.46 * firstEased
        elif entryProgress < 1.0:
            secondPhase = (entryProgress - 0.70) / 0.30
            scale = 1.14 - 0.14 * secondPhase
        else:
            pulse = max(0.0, 1.0 - elapsed / self.BIG_DOG_BARK_SHAKE_DURATION)
            scale = 1.0 + 0.028 * math.sin(elapsed * 25.0) * pulse
        if elapsed > fadeStart:
            fadeProgress = min((elapsed - fadeStart) / self.BIG_DOG_BARK_FADE_OUT_DURATION, 1.0)
            alpha = 1.0 - fadeProgress
        else:
            alpha = min(1.0, entryEased * 1.45)
        shakeX = 0.0
        shakeY = 0.0
        if elapsed < self.BIG_DOG_BARK_SHAKE_DURATION:
            shakeProgress = elapsed / self.BIG_DOG_BARK_SHAKE_DURATION
            shakePower = (1.0 - shakeProgress) * self.BIG_DOG_BARK_SHAKE_DISTANCE * self.layoutScale
            shakeIndex = int(elapsed / 0.055)
            direction = -1.0 if shakeIndex % 2 else 1.0
            shakeX = direction * shakePower
            shakeY = (1.0 if shakeIndex % 3 == 0 else -1.0) * shakePower * 0.32
        size = max(1.0, self.bigDogBarkBaseSize * scale)
        position = (
            self.bigDogBarkBasePosition[0] + shakeX,
            self.bigDogBarkBasePosition[1] + shakeY,
        )
        try:
            ctrl.SetPosition(position)
            ctrl.SetSize((size, size))
            ctrl.SetAlpha(float(alpha))
            ctrl.SetVisible(float(alpha) > 0.001)
            return True
        except Exception:
            return False

    def AddQinshouXianshengKill(self, headshot=False, playSound=True):
        if not self.controls.get('QinshouXiansheng'):
            return False
        self.totalKills += 1
        self.lastHeadshot = bool(headshot)
        self.HideLayers()
        self.HideTextPerformance()
        if not self.SetImage('QinshouXiansheng', self.QINSHOU_XIANSHENG_TEXTURE):
            return False
        self.ResetCanvas()
        self.SetPanelVisible(True)
        self.SetVisible('QinshouXiansheng', True)
        self.ApplyStyleLayout()
        self.PlayQinshouXianshengAnimation()
        if playSound:
            self.PlaySound()
        return True

    def PlayQinshouXianshengAnimation(self):
        self.qinshouXianshengAnimationStartTime = time.time()
        self.entryAnimationStartTime = None
        self.textAnimationStartTime = None
        self.iconHoldUntil = None
        self.animationActive = True
        ctrl = self.controls.get('QinshouXiansheng')
        if ctrl:
            try:
                ctrl.SetAlpha(0.0)
                ctrl.SetVisible(True)
            except Exception:
                pass
        return True

    def UpdateQinshouXianshengAnimation(self, now):
        ctrl = self.controls.get('QinshouXiansheng')
        start = self.qinshouXianshengAnimationStartTime
        if not ctrl or start is None:
            return False
        elapsed = max(0.0, float(now) - float(start))
        fadeStart, fadeOutDuration = self.GetQinshouXianshengTiming()
        if elapsed >= fadeStart + fadeOutDuration:
            self.qinshouXianshengAnimationStartTime = None
            self.ResetQinshouXianshengControl(ctrl)
            return False
        scale, alpha = self.GetQinshouXianshengVisualState(
            elapsed, fadeStart, fadeOutDuration)
        try:
            ctrl.SetPosition(self.qinshouXianshengBasePosition)
            self.SetQinshouXianshengSize(ctrl, scale)
            ctrl.SetAlpha(float(alpha))
            ctrl.SetVisible(float(alpha) > 0.001)
            return True
        except Exception:
            return False

    def ResetQinshouXianshengControl(self, control):
        try:
            control.SetVisible(False)
            control.SetAlpha(1.0)
            control.SetPosition(self.qinshouXianshengBasePosition)
            self.SetQinshouXianshengSize(control, 1.0)
            return True
        except Exception:
            return False

    def SetQinshouXianshengSize(self, control, scale):
        scale = max(0.01, float(scale))
        baseSize = self.qinshouXianshengBaseSize
        width = max(1.0, float(baseSize[0]) * scale)
        height = max(1.0, float(baseSize[1]) * scale)
        try:
            resultX = control.SetFullSize('x', {
                'followType': 'none',
                'relativeValue': 0.0,
                'absoluteValue': width,
            })
            resultY = control.SetFullSize('y', {
                'followType': 'none',
                'relativeValue': 0.0,
                'absoluteValue': height,
            })
            if resultX is False or resultY is False:
                raise ValueError('SetFullSize failed')
            return True
        except Exception:
            control.SetSize((width, height))
            return True

    def GetQinshouXianshengVisualState(
        self, elapsed, fadeStart=None, fadeOutDuration=None
    ):
        if fadeStart is None or fadeOutDuration is None:
            fadeStart, fadeOutDuration = self.GetQinshouXianshengTiming()
        entryProgress = min(
            elapsed / self.QINSHOU_XIANSHENG_ENTRY_DURATION, 1.0)
        entryEased = 1.0 - (1.0 - entryProgress) * (1.0 - entryProgress)
        if elapsed < self.QINSHOU_XIANSHENG_ENTRY_DURATION:
            scale = 0.84 + 0.16 * entryEased
            alpha = min(1.0, 0.18 + 0.82 * entryEased)
        else:
            scale = 1.0
            alpha = 1.0
        if elapsed > fadeStart:
            fadeProgress = min(
                (elapsed - fadeStart) / fadeOutDuration,
                1.0,
            )
            alpha = 1.0 - fadeProgress
        return scale, alpha

    def Clear(self):
        if self.style == self.QINSHOU_XIANSHENG_STYLE:
            self.StopQinshouXianshengSound()
        self.ResetKillState()
        self.CancelAnimation()
        self.queueIcons = []
        self.queueDismissing = False
        self.nextQueueDismissTime = None
        self.pubgFeedItems = []
        self.pubgComboBirthTime = None
        self.apexFeedItems = []
        self.battlefield1Queue = []
        self.battlefield1Current = None
        self.battlefield1StartTime = None
        self.battlefield1LastSwitchTime = None
        self.SetPanelVisible(False)
        self.HideQueueControls()
        self.HidePubgControls()
        self.HideBattlefield1()
        self.HideTextPerformance()
        self.MovePaperDollControlsOffscreen()
        self.ResetCanvas()

    def ResetKillState(self):
        self.totalKills = 0
        self.totalScore = 0
        self.lastKillScore = 0
        self.lastHeadshot = False
        self.targetMaxHealth = u'?'
        self.killDistance = None
        self.killDamage = None
        self.codTextLines = ()
        self.paperDollTargetIdentifier = self.VICTIM_PREVIEW_IDENTIFIER
        self.paperDollTargetIsPlayer = False

    def RollKillScore(self, headshot=False):
        score = random.randint(self.KILL_SCORE_MIN, self.KILL_SCORE_MAX)
        if headshot:
            score *= self.HEADSHOT_SCORE_MULTIPLIER
        return int(score)

    def RollCodKillXp(self, headshot=False):
        score = random.randint(self.COD_XP_MIN, self.COD_XP_MAX)
        if headshot:
            score = (
                score * self.COD_HEADSHOT_MULTIPLIER +
                random.randint(self.COD_HEADSHOT_BONUS_MIN, self.COD_HEADSHOT_BONUS_MAX)
            )
        return int(score)

    def RollApexKillScore(self, headshot=False):
        score = random.randint(self.APEX_REWARD_MIN, self.APEX_REWARD_MAX)
        if headshot:
            score = (
                score * self.APEX_HEADSHOT_MULTIPLIER +
                random.randint(self.APEX_HEADSHOT_BONUS_MIN, self.APEX_HEADSHOT_BONUS_MAX)
            )
        return int(score)

    def Destroy(self):
        self.Clear()
        self.controls = {}
        self.queueControls = []
        self.pubgLineControls = []
        self.touchDisabledUiNode = None
        self.uiNode = None

    def Refresh(self):
        self.HideLayers()
        count = max(1, int(self.totalKills))
        if self.style == 'cf_combo':
            maxCombo = int(self.GetStyleOption('MaxCombo', 6))
            self.SetImage('Primary', 'textures/ui/killbroadcast_kill_effect/killicon_combo_%d' % min(count, maxCombo))
            self.SetVisible('Primary', True)
        elif self.style == 'pubg':
            pass
        elif self.style == 'battlefield1':
            if self.battlefield1Current:
                self.RenderBattlefield1(time.time())
        elif self.style == 'valorant':
            tier = min(count, int(self.GetStyleOption('MaxTier', 3)))
            prefix = 'textures/ui/killbroadcast_kill_effect/killicon_valorant_singularity_v%d_' % tier
            self.SetImage('Bar', prefix + 'bar')
            self.SetImage('Ring', 'textures/ui/killbroadcast_kill_effect/killicon_valorant_base_ring')
            self.SetImage('Frame', 'textures/ui/killbroadcast_kill_effect/killicon_valorant_base_frame')
            self.SetImage('Emblem', prefix + 'emblem')
            for name in ('Bar', 'Ring', 'Frame', 'Emblem'):
                self.SetVisible(name, True)
            if self.lastHeadshot and self.GetStyleOption('ShowHeadshot', True):
                self.SetImage('Headshot', 'textures/ui/killbroadcast_kill_effect/killicon_valorant_headshot')
                self.SetVisible('Headshot', True)
        elif self.style in self.STYLE_TEXTURES:
            styleData = self.STYLE_TEXTURES.get(self.style, self.STYLE_TEXTURES['classic'])
            texture = styleData['headshot'] if self.lastHeadshot else styleData['normal']
            self.SetImage('Primary', texture)
            self.SetVisible('Primary', True)
        self.SetPanelVisible(True)
        self.ApplyStyleLayout()

    def HideLayers(self, hideQueue=True):
        for name in (
            'Bar', 'Ring', 'Frame', 'Primary', 'Emblem', 'Headshot', 'Count',
            'CuppingCat', 'XiaoXiaoWorld', 'KingHonor', 'BigDogBark',
            'QinshouXiansheng',
            'XiaoXiaoWorldRightPlayerIcon', 'KingHonorRightPlayerIcon',
        ):
            self.SetVisible(name, False)
        self.MovePaperDollControlsOffscreen()
        if hideQueue:
            self.HideQueueControls()
        self.HidePubgControls()
        self.HideBattlefield1()

    def HideQueueControls(self):
        for ctrl in self.queueControls:
            try:
                if ctrl:
                    ctrl.SetVisible(False)
            except Exception:
                pass

    def HidePubgControls(self):
        self.SetVisible('PubgFeed', False)
        self.SetVisible('PubgCombo', False)
        for lineControls in self.pubgLineControls:
            ctrl = lineControls.get('Panel')
            try:
                if ctrl:
                    ctrl.SetVisible(False)
            except Exception:
                pass

    def HideBattlefield1(self):
        self.SetVisible('Battlefield1', False)
        return True

    def GetBattlefield1HealthText(self, value):
        if value is None or value == '':
            return u'?'
        try:
            return self.ToText(int(float(value)))
        except Exception:
            return u'?'

    def GetBattlefield1QueueLength(self):
        try:
            value = int(self.GetStyleOption(
                'QueueLength', self.BATTLEFIELD1_MAX_QUEUE_SIZE))
        except Exception:
            value = self.BATTLEFIELD1_MAX_QUEUE_SIZE
        return min(self.BATTLEFIELD1_MAX_QUEUE_SIZE, max(1, value))

    def AddBattlefield1Kill(self, headshot, weaponName, targetName, healthText, playSound=True):
        maxVisible = self.GetBattlefield1QueueLength()
        while len(self.battlefield1Queue) >= maxVisible:
            self.battlefield1Queue.pop(0)
        self.battlefield1Queue.append({
            'Headshot': bool(headshot),
            'WeaponName': self.ToText(weaponName),
            'TargetName': self.ToText(targetName),
            'HealthText': self.ToText(healthText) or u'?',
            'PlaySound': bool(playSound),
        })
        self.SetPanelVisible(True)
        self.animationActive = True
        return True

    def ProcessBattlefield1Queue(self, now):
        if not self.battlefield1Queue:
            return False
        if self.battlefield1Current is not None:
            if self.battlefield1LastSwitchTime is None:
                self.battlefield1LastSwitchTime = now
            elapsed = now - float(self.battlefield1LastSwitchTime)
            if elapsed < self.BATTLEFIELD1_ANIMATION_DURATION:
                return False
        context = self.battlefield1Queue.pop(0)
        self.battlefield1Current = context
        self.battlefield1StartTime = now
        self.battlefield1LastSwitchTime = now
        self.totalKills += 1
        self.lastHeadshot = bool(context.get('Headshot'))
        self.weaponName = self.ToText(context.get('WeaponName')) or u'\u672a\u77e5\u6b66\u5668'
        self.targetName = self.ToText(context.get('TargetName')) or u'\u672a\u77e5\u76ee\u6807'
        self.targetMaxHealth = self.ToText(context.get('HealthText')) or u'?'
        self.HideLayers()
        self.HideTextPerformance()
        if context.get('PlaySound'):
            self.PlaySound()
        return True

    def GetBattlefield1Alpha(self, elapsed):
        if elapsed < self.BATTLEFIELD1_ANIMATION_DURATION:
            return min(max(elapsed / self.BATTLEFIELD1_ANIMATION_DURATION, 0.0), 1.0)
        if elapsed > self.BATTLEFIELD1_DISPLAY_DURATION:
            fadeElapsed = elapsed - self.BATTLEFIELD1_DISPLAY_DURATION
            if fadeElapsed >= self.BATTLEFIELD1_ANIMATION_DURATION:
                return 0.0
            return 1.0 - fadeElapsed / self.BATTLEFIELD1_ANIMATION_DURATION
        return 1.0

    def GetBattlefield1Scale(self, elapsed):
        if elapsed >= self.BATTLEFIELD1_ANIMATION_DURATION:
            return 1.0
        progress = min(max(elapsed / self.BATTLEFIELD1_ANIMATION_DURATION, 0.0), 1.0)
        eased = 1.0 - (1.0 - progress) ** 3
        return 0.6 + 0.4 * eased

    def EstimateBattlefield1TextWidth(self, text):
        return self.EstimatePubgTextWidth(text)

    def RenderBattlefield1(self, now):
        if not self.battlefield1Current or self.battlefield1StartTime is None:
            self.HideBattlefield1()
            return False
        canvas = self.controls.get('Canvas')
        root = self.controls.get('Battlefield1')
        if not canvas or not root:
            return False
        canvasSize = self.GetLayoutCanvasSize()
        if not isinstance(canvasSize, (list, tuple)) or len(canvasSize) < 2:
            return False
        canvasWidth = float(canvasSize[0])
        canvasHeight = float(canvasSize[1])
        if canvasWidth <= 0.0 or canvasHeight <= 0.0:
            return False
        elapsed = max(0.0, now - float(self.battlefield1StartTime))
        alpha = self.GetBattlefield1Alpha(elapsed)
        globalScale = self.GetBattlefield1Scale(elapsed)
        layoutScale = self.layoutScale * globalScale
        borderSize = self.BATTLEFIELD1_BORDER_SIZE * layoutScale
        weaponScale = self.BATTLEFIELD1_WEAPON_SCALE
        victimScale = self.BATTLEFIELD1_VICTIM_SCALE
        healthScale = self.BATTLEFIELD1_HEALTH_SCALE

        weaponWidth, weaponHeight = self.PrepareBattlefield1Label(
            'Battlefield1Weapon', self.weaponName, weaponScale, layoutScale
        )
        victimWidth, victimHeight = self.PrepareBattlefield1Label(
            'Battlefield1Victim', self.targetName, victimScale, layoutScale
        )
        healthWidth, healthHeight = self.PrepareBattlefield1Label(
            'Battlefield1Health', self.targetMaxHealth, healthScale, layoutScale
        )

        weaponX = -weaponWidth * 0.5
        weaponY = -weaponHeight * 0.5
        weaponRight = weaponX + weaponWidth
        weaponTop = weaponY
        weaponBottom = weaponY + weaponHeight
        victimRight = weaponRight
        victimX = victimRight - victimWidth
        victimBottom = weaponTop - borderSize
        victimY = victimBottom - victimHeight
        victimTop = victimY
        healthX = weaponRight + borderSize
        spanTop = victimTop
        spanBottom = weaponBottom
        midY = (spanTop + spanBottom) * 0.5
        healthY = midY - healthHeight * 0.5
        healthRight = healthX + healthWidth
        healthTop = healthY
        healthBottom = healthY + healthHeight

        subBoxTop = min(weaponTop, healthTop, victimTop) - borderSize
        distY = max(healthTop - subBoxTop, borderSize)
        subBoxRight = healthRight + distY
        subBoxLeft = min(weaponX, healthX, victimX) - borderSize
        subBoxBottom = max(weaponBottom, healthBottom, victimBottom) + borderSize
        subBoxWidth = subBoxRight - subBoxLeft
        subBoxHeight = subBoxBottom - subBoxTop
        iconBoxSize = subBoxHeight
        iconBoxLeft = subBoxLeft - iconBoxSize
        totalWidth = subBoxRight - iconBoxLeft
        totalHeight = subBoxHeight

        originX = canvasWidth * 0.5
        originY = canvasHeight * 0.5
        rootX = originX + iconBoxLeft
        rootY = originY + subBoxTop
        try:
            root.SetPosition((rootX, rootY))
            root.SetSize((totalWidth, totalHeight))
            root.SetVisible(True)
        except Exception:
            return False

        offsetX = -iconBoxLeft
        offsetY = -subBoxTop
        showBackground = bool(self.GetStyleOption('ShowBackground', True))
        self.ApplyBattlefield1Box(
            'Battlefield1IconBox',
            0.0,
            0.0,
            iconBoxSize,
            iconBoxSize,
            1.0,
            self.BATTLEFIELD1_ICON_BOX_ALPHA * alpha,
            showBackground,
        )
        self.ApplyBattlefield1Box(
            'Battlefield1TextBox',
            iconBoxSize,
            0.0,
            subBoxWidth,
            subBoxHeight,
            1.0,
            self.BATTLEFIELD1_TEXT_BOX_ALPHA * alpha,
            showBackground,
        )
        iconDrawSize = self.BATTLEFIELD1_ICON_SIZE * layoutScale
        self.ApplyBattlefield1Box(
            'Battlefield1Icon',
            (iconBoxSize - iconDrawSize) * 0.5,
            (iconBoxSize - iconDrawSize) * 0.5,
            iconDrawSize,
            iconDrawSize,
            1.0,
            alpha,
        )
        self.SetImage(
            'Battlefield1Icon',
            self.STYLE_TEXTURES['battlefield1']['headshot']
            if self.lastHeadshot else self.STYLE_TEXTURES['battlefield1']['normal'],
        )
        self.PlaceBattlefield1Label(
            'Battlefield1Victim', victimX + offsetX, victimY + offsetY, alpha
        )
        self.PlaceBattlefield1Label(
            'Battlefield1Weapon', weaponX + offsetX, weaponY + offsetY, alpha
        )
        self.PlaceBattlefield1Label(
            'Battlefield1Health', healthX + offsetX, healthY + offsetY, alpha
        )
        self.SetPanelVisible(True)
        return True

    def ApplyBattlefield1Box(self, name, x, y, width, height, scale, alpha, visible=True):
        ctrl = self.controls.get(name)
        if not ctrl:
            return False
        try:
            ctrl.SetPosition((float(x) * scale, float(y) * scale))
            ctrl.SetSize((float(width) * scale, float(height) * scale))
            ctrl.SetAlpha(float(alpha))
            ctrl.SetVisible(bool(visible))
            return True
        except Exception:
            return False

    def PrepareBattlefield1Label(self, name, text, fontScale, scale):
        ctrl = self.controls.get(name)
        label = ctrl.asLabel() if ctrl else None
        if not ctrl or not label:
            return (
                max(self.EstimateBattlefield1TextWidth(text) * fontScale * scale, 1.0),
                max(self.BATTLEFIELD1_FONT_HEIGHT * fontScale * scale, 1.0),
            )
        try:
            label.SetText(self.ToText(text))
            label.SetTextFontSize(float(fontScale) * scale)
        except Exception:
            pass
        try:
            size = ctrl.GetSize()
            if (
                isinstance(size, (list, tuple)) and len(size) >= 2 and
                float(size[0]) > 2.0 and float(size[1]) > 2.0
            ):
                return (float(size[0]), float(size[1]))
        except Exception:
            pass
        fallbackWidth = (
            self.EstimateBattlefield1TextWidth(text) * float(fontScale) + 4.0
        ) * float(scale) * 1.35
        fallbackHeight = (
            self.BATTLEFIELD1_FONT_HEIGHT * float(fontScale) + 2.0
        ) * float(scale)
        return (max(fallbackWidth, 1.0), max(fallbackHeight, 1.0))

    def PlaceBattlefield1Label(self, name, x, y, alpha):
        ctrl = self.controls.get(name)
        if not ctrl:
            return False
        try:
            ctrl.SetPosition((float(x), float(y)))
            ctrl.SetAlpha(float(alpha))
            ctrl.SetVisible(True)
            return True
        except Exception:
            return False

    def UpdateBattlefield1(self, now):
        self.ProcessBattlefield1Queue(now)
        if not self.battlefield1Current or self.battlefield1StartTime is None:
            self.HideBattlefield1()
            self.SetPanelVisible(False)
            return False
        elapsed = max(0.0, now - float(self.battlefield1StartTime))
        alpha = self.GetBattlefield1Alpha(elapsed)
        if (
            not self.battlefield1Queue and
            alpha <= 0.001 and
            elapsed > self.BATTLEFIELD1_DISPLAY_DURATION
        ):
            self.battlefield1Current = None
            self.battlefield1StartTime = None
            self.battlefield1LastSwitchTime = None
            self.HideBattlefield1()
            self.ResetKillState()
            self.SetPanelVisible(False)
            return False
        self.RenderBattlefield1(now)
        return True

    def AddPubgKill(self):
        now = time.time()
        prefix = u'\u4f60'
        if self.GetStyleOption('ShowWeapon', True):
            prefix = u'\u4f60\u7528%s' % self.weaponName
        if self.lastHeadshot:
            prefix += u'\u547d\u4e2d\u5934\u90e8'
        suffix = u'\u4e86 %s' % self.targetName
        if self.GetStyleOption('ShowDistance', True) and self.killDistance is not None:
            suffix += u'  %.1f\u7c73' % float(self.killDistance)
        if len(self.pubgFeedItems) >= self.PUBG_FEED_MAX_LINES:
            self.pubgFeedItems.pop(0)
        self.pubgFeedItems.append({
            'Prefix': prefix,
            'Emphasis': u'\u6dd8\u6c70',
            'Suffix': suffix,
            'BirthTime': now,
            'PreviousY': 0.0,
            'CurrentY': 0.0,
            'TargetY': 0.0,
            'MoveStartTime': now,
        })
        self.pubgComboBirthTime = now
        self.UpdatePubgFeedTargets(now)
        self.RenderPubgFeed(now)
        self.SetPanelVisible(True)
        self.animationActive = True
        return True

    def UpdatePubgFeedTargets(self, now):
        count = len(self.pubgFeedItems)
        spacing = self.PUBG_FEED_LINE_SPACING * self.layoutScale
        for index, item in enumerate(self.pubgFeedItems):
            targetY = -float(count - 1 - index) * spacing
            if abs(float(item.get('TargetY', 0.0)) - targetY) <= 0.01:
                continue
            item['PreviousY'] = float(item.get('CurrentY', 0.0))
            item['TargetY'] = targetY
            item['MoveStartTime'] = now

    def RemoveExpiredPubgItems(self, now):
        remaining = []
        for item in self.pubgFeedItems:
            age = max(0.0, now - float(item.get('BirthTime', now)))
            if age < self.PUBG_FEED_DURATION + self.PUBG_FEED_FADE_OUT_DURATION:
                remaining.append(item)
        if len(remaining) == len(self.pubgFeedItems):
            return False
        self.pubgFeedItems = remaining
        self.UpdatePubgFeedTargets(now)
        return True

    def BeginPubgNaturalDismiss(self):
        if self.style != 'pubg' or not self.pubgFeedItems:
            return False
        self.animationActive = True
        return True

    def RenderPubgFeed(self, now):
        canvasSize = self.GetLayoutCanvasSize()
        if not isinstance(canvasSize, (list, tuple)) or len(canvasSize) < 2:
            return False
        canvasWidth = float(canvasSize[0])
        canvasHeight = float(canvasSize[1])
        if canvasWidth <= 0.0 or canvasHeight <= 0.0:
            return False
        baseY = canvasHeight * 0.68
        for index, lineControls in enumerate(self.pubgLineControls):
            ctrl = lineControls.get('Panel')
            if not ctrl or index >= len(self.pubgFeedItems):
                try:
                    if ctrl:
                        ctrl.SetVisible(False)
                except Exception:
                    pass
                continue
            item = self.pubgFeedItems[index]
            moveElapsed = max(0.0, now - float(item.get('MoveStartTime', now)))
            moveProgress = min(moveElapsed / self.PUBG_FEED_MOVE_DURATION, 1.0)
            moveEased = 1.0 - (1.0 - moveProgress) * (1.0 - moveProgress)
            previousY = float(item.get('PreviousY', 0.0))
            targetY = float(item.get('TargetY', previousY))
            currentY = previousY + (targetY - previousY) * moveEased
            item['CurrentY'] = currentY
            age = max(0.0, now - float(item.get('BirthTime', now)))
            alpha = min(age / self.PUBG_FEED_FADE_IN_DURATION, 1.0)
            if age > self.PUBG_FEED_DURATION:
                alpha *= max(0.0, 1.0 - (age - self.PUBG_FEED_DURATION) / self.PUBG_FEED_FADE_OUT_DURATION)
            positionFromBottom = len(self.pubgFeedItems) - 1 - index
            if self.PUBG_FEED_MAX_LINES > 1:
                alpha *= max(0.20, 1.0 - float(positionFromBottom) / (self.PUBG_FEED_MAX_LINES - 1))
            self.ApplyPubgLineControl(lineControls, item, canvasWidth, baseY + currentY, alpha)
        self.SetVisible('PubgFeed', bool(self.pubgFeedItems))
        self.RefreshPubgCombo(now, canvasWidth, canvasHeight)
        return True

    def ApplyPubgLineControl(self, controls, item, canvasWidth, centerY, alpha):
        panel = controls.get('Panel')
        if not panel:
            return False
        damageControl = controls.get('Damage')
        backgroundControl = controls.get('Background')
        badgeControl = controls.get('Badge')
        try:
            if damageControl:
                damageControl.SetVisible(False)
            if backgroundControl:
                backgroundControl.SetVisible(False)
            if badgeControl:
                badgeControl.SetVisible(False)
        except Exception:
            pass
        lineHeight = self.PUBG_FEED_LINE_HEIGHT * self.layoutScale
        prefix = self.ToText(item.get('Prefix', ''))
        emphasis = self.ToText(item.get('Emphasis', ''))
        suffix = self.ToText(item.get('Suffix', ''))
        widths = [
            self.EstimatePubgTextWidth(prefix),
            self.EstimatePubgTextWidth(emphasis),
            self.EstimatePubgTextWidth(suffix),
        ]
        availableWidth = canvasWidth * 0.94
        rawWidth = sum(widths) * self.layoutScale
        fitScale = min(1.0, availableWidth / rawWidth) if rawWidth > 0.0 else 1.0
        fontScale = self.PUBG_FEED_FONT_SCALE * self.layoutScale * fitScale
        widths = [value * self.layoutScale * fitScale for value in widths]
        startX = (canvasWidth - sum(widths)) * 0.5
        try:
            panel.SetPosition((0.0, float(centerY) - lineHeight * 0.5))
            panel.SetSize((canvasWidth, lineHeight))
            panel.SetAlpha(float(alpha))
            panel.SetVisible(float(alpha) > 0.001)
        except Exception:
            return False
        values = (('Prefix', prefix), ('Emphasis', emphasis), ('Suffix', suffix))
        cursorX = startX
        for index, valueData in enumerate(values):
            name, text = valueData
            ctrl = controls.get(name)
            width = widths[index]
            if not ctrl:
                cursorX += width
                continue
            try:
                ctrl.SetPosition((cursorX, 0.0))
                ctrl.SetSize((width, lineHeight))
                label = ctrl.asLabel()
                if label:
                    label.SetText(text)
                    label.SetTextFontSize(fontScale)
                ctrl.SetVisible(bool(text))
            except Exception:
                pass
            cursorX += width
        return True

    def EstimatePubgTextWidth(self, text):
        width = 0.0
        for char in self.ToText(text):
            code = ord(char)
            if char == u' ':
                width += 3.5
            elif code < 128:
                width += 5.5
            else:
                width += 9.0
        return width

    def RefreshPubgCombo(self, now, canvasWidth, canvasHeight):
        ctrl = self.controls.get('PubgCombo')
        if not ctrl or not self.GetStyleOption('ShowCombo', True) or self.pubgComboBirthTime is None:
            self.SetVisible('PubgCombo', False)
            return False
        age = max(0.0, now - float(self.pubgComboBirthTime))
        if age >= self.PUBG_FEED_DURATION + self.PUBG_FEED_FADE_OUT_DURATION:
            self.SetVisible('PubgCombo', False)
            return False
        alpha = min(age / self.PUBG_FEED_FADE_IN_DURATION, 1.0)
        if age > self.PUBG_FEED_DURATION:
            alpha *= max(0.0, 1.0 - (age - self.PUBG_FEED_DURATION) / self.PUBG_FEED_FADE_OUT_DURATION)
        count = max(1, int(self.totalKills))
        text = u'%d \u6dd8\u6c70' % count if count == 1 else u'%d \u6dd8\u6c70\u6570' % count
        comboHeight = 18.0 * self.layoutScale
        try:
            ctrl.SetPosition((0.0, canvasHeight * 0.68 + 9.0 * self.layoutScale))
            ctrl.SetSize((canvasWidth, comboHeight))
            ctrl.SetAlpha(float(alpha))
            label = ctrl.asLabel()
            if label:
                label.SetText(text)
                label.SetTextFontSize(self.PUBG_COMBO_FONT_SCALE * self.layoutScale)
            ctrl.SetVisible(float(alpha) > 0.001)
            return True
        except Exception:
            return False

    def GetApexDamageText(self):
        value = self.killDamage
        if value is None:
            try:
                value = float(self.targetMaxHealth)
            except Exception:
                value = None
        if value is None or value <= 0.0:
            return u''
        rounded = int(round(float(value)))
        return u'\u9020\u6210 %d \u70b9\u4f24\u5bb3' % rounded

    def AddApexKill(self):
        now = time.time()
        if len(self.apexFeedItems) >= self.APEX_FEED_MAX_LINES:
            self.apexFeedItems.pop(0)
        rewardScore = int(
            self.lastKillScore or self.RollApexKillScore(self.lastHeadshot)
        )
        self.apexFeedItems.append({
            'Prefix': u'\u51fb\u5012 ',
            'Emphasis': self.targetName,
            'Suffix': u' +%d' % rewardScore,
            'Badge': u' \u25b2\u2666',
            'Damage': self.GetApexDamageText(),
            'BirthTime': now,
            'PreviousY': 0.0,
            'CurrentY': 0.0,
            'TargetY': 0.0,
            'MoveStartTime': now,
        })
        self.UpdateApexFeedTargets(now)
        self.RenderApexFeed(now)
        self.SetPanelVisible(True)
        self.animationActive = True
        return True

    def UpdateApexFeedTargets(self, now):
        count = len(self.apexFeedItems)
        spacing = self.APEX_LINE_SPACING * self.layoutScale
        centerIndex = float(count - 1) * 0.5
        for index, item in enumerate(self.apexFeedItems):
            targetY = (float(index) - centerIndex) * spacing
            if abs(float(item.get('TargetY', 0.0)) - targetY) <= 0.01:
                continue
            item['PreviousY'] = float(item.get('CurrentY', 0.0))
            item['TargetY'] = targetY
            item['MoveStartTime'] = now

    def RemoveExpiredApexItems(self, now):
        totalDuration = self.APEX_HOLD_DURATION + self.APEX_FADE_OUT_DURATION
        remaining = []
        for item in self.apexFeedItems:
            age = max(0.0, now - float(item.get('BirthTime', now)))
            if age < totalDuration:
                remaining.append(item)
        if len(remaining) == len(self.apexFeedItems):
            return False
        self.apexFeedItems = remaining
        self.UpdateApexFeedTargets(now)
        return True

    def RenderApexFeed(self, now):
        canvasSize = self.GetLayoutCanvasSize()
        if not isinstance(canvasSize, (list, tuple)) or len(canvasSize) < 2:
            return False
        canvasWidth = float(canvasSize[0])
        canvasHeight = float(canvasSize[1])
        if canvasWidth <= 0.0 or canvasHeight <= 0.0:
            return False
        baseY = canvasHeight * 0.50
        for index, lineControls in enumerate(self.pubgLineControls):
            panel = lineControls.get('Panel')
            if not panel or index >= len(self.apexFeedItems):
                try:
                    if panel:
                        panel.SetVisible(False)
                except Exception:
                    pass
                continue
            item = self.apexFeedItems[index]
            age = max(0.0, now - float(item.get('BirthTime', now)))
            entryProgress = min(age / self.APEX_ENTRY_DURATION, 1.0)
            entryEased = 1.0 - (1.0 - entryProgress) ** 3
            entryScale = self.APEX_START_SCALE + (1.0 - self.APEX_START_SCALE) * entryEased
            alpha = entryEased
            if age > self.APEX_HOLD_DURATION:
                alpha *= max(
                    0.0,
                    1.0 - (age - self.APEX_HOLD_DURATION) / self.APEX_FADE_OUT_DURATION,
                )
            moveElapsed = max(0.0, now - float(item.get('MoveStartTime', now)))
            moveProgress = min(moveElapsed / self.APEX_MOVE_DURATION, 1.0)
            moveEased = 1.0 - (1.0 - moveProgress) ** 3
            previousY = float(item.get('PreviousY', 0.0))
            targetY = float(item.get('TargetY', previousY))
            currentY = previousY + (targetY - previousY) * moveEased
            item['CurrentY'] = currentY
            entryOffsetY = 8.0 * self.layoutScale * (1.0 - entryEased)
            self.ApplyApexLineControl(
                lineControls,
                item,
                canvasWidth,
                baseY + currentY + entryOffsetY,
                alpha,
                entryScale,
            )
        self.SetVisible('PubgFeed', bool(self.apexFeedItems))
        self.SetVisible('PubgCombo', False)
        return True

    def ApplyApexLineControl(self, controls, item, canvasWidth, centerY, alpha, entryScale):
        panel = controls.get('Panel')
        if not panel:
            return False
        scale = self.layoutScale * max(0.01, float(entryScale))
        lineHeight = self.APEX_LINE_HEIGHT * scale
        mainHeight = 10.5 * scale
        damageHeight = 8.5 * scale
        prefix = self.ToText(item.get('Prefix', ''))
        emphasis = self.ToText(item.get('Emphasis', ''))
        suffix = self.ToText(item.get('Suffix', ''))
        badge = self.ToText(item.get('Badge', ''))
        damageText = self.ToText(item.get('Damage', ''))
        widths = [
            self.EstimatePubgTextWidth(prefix) * scale,
            self.EstimatePubgTextWidth(emphasis) * scale,
            self.EstimatePubgTextWidth(suffix) * scale,
            self.EstimatePubgTextWidth(badge) * scale,
        ]
        rawWidth = sum(widths)
        availableWidth = canvasWidth * 0.94
        fitScale = min(1.0, availableWidth / rawWidth) if rawWidth > 0.0 else 1.0
        widths = [width * fitScale for width in widths]
        mainFontScale = self.APEX_MAIN_FONT_SCALE * scale * fitScale
        damageFontScale = self.APEX_DAMAGE_FONT_SCALE * scale * fitScale
        startX = (canvasWidth - sum(widths)) * 0.5
        try:
            panel.SetPosition((0.0, float(centerY) - lineHeight * 0.5))
            panel.SetSize((canvasWidth, lineHeight))
            panel.SetAlpha(float(alpha))
            panel.SetVisible(float(alpha) > 0.001)
        except Exception:
            return False
        cursorX = startX
        values = (
            ('Prefix', prefix, self.APEX_TEXT_COLOR),
            ('Emphasis', emphasis, self.APEX_TARGET_COLOR),
            ('Suffix', suffix, self.APEX_TEXT_COLOR),
            ('Badge', badge, self.APEX_BADGE_COLOR),
        )
        for index, valueData in enumerate(values):
            name, text, color = valueData
            ctrl = controls.get(name)
            width = widths[index]
            if not ctrl:
                cursorX += width
                continue
            try:
                ctrl.SetPosition((cursorX, 0.0))
                ctrl.SetSize((width, mainHeight))
                label = ctrl.asLabel()
                if label:
                    label.SetText(text)
                    label.SetTextFontSize(mainFontScale)
                    label.SetTextColor(color)
                    label.SetTextAlignment('center')
                ctrl.SetVisible(bool(text))
            except Exception:
                pass
            cursorX += width
        backgroundControl = controls.get('Background')
        if backgroundControl:
            damageWidth = self.EstimatePubgTextWidth(damageText) * scale * fitScale
            backgroundWidth = min(
                canvasWidth * 0.96,
                max(sum(widths), damageWidth) + 10.0 * scale,
            )
            try:
                backgroundControl.SetPosition(((canvasWidth - backgroundWidth) * 0.5, 0.0))
                backgroundControl.SetSize((backgroundWidth, lineHeight))
                backgroundControl.SetAlpha(self.APEX_BACKGROUND_ALPHA)
                backgroundControl.SetVisible(bool(self.GetStyleOption('ShowBackground', True)))
            except Exception:
                pass
        damageControl = controls.get('Damage')
        if damageControl:
            try:
                damageControl.SetPosition((0.0, 10.5 * scale))
                damageControl.SetSize((canvasWidth, damageHeight))
                damageLabel = damageControl.asLabel()
                if damageLabel:
                    damageLabel.SetText(damageText)
                    damageLabel.SetTextFontSize(damageFontScale)
                    damageLabel.SetTextColor(self.APEX_TEXT_COLOR)
                    damageLabel.SetTextAlignment('center')
                damageControl.SetVisible(bool(damageText))
            except Exception:
                pass
        return True

    def AddScrollingKill(self, headshot):
        self.HideLayers(False)
        now = time.time()
        if self.queueDismissing:
            self.CancelScrollingDismiss(now)
        maxActive = min(self.SCROLL_MAX_ACTIVE, self.GetScrollMaxVisible() + 1)
        for texture in self.GetScrollingTextures(headshot):
            if len(self.queueIcons) >= maxActive:
                self.queueIcons.pop(0)
            self.queueIcons.append({
                'Texture': texture,
                'BirthTime': now,
                'PreviousX': 0.0,
                'CurrentX': 0.0,
                'TargetX': None,
                'MoveStartTime': now,
                'ForcedFadeStartTime': None,
            })
        self.UpdateScrollingTargets(now)
        self.RenderScrollingQueue(now)
        self.SetPanelVisible(True)
        self.PlayScrollingAnimation()

    def CancelScrollingDismiss(self, now=None):
        if not self.queueDismissing:
            return False
        if now is None:
            now = time.time()
        self.queueDismissing = False
        self.nextQueueDismissTime = None
        for icon in self.queueIcons:
            if icon.get('ForcedFadeStartTime') is None:
                continue
            currentX = float(icon.get('CurrentX', 0.0))
            icon['ForcedFadeStartTime'] = None
            icon['PreviousX'] = currentX
            icon['TargetX'] = currentX
            icon['MoveStartTime'] = now
        return True

    def GetScrollingTexture(self, headshot):
        styleData = self.STYLE_TEXTURES.get(self.style, self.STYLE_TEXTURES['classic'])
        return styleData['headshot'] if headshot else styleData['normal']

    def GetScrollingTextures(self, headshot):
        if self.style != self.OLD_PRIEST_STYLE:
            return (self.GetScrollingTexture(headshot),)
        return (random.choice(self.OLD_PRIEST_TEXTURES),)

    def UpdateScrollingTargets(self, now):
        size = len(self.queueIcons)
        if size <= 0:
            return
        visibleStart = max(0, size - self.GetScrollMaxVisible())
        for index in range(visibleStart):
            icon = self.queueIcons[index]
            if icon.get('ForcedFadeStartTime') is None:
                icon['ForcedFadeStartTime'] = now
        activeIcons = [icon for icon in self.queueIcons if icon.get('ForcedFadeStartTime') is None]
        fadingIcons = [icon for icon in self.queueIcons if icon.get('ForcedFadeStartTime') is not None]
        visibleCount = len(activeIcons)
        spacing = (self.SCROLL_ICON_SIZE + self.SCROLL_ICON_SPACING) * self.layoutScale
        rightmostX = ((visibleCount - 1) / 2.0) * spacing if visibleCount else 0.0
        for index, icon in enumerate(activeIcons):
            position = index - (visibleCount - 1) / 2.0
            self.UpdateScrollingTarget(icon, -position * spacing, now)
        fadingCount = len(fadingIcons)
        for index, icon in enumerate(fadingIcons):
            self.UpdateScrollingTarget(icon, rightmostX + (fadingCount - index) * spacing, now)

    def UpdateScrollingTarget(self, icon, targetX, now):
        if icon.get('TargetX') is None:
            icon['PreviousX'] = targetX
            icon['CurrentX'] = targetX
            icon['TargetX'] = targetX
            icon['MoveStartTime'] = now
        elif abs(float(icon.get('TargetX', 0.0)) - targetX) > 0.01:
            icon['PreviousX'] = float(icon.get('CurrentX', 0.0))
            icon['TargetX'] = targetX
            icon['MoveStartTime'] = now

    def BeginScrollingDismiss(self):
        if self.style not in self.SCROLL_STYLES or not self.queueIcons:
            return False
        now = time.time()
        self.queueDismissing = True
        self.nextQueueDismissTime = now
        self.animationActive = True
        self.StartNextScrollingDismiss(now)
        self.RenderScrollingQueue(now)
        return True

    def StartNextScrollingDismiss(self, now):
        if not self.queueDismissing or self.nextQueueDismissTime is None or now < self.nextQueueDismissTime:
            return False
        for icon in self.queueIcons:
            if icon.get('ForcedFadeStartTime') is None:
                icon['ForcedFadeStartTime'] = now
                self.nextQueueDismissTime = now + self.SCROLL_DISMISS_INTERVAL
                self.UpdateScrollingTargets(now)
                return True
        self.nextQueueDismissTime = None
        return False

    def PlayScrollingAnimation(self):
        self.entryAnimationStartTime = None
        self.animationActive = True
        return True

    def UpdateKingHonorAnimation(self, now):
        panel = self.controls.get('KingHonor')
        start = self.kingHonorAnimationStartTime
        if not panel or start is None:
            return False
        try:
            if self.iconHoldUntil is not None and float(now) < float(self.iconHoldUntil):
                panel.SetVisible(True)
                return True
            panel.SetVisible(False)
            self.SetVisible('KingHonorRightPlayerIcon', False)
            self.MovePaperDollControlsOffscreen((
                'KingHonorLeftDoll', 'KingHonorRightDoll',
            ))
        except Exception:
            return False
        self.kingHonorAnimationStartTime = None
        self.kingHonorBasePosition = None
        try:
            panel.SetAlpha(1.0)
        except Exception:
            pass
        return False

    def UpdateFrame(self, args=None):
        if not self.animationActive:
            return False
        now = time.time()
        if self.style == self.KING_HONOR_STYLE:
            self.animationActive = self.UpdateKingHonorAnimation(now)
            return self.animationActive
        if self.style == self.BIG_DOG_BARK_STYLE:
            self.animationActive = self.UpdateBigDogBarkAnimation(now)
            return self.animationActive
        if self.style == self.QINSHOU_XIANSHENG_STYLE:
            self.animationActive = self.UpdateQinshouXianshengAnimation(now)
            return self.animationActive
        if self.style == self.CUPPING_CAT_STYLE:
            self.animationActive = self.UpdateCuppingCatAnimation(now)
            return self.animationActive
        if self.style == 'battlefield1':
            self.animationActive = self.UpdateBattlefield1(now)
            return self.animationActive
        iconAnimationActive = False
        if self.style in self.SCROLL_STYLES:
            self.StartNextScrollingDismiss(now)
            self.RemoveFadedScrollingIcons(now)
            self.RenderScrollingQueue(now)
            if self.queueDismissing and not self.queueIcons:
                self.queueDismissing = False
                self.nextQueueDismissTime = None
                self.HideQueueControls()
            iconAnimationActive = self.IsScrollingAnimationActive(now) or self.queueDismissing
        elif self.style == 'pubg':
            self.RemoveExpiredPubgItems(now)
            self.RenderPubgFeed(now)
            iconAnimationActive = bool(self.pubgFeedItems)
        elif self.style == 'apex':
            self.RemoveExpiredApexItems(now)
            self.RenderApexFeed(now)
            iconAnimationActive = bool(self.apexFeedItems)
        elif self.entryAnimationStartTime is not None:
            elapsed = now - self.entryAnimationStartTime
            progress = min(max(elapsed / self.ENTRY_DURATION, 0.0), 1.0)
            eased = 1.0 - (1.0 - progress) * (1.0 - progress) * (1.0 - progress)
            self.SetCanvasTransform(1.28 - 0.28 * eased, min(1.0, progress * 4.0))
            iconAnimationActive = progress < 1.0
            if not iconAnimationActive:
                self.entryAnimationStartTime = None
                self.ResetCanvas()
        textAnimationActive = False if self.style in ('pubg', 'apex') else self.UpdateTextPerformance(now)
        holdAnimationActive = bool(
            self.style not in self.SCROLL_STYLES and
            self.iconHoldUntil is not None and
            now < self.iconHoldUntil
        )
        queueHoldActive = bool(self.style in self.SCROLL_STYLES and self.queueIcons)
        pubgHoldActive = bool(self.style == 'pubg' and self.pubgFeedItems)
        apexHoldActive = bool(self.style == 'apex' and self.apexFeedItems)
        self.animationActive = bool(
            iconAnimationActive or
            textAnimationActive or
            holdAnimationActive or
            queueHoldActive or
            pubgHoldActive or
            apexHoldActive
        )
        if not self.animationActive and not self.queueIcons and self.style in self.SCROLL_STYLES:
            self.ResetKillState()
            self.SetPanelVisible(False)
        if not self.animationActive and self.style == 'pubg':
            self.pubgComboBirthTime = None
            self.HidePubgControls()
            self.ResetKillState()
            self.SetPanelVisible(False)
        if not self.animationActive and self.style == 'apex':
            self.HidePubgControls()
            self.ResetKillState()
            self.SetPanelVisible(False)
        if not self.animationActive and self.style == self.XIAOXIAO_WORLD_STYLE:
            self.SetVisible('XiaoXiaoWorld', False)
            self.SetVisible('XiaoXiaoWorldRightPlayerIcon', False)
            self.MovePaperDollControlsOffscreen((
                'XiaoXiaoWorldLeftDoll', 'XiaoXiaoWorldRightDoll',
            ))
        return self.animationActive

    def RemoveFadedScrollingIcons(self, now):
        remaining = []
        removed = False
        for icon in self.queueIcons:
            fadeStart = icon.get('ForcedFadeStartTime')
            if fadeStart is not None and now - fadeStart >= self.SCROLL_ANIMATION_DURATION:
                removed = True
                continue
            remaining.append(icon)
        if removed:
            self.queueIcons = remaining
            self.UpdateScrollingTargets(now)

    def IsScrollingAnimationActive(self, now):
        for icon in self.queueIcons:
            if now - float(icon.get('BirthTime', now)) < self.SCROLL_ANIMATION_DURATION:
                return True
            if now - float(icon.get('MoveStartTime', now)) < self.SCROLL_ANIMATION_DURATION:
                return True
            if icon.get('ForcedFadeStartTime') is not None:
                return True
        return False

    def RenderScrollingQueue(self, now):
        for index, ctrl in enumerate(self.queueControls):
            if not ctrl or index >= len(self.queueIcons):
                try:
                    if ctrl:
                        ctrl.SetVisible(False)
                except Exception:
                    pass
                continue
            icon = self.queueIcons[index]
            moveElapsed = max(0.0, now - float(icon.get('MoveStartTime', now)))
            moveProgress = min(moveElapsed / self.SCROLL_ANIMATION_DURATION, 1.0)
            moveEased = 1.0 - (1.0 - moveProgress) * (1.0 - moveProgress)
            previousX = float(icon.get('PreviousX', 0.0))
            targetX = float(icon.get('TargetX', previousX))
            currentX = previousX + (targetX - previousX) * moveEased
            icon['CurrentX'] = currentX
            birthElapsed = max(0.0, now - float(icon.get('BirthTime', now)))
            entryProgress = min(birthElapsed / self.SCROLL_ANIMATION_DURATION, 1.0)
            entryEased = 1.0 - (1.0 - entryProgress) * (1.0 - entryProgress) * (1.0 - entryProgress)
            scale = self.SCROLL_START_SCALE + (1.0 - self.SCROLL_START_SCALE) * entryEased
            alpha = entryEased
            fadeStart = icon.get('ForcedFadeStartTime')
            if fadeStart is not None:
                fadeProgress = min(max((now - fadeStart) / self.SCROLL_ANIMATION_DURATION, 0.0), 1.0)
                alpha *= 1.0 - fadeProgress
            self.ApplyQueueControl(ctrl, icon.get('Texture', ''), currentX, scale, alpha)

    def ApplyQueueControl(self, ctrl, texture, offsetX, scale, alpha):
        try:
            image = ctrl.asImage()
            if image and texture:
                image.SetSprite(texture)
            size = self.SCROLL_ICON_SIZE * self.layoutScale * max(0.01, float(scale))
            canvasSize = self.GetLayoutCanvasSize()
            if not isinstance(canvasSize, (list, tuple)) or len(canvasSize) < 2:
                canvasSize = (0.0, 0.0)
            centerX = float(canvasSize[0]) * 0.5
            centerY = float(canvasSize[1]) * 0.5
            ctrl.SetPosition((centerX + float(offsetX) - size * 0.5, centerY - size * 0.5))
            ctrl.SetSize((size, size))
            ctrl.SetAlpha(float(alpha))
            ctrl.SetVisible(float(alpha) > 0.001)
            return True
        except Exception:
            return False

    def ApplyXiaoXiaoWorldLayout(self, canvasWidth, canvasHeight):
        panel = self.controls.get('XiaoXiaoWorld')
        banner = self.controls.get('XiaoXiaoWorldBanner')
        leftDoll = self.controls.get('XiaoXiaoWorldLeftDoll')
        rightDoll = self.controls.get('XiaoXiaoWorldRightDoll')
        rightPlayerIcon = self.controls.get('XiaoXiaoWorldRightPlayerIcon')
        if not panel or not banner:
            return False
        bannerHeight = min(canvasHeight * 0.72, canvasWidth * 0.78 / self.XIAOXIAO_WORLD_ASPECT)
        bannerHeight = max(1.0, bannerHeight)
        bannerWidth = bannerHeight * self.XIAOXIAO_WORLD_ASPECT
        scaleX = bannerWidth / self.XIAOXIAO_WORLD_BASE_WIDTH
        scaleY = bannerHeight / self.XIAOXIAO_WORLD_BASE_HEIGHT
        headSize = self.XIAOXIAO_WORLD_HEAD_SIZE * min(scaleX, scaleY)
        dollSize = headSize * self.PAPER_DOLL_VIEWPORT_SCALE
        leftX = self.XIAOXIAO_WORLD_LEFT_HEAD_OFFSET[0] * scaleX
        leftY = self.XIAOXIAO_WORLD_LEFT_HEAD_OFFSET[1] * scaleY
        rightX = self.XIAOXIAO_WORLD_RIGHT_HEAD_OFFSET[0] * scaleX
        rightY = self.XIAOXIAO_WORLD_RIGHT_HEAD_OFFSET[1] * scaleY
        try:
            try:
                panel.SetAnchorFrom('top_left')
                panel.SetAnchorTo('top_left')
                banner.SetAnchorFrom('top_left')
                banner.SetAnchorTo('top_left')
                if leftDoll:
                    leftDoll.SetAnchorFrom('top_left')
                    leftDoll.SetAnchorTo('top_left')
                if rightDoll:
                    rightDoll.SetAnchorFrom('top_left')
                    rightDoll.SetAnchorTo('top_left')
                if rightPlayerIcon:
                    rightPlayerIcon.SetAnchorFrom('top_left')
                    rightPlayerIcon.SetAnchorTo('top_left')
            except Exception:
                pass
            basePosition = (
                (canvasWidth - bannerWidth) * 0.5,
                (canvasHeight - bannerHeight) * 0.5,
            )
            panel.SetPosition(basePosition)
            panel.SetSize((bannerWidth, bannerHeight))
            banner.SetPosition((0.0, 0.0))
            banner.SetSize((bannerWidth, bannerHeight))
            if leftDoll:
                leftDoll.SetPosition((
                    basePosition[0] + leftX - (dollSize - headSize) * 0.5,
                    basePosition[1] + leftY - (dollSize - headSize) * 0.5,
                ))
                leftDoll.SetSize((dollSize, dollSize))
            if rightDoll:
                rightDoll.SetPosition((
                    basePosition[0] + rightX - (dollSize - headSize) * 0.5,
                    basePosition[1] + rightY - (dollSize - headSize) * 0.5,
                ))
                rightDoll.SetSize((dollSize, dollSize))
            if rightPlayerIcon:
                rightPlayerIcon.SetPosition((rightX, rightY))
                rightPlayerIcon.SetSize((headSize, headSize))
            return True
        except Exception:
            return False

    def ApplyKingHonorLayout(self, canvasWidth, canvasHeight):
        panel = self.controls.get('KingHonor')
        banner = self.controls.get('KingHonorBanner')
        leftDoll = self.controls.get('KingHonorLeftDoll')
        rightDoll = self.controls.get('KingHonorRightDoll')
        rightPlayerIcon = self.controls.get('KingHonorRightPlayerIcon')
        if not panel or not banner:
            return False
        bannerHeight = min(canvasHeight * 0.64, canvasWidth * 0.60 / self.KING_HONOR_ASPECT)
        bannerHeight = max(1.0, bannerHeight)
        bannerWidth = bannerHeight * self.KING_HONOR_ASPECT
        scaleX = bannerWidth / self.KING_HONOR_BASE_WIDTH
        scaleY = bannerHeight / self.KING_HONOR_BASE_HEIGHT
        headSize = self.KING_HONOR_HEAD_SIZE * min(scaleX, scaleY)
        dollSize = headSize * self.PAPER_DOLL_VIEWPORT_SCALE
        leftX = self.KING_HONOR_LEFT_HEAD_OFFSET[0] * scaleX
        leftY = self.KING_HONOR_LEFT_HEAD_OFFSET[1] * scaleY
        rightX = self.KING_HONOR_RIGHT_HEAD_OFFSET[0] * scaleX
        rightY = self.KING_HONOR_RIGHT_HEAD_OFFSET[1] * scaleY
        try:
            try:
                panel.SetAnchorFrom('top_left')
                panel.SetAnchorTo('top_left')
                banner.SetAnchorFrom('top_left')
                banner.SetAnchorTo('top_left')
                if leftDoll:
                    leftDoll.SetAnchorFrom('top_left')
                    leftDoll.SetAnchorTo('top_left')
                if rightDoll:
                    rightDoll.SetAnchorFrom('top_left')
                    rightDoll.SetAnchorTo('top_left')
                if rightPlayerIcon:
                    rightPlayerIcon.SetAnchorFrom('top_left')
                    rightPlayerIcon.SetAnchorTo('top_left')
            except Exception:
                pass
            basePosition = (
                (canvasWidth - bannerWidth) * 0.5,
                (canvasHeight - bannerHeight) * 0.5,
            )
            panel.SetPosition(basePosition)
            panel.SetSize((bannerWidth, bannerHeight))
            self.kingHonorBasePosition = basePosition
            banner.SetPosition((0.0, 0.0))
            banner.SetSize((bannerWidth, bannerHeight))
            if leftDoll:
                leftDoll.SetPosition((
                    basePosition[0] + leftX - (dollSize - headSize) * 0.5,
                    basePosition[1] + leftY - (dollSize - headSize) * 0.5,
                ))
                leftDoll.SetSize((dollSize, dollSize))
            if rightDoll:
                rightDoll.SetPosition((
                    basePosition[0] + rightX - (dollSize - headSize) * 0.5,
                    basePosition[1] + rightY - (dollSize - headSize) * 0.5,
                ))
                rightDoll.SetSize((dollSize, dollSize))
            if rightPlayerIcon:
                rightPlayerIcon.SetPosition((rightX, rightY))
                rightPlayerIcon.SetSize((headSize, headSize))
            return True
        except Exception:
            return False

    def ApplyBigDogBarkLayout(self, canvasWidth, canvasHeight):
        ctrl = self.controls.get('BigDogBark')
        if not ctrl:
            return False
        imageSize = min(canvasHeight * 1.85, canvasWidth * 0.68)
        imageSize = max(1.0, imageSize)
        try:
            try:
                ctrl.SetAnchorFrom('center')
                ctrl.SetAnchorTo('center')
            except Exception:
                pass
            self.bigDogBarkBaseSize = float(imageSize)
            self.bigDogBarkBasePosition = (0.0, 0.0)
            ctrl.SetPosition(self.bigDogBarkBasePosition)
            ctrl.SetSize((imageSize, imageSize))
            return True
        except Exception:
            return False

    def GetGameplayHudScreenSize(self):
        if not self.isGameplayHud or not self.uiNode:
            return None
        try:
            reference = self.uiNode.GetBaseUIControl('/GamePanel')
            size = reference.GetSize() if reference else None
            if isinstance(size, (list, tuple)) and len(size) >= 2:
                width = float(size[0])
                height = float(size[1])
                if width > 1.0 and height > 1.0:
                    return (width, height)
        except Exception:
            pass
        return None

    def ApplyQinshouXianshengLayout(self, canvasWidth, canvasHeight):
        ctrl = self.controls.get('QinshouXiansheng')
        if not ctrl:
            return False
        imageSize = (max(1.0, canvasWidth), max(1.0, canvasHeight))
        if self.isGameplayHud:
            screenSize = self.GetGameplayHudScreenSize()
            if screenSize:
                imageSize = (
                    max(1.0, float(screenSize[0]) * self.layoutScale),
                    max(1.0, float(screenSize[1]) * self.layoutScale),
                )
            else:
                imageSize = (
                    max(1.0, canvasWidth),
                    max(1.0, canvasHeight / self.GAME_HUD_PANEL_HEIGHT_RATIO),
                )
        try:
            panel = self.uiNode.GetBaseUIControl(self.PANEL_PATH) if self.uiNode else None
            canvas = self.controls.get('Canvas')
            canvasSize = (canvasWidth, canvasHeight) if self.isGameplayHud else self.qinshouXianshengCanvasBaseSize
            if canvas and not self.isGameplayHud:
                try:
                    value = canvas.GetSize()
                    if isinstance(value, (list, tuple)) and len(value) >= 2:
                        liveSize = (float(value[0]), float(value[1]))
                        if (
                            liveSize[0] > 0.0 and liveSize[1] > 0.0 and
                            (not canvasSize or liveSize[1] < canvasSize[1])
                        ):
                            canvasSize = liveSize
                except Exception:
                    pass
            if panel and not self.isGameplayHud:
                fullPosition = {}
                for axis in ('x', 'y'):
                    try:
                        value = panel.GetFullPosition(axis)
                        if isinstance(value, dict):
                            fullPosition[axis] = dict(value)
                    except Exception:
                        pass
                try:
                    panel.SetAnchorFrom('top_left')
                    panel.SetAnchorTo('center')
                except Exception:
                    pass
                try:
                    panel.SetSize(imageSize, False)
                except TypeError:
                    panel.SetSize(imageSize)
                except Exception:
                    pass
                for axis, value in fullPosition.items():
                    try:
                        panel.SetFullPosition(axis, value)
                    except Exception:
                        pass
            if not self.isGameplayHud:
                self.ApplyPanelLayer()
                for container in (panel, canvas):
                    if container:
                        try:
                            container.SetClipsChildren(False)
                        except Exception:
                            pass
            try:
                ctrl.SetAnchorFrom('center')
                ctrl.SetAnchorTo('center')
            except Exception:
                pass
            if not self.isGameplayHud:
                try:
                    ctrl.SetLayer(self.QINSHOU_XIANSHENG_LAYER)
                except Exception:
                    pass
            self.qinshouXianshengBaseSize = imageSize
            if canvasSize and canvasSize[0] > 0.0 and canvasSize[1] > 0.0:
                self.qinshouXianshengBasePosition = (
                    -max(0.0, imageSize[0] - canvasSize[0]) * 0.5,
                    -max(0.0, imageSize[1] - canvasSize[1]) * 0.5,
                )
            else:
                self.qinshouXianshengBasePosition = (0.0, 0.0)
            ctrl.SetPosition(self.qinshouXianshengBasePosition)
            self.SetQinshouXianshengSize(ctrl, 1.0)
            return True
        except Exception:
            return False

    def ApplyStyleLayout(self):
        canvas = self.controls.get('Canvas')
        if not canvas:
            return False
        canvasSize = self.GetLayoutCanvasSize()
        if not isinstance(canvasSize, (list, tuple)) or len(canvasSize) < 2:
            return False
        canvasWidth = float(canvasSize[0])
        canvasHeight = float(canvasSize[1])
        if canvasWidth <= 0 or canvasHeight <= 0:
            return False
        if self.style == self.KING_HONOR_STYLE:
            return self.ApplyKingHonorLayout(canvasWidth, canvasHeight)
        if self.style == self.XIAOXIAO_WORLD_STYLE:
            return self.ApplyXiaoXiaoWorldLayout(canvasWidth, canvasHeight)
        if self.style == self.BIG_DOG_BARK_STYLE:
            return self.ApplyBigDogBarkLayout(canvasWidth, canvasHeight)
        if self.style == self.QINSHOU_XIANSHENG_STYLE:
            return self.ApplyQinshouXianshengLayout(canvasWidth, canvasHeight)
        if self.style == self.CUPPING_CAT_STYLE:
            ctrl = self.controls.get('CuppingCat')
            if not ctrl:
                return False
            imageSize = min(canvasHeight * 2.2, canvasWidth * 0.85)
            try:
                ctrl.SetSize((imageSize, imageSize))
                return True
            except Exception:
                return False
        if self.style == 'battlefield1':
            if self.battlefield1Current:
                self.RenderBattlefield1(time.time())
            return True
        if self.style == 'cod':
            return self.ApplyCodTextLayout(canvasWidth, canvasHeight)
        if self.style == 'apex':
            if self.apexFeedItems:
                self.RenderApexFeed(time.time())
            return True
        if self.style == 'pubg':
            if self.pubgFeedItems:
                self.RenderPubgFeed(time.time())
            return True
        cfIconBottom = None
        if self.style == 'cf_combo':
            primary = self.controls.get('Primary')
            if primary:
                iconSize = min(canvasHeight * 0.64, canvasWidth * 0.36)
                iconTop = canvasHeight * 0.04
                try:
                    # CF is rendered inside a full-width Canvas.  Keep the
                    # icon in the Canvas' top-left coordinate space and set
                    # its anchor position explicitly every time.  Reusing a
                    # previous SetPosition offset here makes the icon inherit
                    # the parent center offset on some HUD scales, which is
                    # perceived as an unexplained shift to the right after
                    # changing the layout center.
                    try:
                        primary.SetAnchorFrom('top_left')
                        primary.SetAnchorTo('top_left')
                    except Exception:
                        pass
                    primary.SetSize((iconSize, iconSize))
                    resultX = primary.SetFullPosition('x', {
                        'followType': 'parent',
                        'relativeValue': 0.5,
                        'absoluteValue': -iconSize * 0.5,
                    })
                    resultY = primary.SetFullPosition('y', {
                        'followType': 'parent',
                        'relativeValue': 0.04,
                        'absoluteValue': 0.0,
                    })
                    if resultX is False or resultY is False:
                        raise ValueError('CF icon SetFullPosition failed')
                    cfIconBottom = iconTop + iconSize
                except Exception:
                    try:
                        primary.SetPosition(((canvasWidth - iconSize) * 0.5, iconTop))
                    except Exception:
                        pass
        textPanel = self.controls.get('TextPerformance')
        if not textPanel or self.style == 'valorant':
            return True
        textWidth = canvasWidth * 0.90
        textHeight = self.TEXT_BASE_HEIGHT * self.layoutScale
        if self.style == 'cf_combo':
            textY = (cfIconBottom if cfIconBottom is not None else canvasHeight * 0.68) + 4.0 * self.layoutScale
        elif self.style == 'pubg':
            textY = (canvasHeight - textHeight) * 0.5
        else:
            textY = canvasHeight * 0.5 + self.SCROLL_ICON_SIZE * self.layoutScale * 0.55
        try:
            if self.style == 'cf_combo':
                textHeight = self.CF_COMBO_TEXT_HEIGHT * self.layoutScale
            textPanel.SetSize((textWidth, textHeight))
            if self.style == 'cf_combo':
                try:
                    textPanel.SetAnchorFrom('top_left')
                    textPanel.SetAnchorTo('top_left')
                except Exception:
                    pass
                resultX = textPanel.SetFullPosition('x', {
                    'followType': 'parent',
                    'relativeValue': 0.5,
                    'absoluteValue': -textWidth * 0.5,
                })
                resultY = textPanel.SetFullPosition('y', {
                    'followType': 'parent',
                    'relativeValue': 0.0,
                    'absoluteValue': textY,
                })
                if resultX is False or resultY is False:
                    raise ValueError('CF text SetFullPosition failed')
            else:
                textPanel.SetPosition(((canvasWidth - textWidth) * 0.5, textY))
            self.ApplyTextLineLayout(textWidth)
            return True
        except Exception:
            try:
                textPanel.SetPosition(((canvasWidth - textWidth) * 0.5, textY))
                self.ApplyTextLineLayout(textWidth)
                return True
            except Exception:
                return False

    def ApplyTextLineLayout(self, textWidth):
        applied = False
        colors = {
            'Main': (1.0, 1.0, 1.0),
            'Detail': (0.82, 0.86, 0.9),
            'Score': (0.96, 0.77, 0.22),
        }
        for name, layout in self.TEXT_LINE_LAYOUTS.items():
            ctrl = self.controls.get(name)
            if not ctrl:
                continue
            offsetY, height, fontScale = layout
            if self.style == 'cf_combo' and name == 'Score':
                height = self.CF_COMBO_SCORE_HEIGHT
            try:
                ctrl.SetPosition((0.0, offsetY * self.layoutScale))
                ctrl.SetSize((float(textWidth), height * self.layoutScale))
                label = ctrl.asLabel()
                if label:
                    label.SetTextFontSize(fontScale * self.layoutScale)
                    label.SetTextColor(colors.get(name, (1.0, 1.0, 1.0)))
                    label.SetTextAlignment('center')
                applied = True
            except Exception:
                pass
        return applied

    def ApplyCodTextLayout(self, canvasWidth, canvasHeight):
        textPanel = self.controls.get('TextPerformance')
        xpControl = self.controls.get('Main')
        detailControl = self.controls.get('Detail')
        scoreControl = self.controls.get('Score')
        if not textPanel or not xpControl or not detailControl:
            return False
        scale = self.layoutScale
        panelWidth = self.COD_PANEL_WIDTH * scale
        panelHeight = self.COD_PANEL_HEIGHT * scale
        panelX = (float(canvasWidth) - panelWidth) * 0.5
        panelY = (float(canvasHeight) - panelHeight) * 0.5
        xpWidth = self.COD_XP_WIDTH * scale
        textX = xpWidth + self.COD_TEXT_GAP * scale
        textWidth = max(1.0, panelWidth - textX)
        try:
            textPanel.SetSize((panelWidth, panelHeight))
            textPanel.SetPosition((panelX, panelY))
            xpControl.SetPosition((0.0, 9.0 * scale))
            xpControl.SetSize((xpWidth, 22.0 * scale))
            detailControl.SetPosition((textX, 0.0))
            detailControl.SetSize((textWidth, panelHeight))
            if scoreControl:
                scoreControl.SetVisible(False)
            xpLabel = xpControl.asLabel()
            detailLabel = detailControl.asLabel()
            if xpLabel:
                xpLabel.SetTextFontSize(1.25 * scale)
                xpLabel.SetTextColor(self.COD_COLOR)
                xpLabel.SetTextAlignment('right')
            if detailLabel:
                detailLabel.SetTextFontSize(self.GetCodDetailFontSize() * scale)
                detailLabel.SetTextColor(self.COD_COLOR)
                detailLabel.SetTextAlignment('left')
            return True
        except Exception:
            return False

    def GetCodDetailFontSize(self):
        lengths = [len(value) for value in self.codTextLines if value]
        longest = max(lengths) if lengths else 1
        ratio = min(1.0, self.COD_DETAIL_REFERENCE_LENGTH / float(longest))
        return max(self.COD_DETAIL_MIN_FONT_SIZE, self.COD_DETAIL_FONT_SIZE * ratio)

    def GetCodComboText(self, count):
        values = self.COD_COMBO_TEXTS.get(count)
        if values:
            return self.PickCodText(values)
        if count > 5:
            return self.PickCodText(self.COD_HIGH_COMBO_TEXTS) % count
        return u''

    def PickCodText(self, values, fallback=u''):
        if not values:
            return fallback
        try:
            return random.choice(values)
        except Exception:
            return values[0]

    def BuildCodTextLines(self, count, headshot=False):
        if headshot:
            mainText = self.PickCodText(self.COD_HEADSHOT_TEXTS, u'\u7206\u5934\u51fb\u6740')
            rewardText = u'\u7206\u5934\u5956\u52b1 x%d' % self.COD_HEADSHOT_MULTIPLIER
        else:
            mainText = self.PickCodText(self.COD_KILL_TEXTS, u'\u51fb\u6740\u654c\u4eba')
            rewardText = self.PickCodText(self.COD_REWARD_TEXTS, u'\u51fb\u6740\u5f97\u5206')
        comboText = self.GetCodComboText(int(count))
        middleText = comboText or rewardText
        source = self.GetStyleOption('TauntSource', COD_TAUNT_SOURCE_JIAHAO_CHARCOAL)
        tauntText = self.PickCodText(GetCodTauntPool(source))
        return tuple(value for value in (mainText, middleText, tauntText) if value)

    def ApplyCodLineMotion(self, elapsed):
        xpControl = self.controls.get('Main')
        detailControl = self.controls.get('Detail')
        scale = self.layoutScale
        dataRows = (
            (xpControl, 0.0, 9.0, -10.0),
            (detailControl, self.COD_XP_WIDTH + self.COD_TEXT_GAP, 0.0, 8.0),
        )
        for index, data in enumerate(dataRows):
            ctrl, baseX, baseY, entryX = data
            if not ctrl:
                continue
            progress = min(max(
                (float(elapsed) - index * self.COD_LINE_STAGGER) / self.COD_ENTRY_DURATION,
                0.0,
            ), 1.0)
            eased = 1.0 - (1.0 - progress) ** 3
            try:
                ctrl.SetPosition(((baseX + entryX * (1.0 - eased)) * scale, baseY * scale))
                ctrl.SetAlpha(eased)
            except Exception:
                pass
        return True

    def ApplyTextLineMotion(self, elapsed):
        fadeOutStart = self.TEXT_FADE_IN_DURATION + self.TEXT_HOLD_DURATION
        exitProgress = min(max(
            (float(elapsed) - fadeOutStart) / self.TEXT_FADE_OUT_DURATION,
            0.0
        ), 1.0)
        exitEased = exitProgress * exitProgress
        applied = False
        for index, name in enumerate(self.TEXT_LINE_ORDER):
            ctrl = self.controls.get(name)
            layout = self.TEXT_LINE_LAYOUTS.get(name)
            if not ctrl or not layout:
                continue
            entryProgress = min(max(
                (float(elapsed) - index * self.TEXT_LINE_STAGGER) / self.TEXT_MOVE_IN_DURATION,
                0.0
            ), 1.0)
            entryEased = 1.0 - (1.0 - entryProgress) ** 3
            entryOffset = self.TEXT_LINE_ENTRY_OFFSETS.get(name, (0.0, 0.0))
            exitOffset = self.TEXT_LINE_EXIT_OFFSETS.get(name, (0.0, 0.0))
            x = (
                float(entryOffset[0]) * (1.0 - entryEased) +
                float(exitOffset[0]) * exitEased
            ) * self.layoutScale
            y = (
                float(layout[0]) +
                float(entryOffset[1]) * (1.0 - entryEased) +
                float(exitOffset[1]) * exitEased
            ) * self.layoutScale
            try:
                ctrl.SetPosition((x, y))
                ctrl.SetAlpha(entryEased)
                applied = True
            except Exception:
                pass
        return applied

    def GetDistanceText(self):
        if self.killDistance is None:
            return u''
        return u'\u8ddd\u79bb %.1f\u7c73' % float(self.killDistance)

    def JoinTextParts(self, parts):
        return u'  |  '.join([self.ToText(part) for part in parts if part])

    def PlayTextPerformance(self, previousScore, targetScore):
        if (
            self.style in ('valorant', 'pubg') or
            self.style == 'battlefield1' or
            not self.controls.get('TextPerformance')
        ):
            self.HideTextPerformance()
            return False
        self.textScoreStart = int(previousScore)
        self.textScoreTarget = int(targetScore)
        self.textAnimationStartTime = time.time()
        self.RefreshTextPerformance(self.textScoreStart)
        self.SetVisible('TextPerformance', True)
        self.SetTextPerformanceAlpha(0.0)
        self.ApplyStyleLayout()
        if self.style == 'cod':
            self.ApplyCodLineMotion(0.0)
        else:
            self.ApplyTextLineMotion(0.0)
        self.animationActive = True
        self.SetPanelVisible(True)
        return True

    def RefreshTextPerformance(self, displayScore=None):
        count = max(1, int(self.totalKills))
        weapon = self.weaponName
        target = self.targetName
        if displayScore is None:
            displayScore = self.textScoreTarget
        main = u''
        detail = u''
        score = u''
        distanceText = self.GetDistanceText()
        killTypeText = u'\u7206\u5934' if self.lastHeadshot else u'\u666e\u901a\u51fb\u6740'
        if self.style == 'cod':
            main = u'+%d XP' % int(displayScore)
            if not self.codTextLines:
                self.codTextLines = self.BuildCodTextLines(count, self.lastHeadshot)
            detail = u'\n'.join(self.codTextLines)
        elif self.style == 'cf_combo':
            main = u'\u8fde\u7eed\u51fb\u6740 x%d' % count
            if self.GetStyleOption('ShowDetails', True):
                detail = u'\u51fb\u6740 %s  [%s]' % (target, weapon)
                scoreDetails = [u'\u5f97\u5206 +%d' % self.lastKillScore]
                if self.GetStyleOption('ShowDistance', True) and distanceText:
                    scoreDetails.append(distanceText)
                score = u'\n'.join((
                    killTypeText,
                    self.JoinTextParts(scoreDetails),
                ))
        elif self.style == 'pubg':
            self.HideTextPerformance()
            return False
        elif self.style == 'battlefield5':
            main = u'\u51fb\u6740 %s  [%s]  +%d' % (target, weapon, self.lastKillScore)
            detailParts = []
            if self.GetStyleOption('ShowScoreDetails', True):
                detailParts.append(
                    (u'\u7206\u5934\u51fb\u6740' if self.lastHeadshot else u'\u51fb\u6740\u786e\u8ba4') +
                    u' +%d' % self.lastKillScore
                )
                score = u'\u603b\u5f97\u5206 %d' % int(displayScore)
            if self.GetStyleOption('ShowDistance', True):
                detailParts.append(distanceText)
            detail = self.JoinTextParts(detailParts)
        elif self.style in ('delta_force', self.OLD_PRIEST_STYLE):
            main = u'\u6dd8\u6c70 %s' % target
            detail = u'\u7206\u5934\u6dd8\u6c70' if self.lastHeadshot else u'\u666e\u901a\u6dd8\u6c70'
        else:
            self.HideTextPerformance()
            return False
        textValues = {'Main': main, 'Detail': detail, 'Score': score}
        for name, value in textValues.items():
            self.SetLabel(name, value)
            self.SetVisible(name, bool(value))
        self.ApplyStyleLayout()
        return True

    def UpdateTextPerformance(self, now):
        if self.textAnimationStartTime is None:
            return False
        elapsed = max(0.0, now - self.textAnimationStartTime)
        fadeOutStart = self.TEXT_FADE_IN_DURATION + self.TEXT_HOLD_DURATION
        totalDuration = fadeOutStart + self.TEXT_FADE_OUT_DURATION
        if elapsed < self.TEXT_FADE_IN_DURATION:
            progress = elapsed / self.TEXT_FADE_IN_DURATION
            alpha = 1.0 - (1.0 - progress) * (1.0 - progress) * (1.0 - progress)
        elif elapsed < fadeOutStart:
            alpha = 1.0
        elif elapsed < totalDuration:
            alpha = 1.0 - (elapsed - fadeOutStart) / self.TEXT_FADE_OUT_DURATION
        else:
            self.textAnimationStartTime = None
            self.HideTextPerformance()
            return False
        scoreProgress = min(elapsed / self.TEXT_SCORE_ROLL_DURATION, 1.0)
        scoreProgress = 1.0 - (1.0 - scoreProgress) * (1.0 - scoreProgress)
        displayScore = int(round(self.textScoreStart + (self.textScoreTarget - self.textScoreStart) * scoreProgress))
        if self.style == 'battlefield5':
            self.RefreshTextPerformance(displayScore)
        if self.style == 'cod':
            self.ApplyCodLineMotion(elapsed)
        else:
            self.ApplyTextLineMotion(elapsed)
        self.SetTextPerformanceAlpha(alpha)
        return True

    def HideTextPerformance(self):
        self.textAnimationStartTime = None
        self.SetVisible('TextPerformance', False)
        self.SetTextPerformanceAlpha(0.0)

    def SetTextPerformanceAlpha(self, alpha):
        ctrl = self.controls.get('TextPerformance')
        if not ctrl:
            return False
        try:
            ctrl.SetAlpha(float(alpha))
            return True
        except Exception:
            return False

    def GetLabelTextValue(self, name):
        ctrl = self.controls.get(name)
        return bool(ctrl)

    def SetVisible(self, name, visible):
        ctrl = self.controls.get(name)
        if not ctrl:
            return False
        try:
            ctrl.SetVisible(bool(visible))
            return True
        except Exception:
            return False

    def SetImage(self, name, texture):
        ctrl = self.controls.get(name)
        image = ctrl.asImage() if ctrl else None
        if not image:
            return False
        try:
            image.SetSprite(texture)
            return True
        except Exception:
            return False

    def SetLabel(self, name, text):
        ctrl = self.controls.get(name)
        label = ctrl.asLabel() if ctrl else None
        if not label:
            return False
        try:
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

    def PlaySound(self):
        count = min(max(int(self.totalKills), 1), 6)
        soundName = None
        soundPitch = 1.0
        if self.style == 'cf_combo':
            count = min(count, int(self.GetStyleOption('MaxCombo', 6)))
            soundName = 'killbroadcast.kill.cf.%d' % count
        elif self.style == 'cod':
            soundName = 'killbroadcast.kill.cod'
        elif self.style == 'apex':
            suffix = '.headshot' if self.lastHeadshot else ''
            soundName = 'killbroadcast.kill.apex%s' % suffix
        elif self.style == self.OLD_PRIEST_STYLE:
            soundName = 'killbroadcast.kill.old_priest.%d' % random.randint(
                1, self.OLD_PRIEST_SOUND_COUNT
            )
        elif self.style in ('battlefield1', 'battlefield5', 'delta_force'):
            suffix = '.headshot' if self.lastHeadshot else ''
            soundName = 'killbroadcast.kill.%s%s' % (self.style, suffix)
        elif self.style == 'valorant':
            soundName = 'killbroadcast.kill.valorant.%d' % min(count, 5)
        elif self.style == self.KING_HONOR_STYLE:
            soundName = 'killbroadcast.kill.king_honor.%d' % count
        elif self.style == self.XIAOXIAO_WORLD_STYLE:
            soundName = 'killbroadcast.kill.xiaoxiao_world.%d' % min(count, 6)
        elif self.style == self.CUPPING_CAT_STYLE:
            soundName = 'killbroadcast.kill.cupping_cat.%d' % min(count, 5)
        elif self.style == self.BIG_DOG_BARK_STYLE:
            soundName = 'killbroadcast.kill.big_dog_bark.%d' % min(count, 5)
        elif self.style == self.QINSHOU_XIANSHENG_STYLE:
            soundName = 'killbroadcast.kill.qinshou_xiansheng'
            soundPitch = random.uniform(*self.GetQinshouXianshengPitchRange())
        if not soundName:
            return False
        try:
            if self.style == self.QINSHOU_XIANSHENG_STYLE:
                AudioComp.StopCustomMusic(soundName, 0.0)
            AudioComp.PlayCustomUIMusic(soundName, 1.0, soundPitch, False)
            if self.style == 'valorant' and self.lastHeadshot:
                AudioComp.PlayCustomUIMusic('killbroadcast.kill.valorant.headshot', 1.0, 1.0, False)
            elif self.style == 'cod' and self.lastHeadshot:
                AudioComp.PlayCustomUIMusic('killbroadcast.kill.cod.headshot', 1.0, 1.0, False)
            return True
        except Exception as e:
            print('KillBroadcast play gd656 kill effect sound error:', soundName, e)
            return False

    def StopQinshouXianshengSound(self):
        try:
            AudioComp.StopCustomMusic(
                'killbroadcast.kill.qinshou_xiansheng', 0.0)
            return True
        except Exception:
            return False

    def PlayEntryAnimation(self):
        canvas = self.controls.get('Canvas')
        if not canvas:
            return False
        self.entryAnimationStartTime = time.time()
        self.animationActive = True
        self.SetCanvasTransform(1.28, 0.0)
        return True

    def SetCanvasTransform(self, scale, alpha):
        canvas = self.controls.get('Canvas')
        if not canvas:
            return False
        try:
            self.canvasAnimationAlpha = min(max(float(alpha), 0.0), 1.0)
            canvas.SetFullSize('x', {'followType': 'parent', 'relativeValue': float(scale)})
            canvas.SetFullSize('y', {'followType': 'parent', 'relativeValue': float(scale)})
            canvas.SetAlpha(self.canvasAnimationAlpha * self.layoutAlpha)
            return True
        except Exception:
            return False

    def ResetCanvas(self):
        return self.SetCanvasTransform(1.0, 1.0)

    def CancelAnimation(self):
        self.entryAnimationStartTime = None
        self.iconHoldUntil = None
        self.textAnimationStartTime = None
        self.cuppingCatAnimationStartTime = None
        self.cuppingCatFrameIndex = -1
        self.cuppingCatStage = 0
        self.kingHonorAnimationStartTime = None
        self.kingHonorBasePosition = None
        self.bigDogBarkAnimationStartTime = None
        self.qinshouXianshengAnimationStartTime = None
        kingHonor = self.controls.get('KingHonor')
        if kingHonor:
            try:
                kingHonor.SetAlpha(1.0)
            except Exception:
                pass
        bigDogBark = self.controls.get('BigDogBark')
        if bigDogBark:
            try:
                bigDogBark.SetAlpha(1.0)
                bigDogBark.SetPosition(self.bigDogBarkBasePosition)
            except Exception:
                pass
        qinshouXiansheng = self.controls.get('QinshouXiansheng')
        if qinshouXiansheng:
            try:
                self.ResetQinshouXianshengControl(qinshouXiansheng)
            except Exception:
                pass
        self.animationActive = False
