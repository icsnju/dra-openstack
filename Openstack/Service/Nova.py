# -*- coding: utf-8 -*-
from .OpenstackService import *
from ...Utils.HttpUtil import OpenstackRestful
from ..Conf import OpenstackConf


class Nova(OpenstackService):

    def __init__(self):

        OpenstackService.__init__(self)

    def get_rest_data(self, url):
        try:
            return self.restful.get_req(url)
        except:
            print "Token expires, update it now..."
            self.update_token()
            return self.restful.get_req(url)

    def post_rest_data(self, url, data):
        try:
            self.restful.post_req(url, data)
        except:
            print "Token expires, update it now..."
            self.update_token()
            self.restful.post_req(url, data)

    def getInstances(self):
        """
        get instances that belong to a tenant
        """
        url = "%s/v2/%s/servers" % (OpenstackConf.NOVA_URL, self.tenantId)

        result = self.get_rest_data(url)
        servers = result['servers']
        instances = []
        for s in servers:
            instances.append(str(s['id']))
        return instances

    def getInstancesOnHost(self, host):
        url = "%s/v2/%s/servers?host=%s" % (OpenstackConf.NOVA_URL, self.tenantId, host)

        result = self.get_rest_data(url)
        servers = result['servers']

        instances = []
        for s in servers:
            instances.append(str(s['id']))

        return instances

    def getComputeHosts(self):
        url = "%s/v2/%s/os-hosts" % (OpenstackConf.NOVA_URL, self.tenantId)
        result = self.get_rest_data(url)
        hostsList = result['hosts']
        hosts = []
        for host in hostsList:
            if host['service'] == 'compute':
                hosts.append(str(host['host_name']))
        return hosts

    def inspect_host(self, host):
        """
        Get the detail msg of a specific host
        :param host: host to inspect
        :return: dict info of a host
        """
        url = "%s/v2/%s/os-hosts/%s" % (OpenstackConf.NOVA_URL, self.tenantId, host)
        results = self.get_rest_data(url)['host']
        assert results[0]['resource']['project'] == '(total)'
        assert results[1]['resource']['project'] == '(used_now)'
        info = dict()
        info['cpu'] = {'total': results[0]['resource']['cpu'], 'used': results[1]['resource']['cpu']}
        info['mem'] = {'total': results[0]['resource']['memory_mb'], 'used': results[1]['resource']['memory_mb']}
        info['disk'] = {'total': results[0]['resource']['disk_gb'], 'used': results[1]['resource']['disk_gb']}
        return info

    def inspect_flavor(self, flavor_id):
        """
        Get openstack flavor info by its id, flavor contains vm's config of cpu virtual core num, ram and disk size
        :param flavor_id: id of the flavor
        :return: flavor info, disk in GB, RAM in MB, vpus num
        """
        url = "{0}/v2/{1}/flavors/{2}".format(OpenstackConf.NOVA_URL, self.tenantId, flavor_id)
        results = self.get_rest_data(url)['flavor']
        return results

    def inspect_instance(self, vm_uuid):
        """
        Get detail info of a instance
        :param vm_uuid: the uuid of the instance
        :return: dict info of the instance
        """
        url = "{0}/v2/{1}/servers/{2}".format(OpenstackConf.NOVA_URL, self.tenantId, vm_uuid)
        info = self.get_rest_data(url)['server']
        flavor_id = info['flavor']['id']
        flavor_info = self.inspect_flavor(flavor_id)
        info['disk'] = flavor_info['disk']
        info['cpu'] = flavor_info['vcpus']
        info['ram'] = flavor_info['ram']
        return info

    def liveMigration(self, instance_id, host):
        """ live migrate an instance to dest host
        @param instance_id:
        @param host:
        """
        url = "{base}/v2/{tenant}/servers/{instance}/action".format(base=OpenstackConf.NOVA_URL,
                                                                    tenant=self.tenantId, instance=instance_id)
        values = {"os-migrateLive": {"block_migration": "true", "host": host, 'disk_over_commit': "false"}}
        self.post_rest_data(url, values)

    def get_interhost_bandwidth(self, host):
        """
        Get bandwidth between the specific host and others
        :param host: the specific host
        :return dict type of bandwidth msg
        @param host:
        @return:
        """
        import random
        # TODO get real bandwidth between hosts(MB/s)
        hosts = self.getComputeHosts()
        hosts.remove(host)
        bd = dict()
        for h in hosts:
            bd[h] = random.uniform(5, 10)
        return bd


if __name__ == "__main__":
    nova = Nova()
    # print nova.getInstances()
    # for instance in instances:
    #    print instance.getId()
    #
    # host = Host("compute1", OpenstackConf.COMPUTE1_HOST)
    #
    # Nova.liveMigration(instances[0], host)
    # hosts = nova.getHosts()
    # for host in hosts:
    #    print host.getHostName()
    #
    # nova.liveMigration('4071a9ba-5fa2-4dbd-a9be-36c230e0eafe', "compute1")
    print nova.inspect_host('compute1')
    # print nova.getInstancesOnHost('compute1')
    # nova.liveMigration('007a49ac-9f7e-4440-8b3d-514b4737879f', "compute1")
    # print nova.getComputeHosts()
    # nova.test('compute1')
    # print nova.inspect_host('compute1')
    # print nova.inspect_instance('c3f12b05-d9ed-4691-a41e-4de8def65d58')['disk']
