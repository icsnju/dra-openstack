# coding: utf-8

from .OpenstackService import *
from ..Conf import OpenstackConf
from ...Utils.HttpUtil import OpenstackRestful
from .Nova import Nova

import time
import datetime
import ceilometerclient.client


CEILOMETER_CLIENT_VERSION = 2
# TODO read threshold from conf file
OVERLOAD_OTF_THRESHOLD = 4


class Ceilometer(OpenstackService):

    def __init__(self):
        OpenstackService.__init__(self)
        self.cclient = ceilometerclient.client.get_client(
                CEILOMETER_CLIENT_VERSION,
                os_username=OpenstackConf.USERNAME,
                os_password=OpenstackConf.PASSWORD,
                os_tenant_name=OpenstackConf.TENANTNAME,
                os_auth_url=OpenstackConf.AUTH_URL+'/v2.0/'
        )

    def get_rest_data(self, url):
        """
        Use GET Method to fetch data from url
        @param url:
        @return:
        """
        try:
            return self.restful.get_req(url)
        except:
            print "Token expires, update it now.."
            self.update_token()
            return self.restful.get_req(url)

    def getAllMeters(self):
        url = "%s/v2/meters" % OpenstackConf.CEILOMETER_URL
        result = self.get_rest_data(url)
        return result

    def getAllResources(self):
        url = "%s/v2/resources" % OpenstackConf.CEILOMETER_URL
        result = self.get_rest_data(url)
        return result

    def getMeter(self, meter_name, queryFilter):
        url = "%s/v2/meters/%s" % (OpenstackConf.CEILOMETER_URL, meter_name)

        #transfer str to list
        queryFilter = eval(queryFilter)

        params = ""
        for queryItem in queryFilter:
            param = ""
            for key in queryItem:
                param += "&q.%s=%s" % (key, queryItem[key])
            params += param

        url = url + "?" + params

        result = self.get_rest_data(url)
        return result[0]

    def getMeterStatistics(self, meter_name, queryFilter, groupby = None, period = None, aggregate = None):
        url = "%s/v2/meters/%s/statistics" % (OpenstackConf.CEILOMETER_URL, meter_name)

        #transfer str to list
        queryFilter = eval(queryFilter)
        #print queryFilter

        params = ""
        for queryItem in queryFilter:
            param = ""
            for key in queryItem:
                param += "&q.%s=%s" % (key, queryItem[key])
            params += param

        url = url + "?" + params

        result = self.get_rest_data(url)
        if result:
            return result[0]
        else:
            print "query result is None"
            return None

    def get_resource_meter_sample_list(self, resource_id, n, meter_name):
        """
        Get meter sample list of resource(vm or pm), with filter specified in query
        :param resource_id: uuid of vm or hostname
        :param n: num of hours to get samples
        :param meter_name: samples' type, such as 'cpu', 'cpu_util'
        :return: list of samples values
        """
        now_time = time.gmtime()
        end_time = datetime.datetime(*now_time[:6])
        begin_time = end_time - datetime.timedelta(hours=n)

        query_filter = [
            dict(field='resource_id', op='eq', value=resource_id),
            dict(field='timestamp', op='ge', value=begin_time.isoformat()),
            dict(field='timestamp', op='lt', value=end_time.isoformat()),
        ]
        samples = self.cclient.samples.list(meter_name=meter_name, q=query_filter)
        info = list()
        for s in samples:
            info.append(s.counter_volume)
        return info
    
    def last_n_average_statistic(self, n, resource_id, meter_name='compute.node.cpu.percent'):
        """
        get last n hours meter statistics
        @param n:
        @param meter_name:
        @param resource_id:
        @return:
        """
        now_time = time.gmtime()
        end_time = datetime.datetime(*now_time[:6])
        begin_time = end_time - datetime.timedelta(hours=n)

        qry = '''[{"field": "timestamp",
        "op": "ge",
        "value": "%s"},
        {"field": "timestamp",
        "op": "lt",
        "value": "%s"},
        {"field": "resource_id",
        "op": "eq",
        "value": "%s"}]''' % (begin_time.isoformat(), end_time.isoformat(), resource_id)
        statistics = self.getMeterStatistics(meter_name, qry)
        if statistics:
            return statistics['avg']
        else:
            return 0

    def last_n_otf_statistic(self, n, hostname, meter_name='compute.node.cpu.percent'):
        """
        NOTE: overload_time and total_time is not actually time, but num of samples
        during n hours
        :param n: last n hours
        :param hostname: host to get otf time
        :return: two time value
        @param otf_threshold:
        """
        overload_num = 0
        samples = self.get_resource_meter_sample_list(hostname+'_'+hostname, n, meter_name)
        total_num = len(samples)
        for s in samples:
            if s > OVERLOAD_OTF_THRESHOLD:
                overload_num += 1
        return overload_num, total_num


if __name__ == "__main__":
    now_t = time.gmtime()
    end_t = datetime.datetime(*now_t[:6])
    begin_t = end_t - datetime.timedelta(hours=1)

    ceilometerTest = Ceilometer()

    """
    q = '''[{"field": "timestamp",
    "op": "ge",
    "value": "%s"},
    {"field": "timestamp",
    "op": "lt",
    "value": "%s"},
    {"field": "resource_id",
    "op": "eq",
    "value": "34033067-3f85-4fa9-a6af-22ef4f6d9f94"}]''' % (begin_t.isoformat(), end_t.isoformat())
    """
    q = '''[{"field": "timestamp",
    "op": "ge",
    "value": "2016-04-06T00:00:00"},
    {"field": "timestamp",
    "op": "lt",
    "value": "2016-04-06T02:00:00"},
    {"field": "resource_id",
    "op": "eq",
    "value": "compute1_compute1"}]'''

    q2 = '''[{"field": "resource_id",
    "op": "eq",
    "value": "4071a9ba-5fa2-4dbd-a9be-36c230e0eafe"}]'''

    # print ceilometerTest.getMeterStatistics("compute.node.cpu.percent", q)
    # print ceilometerTest.last_n_average_statistic(1, '2aebe8ae-1f08-4301-ae55-9aa50aa13db6', 'cpu_util')
    print ceilometerTest.last_n_average_statistic(1, 'compute1_compute1')
    print ceilometerTest.last_n_average_statistic(1, 'compute0_compute0')
    # print ceilometerTest.getMeter("compute.node.cpu.percent", q)
    # print ceilometerTest.getCpuStat("2014-12-12T00:00:00", "2014-12-16T00:00:00",
    #                                 "feebf6dc-2f04-4e1d-977e-6c7fde4e4cb3")
    # print ceilometerTest.getAllResources()
    # print ceilometerTest.get_resource_meter_sample_list('34033067-3f85-4fa9-a6af-22ef4f6d9f94', 1, 'cpu_util')
