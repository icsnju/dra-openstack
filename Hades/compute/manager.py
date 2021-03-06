# -*- coding: utf-8 -*_

import socket
import datetime
import logging
import oslo_messaging as messaging
from oslo_config import cfg
from ..Manager import Manager

from ...Openstack.Service.Nova import Nova
from ...Openstack.Conf import OpenstackConf
from ..controller.rpcapi import ControllerManagerApi
from ...Openstack.Service.Nova import Nova
from ...detector import (
    overload,
    underload,
    vm_selection
)


CONF = cfg.CONF
_nova = Nova()

UNDERLOAD_THRESHOLD = 0
OVERLOAD_THRESHOLD = 80
TIME_LENGTH = 1  # for 1 hour statistics
HOSTNAME = socket.gethostname()
logger = logging.getLogger("DRA.computeService")


class ComputeManager(Manager):
    """
    @doc:
    """
    target = messaging.Target()

    def __init__(self, *args, **kwargs):
        super(ComputeManager, self).__init__(service_name='hades_compute_manager', 
                *args, **kwargs)


    def res_health_check(self, ctxt):
        """
        receive a req from controller to check node's health, underload or overload
        """
        logger.info(socket.gethostname() + " resource health check.")
        controller_api = ControllerManagerApi(CONF.hades_controller_topic, CONF.hades_exchange)
        node_info = {}
        node_info['res'] = _nova.inspect_host(HOSTNAME)

        underld = underload.last_n_average_threshold(UNDERLOAD_THRESHOLD, 
                TIME_LENGTH, HOSTNAME)
        overld = overload.last_n_average_threshold(0, OVERLOAD_THRESHOLD,
                TIME_LENGTH, HOSTNAME)

        if underld:
            logger.info("underload detected...")
            node_info["status"] = "underload"
            node_info["select_vms"] = []
        elif overld:
            logger.info("overload detected...")
            node_info["status"] = "overload"
            # NOTE: change this to OD_based selecetion
            node_info["select_vms"] = vm_selection.od_vm_select(HOSTNAME, TIME_LENGTH)
            logger.info("OD selected VMS: " + str(node_info["select_vms"]))
        else:
            logger.info("Node: " + HOSTNAME + "'s resource status is ok...\n")
            node_info["status"] = "healthy"
            node_info["select_vms"] = []

        controller_api.collect_compute_info({}, HOSTNAME, node_info)
