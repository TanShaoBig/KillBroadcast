# KillBroadcast

KillBroadcast 是面向网易《我的世界》基岩版 ModSDK 的独立击杀反馈模组，提供命中标记、爆头判断、击杀卡片、多种 FPS 风格击杀特效、布局配置和外部模组兼容接口。

当前发布版本：`0.1.10`

## 下载

- [下载最新 Release](https://github.com/TanShaoBig/KillBroadcast/releases/latest)
- [下载 v0.1.10 安装包](https://github.com/TanShaoBig/KillBroadcast/releases/download/v0.1.10/KillBroadcast-v0.1.10.zip)
- [查看全部 Tag](https://github.com/TanShaoBig/KillBroadcast/tags)

Release ZIP 内包含完整的行为包、资源包、开源许可和第三方内容声明。

## 主要功能

- 服务端攻击者、投射物和武器归因；
- 普通命中、爆头与击杀反馈；
- 多种可切换的 FPS 风格击杀特效和音效；
- 击杀特效位置、大小、透明度和样式选项持久化；
- 玩家及生物目标名称、头像和纸娃娃显示；
- TsGuns 和其他武器模组兼容；
- 外部死亡动画模组的权威击杀确认接口；
- 重复击杀、重复命中反馈和实体移除链路去重。

## 目录结构

```text
behavior_pack_KillBroadcast/   行为包与 Python 2.7 脚本
resource_pack_KillBroadcast/   JSON UI、纹理与音频资源
```

## 安装

1. 下载 Release 中的 `KillBroadcast-v0.1.10.zip` 并解压；
2. 将 `behavior_pack_KillBroadcast` 和 `resource_pack_KillBroadcast` 放入对应的网易开发包或地图组件目录；
3. 在世界配置中同时启用行为包和资源包；
4. 完全重启世界或客户端，避免旧 UI、音频和资源缓存影响判断。

行为包依赖资源包，两个包的版本应保持一致。

## 外部模组接入

外部武器模组可以上报攻击者、武器名、投射物和爆头信息。会自行播放死亡动画的模组还可以注册托管实体类型，并在逻辑死亡真正成立时调用 `ReportExternalKill`。

完整参数、生命周期、示例和排错说明见：

- [外部击杀确认 API](behavior_pack_KillBroadcast/KillBroadcastScript/script/EXTERNAL_KILL_API.md)
- [兼容 Helper 说明](behavior_pack_KillBroadcast/KillBroadcastScript/script/README.txt)

## 开发与验证

运行环境为网易 ModSDK 使用的 Python 2.7。本次发布已在完整开发工作区通过包依赖闭合、JSON/UI/音频引用、击杀归因、外部死亡确认和布局逻辑等静态测试；为保持公开仓库精简，内部维护脚本不包含在发布内容中。

静态测试通过不等同于真机或联机环境验收；触摸输入、音频、加载顺序和最终 UI 合成仍需进入游戏验证。

## 开源与署名

本项目的击杀反馈设计与部分实现基于或参考 [GD656Killicon](https://github.com/MinecraftGD656/gd656killicon)，上游作者为 `Minecraft_GD656`，上游项目声明采用 MIT License。

软件代码采用仓库根目录的 [MIT License](LICENSE)。允许使用、修改、分发和商业使用，但复制或再发布软件及其主要部分时，必须保留完整版权声明和 MIT 许可文本。

网易基岩版移植、兼容层和后续扩展由 `TanShaoBig` 维护。

图片、音频及第三方游戏风格素材不统一纳入 MIT 软件许可。其来源与权利边界见 [第三方内容与署名](THIRD_PARTY_NOTICES.md)。公开可见不等于获得这些媒体文件的再授权。

## 免责声明

本项目是社区创作，不是 Mojang Studios、Microsoft、网易或其他游戏厂商的官方产品，也未获得其背书。使用者应遵守网易《我的世界》开发者平台规则及其所在地适用法律。
