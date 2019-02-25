# Project structure

Q: Where is the entrypoint module which is loaded by mod_wsgi?

```
sdnms_api/app/wsgi.py

The entrypoint module must return an application object.
```

Q: Where is the main module which creates `application` object?

```
sdnms_api/app/server.py

The main module must
* load configuration file
* load command line arguments
* register RESTful API routes
* register WSGI middlewares
* launch dev http server if needed
```

Q: How do we organize the backend via some sort of plugin mechanism?

About plugin invocation patterns see [this](https://docs.openstack.org/stevedore/latest/user/essays/pycon2013.html)

```
Use driver pattern

Each driver has its own configuration file in which specifies backend endpoint and access credential.

There are 3 driver types
* FW
* WAF
* SWITCH
```

Q: How do we load the backend plugin?

```
We leverage stevedore.
```

Q: How do we organize the configuration file?

```
There is are a main configuraiton file and many backend configuraiton files.

The main configuration file specifies
* db connection string
* log file location
* backend driver type
  * fw
  * waf
  * switch

These configuraiton files are .ini files.
* etc/sdnms_api/sdnms_api.ini
* etc/sdnms_api/sdnms_api_dev.ini
* etc/sdnms_api/backends/fw_fortinet_v5.6.3.ini
* etc/sdnms_api/backends/fw_paloalto_v?.ini
* etc/sdnms_api/backends/waf_f5_v13.1.ini
* etc/sdnms_api/backends/switch_mellanox_neo_v?.ini
* etc/sdnms_api/backends/switch_mellanox_v?.ini
```

Q: How do we load the configuration file?

```
mod sdnms_api/app/server.py

We leverage oslo.config to load the configuration file.
```

Q: How do we organize the routing code?

```
All routing code are put in the sdnms_api/resources/ folder.

If you need create a new resource
e.g., my_resource, add sdnms_api/resources/my_resource.py
```

Q: How do we load the routing code?

```
mod sdnms_api/config.py
mod sdnms_api/app/server.py
```

Q: How do we organize the middleware code?

```
All middleware code are put in the sdnms_api/middlewares/ folder.

If you need create a new middleware
e.g., my_middleware, add sdnms_api/middlewares/my_middleware.py
```

Q: How do we load the middleware code?

```
mod sdnms_api/app/server.py
```

Q: How do we organize the model code?

```
All model code are put in the sdnms_api/models/ folder.

If you need create a new model
e.g., my_model, add sdnms_api/models/my_model.py
```

Q: How do we organize the falcon media code?

```
All falcon media code are put in the sdnms_api/medium/ folder.
```

Q: How do we use the logging function?

```
We leverage oslo.log.
```

Q: How do we map the RESTful API to the backend driver?

```
Maybe like DB Connection founctional. (Alan)
```