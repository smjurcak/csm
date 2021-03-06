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
from schema.base import BaseMigrate
from database import DBSession
from constants import UserPrivilege

sql_statements = [
    'alter table host add location VARCHAR(100)',
    'alter table smu_info add smu_category VARCHAR(20)',
    'alter table system_option add ldap_server_distinguished_names VARCHAR(100)',
    'alter table system_option add use_utc_timezone BOOLEAN default 0',
    'alter table server add destination_on_host VARCHAR(50)',
    'alter table email_job add attachment_file_paths VARCHAR(300)',
    'alter table host add software_profile_id INTEGER',
    'alter table conformance_report_entry change platform software_platform VARCHAR(20)',
    'alter table conformance_report_entry change software software_version VARCHAR(20)',
    'alter table system_option add ldap_default_user_privilege VARCHAR(20) default "Viewer"',
    'alter table install_job change column custom_command_profile_id custom_command_profile_ids VARCHAR(20)',
    'alter table install_job add data TEXT',
    'alter table install_job_history add data TEXT',
    ]


class SchemaMigrate(BaseMigrate):
    def __init__(self, version):
        BaseMigrate.__init__(self, version)

    def start(self):
        db_session = DBSession()
        for sql in sql_statements:
            try:
                db_session.execute(sql)
            except Exception as e:
                pass
