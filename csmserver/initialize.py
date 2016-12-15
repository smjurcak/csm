# =============================================================================
# Copyright (c) 2016, Cisco Systems, Inc
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
from models import initialize
from models import SystemVersion

from database import DBSession
from database import CURRENT_SCHEMA_VERSION

from models import SystemOption

from utils import import_module

from schema.loader import get_schema_migrate_class

from constants import get_csm_data_directory

import os
import traceback


def init():
    db_session = DBSession()
    system_version = SystemVersion.get(db_session)

    # Handles database schema migration starting from the next schema version
    for version in range(system_version.schema_version + 1, CURRENT_SCHEMA_VERSION + 1):
        handler_class = get_schema_migrate_class(version)
        if handler_class is not None:
            try:
                handler_class(version).execute()
            except:
                print(traceback.format_exc())

    # Initialize certain tables 
    initialize()
    get_doc_central_config()


def apply_dialect_specific_codes():
    """
    Apply database engine specific codes.  Unlike schema migration codes, these codes are applied to
    new CSM installation which does not require schema migration.
    """
    db_session = DBSession()

    # For MYSQL: MEDIUMTEXT stores 2^24 characters. TEXT (65535) type is not enough when working with NCS6K
    # Multi-Chassis which has twice as much information as a single chassis.
    try:
        db_session.execute('alter table host_context modify data MEDIUMTEXT')
    except Exception:
        pass


def get_doc_central_config():
    db_session = DBSession()
    module = import_module('ConfigParser')
    if module is None:
        module = import_module('configparser')

    config = module.RawConfigParser()

    config.read(os.path.join(get_csm_data_directory(), 'config'))
    system_option = SystemOption.get(db_session)

    if not config.has_section('Doc Central'):
        system_option.doc_central_path = None
        db_session.commit()
    else:
        doc_central_dict = dict(config.items('Doc Central'))
        system_option.doc_central_path = doc_central_dict['directory_path']
        db_session.commit()


if __name__ == '__main__':
    init()