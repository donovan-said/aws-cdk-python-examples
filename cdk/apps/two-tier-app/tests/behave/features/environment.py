#!/usr/bin/env python3


def before_all(context):
    userdata = context.config.userdata
    if userdata["env"] == "dev":
        context.domain = "{INSERT_DOMAIN}"
    elif userdata["env"] == "uat":
        context.domain = "{INSERT_DOMAIN}"
    elif userdata["env"] == "prod":
        context.domain = "{INSERT_DOMAIN}"
