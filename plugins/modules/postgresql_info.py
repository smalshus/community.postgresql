#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Andrew Klychkov (@Andersson007) <andrew.a.klychkov@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: postgresql_info
short_description: Gather information about PostgreSQL servers
description:
- Gathers information about PostgreSQL servers.
options:
  filter:
    description:
    - Limit the collected information by comma separated string or YAML list.
    - Allowable values are C(version),
      C(databases), C(in_recovery), C(settings), C(tablespaces), C(roles),
      C(replications), C(repl_slots).
    - By default, collects all subsets.
    - You can use shell-style (fnmatch) wildcard to pass groups of values (see Examples).
    - You can use '!' before value (for example, C(!settings)) to exclude it from the information.
    - If you pass including and excluding values to the filter, for example, I(filter=!settings,ver),
      the excluding values will be ignored.
    type: list
    elements: str
  db:
    description:
    - Name of database to connect.
    type: str
    aliases:
    - login_db
  session_role:
    description:
    - Switch to session_role after connecting. The specified session_role must
      be a role that the current login_user is a member of.
    - Permissions checking for SQL commands is carried out as though
      the session_role were the one that had logged in originally.
    type: str
  trust_input:
    description:
    - If C(false), check whether a value of I(session_role) is potentially dangerous.
    - It makes sense to use C(false) only when SQL injections via I(session_role) are possible.
    type: bool
    default: true
    version_added: '0.2.0'

attributes:
  check_mode:
    support: full

seealso:
- module: community.postgresql.postgresql_ping

author:
- Andrew Klychkov (@Andersson007)

extends_documentation_fragment:
- community.postgresql.postgres
'''

EXAMPLES = r'''
# Display info from postgres hosts.
# ansible postgres -m postgresql_info

# Display only databases and roles info from all hosts using shell-style wildcards:
# ansible all -m postgresql_info -a 'filter=dat*,rol*'

# Display only replications and repl_slots info from standby hosts using shell-style wildcards:
# ansible standby -m postgresql_info -a 'filter=repl*'

# Display all info from databases hosts except settings:
# ansible databases -m postgresql_info -a 'filter=!settings'

- name: Collect PostgreSQL version and extensions
  become: true
  become_user: postgres
  community.postgresql.postgresql_info:
    filter: ver*,ext*

- name: Collect all info except settings and roles
  become: true
  become_user: postgres
  community.postgresql.postgresql_info:
    filter: "!settings,!roles"

# On FreeBSD with PostgreSQL 9.5 version and lower use pgsql user to become
# and pass "postgres" as a database to connect to
- name: Collect tablespaces and repl_slots info
  become: true
  become_user: pgsql
  community.postgresql.postgresql_info:
    db: postgres
    filter:
    - tablesp*
    - repl_sl*

- name: Collect all info except databases
  become: true
  become_user: postgres
  community.postgresql.postgresql_info:
    filter:
    - "!databases"
'''

RETURN = r'''
version:
  description: Database server version U(https://www.postgresql.org/support/versioning/).
  returned: success
  type: dict
  sample: { "version": { "major": 10, "minor": 6 } }
  contains:
    major:
      description: Major server version.
      returned: success
      type: int
      sample: 11
    minor:
      description: Minor server version.
      returned: success
      type: int
      sample: 1
    patch:
      description: Patch server version.
      returned: if supported
      type: int
      sample: 5
      version_added: '1.2.0'
    full:
      description: Full server version.
      returned: success
      type: str
      sample: '13.2'
      version_added: '1.2.0'
    raw:
      description: Full output returned by ``SELECT version()``.
      returned: success
      type: str
      sample: 'PostgreSQL 13.2 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 10.2.1 20201125 (Red Hat 10.2.1-9), 64-bit'
      version_added: '1.2.0'
in_recovery:
  description: Indicates if the service is in recovery mode or not.
  returned: success
  type: bool
  sample: false
databases:
  description: Information about databases.
  returned: success
  type: dict
  sample:
  - { "postgres": { "access_priv": "", "collate": "en_US.UTF-8",
  "ctype": "en_US.UTF-8", "encoding": "UTF8", "owner": "postgres", "size": "7997 kB" } }
  contains:
    database_name:
      description: Database name.
      returned: success
      type: dict
      sample: template1
      contains:
        access_priv:
          description: Database access privileges.
          returned: success
          type: str
          sample: "=c/postgres_npostgres=CTc/postgres"
        collate:
          description:
          - Database collation U(https://www.postgresql.org/docs/current/collation.html).
          returned: success
          type: str
          sample: en_US.UTF-8
        ctype:
          description:
          - Database LC_CTYPE U(https://www.postgresql.org/docs/current/multibyte.html).
          returned: success
          type: str
          sample: en_US.UTF-8
        icu_locale:
          description:
          - Database ICU_LOCALE U(https://www.postgresql.org/docs/current/locale.html#ICU-LOCALES).
          returned: success
          type: str
          sample: en_US.UTF-8
        locale_provider:
          description:
          - Database LOCALE_PROVIDER U(https://www.postgresql.org/docs/current/locale.html#LOCALE-PROVIDERS).
          returned: success
          type: str
          sample: en_US.UTF-8
        encoding:
          description:
          - Database encoding U(https://www.postgresql.org/docs/current/multibyte.html).
          returned: success
          type: str
          sample: UTF8
        owner:
          description:
          - Database owner U(https://www.postgresql.org/docs/current/sql-createdatabase.html).
          returned: success
          type: str
          sample: postgres
        size:
          description: Database size in bytes.
          returned: success
          type: str
          sample: 8189415
        extensions:
          description:
          - Extensions U(https://www.postgresql.org/docs/current/sql-createextension.html).
          returned: success
          type: dict
          sample:
          - { "plpgsql": { "description": "PL/pgSQL procedural language",
            "extversion": { "major": 1, "minor": 0, "raw": '1.0' } } }
          contains:
            extdescription:
              description: Extension description.
              returned: if existent
              type: str
              sample: PL/pgSQL procedural language
            extversion:
              description: Extension description.
              returned: success
              type: dict
              contains:
                major:
                  description: Extension major version.
                  returned: success
                  type: int
                  sample: 1
                minor:
                  description: Extension minor version.
                  returned: success
                  type: int
                  sample: 0
                raw:
                  description: Extension full version.
                  returned: success
                  type: str
                  sample: '1.0'
            nspname:
              description: Namespace where the extension is.
              returned: success
              type: str
              sample: pg_catalog
        languages:
          description: Procedural languages U(https://www.postgresql.org/docs/current/xplang.html).
          returned: success
          type: dict
          sample: { "sql": { "lanacl": "", "lanowner": "postgres" } }
          contains:
            lanacl:
              description:
              - Language access privileges
                U(https://www.postgresql.org/docs/current/catalog-pg-language.html).
              returned: success
              type: str
              sample: "{postgres=UC/postgres,=U/postgres}"
            lanowner:
              description:
              - Language owner U(https://www.postgresql.org/docs/current/catalog-pg-language.html).
              returned: success
              type: str
              sample: postgres
        namespaces:
          description:
          - Namespaces (schema) U(https://www.postgresql.org/docs/current/sql-createschema.html).
          returned: success
          type: dict
          sample: { "pg_catalog": { "nspacl": "{postgres=UC/postgres,=U/postgres}", "nspowner": "postgres" } }
          contains:
            nspacl:
              description:
              - Access privileges U(https://www.postgresql.org/docs/current/catalog-pg-namespace.html).
              returned: success
              type: str
              sample: "{postgres=UC/postgres,=U/postgres}"
            nspowner:
              description:
              - Schema owner U(https://www.postgresql.org/docs/current/catalog-pg-namespace.html).
              returned: success
              type: str
              sample: postgres
        publications:
          description:
          - Information about logical replication publications (available for PostgreSQL 10 and higher)
            U(https://www.postgresql.org/docs/current/logical-replication-publication.html).
          - Content depends on PostgreSQL server version.
          returned: if configured
          type: dict
          sample: { "pub1": { "ownername": "postgres", "puballtables": true, "pubinsert": true, "pubupdate": true } }
          version_added: '0.2.0'
        subscriptions:
          description:
          - Information about replication subscriptions (available for PostgreSQL 10 and higher)
            U(https://www.postgresql.org/docs/current/logical-replication-subscription.html).
          - Content depends on PostgreSQL server version.
          - The return values for the superuser and the normal user may differ
            U(https://www.postgresql.org/docs/current/catalog-pg-subscription.html).
          returned: if configured
          type: dict
          sample:
          - { "my_subscription": {"ownername": "postgres", "subenabled": true, "subpublications": ["first_publication"] } }
          version_added: '0.2.0'
repl_slots:
  description:
  - Replication slots (available in 9.4 and later)
    U(https://www.postgresql.org/docs/current/view-pg-replication-slots.html).
  returned: if existent
  type: dict
  sample: { "slot0": { "active": false, "database": null, "plugin": null, "slot_type": "physical" } }
  contains:
    active:
      description:
      - True means that a receiver has connected to it, and it is currently reserving archives.
      returned: success
      type: bool
      sample: true
    database:
      description: Database name this slot is associated with, or null.
      returned: success
      type: str
      sample: acme
    plugin:
      description:
      - Base name of the shared object containing the output plugin
        this logical slot is using, or null for physical slots.
      returned: success
      type: str
      sample: pgoutput
    slot_type:
      description: The slot type - physical or logical.
      returned: success
      type: str
      sample: logical
replications:
  description:
  - Information about the current replications by process PIDs
    U(https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-STATS-VIEWS-TABLE).
  returned: if pg_stat_replication view existent
  type: dict
  sample:
  - { "76580": { "app_name": "standby1", "backend_start": "2019-02-03 00:14:33.908593+03",
    "client_addr": "10.10.10.2", "client_hostname": "", "state": "streaming", "usename": "postgres" } }
  contains:
    usename:
      description:
      - Name of the user logged into this WAL sender process ('usename' is a column name in pg_stat_replication view).
      returned: success
      type: str
      sample: replication_user
    app_name:
      description: Name of the application that is connected to this WAL sender.
      returned: if existent
      type: str
      sample: acme_srv
    client_addr:
      description:
      - IP address of the client connected to this WAL sender.
      - If this field is null, it indicates that the client is connected
        via a Unix socket on the server machine.
      returned: success
      type: str
      sample: 10.0.0.101
    client_hostname:
      description:
      - Host name of the connected client, as reported by a reverse DNS lookup of client_addr.
      - This field will only be non-null for IP connections, and only when log_hostname is enabled.
      returned: success
      type: str
      sample: dbsrv1
    backend_start:
      description: Time when this process was started, i.e., when the client connected to this WAL sender.
      returned: success
      type: str
      sample: "2019-02-03 00:14:33.908593+03"
    state:
      description: Current WAL sender state.
      returned: success
      type: str
      sample: streaming
tablespaces:
  description:
  - Information about tablespaces U(https://www.postgresql.org/docs/current/catalog-pg-tablespace.html).
  returned: success
  type: dict
  sample:
  - { "test": { "spcacl": "{postgres=C/postgres,andreyk=C/postgres}", "spcoptions": [ "seq_page_cost=1" ],
    "spcowner": "postgres" } }
  contains:
    spcacl:
      description: Tablespace access privileges.
      returned: success
      type: str
      sample: "{postgres=C/postgres,andreyk=C/postgres}"
    spcoptions:
      description: Tablespace-level options.
      returned: success
      type: list
      sample: [ "seq_page_cost=1" ]
    spcowner:
      description: Owner of the tablespace.
      returned: success
      type: str
      sample: test_user
roles:
  description:
  - Information about roles U(https://www.postgresql.org/docs/current/user-manag.html).
  returned: success
  type: dict
  sample:
  - { "test_role": { "canlogin": true, "member_of": [ "user_ro" ], "superuser": false,
    "valid_until": "9999-12-31T23:59:59.999999+00:00" } }
  contains:
    canlogin:
      description: Login privilege U(https://www.postgresql.org/docs/current/role-attributes.html).
      returned: success
      type: bool
      sample: true
    member_of:
      description:
      - Role membership U(https://www.postgresql.org/docs/current/role-membership.html).
      returned: success
      type: list
      sample: [ "read_only_users" ]
    superuser:
      description: User is a superuser or not.
      returned: success
      type: bool
      sample: false
    valid_until:
      description:
      - Password expiration date U(https://www.postgresql.org/docs/current/sql-alterrole.html).
      returned: success
      type: str
      sample: "9999-12-31T23:59:59.999999+00:00"
pending_restart_settings:
  description:
  - List of settings that are pending restart to be set.
  returned: success
  type: list
  sample: [ "shared_buffers" ]
settings:
  description:
  - Information about run-time server parameters
    U(https://www.postgresql.org/docs/current/view-pg-settings.html).
  returned: success
  type: dict
  sample:
  - { "work_mem": { "boot_val": "4096", "context": "user", "max_val": "2147483647",
    "min_val": "64", "setting": "8192", "sourcefile": "/var/lib/pgsql/10/data/postgresql.auto.conf",
    "unit": "kB", "vartype": "integer", "val_in_bytes": 4194304 } }
  contains:
    setting:
      description: Current value of the parameter.
      returned: success
      type: str
      sample: 49152
    unit:
      description: Implicit unit of the parameter.
      returned: success
      type: str
      sample: kB
    boot_val:
      description:
      - Parameter value assumed at server startup if the parameter is not otherwise set.
      returned: success
      type: str
      sample: 4096
    min_val:
      description:
      - Minimum allowed value of the parameter (null for non-numeric values).
      returned: success
      type: str
      sample: 64
    max_val:
      description:
      - Maximum allowed value of the parameter (null for non-numeric values).
      returned: success
      type: str
      sample: 2147483647
    sourcefile:
      description:
      - Configuration file the current value was set in.
      - Null for values set from sources other than configuration files,
        or when examined by a user who is neither a superuser or a member of pg_read_all_settings.
      - Helpful when using include directives in configuration files.
      returned: success
      type: str
      sample: /var/lib/pgsql/10/data/postgresql.auto.conf
    context:
      description:
      - Context required to set the parameter's value.
      - For more information see U(https://www.postgresql.org/docs/current/view-pg-settings.html).
      returned: success
      type: str
      sample: user
    vartype:
      description:
      - Parameter type (bool, enum, integer, real, or string).
      returned: success
      type: str
      sample: integer
    val_in_bytes:
      description:
      - Current value of the parameter in bytes.
      returned: if supported
      type: int
      sample: 2147483647
    pretty_val:
      description:
      - Value presented in the pretty form.
      returned: success
      type: str
      sample: 2MB
    pending_restart:
      description:
      - True if the value has been changed in the configuration file but needs a restart; or false otherwise.
      - Returns only if C(settings) is passed.
      returned: success
      type: bool
      sample: false
'''

import re
from fnmatch import fnmatch

from ansible.module_utils._text import to_native
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible_collections.community.postgresql.plugins.module_utils.database import \
    check_input
from ansible_collections.community.postgresql.plugins.module_utils.postgres import (
    connect_to_db,
    ensure_required_libs,
    get_conn_params,
    get_server_version,
    pg_cursor_args,
    postgres_common_argument_spec,
)

# ===========================================
# PostgreSQL module specific support methods.
#


class PgDbConn(object):
    """Auxiliary class for working with PostgreSQL connection objects.

    Arguments:
        module (AnsibleModule): Object of AnsibleModule class that
            contains connection parameters.
    """

    def __init__(self, module):
        self.module = module
        self.db_conn = None
        self.cursor = None

    def connect(self, fail_on_conn=True):
        """Connect to a PostgreSQL database and return a cursor object.

        Note: connection parameters are passed by self.module object.
        """
        # Ensure psycopg libraries are available before connecting to DB:
        ensure_required_libs(self.module)
        conn_params = get_conn_params(self.module, self.module.params, warn_db_default=False)
        self.db_conn, dummy = connect_to_db(self.module, conn_params, fail_on_conn=fail_on_conn)
        if self.db_conn is None:
            # only happens if fail_on_conn is False and there actually was an issue connecting to the DB
            return None
        return self.db_conn.cursor(**pg_cursor_args)

    def reconnect(self, dbname):
        """Reconnect to another database and return a PostgreSQL cursor object.

        Arguments:
            dbname (string): Database name to connect to.
        """
        if self.db_conn is not None:
            self.db_conn.close()

        # the lines below seem redundant but they are actually needed for connect to work as expected
        self.module.params['db'] = dbname
        self.module.params['database'] = dbname
        self.module.params['login_db'] = dbname
        return self.connect(fail_on_conn=False)


class PgClusterInfo(object):
    """Class for collection information about a PostgreSQL instance.

    Arguments:
        module (AnsibleModule): Object of AnsibleModule class.
        db_conn_obj (psycopg.connect): PostgreSQL connection object.
    """

    def __init__(self, module, db_conn_obj):
        self.module = module
        self.db_obj = db_conn_obj
        self.cursor = db_conn_obj.connect()
        self.pg_info = {
            "version": {},
            "in_recovery": None,
            "tablespaces": {},
            "databases": {},
            "replications": {},
            "repl_slots": {},
            "settings": {},
            "roles": {},
            "pending_restart_settings": [],
        }

    def collect(self, val_list=False):
        """Collect information based on 'filter' option."""
        subset_map = {
            "version": self.get_pg_version,
            "in_recovery": self.get_recovery_state,
            "tablespaces": self.get_tablespaces,
            "databases": self.get_db_info,
            "replications": self.get_repl_info,
            "repl_slots": self.get_rslot_info,
            "settings": self.get_settings,
            "roles": self.get_role_info,
        }

        incl_list = []
        excl_list = []
        # Notice: incl_list and excl_list
        # don't make sense together, therefore,
        # if incl_list is not empty, we collect
        # only values from it:
        if val_list:
            for i in val_list:
                if i[0] != '!':
                    incl_list.append(i)
                else:
                    excl_list.append(i.lstrip('!'))

            if incl_list:
                for s in subset_map:
                    for i in incl_list:
                        if fnmatch(s, i):
                            subset_map[s]()
                            break
            elif excl_list:
                found = False
                # Collect info:
                for s in subset_map:
                    for e in excl_list:
                        if fnmatch(s, e):
                            found = True

                    if not found:
                        subset_map[s]()
                    else:
                        found = False

        # Default behaviour, if include or exclude is not passed:
        else:
            # Just collect info for each item:
            for s in subset_map:
                subset_map[s]()

        self.cursor.close()
        self.db_obj.db_conn.close()

        return self.pg_info

    def get_pub_info(self):
        """Get publication statistics."""
        query = ("SELECT p.*, r.rolname AS ownername "
                 "FROM pg_catalog.pg_publication AS p "
                 "JOIN pg_catalog.pg_roles AS r "
                 "ON p.pubowner = r.oid")

        result = self.__exec_sql(query)

        if result:
            result = [dict(row) for row in result]
        else:
            return {}

        publications = {}

        for elem in result:
            if not publications.get(elem['pubname']):
                publications[elem['pubname']] = {}

            for key, val in iteritems(elem):
                if key != 'pubname':
                    publications[elem['pubname']][key] = val

        return publications

    def get_subscr_info(self):
        """Get subscription statistics."""
        columns_sub_table = ("SELECT column_name "
                             "FROM information_schema.columns "
                             "WHERE table_schema = 'pg_catalog' "
                             "AND table_name = 'pg_subscription'")
        columns_result = self.__exec_sql(columns_sub_table)
        columns = ", ".join(["s.%s" % column["column_name"] for column in columns_result])

        query = ("SELECT %s, r.rolname AS ownername, d.datname AS dbname "
                 "FROM pg_catalog.pg_subscription s "
                 "JOIN pg_catalog.pg_database d "
                 "ON s.subdbid = d.oid "
                 "JOIN pg_catalog.pg_roles AS r "
                 "ON s.subowner = r.oid" % columns)

        result = self.__exec_sql(query)

        if result:
            result = [dict(row) for row in result]
        else:
            return {}

        subscr_info = {}

        for elem in result:
            if not subscr_info.get(elem['dbname']):
                subscr_info[elem['dbname']] = {}

            if not subscr_info[elem['dbname']].get(elem['subname']):
                subscr_info[elem['dbname']][elem['subname']] = {}

                for key, val in iteritems(elem):
                    if key not in ('subname', 'dbname'):
                        subscr_info[elem['dbname']][elem['subname']][key] = val

        return subscr_info

    def get_tablespaces(self):
        """Get information about tablespaces."""
        # Check spcoption exists:
        opt = self.__exec_sql("SELECT column_name "
                              "FROM information_schema.columns "
                              "WHERE table_name = 'pg_tablespace' "
                              "AND column_name = 'spcoptions'")

        if not opt:
            query = ("SELECT s.spcname, pg_catalog.pg_get_userbyid(s.spcowner) as rolname, s.spcacl::text "
                     "FROM pg_tablespace AS s ")
        else:
            query = ("SELECT s.spcname, pg_catalog.pg_get_userbyid(s.spcowner) as rolname, s.spcacl::text, s.spcoptions "
                     "FROM pg_tablespace AS s ")

        res = self.__exec_sql(query)
        ts_dict = {}
        for i in res:
            ts_name = i["spcname"]
            ts_info = dict(
                spcowner=i["rolname"],
                spcacl=i["spcacl"] if i["spcacl"] else '',
            )
            if opt:
                ts_info["spcoptions"] = i["spcoptions"] if i["spcoptions"] else []

            ts_dict[ts_name] = ts_info

        self.pg_info["tablespaces"] = ts_dict

    def get_ext_info(self):
        """Get information about existing extensions."""
        # Check that pg_extension exists:
        res = self.__exec_sql("SELECT EXISTS (SELECT 1 FROM "
                              "information_schema.tables "
                              "WHERE table_name = 'pg_extension')")
        if not res[0]["exists"]:
            return True

        query = ("SELECT e.extname, e.extversion, n.nspname, c.description "
                 "FROM pg_catalog.pg_extension AS e "
                 "LEFT JOIN pg_catalog.pg_namespace AS n "
                 "ON n.oid = e.extnamespace "
                 "LEFT JOIN pg_catalog.pg_description AS c "
                 "ON c.objoid = e.oid "
                 "AND c.classoid = 'pg_catalog.pg_extension'::pg_catalog.regclass")
        res = self.__exec_sql(query)
        ext_dict = {}
        for i in res:
            ext_ver_raw = i["extversion"]

            if re.search(r'^([0-9]+([\-]*[0-9]+)?\.)*[0-9]+([\-]*[0-9]+)?$', i["extversion"]) is None:
                ext_ver = [None, None]
            else:
                ext_ver = i["extversion"].split('.')
                if re.search(r'-', ext_ver[0]) is not None:
                    ext_ver = ext_ver[0].split('-')
                else:
                    try:
                        if re.search(r'-', ext_ver[1]) is not None:
                            ext_ver[1] = ext_ver[1].split('-')[0]
                    except IndexError:
                        ext_ver.append(None)

            ext_dict[i["extname"]] = dict(
                extversion=dict(
                    major=int(ext_ver[0]) if ext_ver[0] else None,
                    minor=int(ext_ver[1]) if ext_ver[1] else None,
                    raw=ext_ver_raw,
                ),
                nspname=i["nspname"],
                description=i["description"],
            )

        return ext_dict

    def get_role_info(self):
        """Get information about roles (in PgSQL groups and users are roles)."""
        query = ("SELECT r.rolname, r.rolsuper, r.rolcanlogin, "
                 "r.rolvaliduntil, "
                 "ARRAY(SELECT b.rolname "
                 "FROM pg_catalog.pg_auth_members AS m "
                 "JOIN pg_catalog.pg_roles AS b ON (m.roleid = b.oid) "
                 "WHERE m.member = r.oid) AS memberof "
                 "FROM pg_catalog.pg_roles AS r "
                 "WHERE r.rolname !~ '^pg_'")

        res = self.__exec_sql(query)
        rol_dict = {}
        for i in res:
            rol_dict[i["rolname"]] = dict(
                superuser=i["rolsuper"],
                canlogin=i["rolcanlogin"],
                valid_until=i["rolvaliduntil"] if i["rolvaliduntil"] else '',
                member_of=i["memberof"] if i["memberof"] else [],
            )

        self.pg_info["roles"] = rol_dict

    def get_rslot_info(self):
        """Get information about replication slots if exist."""
        # Check that pg_replication_slots exists:
        res = self.__exec_sql("SELECT EXISTS (SELECT 1 FROM "
                              "information_schema.tables "
                              "WHERE table_name = 'pg_replication_slots')")
        if not res[0]["exists"]:
            return True

        query = ("SELECT slot_name, plugin, slot_type, database, "
                 "active FROM pg_replication_slots")
        res = self.__exec_sql(query)

        # If there is no replication:
        if not res:
            return True

        rslot_dict = {}
        for i in res:
            rslot_dict[i["slot_name"]] = dict(
                plugin=i["plugin"],
                slot_type=i["slot_type"],
                database=i["database"],
                active=i["active"],
            )

        self.pg_info["repl_slots"] = rslot_dict

    def get_settings(self):
        """Get server settings."""
        # Check pending restart column exists:
        pend_rest_col_exists = self.__exec_sql("SELECT 1 FROM information_schema.columns "
                                               "WHERE table_name = 'pg_settings' "
                                               "AND column_name = 'pending_restart'")
        if not pend_rest_col_exists:
            query = ("SELECT name, setting, unit, context, vartype, "
                     "boot_val, min_val, max_val, sourcefile "
                     "FROM pg_settings")
        else:
            query = ("SELECT name, setting, unit, context, vartype, "
                     "boot_val, min_val, max_val, sourcefile, pending_restart "
                     "FROM pg_settings")

        res = self.__exec_sql(query)

        set_dict = {}
        for i in res:
            val_in_bytes = None
            setting = i["setting"]
            if i["unit"]:
                unit = i["unit"]
            else:
                unit = ''

            if unit == 'kB':
                val_in_bytes = int(setting) * 1024

            elif unit == '8kB':
                val_in_bytes = int(setting) * 1024 * 8

            elif unit == 'MB':
                val_in_bytes = int(setting) * 1024 * 1024

            if val_in_bytes is not None and val_in_bytes < 0:
                val_in_bytes = 0

            setting_name = i["name"]
            pretty_val = self.__get_pretty_val(setting_name)

            pending_restart = None
            if pend_rest_col_exists:
                pending_restart = i["pending_restart"]

            set_dict[setting_name] = dict(
                setting=setting,
                unit=unit,
                context=i["context"],
                vartype=i["vartype"],
                boot_val=i["boot_val"] if i["boot_val"] else '',
                min_val=i["min_val"] if i["min_val"] else '',
                max_val=i["max_val"] if i["max_val"] else '',
                sourcefile=i["sourcefile"] if i["sourcefile"] else '',
                pretty_val=pretty_val,
            )
            if val_in_bytes is not None:
                set_dict[setting_name]['val_in_bytes'] = val_in_bytes

            if pending_restart is not None:
                set_dict[setting_name]['pending_restart'] = pending_restart
                if pending_restart:
                    self.pg_info["pending_restart_settings"].append(setting_name)

        self.pg_info["settings"] = set_dict

    def get_repl_info(self):
        """Get information about replication if the server is a primary."""
        # Check that pg_replication_slots exists:
        res = self.__exec_sql("SELECT EXISTS (SELECT 1 FROM "
                              "information_schema.tables "
                              "WHERE table_name = 'pg_stat_replication')")
        if not res[0]["exists"]:
            return True

        query = ("SELECT r.pid, pg_catalog.pg_get_userbyid(r.usesysid) AS rolname, r.application_name, r.client_addr::text, "
                 "r.client_hostname, r.backend_start::text, r.state "
                 "FROM pg_stat_replication AS r ")
        res = self.__exec_sql(query)

        # If there is no replication:
        if not res:
            return True

        repl_dict = {}
        for i in res:
            repl_dict[i["pid"]] = dict(
                usename=i["rolname"],
                app_name=i["application_name"] if i["application_name"] else '',
                client_addr=i["client_addr"],
                client_hostname=i["client_hostname"] if i["client_hostname"] else '',
                backend_start=i["backend_start"],
                state=i["state"],
            )

        self.pg_info["replications"] = repl_dict

    def get_lang_info(self):
        """Get information about current supported languages."""
        query = ("SELECT l.lanname, pg_catalog.pg_get_userbyid(l.lanowner) AS rolname, l.lanacl::text "
                 "FROM pg_language AS l ")
        res = self.__exec_sql(query)
        lang_dict = {}
        for i in res:
            lang_dict[i["lanname"]] = dict(
                lanowner=i["rolname"],
                lanacl=i["lanacl"] if i["lanacl"] else '',
            )

        return lang_dict

    def get_namespaces(self):
        """Get information about namespaces."""
        query = ("SELECT n.nspname, pg_catalog.pg_get_userbyid(n.nspowner) AS rolname, n.nspacl::text "
                 "FROM pg_catalog.pg_namespace AS n ")
        res = self.__exec_sql(query)

        nsp_dict = {}
        for i in res:
            nsp_dict[i["nspname"]] = dict(
                nspowner=i["rolname"],
                nspacl=i["nspacl"] if i["nspacl"] else '',
            )

        return nsp_dict

    def get_pg_version(self):
        """Get major and minor PostgreSQL server version."""
        query = "SELECT current_setting('server_version_num')"
        srv_ver = self.__exec_sql(query)[0]["current_setting"]
        query = "SELECT version()"
        raw = self.__exec_sql(query)[0]["version"]

        major = int(srv_ver[0:2])
        minor = int(srv_ver[2:4])
        patch = int(srv_ver[4:6])

        if minor == 0:
            # PG 10+
            full = '.'.join([str(major), str(patch)])
        else:
            # PG < 10
            full = '.'.join([str(major), str(minor), str(patch)])

        self.pg_info["version"] = dict(
            major=major,
            minor=minor,
            patch=patch,
            full=full,
            raw=raw,
        )

        if minor == 0:
            self.pg_info["version"]["minor"] = patch
            self.pg_info["version"]["patch"] = None

    def get_recovery_state(self):
        """Get if the service is in recovery mode."""
        self.pg_info["in_recovery"] = self.__exec_sql("SELECT pg_is_in_recovery()")[0]["pg_is_in_recovery"]

    def get_db_info(self):
        """Get information about the current database."""
        # Following query returns:
        # Name, Owner, Encoding, Collate, Ctype, Access Priv, Size
        query = ("SELECT d.datname, "
                 "pg_catalog.pg_get_userbyid(d.datdba) AS username, "
                 "pg_catalog.pg_encoding_to_char(d.encoding) AS encoding, "
                 "d.datcollate, "
                 "d.datctype, "
                 "pg_catalog.array_to_string(d.datacl, E'\n') aclstring, "
                 "CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT') "
                 "THEN pg_catalog.pg_database_size(d.datname)::text "
                 "ELSE 'No Access' END as dbsize, "
                 "t.spcname "
                 "FROM pg_catalog.pg_database AS d "
                 "JOIN pg_catalog.pg_tablespace t ON d.dattablespace = t.oid "
                 "WHERE d.datname != 'template0'")

        res = self.__exec_sql(query)

        db_dict = {}
        for i in res:
            db_dict[i["datname"]] = dict(
                owner=i["username"],
                encoding=i["encoding"],
                collate=i["datcollate"],
                ctype=i["datctype"],
                access_priv=i["aclstring"] if i["aclstring"] else '',
                size=i["dbsize"],
            )

        if get_server_version(self.cursor.connection) >= 100000:
            subscr_info = self.get_subscr_info()

        for datname in db_dict:
            self.cursor = self.db_obj.reconnect(datname)
            if self.cursor is None:
                # that means we don't have permission to access these database
                db_dict[datname]['namespaces'] = {}
                db_dict[datname]['extensions'] = {}
                db_dict[datname]['languages'] = {}
                db_dict[datname]['error'] = "Could not connect to the database."
                continue
            db_dict[datname]['namespaces'] = self.get_namespaces()
            db_dict[datname]['extensions'] = self.get_ext_info()
            db_dict[datname]['languages'] = self.get_lang_info()
            if get_server_version(self.cursor.connection) >= 100000:
                db_dict[datname]['publications'] = self.get_pub_info()
                db_dict[datname]['subscriptions'] = subscr_info.get(datname, {})

        self.pg_info["databases"] = db_dict

    def __get_pretty_val(self, setting):
        """Get setting's value represented by SHOW command."""
        return self.__exec_sql('SHOW "%s"' % setting)[0][setting]

    def __exec_sql(self, query):
        """Execute SQL and return the result."""
        try:
            self.cursor.execute(query)
            res = self.cursor.fetchall()
            if res:
                return res
        except Exception as e:
            self.module.fail_json(msg="Cannot execute SQL '%s': %s" % (query, to_native(e)))
            self.cursor.close()
        return False

# ===========================================
# Module execution.
#


def main():
    argument_spec = postgres_common_argument_spec()
    argument_spec.update(
        db=dict(type='str', aliases=['login_db']),
        filter=dict(type='list', elements='str'),
        session_role=dict(type='str'),
        trust_input=dict(type='bool', default=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    filter_ = module.params['filter']

    if not module.params['trust_input']:
        # Check input for potentially dangerous elements:
        check_input(module, module.params['session_role'])

    db_conn_obj = PgDbConn(module)

    # Do job:
    pg_info = PgClusterInfo(module, db_conn_obj)

    module.exit_json(**pg_info.collect(filter_))


if __name__ == '__main__':
    main()
