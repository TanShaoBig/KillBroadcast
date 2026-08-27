# KillBroadcast 外部击杀确认 API

本文面向会拦截原生死亡、钳制生命值，或自行播放生物死亡动画的网易《我的世界》服务端模组。接入后，外部模组负责确认“逻辑死亡”，KillBroadcast 继续负责攻击者/武器归因、爆头信息、命中反馈和击杀 UI。

> API 版本：`1`；运行侧：服务端 Python 2.7；系统：`KillBroadcast` / `KillBroadcastServerSystem`

## 项目与下载

- GitHub 仓库：[TanShaoBig/KillBroadcast](https://github.com/TanShaoBig/KillBroadcast)
- 开发者接入指南：[DEVELOPER_INTEGRATION.md](https://github.com/TanShaoBig/KillBroadcast/blob/main/DEVELOPER_INTEGRATION.md)
- 最新 Release：[GitHub Releases](https://github.com/TanShaoBig/KillBroadcast/releases/latest)
- 当前版本：[`v0.1.10`](https://github.com/TanShaoBig/KillBroadcast/releases/tag/v0.1.10)
- ZIP 直链：[下载 `KillBroadcast-v0.1.10.zip`](https://github.com/TanShaoBig/KillBroadcast/releases/download/v0.1.10/KillBroadcast-v0.1.10.zip)
- 问题反馈：[GitHub Issues](https://github.com/TanShaoBig/KillBroadcast/issues)
- 开源协议：[MIT License](https://github.com/TanShaoBig/KillBroadcast/blob/main/LICENSE)
- 第三方素材声明：[THIRD_PARTY_NOTICES.md](https://github.com/TanShaoBig/KillBroadcast/blob/main/THIRD_PARTY_NOTICES.md)

代码及本项目移植、改造部分采用 MIT License，使用、修改或再发布时须保留版权和许可声明。图片、音频等非原创第三方素材不包含在本项目 MIT 授权范围内，使用前请查看第三方素材声明。

## 目录

- [项目与下载](#项目与下载)
- [1. 接入前须知](#1-接入前须知)
- [2. 最小接入流程](#2-最小接入流程)
- [3. 注册和注销托管实体类型](#3-注册和注销托管实体类型)
- [4. 上报已确认的击杀](#4-上报已确认的击杀)
- [5. 参数说明](#5-参数说明)
- [6. 爆头三态规则](#6-爆头三态规则)
- [7. Helper 用法](#7-helper-用法)
- [8. 可选依赖与重试](#8-可选依赖与重试)
- [9. 返回值、时机与去重](#9-返回值时机与去重)
- [10. 能力查询](#10-能力查询)
- [11. 常见问题排查](#11-常见问题排查)
- [12. 接入验收清单](#12-接入验收清单)

## 1. 接入前须知

外部模组需要注册自己负责的实体类型 identifier，例如：

```text
demo:animated_zombie
demo:animated_boss
```

这里传的是稳定的 `namespace:entity_name`，不能传某次生成实体的运行时 `entityId`。identifier 会去除首尾空白并转为小写；缺少命名空间、冒号位于首尾的值会被视为无效。

注册后，KillBroadcast 对这些类型执行以下规则：

- 继续记录攻击者、武器、投射物、命中位置和爆头证据；
- 继续发送普通命中反馈；
- 不再根据伤害预测、`MobDieEvent` 或 `EntityRemoveEvent` 自动弹出击杀；
- 只在外部模组调用 `ReportExternalKill` 后进入击杀显示链路。

典型生命周期如下：

```text
服务器加载
  -> 获取 KillBroadcast 服务系统
  -> 注册托管实体类型
  -> 实体受到伤害（KillBroadcast 只缓存归因）
  -> 外部模组确认逻辑死亡并开始死亡动画
  -> 调用 ReportExternalKill
  -> KillBroadcast 去重并发送击杀 UI
  -> 外部模组卸载时注销 owner
```

注册表直接约束 KillBroadcast 自己的自动击杀链。如果武器模组或其他 UI 提供方还有独立的 `CreateKill` 路径，也应在发送前查询同一个系统：

```python
managed = bool(
    system and
    hasattr(system, 'IsExternallyManagedEntityType') and
    system.IsExternallyManagedEntityType(targetType)
)
if not managed:
    SendOwnKillUi()
```

注册表只存在于本轮服务器运行期间，不写入存档。每次服务器、世界或 KillBroadcast 服务系统重新加载后都要重新获取 system 并注册；不要跨重载长期缓存旧 system 对象。

## 2. 最小接入流程

只需完成三件事：

1. 服务器加载后获取 KillBroadcast 服务系统；
2. 注册由本模组负责死亡确认的实体类型；
3. 在逻辑死亡真正成立时上报一次击杀，卸载时注销 owner。

最小示例：

```python
# -*- coding: utf-8 -*-
import mod.server.extraServerApi as serverApi


OWNER_ID = 'demo_death_animation'


def GetKillBroadcastSystem():
    return serverApi.GetSystem(
        'KillBroadcast',
        'KillBroadcastServerSystem'
    )


def RegisterKillBroadcastEntities():
    system = GetKillBroadcastSystem()
    if not system or not hasattr(system, 'RegisterExternallyManagedEntityTypes'):
        return False
    return bool(system.RegisterExternallyManagedEntityTypes({
        'OwnerId': OWNER_ID,
        'EntityTypes': ['demo:animated_zombie'],
    }))


def ReportAnimatedDeath(playerId, targetId, headShot):
    system = GetKillBroadcastSystem()
    if not system or not hasattr(system, 'ReportExternalKill'):
        return False
    return bool(system.ReportExternalKill({
        'srcId': playerId,
        'entityId': targetId,
        'TargetType': 'demo:animated_zombie',
        'HeadShot': bool(headShot),
    }))


def UnregisterKillBroadcastEntities():
    system = GetKillBroadcastSystem()
    if not system or not hasattr(system, 'UnregisterExternallyManagedEntityTypes'):
        return False
    return bool(system.UnregisterExternallyManagedEntityTypes({
        'OwnerId': OWNER_ID,
    }))
```

## 3. 注册和注销托管实体类型

### 3.1 注册

推荐使用不依赖跨包 import 的服务系统接口：

```python
system.RegisterExternallyManagedEntityTypes({
    'OwnerId': 'demo_death_animation',
    'EntityTypes': [
        'demo:animated_zombie',
        'demo:animated_boss',
    ],
})
```

`OwnerId` 应使用本模组稳定、唯一的英文标识。它会被去除首尾空白并转为小写，不是玩家 ID，也不是实体 ID。

支持的字段别名：

| 含义 | 字段名 |
| --- | --- |
| owner | `OwnerId`、`ownerId`、`ProviderId`、`providerId` |
| 实体类型 | `EntityTypes`、`entityTypes`、`EntityIdentifiers`、`entityIdentifiers`、`Identifiers`、`identifiers` |

实体类型可以传单个字符串，也可以传 `list`、`tuple`、`set` 或 `frozenset`。混合列表中的重复项和无效项会被忽略。

注册接口不要求 KillBroadcast 已经进入 enabled 状态，因此可以在加载阶段调用。相同 owner 重复注册相同类型是幂等的，但再次注册不会自动删除该 owner 以前的旧类型；热重载或配置列表变化时，应先注销该 owner 的全部类型，再注册完整新列表。

同一种实体类型可以被多个 owner 注册。只有所有 owner 都注销后，该类型才恢复 KillBroadcast 自动确认。

### 3.2 注销指定类型

```python
system.UnregisterExternallyManagedEntityTypes({
    'OwnerId': OWNER_ID,
    'EntityTypes': ['demo:animated_zombie'],
})
```

### 3.3 注销 owner 的全部类型

```python
system.UnregisterExternallyManagedEntityTypes({
    'OwnerId': OWNER_ID,
})
```

外部模组的 `DestroyServer` 应执行完整注销，避免开发环境热卸载后留下仍被抑制的类型。

## 4. 上报已确认的击杀

外部模组确认一次逻辑死亡并开始死亡动画时调用：

```python
# -*- coding: utf-8 -*-
system = serverApi.GetSystem(
    'KillBroadcast',
    'KillBroadcastServerSystem'
)

reported = False
if system and hasattr(system, 'ReportExternalKill'):
    reported = bool(system.ReportExternalKill({
        'srcId': playerId,
        'entityId': targetId,
        'TargetType': 'demo:animated_zombie',
        'WeaponId': 'demo:rifle',
        'WeaponName': u'示例步枪',
        'HeadShot': True,
    }))
```

`ConfirmExternalKill` 是 `ReportExternalKill` 的等价入口。推荐统一使用 `ReportExternalKill`，便于代码检索和兼容性检查。

注意：注册可以在 KillBroadcast 尚未启用时成功，但击杀上报只有在 KillBroadcast 服务系统已经 enabled 后才会成功。若上报返回 `False`，不要无期限地对同一次死亡每 Tick 重试；应先区分“系统尚未就绪”和“参数/去重拒绝”。

## 5. 参数说明

### 5.1 必填字段

| 含义 | 支持的字段名 | 类型与要求 |
| --- | --- | --- |
| 玩家攻击者或其伤害源 entityId | `srcId`、`attacker`、`AttackerId`、`attackerId`、`ownerId`、`spawnerId` | 必须最终解析为在线玩家；也可传该玩家拥有的投射物 entityId |
| 被击杀实体 entityId | `TargetId`、`targetId`、`EntityId`、`entityId` | 本次死亡目标的运行时 entityId |

攻击者不能与目标相同。若传入 `projectileId` / `ProjectileId`，系统会优先尝试从投射物缓存和引擎拥有者解析玩家与武器上下文。

### 5.2 可选字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `HeadShot` / `headshot` | `bool` | 显式传 `True` 或 `False` 时严格采用；完全不传才进入自动判定 |
| `hitPos` / `HitPos` / `hitPosition` / `HitPosition` / `damagePos` | `(x, y, z)` | 命中坐标；未显式传 `HeadShot` 时用于自动判断爆头 |
| `projectileId` / `ProjectileId` | entityId | 用于恢复投射物拥有者和武器上下文 |
| `WeaponId` / `weaponId` | identifier | 武器物品 identifier |
| `WeaponAux` / `weaponAux` | `int` | 武器 aux 值 |
| `WeaponName` / `weaponName` | `str` / `unicode` | 击杀界面显示的武器名称；优先于自动名称解析 |
| `WeaponCustomName` / `weaponCustomName` | `str` / `unicode` | 武器自定义名称 |
| `WeaponExtraId` / `weaponExtraId` | `str` | 动态物品 extraId |
| `TargetType` / `targetType` / `EntityType` / `entityType` / `Identifier` / `identifier` | identifier | 目标实体类型；目标可能已被移除时强烈建议传入 |
| `TargetName` / `targetName` | `str` / `unicode` | 目标显示名称 |
| `TargetMaxHealth` / `targetMaxHealth` | `int` / `float` | 目标最大生命值 |
| `Damage` / `damage` / `Amount` / `amount` | `int` / `float` | 本次新增伤害；同一次伤害已由原生事件记录时应省略，避免累计两次 |

### 5.3 数据补全来源

KillBroadcast 会优先尊重本次 payload 中支持显式覆盖的字段，并按字段需要组合目标最近约 8 秒内的伤害上下文、投射物缓存、攻击者手持物和目标引擎组件。无法读取的信息最终使用空值或通用显示；不同字段的内部读取顺序不应作为外部 API 契约依赖。

目标被移除后，引擎可能无法再提供类型、名称、位置、碰撞箱和最大生命值。因此延迟上报时至少应保留 `TargetType`，最好同时保留 `TargetName`、`TargetMaxHealth` 和明确的 `HeadShot`。

## 6. 爆头三态规则

```python
# 明确是爆头
{'HeadShot': True}

# 明确不是爆头，不会再被视线检测改成爆头
{'HeadShot': False}

# 不放 HeadShot 字段：由 KillBroadcast 自动检测
{'hitPos': hitPos}
```

完全省略 `HeadShot` 时，KillBroadcast 会依次复用近期伤害上下文、传入的 `hitPos` 和服务器视线射线。`None` 不等同于“省略”：直接系统调用时若需要自动判定，请不要放入 `HeadShot` / `headshot` 键。

实体移除后碰撞箱和位置可能已经无法读取，因此最好在死亡动画开始、原实体仍存在时上报；否则应显式传入 `HeadShot` 和 `TargetType`。

## 7. Helper 用法

若 KillBroadcast 是外部模组的强依赖，可以使用随包 helper：

```python
# -*- coding: utf-8 -*-
from KillBroadcastScript.script.DamageSourceCompat import (
    RegisterManagedEntityTypes,
    ReportKill,
)

RegisterManagedEntityTypes(
    'demo_death_animation',
    ['demo:animated_zombie']
)

ReportKill(
    playerId,
    targetId,
    'demo:rifle',
    u'示例步枪',
    None,       # Helper 中 None 表示不放 HeadShot，交给系统自动检测
    0,
    hitPos,
    'demo:animated_zombie',
)
```

已有 `ReportKill` 位置参数保持兼容，新参数均追加在末尾。其完整签名为：

```python
ReportKill(
    attackerId,
    targetId,
    weaponId='',
    weaponName='',
    headshot=None,
    weaponAux=0,
    hitPos=None,
    targetType='',
    targetName='',
    damage=None,
)
```

`TargetMaxHealth` 等不在位置参数签名中的扩展字段，请通过 `ReportKillInfo` 字典入口传入。

也可以直接转发字典：

```python
from KillBroadcastScript.script.DamageSourceCompat import ReportKillInfo

ReportKillInfo({
    'srcId': playerId,
    'entityId': targetId,
    'HeadShot': False,
})
```

Helper 还提供以下入口：

| Helper | 用途 |
| --- | --- |
| `RegisterManagedEntityTypes(ownerId, entityTypes)` | 注册托管类型 |
| `UnregisterManagedEntityTypes(ownerId, entityTypes=None)` | 注销指定类型或 owner 全部类型 |
| `GetManagedEntityTypes(ownerId=None)` | 查询全部或某 owner 的托管类型 |
| `ReportKillInfo(killInfo)` | 原样转发击杀字典 |
| `ConfirmKill` | `ReportKill` 的别名 |
| `ConfirmKillInfo` | `ReportKillInfo` 的别名 |

如果 KillBroadcast 只是可选依赖，优先使用 `serverApi.GetSystem(...)`，避免包不存在时跨包 import 失败。

## 8. 可选依赖与重试

推荐在外部模组的 `LoadServerAddonScriptsAfter` 回调中首次注册。若初始化顺序导致 `GetSystem` 暂时返回 `None`，可以在后续服务器 Tick 有限重试，直到成功或达到本模组设定的重试上限。

建议遵循以下规则：

- 每次重试都重新调用 `serverApi.GetSystem(...)`；
- 注册成功后立即停止 Tick 重试；
- 只检查 `hasattr`，不要假设旧版 KillBroadcast 已包含此 API；
- 击杀事件到达时系统不可用，应让游戏逻辑继续运行，不要让可选 UI 依赖阻断死亡流程；
- `DestroyServer` 中只注销本模组自己的 `OwnerId`；
- 热重载后重新获取系统对象并注册完整列表。

若外部模组要求 KillBroadcast 必装，可在重试结束后输出一次明确日志；若只是可选依赖，建议静默降级或只输出一次提示，避免每 Tick 刷屏。

## 9. 返回值、时机与去重

- 注册接口：至少包含一个合法 identifier 时返回 `True`；混合列表会忽略非法项。空 owner、空列表或全部 identifier 都不合法时返回 `False`。
- 注销接口：实际移除至少一项注册时返回 `True`；没有匹配项返回 `False`。
- 击杀上报：本次成功进入击杀显示链路时返回 `True`；系统未就绪、参数无效、攻击者不是玩家、自杀、重复上报或被其他归因链拒绝时返回 `False`。
- TsGuns 已归因的未托管目标仍交给 TsGuns 处理并返回 `False`；已注册的托管目标允许外部确认穿透这项检查。
- 同一目标当前使用 10 秒死亡锁去重。外部上报后再出现 `MobDieEvent`、`EntityRemoveEvent` 或重复上报，不会重复弹出。
- 应在“逻辑死亡已经确定、死亡动画正式开始”时上报一次。若流程可能复活、取消或进入假死状态，不要在仅仅预测致死时提前上报。

`ReportExternalKill` 返回 `False` 不代表应该立即重复上报。建议调用方自行维护“一次逻辑死亡只上报一次”的标记；只有已明确判断为加载顺序导致的系统未就绪时，才做有限重试。

## 10. 能力查询

接入方可以先检查 API 版本和能力，再决定是否启用高级行为：

```python
info = system.GetExternalKillApiInfo()
managedTypes = system.GetExternallyManagedEntityTypes()
myTypes = system.GetExternallyManagedEntityTypes(OWNER_ID)
isManaged = system.IsExternallyManagedEntityType(
    'demo:animated_zombie'
)
```

当前 `info` 结构：

```python
{
    'Version': 1,
    'ManagedEntityTypes': ['demo:animated_zombie'],
    'SupportsNativeEventArgs': True,
    'SupportsOptionalHeadShot': True,
    'SupportsManagedTypeQuery': True,
}
```

兼容写法：

```python
info = system.GetExternalKillApiInfo()
if int(info.get('Version', 0)) < 1:
    return False
if not info.get('SupportsManagedTypeQuery'):
    return False
```

未来版本可能增加字段。调用方应读取自己认识的键，不要要求字典只能包含当前这些键。

## 11. 常见问题排查

### 注册返回 `False`

检查：

- `OwnerId` 是否为空；
- `EntityTypes` 是否为字符串或受支持的容器；
- identifier 是否包含非首尾位置的 `:`；
- 是否误把运行时 `entityId` 当成实体类型 identifier。

### 注册成功，但仍出现自动击杀

检查：

- 实际目标类型是否与注册值一致；
- 是否在服务器/世界重载后遗漏重新注册；
- 重载时是否仍缓存了旧 system 对象；
- 弹出的 UI 是否来自另一个模组自己的 `CreateKill` 路径；
- 另一个 UI 提供方是否在发送前调用了 `IsExternallyManagedEntityType`。

### `ReportExternalKill` 返回 `False`

常见原因：

- KillBroadcast 尚未 enabled 或已经销毁；
- payload 不是字典；
- 缺少攻击者或目标 entityId；
- 攻击者无法解析为在线玩家；
- 攻击者与目标相同；
- 同一目标已在 10 秒死亡锁内上报；
- 目标未注册为托管类型，同时该击杀已由 TsGuns 归因链负责。

### 击杀能显示，但武器名或爆头不正确

检查：

- 延迟到实体移除后才上报时，是否显式传了 `TargetType` 和 `HeadShot`；
- 是否把 `HeadShot: None` 放进字典，导致其被视为显式 `False`；
- 是否重复传入已由原生伤害事件累计过的 `Damage`；
- 投射物击杀是否传入了 `projectileId`；
- 自定义武器是否传入 `WeaponId` / `WeaponName`，或提前注册了武器显示名。

## 12. 接入验收清单

发布前至少验证以下场景：

- 普通伤害仍有命中反馈，但托管实体不会提前弹出击杀；
- 外部死亡动画开始时只弹出一次击杀；
- `HeadShot=True`、`False` 和完全省略三种情况分别正确；
- 近战、直接伤害和投射物都能解析到正确玩家与武器；
- 目标先移除再上报时，保存的 `TargetType` / `TargetName` 仍能正确显示；
- 两个 owner 同时注册同一类型时，单个 owner 注销不会恢复自动确认；
- 世界重载、服务器重载和开发热重载后能重新注册；
- KillBroadcast 未安装或旧版本无此 API 时，外部模组能安全降级；
- 重复上报、`MobDieEvent`、`EntityRemoveEvent` 不会产生第二条击杀；
- `DestroyServer` 后该 owner 的托管类型已清理。

静态测试可以验证参数契约和去重逻辑，但不能替代真实联机环境中的加载顺序、实体移除时机和 UI 显示验证。
