# KillBroadcast 开发者接入指南

本文是第三方网易《我的世界》ModSDK 模组接入 KillBroadcast 的起点。普通武器模组、自定义伤害模组和自行接管死亡动画的模组，请先根据下面的场景选择接入方式，再阅读完整 API 参考。

> API 版本：`1`；运行侧：服务端 Python 2.7；服务系统：`KillBroadcast` / `KillBroadcastServerSystem`

## 先选择你的接入场景

| 场景 | 推荐接入方式 |
| --- | --- |
| 使用原生伤害、投射物和死亡流程 | 通常无需额外处理，KillBroadcast 会自动识别攻击者和武器 |
| 使用自定义 hitscan、伤害或投射物链路 | 调用 `RecordDamageSource`，主动提供武器、爆头或命中位置 |
| 模组会拦截原生死亡、钳制生命值或播放自定义死亡动画 | 注册托管实体类型，并在逻辑死亡成立时调用 `ReportExternalKill` |
| KillBroadcast 只是可选依赖 | 使用服务系统接口，并对系统尚未加载的情况做有限重试 |

完整字段、返回值、去重规则和排错说明见[外部击杀确认 API](behavior_pack_KillBroadcast/KillBroadcastScript/script/EXTERNAL_KILL_API.md)。兼容 Helper 的函数说明见[兼容 Helper 文档](behavior_pack_KillBroadcast/KillBroadcastScript/script/README.txt)。

## 自定义死亡动画接入流程

```text
服务器或世界加载
  -> 获取 KillBroadcast 服务系统
  -> 注册本模组接管的实体类型 identifier
  -> 正常伤害阶段由 KillBroadcast 缓存攻击者、武器和爆头证据
  -> 外部模组确认逻辑死亡并启动自己的死亡动画
  -> 调用 ReportExternalKill 上报一次已确认击杀
  -> KillBroadcast 去重并向攻击者发送击杀反馈
  -> 模组卸载或热重载前注销 owner
```

注册时传入的是稳定的 `namespace:entity_name`，不是某个实体实例的运行时 `entityId`。每次服务器、世界或服务系统重新加载后，都需要重新获取 system 并重新注册。

## 最小服务系统示例

```python
# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi


OWNER_ID = 'demo_death_animation'
MANAGED_TYPES = ['demo:animated_zombie']


def GetKillBroadcastSystem():
    return serverApi.GetSystem(
        'KillBroadcast',
        'KillBroadcastServerSystem'
    )


def RegisterKillBroadcastTypes():
    system = GetKillBroadcastSystem()
    if not system or not hasattr(system, 'RegisterExternallyManagedEntityTypes'):
        return False
    return bool(system.RegisterExternallyManagedEntityTypes({
        'OwnerId': OWNER_ID,
        'EntityTypes': MANAGED_TYPES,
    }))


def ReportConfirmedKill(playerId, targetId, headShot):
    system = GetKillBroadcastSystem()
    if not system or not hasattr(system, 'ReportExternalKill'):
        return False
    return bool(system.ReportExternalKill({
        'srcId': playerId,
        'entityId': targetId,
        'TargetType': 'demo:animated_zombie',
        'WeaponId': 'demo:rifle',
        'WeaponName': u'示例步枪',
        'HeadShot': headShot,
    }))


def UnregisterKillBroadcastTypes():
    system = GetKillBroadcastSystem()
    if not system or not hasattr(system, 'UnregisterExternallyManagedEntityTypes'):
        return False
    return bool(system.UnregisterExternallyManagedEntityTypes({
        'OwnerId': OWNER_ID,
    }))
```

## 普通自定义伤害接入

多数武器模组无需调用外部击杀确认 API。如果自定义伤害链路无法被原生事件识别，可以在造成伤害时主动记录精确信息：

```python
from KillBroadcastScript.script.DamageSourceCompat import RecordDamageSource

RecordDamageSource(
    playerId,
    targetId,
    'demo:rifle',
    u'示例步枪',
    headShot,
    0,
    hitPos
)
```

如果 KillBroadcast 是可选依赖，优先通过 `serverApi.GetSystem` 调用 `RecordExternalDamageSource`，不要在模块顶层强制 import KillBroadcast 的 Helper。

## 必须遵守的时机规则

- 注册成功只表示托管关系已记录；`ReportExternalKill` 需要服务系统已经 enabled。
- 只在逻辑死亡真正成立时上报一次，不要在预测伤害阶段提前上报。
- 返回 `False` 时不要对同一次死亡每 Tick 无限重试，应先判断加载顺序、参数或去重状态。
- `HeadShot=True` 和 `False` 表示外部模组给出的确定结论；传 `None` 或省略字段时，KillBroadcast 才会尝试使用已有证据补全。
- 热重载或托管类型列表变化时，先注销 owner，再注册完整的新列表。
- 模组卸载时注销 owner，避免开发环境中留下被抑制的实体类型。

## 接入完成后的检查

- 普通击杀只出现一次反馈；
- 自定义死亡动画开始后才出现击杀反馈；
- 普通命中仍有命中反馈，但托管实体不会被 KillBroadcast 提前判死；
- 直接伤害、投射物和自定义 hitscan 都能正确归因到玩家；
- 武器名、爆头结果和目标类型正确；
- 世界重载、热重载和模组卸载后不会遗留旧注册；
- 未安装或晚加载 KillBroadcast 时，外部模组自身仍能正常运行。

## 相关链接

- [完整外部击杀确认 API](behavior_pack_KillBroadcast/KillBroadcastScript/script/EXTERNAL_KILL_API.md)
- [兼容 Helper 文档](behavior_pack_KillBroadcast/KillBroadcastScript/script/README.txt)
- [GitHub 仓库](https://github.com/TanShaoBig/KillBroadcast)
- [最新 Release](https://github.com/TanShaoBig/KillBroadcast/releases/latest)
- [问题反馈](https://github.com/TanShaoBig/KillBroadcast/issues)

