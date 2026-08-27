KillBroadcast settings ownership protocol

If another addon owns kill-effect settings, copy HideKillEffectSettings.py
into that addon's script package and call this function from its client init:

    from .script.HideKillEffectSettings import RegisterHideKillEffectSettings
    RegisterHideKillEffectSettings()

The provider registers the shared system:
    namespace: KillBroadcastCompat
    system: HideKillEffectSettings

KillBroadcast checks that system after addon loading and hides its own kill
effect settings category. A file that is never imported cannot be detected by
the game runtime, so the registration call is required.


KillBroadcast damage-source compatibility

Most weapon addons are detected automatically from ActuallyHurtServerEvent,
projectile ownership, and the item held when the projectile was spawned.
KillBroadcast opens the native player critical-hit box and consumes exact
ProjectileCritHitEvent / ProjectileDoHitEffectEvent data for third-party
projectiles.  For player targets without exact hit data, it also performs an
unspread server view ray at damage time.  The first valid ray hit must be the
damaged player, and its hit height must be inside the standing/crouching head
range.  Custom hitscan addons should report HeadShot or hitPos when available.

An addon with a custom damage pipeline can report exact weapon/headshot data:

    from KillBroadcastScript.script.DamageSourceCompat import RecordDamageSource

    RecordDamageSource(
        playerId,
        targetId,
        'otherguns:ak47',
        u'AK-47',
        headshot,
        0,
        hitPos
    )

Pass headshot=None with hitPos=(x, y, z) to let KillBroadcast evaluate the
player head range.  Existing calls that pass a boolean headshot remain valid.

Static names can be registered once during server initialization:

    from KillBroadcastScript.script.DamageSourceCompat import RegisterWeaponDisplayName
    RegisterWeaponDisplayName('otherguns:ak47', u'AK-47')

Direct service API (for addons that do not import helper modules):

    system = serverApi.GetSystem('KillBroadcast', 'KillBroadcastServerSystem')
    system.RecordExternalDamageSource({
        'AttackerId': playerId,
        'TargetId': targetId,
        'WeaponId': 'otherguns:ak47',
        'WeaponName': u'AK-47',
        'HeadShot': True,
    })


KillBroadcast custom death-animation compatibility

The complete public API, field table, lifecycle and examples are documented in:

    KillBroadcastScript/script/EXTERNAL_KILL_API.md

A death-animation addon can register entity type identifiers during server
loading.  KillBroadcast keeps collecting damage, weapon and headshot evidence
for those types, but does not automatically show their kills.  The external
owner confirms the logical death when its animation starts:

    from KillBroadcastScript.script.DamageSourceCompat import (
        RegisterManagedEntityTypes,
        ReportKill,
    )

    RegisterManagedEntityTypes(
        'other_death_animation',
        ['other:animated_zombie']
    )

    ReportKill(
        playerId,
        targetId,
        'otherguns:ak47',
        u'AK-47',
        headshot,
        0,
        hitPos
    )

Pass headshot=True or False to provide an exact result.  Pass headshot=None, or
omit HeadShot from the direct payload, to let KillBroadcast use recent hit
evidence, hitPos and server view-ray detection.  Explicit False is never
overridden by automatic detection.

For an optional dependency, use the direct service API instead of importing
the helper module:

    system = serverApi.GetSystem('KillBroadcast', 'KillBroadcastServerSystem')
    system.RegisterExternallyManagedEntityTypes({
        'OwnerId': 'other_death_animation',
        'EntityTypes': ['other:animated_zombie'],
    })
    system.ReportExternalKill({
        'srcId': playerId,
        'entityId': targetId,
        'TargetType': 'other:animated_zombie',
        'WeaponId': 'otherguns:ak47',
        'WeaponName': u'AK-47',
        'HeadShot': True,
    })

Registration uses namespace-qualified entity type identifiers, not runtime
entityIds.  Re-register on every server/world load.  If GetSystem is not ready
because of addon initialization order, retry after LoadServerAddonScriptsAfter
or on a later server tick.  Registration is additive; on hot reload or list
changes, unregister the owner first, then register the complete new list.  An
external DestroyServer should also unregister its owner.
