# -*- coding: utf-8 -*-


ENTITY_CHINESE_NAMES = {
    'minecraft:allay': u'悦灵',
    'minecraft:armadillo': u'犰狳',
    'minecraft:axolotl': u'美西螈',
    'minecraft:bat': u'蝙蝠',
    'minecraft:bee': u'蜜蜂',
    'minecraft:blaze': u'烈焰人',
    'minecraft:bogged': u'沼骸',
    'minecraft:breeze': u'旋风人',
    'minecraft:camel': u'骆驼',
    'minecraft:cat': u'猫',
    'minecraft:cave_spider': u'洞穴蜘蛛',
    'minecraft:chicken': u'鸡',
    'minecraft:cod': u'鳕鱼',
    'minecraft:cow': u'牛',
    'minecraft:creaking': u'嘎枝',
    'minecraft:creeper': u'苦力怕',
    'minecraft:dolphin': u'海豚',
    'minecraft:donkey': u'驴',
    'minecraft:drowned': u'溺尸',
    'minecraft:elder_guardian': u'远古守卫者',
    'minecraft:ender_dragon': u'末影龙',
    'minecraft:enderman': u'末影人',
    'minecraft:endermite': u'末影螨',
    'minecraft:evocation_illager': u'唤魔者',
    'minecraft:evoker': u'唤魔者',
    'minecraft:fox': u'狐狸',
    'minecraft:frog': u'青蛙',
    'minecraft:ghast': u'恶魂',
    'minecraft:glow_squid': u'发光鱿鱼',
    'minecraft:goat': u'山羊',
    'minecraft:guardian': u'守卫者',
    'minecraft:happy_ghast': u'快乐恶魂',
    'minecraft:hoglin': u'疣猪兽',
    'minecraft:horse': u'马',
    'minecraft:husk': u'尸壳',
    'minecraft:iron_golem': u'铁傀儡',
    'minecraft:llama': u'羊驼',
    'minecraft:magma_cube': u'岩浆怪',
    'minecraft:mooshroom': u'哞菇',
    'minecraft:mule': u'骡',
    'minecraft:ocelot': u'豹猫',
    'minecraft:panda': u'熊猫',
    'minecraft:parrot': u'鹦鹉',
    'minecraft:phantom': u'幻翼',
    'minecraft:pig': u'猪',
    'minecraft:piglin': u'猪灵',
    'minecraft:piglin_brute': u'猪灵蛮兵',
    'minecraft:pillager': u'掠夺者',
    'minecraft:polar_bear': u'北极熊',
    'minecraft:pufferfish': u'河豚',
    'minecraft:rabbit': u'兔子',
    'minecraft:ravager': u'劫掠兽',
    'minecraft:salmon': u'鲑鱼',
    'minecraft:sheep': u'绵羊',
    'minecraft:shulker': u'潜影贝',
    'minecraft:silverfish': u'蠹虫',
    'minecraft:skeleton': u'骷髅',
    'minecraft:skeleton_horse': u'骷髅马',
    'minecraft:slime': u'史莱姆',
    'minecraft:sniffer': u'嗅探兽',
    'minecraft:snow_golem': u'雪傀儡',
    'minecraft:spider': u'蜘蛛',
    'minecraft:squid': u'鱿鱼',
    'minecraft:stray': u'流浪者',
    'minecraft:strider': u'炽足兽',
    'minecraft:tadpole': u'蝌蚪',
    'minecraft:trader_llama': u'行商羊驼',
    'minecraft:tropical_fish': u'热带鱼',
    'minecraft:tropicalfish': u'热带鱼',
    'minecraft:turtle': u'海龟',
    'minecraft:vex': u'恼鬼',
    'minecraft:villager': u'村民',
    'minecraft:villager_v2': u'村民',
    'minecraft:vindicator': u'卫道士',
    'minecraft:wandering_trader': u'流浪商人',
    'minecraft:warden': u'监守者',
    'minecraft:witch': u'女巫',
    'minecraft:wither': u'凋灵',
    'minecraft:wither_skeleton': u'凋灵骷髅',
    'minecraft:wolf': u'狼',
    'minecraft:zoglin': u'僵尸疣猪兽',
    'minecraft:zombie': u'僵尸',
    'minecraft:zombie_horse': u'僵尸马',
    'minecraft:zombie_pigman': u'僵尸猪人',
    'minecraft:zombie_villager': u'僵尸村民',
    'minecraft:zombie_villager_v2': u'僵尸村民',
    'minecraft:zombified_piglin': u'僵尸猪灵',
}


def ToUnicode(value):
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


def FormatIdentifier(identifier):
    text = ToUnicode(identifier).strip()
    if not text:
        return u''
    shortName = text.rsplit(':', 1)[-1].replace('_', ' ').replace('-', ' ')
    words = [word for word in shortName.split(' ') if word]
    return u' '.join(word.upper() if any(char.isdigit() for char in word) else word.title() for word in words)


def GetEntityDisplayName(entityType, fallbackName='', isPlayer=False):
    fallbackName = ToUnicode(fallbackName).strip()
    entityType = ToUnicode(entityType).strip().lower()
    if isPlayer:
        return fallbackName or u'玩家'
    if entityType in ENTITY_CHINESE_NAMES:
        return ENTITY_CHINESE_NAMES[entityType]
    shortType = entityType.rsplit(':', 1)[-1]
    if fallbackName and fallbackName.lower() not in (entityType, shortType):
        return fallbackName
    return FormatIdentifier(entityType or fallbackName) or u'未知生物'
