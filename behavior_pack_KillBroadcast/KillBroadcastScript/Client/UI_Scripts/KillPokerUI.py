# -*- coding: utf-8 -*-
import time
import mod.client.extraClientApi as clientApi

GameComp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())


class KillPokerUI(object):
    EFFECT_BASE_LENGTH = 5.2
    EFFECT_WIDTH = 1.0
    EFFECT_DURATION = 1.0
    EFFECT_GROW_DURATION = 0.2
    EFFECT_SHRINK_START = 0.8
    EFFECT_TICK = 0.03

    def __init__(self, ui_namespace='KillBroadcast', ui_name='Game', card_count=5, step_angle=22.0, base_angle=0.0, max_spread=140.0):
        self.ns = ui_namespace
        self.ui = ui_name
        self.card_count = int(card_count)
        self.step_angle = float(step_angle)
        self.base_angle = float(base_angle)
        self.max_spread = float(max_spread)
        self.root_pivot = (0.5, 1.0)
        self.parent_aspect = 1.0 / 1.38
        self.path_tpl = {
            'around': '/KillPanel/Team/circle/poker_kill_bar/{i}',
            'bone_1': '/KillPanel/Team/circle/poker_kill_bar/{i}/bone_1',
            'count': '/KillPanel/Team/circle/poker_kill_bar/{i}/count',
            'bone_2': '/KillPanel/Team/circle/poker_kill_bar/{i}/bone_2',
            'bg': '/KillPanel/Team/circle/poker_kill_bar/{i}/bg',
            'effect': '/KillPanel/Team/circle/poker_kill_bar/{i}/effect',
            'count_label': '/KillPanel/Team/circle/poker_kill_bar/1/count_label',
        }
        self.spr_bone = 'textures/ui/killbroadcast_csgo_map_ui/Game_UI/bones/bone'
        self.spr_bone_u = 'textures/ui/killbroadcast_csgo_map_ui/Game_UI/bones/upsidedown_bone'
        self.spr_shoted = 'textures/ui/killbroadcast_csgo_map_ui/Game_UI/bones/shoted_bone'
        self.spr_shoted_u = 'textures/ui/killbroadcast_csgo_map_ui/Game_UI/bones/upsidedown_shoted_bone'
        self.ready = False
        self.cards = []
        self.pivots = []
        self.angles_cache = {}
        self.kill_flags = []
        self.total_kills = 0
        self.last_headshot = False
        self.trail_length = 1.0
        self.effect_timers = {}

    def _get_ui(self):
        return clientApi.GetUI(self.ns, self.ui)

    def _safe_dict(self, value):
        if isinstance(value, dict):
            return value
        return {'absoluteValue': 0.0, 'relativeValue': 0.0, 'followType': 'parent'}

    def _rel_pos_ratio(self, base_ctrl, axis):
        info = self._safe_dict(base_ctrl.GetFullPosition(axis=axis))
        return float(info.get('relativeValue', 0.0))

    def _rel_size_x_ratio(self, base_ctrl):
        info = self._safe_dict(base_ctrl.GetFullSize(axis='x'))
        return float(info.get('relativeValue', 0.0))

    def _rel_size_y_ratio(self, base_ctrl):
        info = self._safe_dict(base_ctrl.GetFullSize(axis='y'))
        follow_type = info.get('followType', 'parent')
        relative_value = float(info.get('relativeValue', 0.0))
        if follow_type == 'x':
            return relative_value * self._rel_size_x_ratio(base_ctrl) * self.parent_aspect
        return relative_value

    def _calc_child_pivot(self, child_base_ctrl):
        cx = self._rel_pos_ratio(child_base_ctrl, 'x')
        cy = self._rel_pos_ratio(child_base_ctrl, 'y')
        cw = self._rel_size_x_ratio(child_base_ctrl)
        ch = self._rel_size_y_ratio(child_base_ctrl)
        px = 0.5 if cw == 0.0 else (self.root_pivot[0] - cx) / cw
        py = 0.5 if ch == 0.0 else (self.root_pivot[1] - cy) / ch
        return (px, py)

    def _set_visible(self, ctrl, visible):
        try:
            if ctrl:
                ctrl.SetVisible(bool(visible))
        except Exception:
            pass

    def _set_label_text(self, label_ctrl, text):
        if label_ctrl is None:
            return
        try:
            label_ctrl.SetText(str(text))
        except Exception:
            pass

    def SetTrailLength(self, value):
        try:
            value = float(value)
        except Exception:
            value = 1.0
        self.trail_length = max(0.5, min(2.0, value))

    def Init(self):
        ui_node = self._get_ui()
        if ui_node is None:
            self.ready = False
            return False

        self.cards = []
        self.pivots = []
        self.angles_cache = {}

        for i in range(1, self.card_count + 1):
            one = {}
            piv = {}
            around_base = ui_node.GetBaseUIControl(self.path_tpl['around'].format(i=i))
            one['around'] = around_base.asImage() if around_base else None
            keys = ('bone_1', 'count', 'bone_2', 'bg', 'effect') if i == 1 else ('bone_1', 'bg')
            for key in keys:
                base = ui_node.GetBaseUIControl(self.path_tpl[key].format(i=i))
                one[key] = base.asImage() if base else None
                piv[key] = self.root_pivot if key in ('bg', 'effect') else (self._calc_child_pivot(base) if base else (0.5, 0.5))
            self.cards.append(one)
            self.pivots.append(piv)

        label_base = ui_node.GetBaseUIControl(self.path_tpl['count_label'])
        label_ctrl = None
        if label_base:
            try:
                label_ctrl = label_base.asLabel()
            except Exception:
                label_ctrl = label_base
        if self.cards:
            self.cards[0]['count_label'] = label_ctrl

        self.ready = True
        return True

    def _get_angles(self, show):
        show = int(show)
        if show in self.angles_cache:
            return self.angles_cache[show]
        if show <= 0:
            angles = []
        elif show == 1:
            angles = [self.base_angle]
        else:
            step = min(self.step_angle, self.max_spread / float(show - 1))
            mid = (show - 1) / 2.0
            angles = [self.base_angle + (float(idx) - mid) * step for idx in range(show)]
        self.angles_cache[show] = angles
        return angles

    def AddKill(self, is_headshot):
        if not self.ready and not self.Init():
            return
        self.total_kills += 1
        self.last_headshot = bool(is_headshot)
        if len(self.kill_flags) >= self.card_count:
            self.kill_flags.pop(0)
        self.kill_flags.append(self.last_headshot)
        self.Refresh()

    def Clear(self):
        self.kill_flags = []
        self.total_kills = 0
        self.last_headshot = False
        self._cancel_effect_timers()
        if not self.ready and not self.Init():
            return
        self.Refresh()

    def _cancel_effect_timers(self):
        for timer in list(self.effect_timers.values()):
            try:
                GameComp.CancelTimer(timer)
            except Exception:
                pass
        self.effect_timers = {}

    def _apply_bone_sprite(self, card, headshot):
        spr1 = self.spr_shoted if headshot else self.spr_bone
        spr2 = self.spr_shoted_u if headshot else self.spr_bone_u
        for key, sprite in (('bone_1', spr1), ('bone_2', spr2)):
            image = card.get(key)
            if image:
                try:
                    image.SetSprite(sprite)
                except Exception:
                    pass

    def _play_effect(self, effect):
        if not effect:
            return
        try:
            effect.StopAnimation()
        except Exception:
            pass
        try:
            effect.PlayAnimation()
        except Exception:
            pass
        self._start_effect_size_override(effect)

    def _start_effect_size_override(self, effect):
        key = id(effect)
        oldTimer = self.effect_timers.pop(key, None)
        if oldTimer is not None:
            try:
                GameComp.CancelTimer(oldTimer)
            except Exception:
                pass
        startTime = time.time()

        def update_size():
            elapsed = time.time() - startTime
            if elapsed >= self.EFFECT_DURATION:
                self.effect_timers.pop(key, None)
                try:
                    GameComp.CancelTimer(timer)
                except Exception:
                    pass
                self._set_effect_size(effect, 0.0)
                return
            if elapsed < self.EFFECT_GROW_DURATION:
                factor = elapsed / self.EFFECT_GROW_DURATION
            elif elapsed > self.EFFECT_SHRINK_START:
                factor = max(0.0, 1.0 - (elapsed - self.EFFECT_SHRINK_START) / (self.EFFECT_DURATION - self.EFFECT_SHRINK_START))
            else:
                factor = 1.0
            self._set_effect_size(effect, factor)

        self._set_effect_size(effect, 0.0)
        try:
            timer = GameComp.AddRepeatedTimer(self.EFFECT_TICK, update_size)
            self.effect_timers[key] = timer
        except Exception:
            self._set_effect_size(effect, 1.0)

    def _set_effect_size(self, effect, factor):
        try:
            effect.SetFullSize('x', {'followType': 'parent', 'relativeValue': self.EFFECT_WIDTH})
            effect.SetFullSize('y', {'followType': 'parent', 'relativeValue': self.EFFECT_BASE_LENGTH * self.trail_length * factor})
        except Exception:
            pass

    def _render_overflow(self):
        for index, card in enumerate(self.cards, 1):
            self._set_visible(card.get('around'), index == 1)
        if not self.cards:
            return
        card = self.cards[0]
        piv = self.pivots[0] if self.pivots else {}
        around = card.get('around')
        if around:
            around.SetRotatePivot(self.root_pivot)
            around.Rotate(self.base_angle)
        self._set_visible(card.get('count'), False)
        self._set_visible(card.get('count_label'), True)
        self._set_label_text(card.get('count_label'), self.total_kills)
        for key in ('bone_1', 'count', 'bone_2', 'bg', 'effect'):
            image = card.get(key)
            if not image:
                continue
            image.SetRotatePivot(piv.get(key, (0.5, 0.5)))
            image.Rotate(self.base_angle)
        self._apply_bone_sprite(card, self.last_headshot)
        self._play_effect(card.get('effect'))

    def _render_normal(self):
        show = min(max(len(self.kill_flags), 0), self.card_count)
        angles = self._get_angles(show)
        if self.cards:
            self._set_visible(self.cards[0].get('count_label'), False)
            self._set_visible(self.cards[0].get('count'), True)
        for i in range(1, self.card_count + 1):
            card = self.cards[i - 1]
            around = card.get('around')
            if not around:
                continue
            visible = i <= show
            around.SetVisible(visible)
            if not visible:
                continue
            angle = angles[i - 1] if i - 1 < len(angles) else self.base_angle
            around.SetRotatePivot(self.root_pivot)
            around.Rotate(angle)
            piv = self.pivots[i - 1]
            keys = ('bone_1', 'count', 'bone_2', 'bg', 'effect') if i == 1 else ('bone_1', 'bg')
            for key in keys:
                image = card.get(key)
                if not image:
                    continue
                image.SetRotatePivot(piv.get(key, (0.5, 0.5)))
                image.Rotate(angle)
            self._apply_bone_sprite(card, self.kill_flags[show - i])
            if i == 1:
                count = card.get('count')
                if count:
                    try:
                        count.SetSprite('textures/ui/killbroadcast_number/%d' % int(show))
                    except Exception:
                        pass
                self._play_effect(card.get('effect'))

    def Refresh(self):
        if not self.ready and not self.Init():
            return
        if int(self.total_kills) > self.card_count:
            self._render_overflow()
        else:
            self._render_normal()
