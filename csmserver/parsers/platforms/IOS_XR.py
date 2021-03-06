# =============================================================================
# Copyright (c) 2015, Cisco Systems, Inc
# All rights reserved.
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
import re

from models import Package
from constants import PackageState
from base import BaseSoftwarePackageParser, BaseInventoryParser
from models import get_db_session_logger


class IOSXRSoftwarePackageParser(BaseSoftwarePackageParser):

    def set_host_packages_from_cli(self, ctx):
        inactive_packages = {}
        active_packages = {}
        committed_packages = {}
        host_packages = []

        cli_show_install_inactive = ctx.load_data('cli_show_install_inactive')
        cli_show_install_active = ctx.load_data('cli_show_install_active')
        cli_show_install_committed = ctx.load_data('cli_show_install_committed')

        if isinstance(cli_show_install_inactive, list):
            inactive_packages = self.parseContents(cli_show_install_inactive[0], PackageState.INACTIVE)
        
        if isinstance(cli_show_install_active, list):
            active_packages = self.parseContents(cli_show_install_active[0], PackageState.ACTIVE)
        
        if isinstance(cli_show_install_committed, list):
            committed_packages = self.parseContents(cli_show_install_committed[0], PackageState.ACTIVE_COMMITTED)
        
        if committed_packages:
            for package in active_packages.values():
                if package.name in committed_packages:
                    package.state = PackageState.ACTIVE_COMMITTED
             
            for package in inactive_packages.values():
                if package.name in committed_packages:
                    # This is when the package is deactivated
                    package.state = PackageState.INACTIVE_COMMITTED
        
        for package in active_packages.values():
            host_packages.append(package)
            
        for package in inactive_packages.values():
            host_packages.append(package)
        
        if len(host_packages) > 0:
            ctx.host.packages = host_packages
            return True
        
        return False
        
    def parseContents(self, lines, package_state):
        package_dict = {}

        if lines is None:
            return package_dict

        found = False
        lines = lines.splitlines()

        for line in lines:
            if found:
                line = line.strip()

                if ':' in line:
                    location, name = line.split(':')
                else:
                    location = ''
                    name = line

                # skip anything after the blank line
                if len(line) == 0:
                    break
                
                package = Package(location=location, name=name, state=package_state)
                package_dict[name] = package

            elif 'Packages' in line:
                found = True

        return package_dict


class ASR9KInventoryParser(BaseInventoryParser):

    REGEX_SATELLITE_CHASSIS = re.compile(r'satellite chassis', flags=re.IGNORECASE)

    def parse_inventory_output(self, output):
        """
        Get everything except for the Generic Fan inventories from the inventory data
        """
        return [m.groupdict() for m in self.REGEX_BASIC_PATTERN.finditer(output)
                if 'Generic Fan' not in m.group('description')]

    def process_inventory(self, ctx):
        """
        For ASR9K IOS-XR.
        There is only one chassis in this case. It most likely shows up last in the
        output of "admin show inventory".
        Example:
        NAME: "chassis ASR-9006-AC", DESCR: "ASR 9006 4 Line Card Slot Chassis with V1 AC PEM"
        PID: ASR-9006-AC, VID: V01, SN: FOX1523H7HA
        """
        if not ctx.load_data('cli_show_inventory'):
            return
        inventory_output = ctx.load_data('cli_show_inventory')[0]

        inventory_data = self.parse_inventory_output(inventory_output)

        chassis_indices = []

        for idx in xrange(0, len(inventory_data)):
            if self.REGEX_CHASSIS.search(inventory_data[idx]['name']) and \
                    (not self.REGEX_SATELLITE_CHASSIS.search(inventory_data[idx]['name'])) and \
                    self.REGEX_CHASSIS.search(inventory_data[idx]['description']):
                chassis_indices.append(idx)

        if chassis_indices:
            return self.store_inventory(ctx, inventory_data, chassis_indices)

        logger = get_db_session_logger(ctx.db_session)
        logger.exception('Failed to find chassis in inventory output for host {}.'.format(ctx.host.hostname))
        return


class CRSInventoryParser(BaseInventoryParser):

    def process_inventory(self, ctx):
        """
        For CRS.
        There can be more than one chassis in this case.
        Example for CRS:
        NAME: "Rack 0 - Chassis", DESCR: "CRS 16 Slots Line Card Chassis for CRS-16/S-B"
        PID: CRS-16-LCC-B, VID: V03, SN: FXS1804Q576
        """
        if not ctx.load_data('cli_show_inventory'):
            return
        inventory_output = ctx.load_data('cli_show_inventory')[0]

        inventory_data = self.parse_inventory_output(inventory_output)

        chassis_indices = []

        for idx in xrange(0, len(inventory_data)):
            if self.REGEX_CHASSIS.search(inventory_data[idx]['name']) and \
                    self.REGEX_CHASSIS.search(inventory_data[idx]['description']):
                chassis_indices.append(idx)

        if chassis_indices:
            return self.store_inventory(ctx, inventory_data, chassis_indices)

        logger = get_db_session_logger(ctx.db_session)
        logger.exception('Failed to find chassis in inventory output for host {}.'.format(ctx.host.hostname))
        return
