# =============================================================================
# plugin.py - Generic Plugin Class
#
# Copyright (c) 2014, Cisco Systems
# All rights reserved.
#
# Author: Klaudiusz Staniek
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# =============================================================================


from inspect import isclass
from collections import defaultdict

# Add plugin classes below to be automatically imported
from plugin import IPlugin
from csmserver.plugins.not_migrated.device_connect import DeviceConnectPlugin
from version_check import SoftwareVersionPlugin
from node_status import NodeStatusPlugin
from ping_test import PingTestPlugin
from disk_space_plugin import DiskSpacePlugin
# from package_check_plugin_act import ActivePackagesPlugin
# from package_check_plugin_inact import InactivePackagesPlugin
# from package_check_plugin_committed import CommittedPackagesPlugin
from redundancy_check import NodeRedundancyPlugin
# from ospf_isis_nei_precheck import OspfIsisPrePlugin
# from ospf_isis_nei_postcheck import OspfIsisPostPlugin
from cfg_backup import ConfigBackupPlugin
# from cmd_snapshot_backup import CommandSnapshotPlugin
from install_add import InstallAddPlugin
from install_act import InstallActivatePlugin
from install_deact import InstallDeactivatePlugin
from install_remove import InstallRemovePlugin
from install_commit import InstallCommitPlugin
# from cfg_consistency import ConfigConsistencyPlugin
# from err_core_check import ErrorCorePlugin
# from device_pkg_poll import DevicePackageSatePlugin
#from au.plugins.isis_setoverload import isisSetOverloadPrePlugin
#from au.plugins.isis_unsetoverload import isisunSetOverloadPostPlugin

# Added manually to preserve the order
plugin_classes = [
#    DeviceConnectPlugin,
    SoftwareVersionPlugin,
    InstallDeactivatePlugin,
    InstallRemovePlugin,
    ConfigBackupPlugin,
    NodeStatusPlugin,
    DiskSpacePlugin,
    PingTestPlugin,
#     ActivePackagesPlugin,
#     InactivePackagesPlugin,
#     CommittedPackagesPlugin,
    NodeRedundancyPlugin,
#     CommandSnapshotPlugin,
#     OspfIsisPrePlugin,
# #    isisSetOverloadPrePlugin,
    InstallAddPlugin,
    InstallActivatePlugin,
#     ConfigConsistencyPlugin,
#     OspfIsisPostPlugin,
# #    isisunSetOverloadPostPlugin,
#     ErrorCorePlugin,
#     DevicePackageSatePlugin,
    InstallCommitPlugin,
]
plugins = []
plugin_map = defaultdict(list)

plugin_types = ["DEACTIVATE", "REMOVE", "ADD", "UPGRADE", "PRE_UPGRADE", "PRE_UPGRADE_AND_POST_UPGRADE",
                "PRE_UPGRADE_AND_UPGRADE", "TURBOBOOT", "POST_UPGRADE", "COMMIT"]
phases = {
    "POLL": ["POLL"],
    "ADD": ["ADD"],
    "COMMIT": ["COMMIT"],
    "PRE_UPGRADE": [
        "PRE_UPGRADE", "PRE_UPGRADE_AND_POST_UPGRADE", "CONNECTION"
    ],
    "UPGRADE": [
        "PRE_UPGRADE_AND_UPGRADE", "UPGRADE"
    ],
    "TURBOBOOT": [
        "PRE_UPGRADE", "TURBOBOOT", "POST_UPGRADE"
    ],
    "POST_UPGRADE": [
        "POST_UPGRADE",
        "PRE_UPGRADE_AND_POST_UPGRADE"
    ],
    "ALL": [
        "PRE_UPGRADE",
        "PRE_UPGRADE_AND_POST_UPGRADE",
        "PRE_UPGRADE_AND_UPGRADE",
        "ADD",
        "UPGRADE",
        "POST_UPGRADE",
    ],
    "DEACTIVATE": ["DEACTIVATE", "POLL"],
    "REMOVE": ["REMOVE", "POLL"]
}


def is_plugin(o):
    return isclass(o) and issubclass(o, IPlugin) and o is not IPlugin


def add_plugin(cls):
    plugin = cls()
    # plugin_classes.append(cls)
    plugins.append(plugin)
    for phase in phases:
        # Connecting the device should be in all phase of operation
        if plugin.TYPE in phases[phase] or plugin.NAME == "CONNECTION":         
            plugin_map[phase].append(plugin)


def get_plugins_of_phase(phase):
    return iter(plugin_map[phase])

for obj in plugin_classes:
    if is_plugin(obj):
        add_plugin(obj)
