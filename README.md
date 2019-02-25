# Scope

* relay API call from CMP to backends (one to one. **DO NOT issue additional subsequent API call i.e. NO workflow control !!! NO operation rollback !!!**)
* record the relationship between CMP object and backend object

# Future scope

* SFC
* 1 site -> 2 sites -> 3 sites (i.e. sdnms cluster)

# Arch.

```
----------------------------------------------
|                   CMP                      |
----------------------------------------------
                      |
                    -----
                    |vip|
                    -----
                /           \
            /                   \
        /                           \
-------------------            -------------------
| RESTful API -|  |            | RESTful API -|  |
|              |  |            |              |  |
| [ Active ]   |  | -> sync -> | [ Standby ]  |  |
|              |  |            |              |  |
|-----         |  |            |-----         |  |
| DB | <-------|  |            | DB | <-------|  |
-------------------            -------------------
    \                               /
        \                       /
            \               /
                \       /
                    \/
                    |
                SSH | HTTPS
                    |
                    v
----------------------------------------------
|   |   |   |   |   Backends     |   |   |   |
----------------------------------------------
```

Lifecycle

```
AP mode -> Master fails (unplanned outage) -> Auto-failover (promote the slave to master) -> Manually turn the original master to new slave -> |
^       \                                                                               /                                                      |
|        \ -> Planned outage for master -> Switchover (promote the slave to master) -> /                                                       |
|                                                                                                                                              |
|----------------------------------------------------------------------------------------------------------------------------------------------|
```

RESTful API Internal

```
    +-------------------+
    | Route             |
    +-------------------+
            ^
            |
            v
    +-------------------+
    | Resource          |
    +-------------------+
            ^
            |
            v
    +-------------------+
    | BackendManager    |
    +-------------------+
            ^
            |
            v
    +-------------------+
    | DriverManager     |
    +-------------------+
            ^
            |
            v
    +-------------------+
    | Driver            |
    +-------------------+
```

Notice

* The unplanned outage may lose 1 or 2 transacation(s).
* CMP need implement some sort of retry during the failover.
* RESTful API layer need issue a query to confirm whether write commit is replicated to slave or not during the failover

# Milestones

1. Prototype of AP mode stateful RESTful API server (1 ~ 2 weeks)
2. Implementation of backends client librabry (1 ~ 2 weeks)
3. Clarification of CMP use cases, RESTful API spec, DB schema, backend API usage, backend instance selection (4 ~ 8 weeks)
4. Implementation of RESTful API (2 ~ 4 weeks)

# Milestone 1 :: Prototype of AP mode stateful RESTful API server

* vip : Keepalived v1.3.5 (the current version provided by CentOS v7.4 yum repo)
* RESTful API
  * Programming language : Python v2.7.5 (the built-in Python version of CentOS v7.4)
  * Framework : Falcon (the same framework used in monasca-api project)
      * https://pypi.python.org/pypi/falcon/1.4.1 (latest)
  * 3rd-party library :
      * https://pypi.python.org/pypi/SQLAlchemy/1.2.6 (latest)
      * https://pypi.python.org/pypi/requests/2.18.4 (latest)
      * https://pypi.python.org/pypi/paramiko/2.4.1 (latest) (optional)
      * https://pypi.python.org/pypi/prometheus_client/0.2.0 (lastest) (optional)
  * Web server : Apache httpd v2.4.6 (the current version provided by CentOS v7.4 yum repo)
      * mod_wsgi 
* DB replication & failover solution
  * ~~SQLite + rsync~~
  * MariaDB v10.2 + MariaDB transaction-based async replication + Keepalived tracking script + Keepalived notification script
      * Topology : master(rw) - - async - - > backup master(ro)
* OS : CentOS v7.4

References

* [Why don't we use rsync + SQLite as our DB replication & failover solution?](https://serverfault.com/questions/89329/rsync-sqlite-database)
* [Two Node Planned Manual Failover for the MySQL Database Administrator](https://www.databasejournal.com/features/mysql/article.php/3890596/Two-Node-Planned-Manual-Failover-for-the-MySQL-Database-Administrator.htm)
* Who and how use Falcon framework
  * https://github.com/openstack/monasca-api
  * https://github.com/openstack/monasca-events-api
  * https://github.com/openstack/monasca-log-api
* [Example of one project with two top python packages](https://github.com/openstack/monasca-agent)
* [How to select specific the cipher while sending request via python request module](https://stackoverflow.com/questions/40373115/how-to-select-specific-the-cipher-while-sending-request-via-python-request-modul)
* [How to select specific the ssl/tls protocol while sending request via python request module](https://www.pydoc.io/pypi/requests-2.11.1/autoapi/ssl_/index.html)
* [How to send https request via urllib2+httplib](https://blog.csdn.net/ns2250225/article/details/79528827)

# Milestone 2 :: Implementation of backends client librabry

Backends List

* 1 ~ N WAF
* 1 ~ N FW
* N SWITCH
* 1 Neo?
* 1 ~ N Neutron Server?

Note

* use super administrator privilege to access backend API

# Milestone 3 :: Clarification of CMP use cases, RESTful API spec, DB schema, backend API usage, backend instance selection

CMP Use Cases

* TBD
* TBD
* TBD

RESTful API Spec

* Category 1 :: init .. priority 2 (out of scope)
* Category 2 :: user .. priority 1
  * TBD
  * TBD
  * TBD

DB Schema

* TBD
* TBD
* TBD

Backend API ~~(one use case one sequence diagram)~~

* TBD
* TBD
* TBD

# Milestone 4 :: Implementation of RESTful API
