# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
import mod.server.extraServerApi as serverApi
from mod.common.mod import Mod

from .ModConfig import (
    CLIENT_SYSTEM_NAME,
    CLIENT_SYSTEM_PATH,
    MOD_BINDING_NAME,
    MOD_NAMESPACE,
    SERVER_SYSTEM_NAME,
    SERVER_SYSTEM_PATH,
)


@Mod.Binding(name=MOD_BINDING_NAME, version='0.1.10')
class KillBroadcastScript(object):
    @Mod.InitServer()
    def InitServer(self):
        serverApi.RegisterSystem(MOD_NAMESPACE, SERVER_SYSTEM_NAME, SERVER_SYSTEM_PATH)

    @Mod.DestroyServer()
    def DestroyServer(self):
        pass

    @Mod.InitClient()
    def InitClient(self):
        clientApi.RegisterSystem(MOD_NAMESPACE, CLIENT_SYSTEM_NAME, CLIENT_SYSTEM_PATH)

    @Mod.DestroyClient()
    def DestroyClient(self):
        pass
