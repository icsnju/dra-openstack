__author__ = 'pike'

# in our simulation, the workload refers to the load of each hour in a day, and is periodical
# each host has 24 vcpu and allocate 2 vcpu to each instance
# each host has 1G bandwidth each instance usually use 100M

import threading
import random
import matplotlib.pyplot as plt

#global host and instance list
host_list = {}
instance_list = {}
time_count = 0

host_distance_matrix = [[0.5, 2, 3, 4],
                        [2, 0.5, 2, 3],
                        [3, 2, 0.5, 2],
                        [4, 3, 2, 0.5]]

host_mapper = {'host_1' : 0, 'host_2' : 1, 'host_3' : 2, 'host_4' : 3}

#enum
class ResourceType:
    (CPU_UTIL, BANDWIDTH, DISK_IO) = ('CPU_UTIL', 'BANDWIDTH', 'DISK_IO')

class InstanceType:
    (ALL, MATLAB_1, MATLAB_1_MASTER, MATLAB_2, MATLAB_2_MASTER, WEB_SERVER_1, GAME_1, STORAGE_1) = ('ALL', 'MATLAB_1', 'MATLAB_1_MASTER', 'MATLAB_2', 'MATLAB_2_MASTER', 'WEB_SERVER_1', 'GAME_1', 'STORAGE_1')

############################################### base entity ###############################################

class Host(object):
    def __init__(self, hostId, host_list):
        self.id = hostId
        self.vCpu = 24
        self.bandwidth = 1000
        self.instanceList = {}

        #add to host_list
        host_list[self.id] = self

        #use lock to ensure one thread modify the instanceList
        self.lock = threading.RLock()

    def getId(self):
        return self.id

    def addInstance(self, instance):
        self.lock.acquire()
        self.instanceList[instance.getId()] = instance
        self.lock.release()

    def removeInstance(self, instance):
        self.lock.acquire()
        del self.instanceList[instance.getId()]
        self.lock.release()

    def getInstanceNum(self, instanceType):
        return len(self.getInstance(instanceType))

    def getInstance(self, instanceType):
        result = []
        for instanceId in self.instanceList:
            instance = self.instanceList[instanceId]
            if instanceType == InstanceType.ALL:
                result.append(instance)
            elif instance.getType() == instanceType:
                result.append(instance)
        return result

    def getStatisticData(self, flag, resourceType, time, interval):
        if resourceType == ResourceType.CPU_UTIL:
            total = 0
            for instanceId in self.instanceList:
                instance = self.instanceList[instanceId]
                total += instance.getStatisticData(flag, resourceType, time, interval)
            return total / (self.vCpu / 2)
        elif resourceType == ResourceType.BANDWIDTH:
            total = 0
            for instanceId in self.instanceList:
                instance = self.instanceList[instanceId]
                total += instance.getStatisticData(flag, resourceType, time, interval)
            return total
        elif resourceType == ResourceType.DISK_IO:
            pass
        else:
            print 'invalid resourceType'
            return None



class Instance(object):
    def __init__(self, instanceId, instanceType, host, instance_list):
        self.id = instanceId
        self.type = instanceType

        #add instance to host
        self.host = host
        self.host.addInstance(self)

        #add instance to instance_list
        instance_list[self.id] = self

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def getHost(self):
        return self.host

    def setHost(self, host):
        self.host = host

    def getStatisticData(self, flag, resourceType, time, interval):
        # judge the resource type
        generateFunc = None
        if resourceType == ResourceType.CPU_UTIL:
            generateFunc = self.generateCpuUtil
        elif resourceType == ResourceType.BANDWIDTH:
            generateFunc = self.generateBandwidth
        elif resourceType == ResourceType.DISK_IO:
            generateFunc = self.generateDiskIo
        else:
            print 'getAvgCpuUtil type error'
            return None

        result = 0
        #predict future data
        if flag == 'future':
            for i in range(interval):
                result += generateFunc(time + i)
            result = result / interval
        #analyze history data
        elif flag == 'history':
            for i in range(interval):
                result += generateFunc(time - i)
            result = result / interval
        else:
            print 'not a valid flag'
            return None
        return result

    def generateCpuUtil(self, time):
        return None

    def generateBandwidth(self, time):
        return None

    def generateDiskIo(self, time):
        return None


############################################### specific entity ###############################################


class Instance_Matlab_1(Instance):
    # time refers to the time point in a day (0-24)
    def __init__(self, instanceId, instanceType, host, instance_list):
        super(Instance_Matlab_1, self).__init__(instanceId, instanceType, host, instance_list)
        self.cpu = [95, 95, 95, 95, 95, 95,
                    95, 95, 95, 95, 95, 95,
                    95, 95, 95, 95, 95, 95,
                    95, 95, 95, 95, 95, 95]

    def generateCpuUtil(self, time):
        result = self.cpu[time % 24] + random.randint(0, 5)
        return result

class Instance_Matlab_2(Instance):
    def __init__(self, instanceId, instanceType, host, instance_list):
        super(Instance_Matlab_2, self).__init__(instanceId, instanceType, host, instance_list)
        self.cpu = [95, 95, 95, 95, 95, 95,
                    95, 95, 95, 95, 95, 95,
                    95, 95, 95, 95, 95, 95,
                    95, 95, 95, 95, 95, 95]

    def generateCpuUtil(self, time):
        result = self.cpu[time % 24] + random.randint(0, 5)
        return result

class Instance_WebServer_1(Instance):
    def __init__(self, instanceId, instanceType, host, instance_list):
        super(Instance_WebServer_1, self).__init__(instanceId, instanceType, host, instance_list)
        self.cpu = [20, 20, 20, 20, 20, 20,
                    30, 40, 60, 80, 70, 60,
                    60, 80, 80, 80, 60, 50,
                    50, 40, 40, 30, 30, 20]
    def generateCpuUtil(self, time):
        return self.cpu[time % 24] + random.randint(-5, 5)

class Instance_Game_1(Instance):
    def __init__(self, instanceId, instanceType, host, instance_list):
        super(Instance_Game_1, self).__init__(instanceId, instanceType, host, instance_list)
        self.bandwidth = [70, 55, 50, 45, 40, 35,
                          35, 35, 40, 40, 40, 45,
                          45, 50, 50, 60, 70, 80,
                          90, 95, 95, 95, 95, 85]
    def generateCpuUtil(self, time):
        pass
    def generateBandwidth(self, time):
        return self.bandwidth[time % 24] + random.randint(-5, 5)

class Instance_Storage_1(Instance):
    def __init__(self, instanceId, instanceType, host, instance_list):
        super(Instance_Storage_1, self).__init__(instanceId, instanceType, host, instance_list)
        self.bandwidth = [45, 40, 40, 40, 40, 40,
                          50, 50, 50, 55, 60, 60,
                          60, 70, 70, 65, 65, 70,
                          70, 70, 70, 70, 60, 50]
    def generateBandwidth(self, time):
        return self.bandwidth[time % 24] + random.randint(-5, 5)
    def generateDiskIo(self, time):
        pass

############################################### filter ###############################################
def filter_host_instanceType(host_list, instanceType, flag):
    result = []

    if type(host_list) == list:
        temp = {}
        for host in host_list:
            temp[host.getId()] = host
        host_list = temp

    for hostId in host_list:
        host = host_list[hostId]
        if host.getInstanceNum(instanceType) > 0 and flag:
            result.append(host)
        if host.getInstanceNum(instanceType) == 0 and not flag:
            result.append(host)
    return result

# less than threshold
def filter_host_cpu(host_list, flag, time_count, interval, threshold):
    result = []
    for hostId in host_list:
        host = host_list[hostId]
        cpu = host.getStatisticData(flag, ResourceType.CPU_UTIL, time_count, interval)
        if cpu < threshold :
            result.append(host)
    return result

############################################### rank ###############################################
def select_host_max_instance(host_list, instanceType):
    result_host = None
    max = 0
    for hostId in host_list:
        host = host_list[hostId]
        if host.getInstanceNum(instanceType) >= max:
            result_host = host
            max = host.getInstanceNum(instanceType)
    return result_host

def select_host_min_instance(host_list, instanceType):
    result_host = None
    min = 10000
    for hostId in host_list:
        host = host_list[hostId]
        if host.getInstanceNum(instanceType) <= min and host.getInstanceNum(instanceType) != 0:
            result_host = host
            min = host.getInstanceNum(instanceType)
    return result_host

def select_instance_random(host, instanceType):
    instances = host.getInstance(instanceType)
    if len(instances) == 0:
        return None
    index = random.randint(0, len(instances) - 1)
    return instances[index]

def select_host_random(host_list):
    index = random.randint(0, len(host_list) - 1)
    return host_list[index]

def select_host_min_cpu(host_list, flag, time_count, interval):
    minCpu = 1000
    resultHost = None

    for host in host_list:
        cpu = host.getStatisticData(flag, ResourceType.CPU_UTIL, time_count, interval)
        if cpu < minCpu:
            minCpu = cpu
            resultHost = host
    return resultHost

def select_host_max_cpu(host_list, flag, time_count, interval):
    maxCpu = 0
    resultHost = None

    for host in host_list:
        cpu = host.getStatisticData(flag, ResourceType.CPU_UTIL, time_count, interval)
        if cpu > maxCpu:
            maxCpu = cpu
            resultHost = host
    return resultHost

# select the best host : rank = cpuutil - distance * 50
def select_host_cpu_distance(host, host_list, distance_matrix, flag, time_count, interval):
    maxRank = -1000
    resultHost = None
    for destHost in host_list :
        #distance
        srcHostIndex = host_mapper[host.getId()]
        destHostIndex = host_mapper[destHost.getId()]
        distance = distance_matrix[srcHostIndex][destHostIndex]

        #cpuutil
        cpu = destHost.getStatisticData(flag, ResourceType.CPU_UTIL, time_count, interval)

        rank = cpu - distance * 50
        if rank > maxRank:
            resultHost = destHost
            maxRank = rank
    return resultHost



############################################### migrate ###############################################
def migrate_instance(srcHost, destHost, instance):
        if not instance:
            print 'no instance to migrate'
            return
        if srcHost.getId() == destHost.getId():
            return
        if srcHost == None or destHost == None:
            print 'no host to migrate'
            return
        srcHost.removeInstance(instance)
        destHost.addInstance(instance)
        instance.setHost(destHost)
        print '%s\t==>\t%s\t==>\t%s' % (srcHost.id, instance.getId(), destHost.getId())

############################################### work thread ###############################################

def matlab_1_consolidate(period):
    if (time_count % period == 0):
        #srcHost = select_host_min_instance(host_list, InstanceType.MATLAB_1)
        #migrateInstance = select_instance_random(srcHost, InstanceType.MATLAB_1)
        #destHost = select_host_max_instance(host_list, InstanceType.MATLAB_1)
        #migrate_instance(srcHost, destHost, migrateInstance)
        src_host_list = filter_host_instanceType(host_list, InstanceType.MATLAB_1_MASTER, False)
        src_host_list = filter_host_instanceType(src_host_list, InstanceType.MATLAB_1, True)
        #srcHost = select_host_min_cpu(src_host_list, 'future', time_count, 2)
        srcHost = select_host_random(src_host_list)

        migrateInstance = select_instance_random(srcHost, InstanceType.MATLAB_1)

        masterHost = filter_host_instanceType(host_list, InstanceType.MATLAB_1_MASTER, True)[0]
        dest_host_list = filter_host_cpu(host_list, 'future', time_count, 2, 80)
        destHost = select_host_cpu_distance(masterHost, dest_host_list, host_distance_matrix, 'future', time_count, 2)

        migrate_instance(srcHost, destHost, migrateInstance)

def matlab_2_consolidate(period):
    if (time_count % period == 0):
        src_host_list = filter_host_instanceType(host_list, InstanceType.MATLAB_2_MASTER, False)
        src_host_list = filter_host_instanceType(src_host_list, InstanceType.MATLAB_2, True)
        #srcHost = select_host_min_cpu(src_host_list, 'future', time_count, 2)
        srcHost = select_host_random(src_host_list)

        migrateInstance = select_instance_random(srcHost, InstanceType.MATLAB_2)

        masterHost = filter_host_instanceType(host_list, InstanceType.MATLAB_2_MASTER, True)[0]
        dest_host_list = filter_host_cpu(host_list, 'future', time_count, 2, 80)
        destHost = select_host_cpu_distance(masterHost, dest_host_list, host_distance_matrix, 'future', time_count, 2)

        migrate_instance(srcHost, destHost, migrateInstance)

def matlab_1_consolidate_comparison(period):
    if (time_count % period == 0):
        src_host_list = filter_host_instanceType(host_list, InstanceType.ALL, True)
        srcHost = select_host_min_cpu(src_host_list, 'future', time_count, 2)
        migrateInstance = select_instance_random(srcHost, InstanceType.ALL)
        dest_host_list = filter_host_cpu(host_list, 'future', time_count, 2, 80)
        destHost = select_host_max_cpu(dest_host_list, 'future', time_count, 2)
        migrate_instance(srcHost, destHost, migrateInstance)

def matlab_2_consolidate_comparison(period):
    if (time_count % period == 0):
        src_host_list = filter_host_instanceType(host_list, InstanceType.ALL, True)
        srcHost = select_host_min_cpu(src_host_list, 'future', time_count, 2)
        migrateInstance = select_instance_random(srcHost, InstanceType.ALL)
        dest_host_list = filter_host_cpu(host_list, 'future', time_count, 2, 80)
        destHost = select_host_max_cpu(dest_host_list, 'future', time_count, 2)
        migrate_instance(srcHost, destHost, migrateInstance)


def game_1_guarantee_qos(period):
    if (time_count % period == 0):
        game_hostList = filter_host_instanceType(host_list, InstanceType.GAME_1, True)
        for host in game_hostList:
            if host.getStatisticData('future', ResourceType.BANDWIDTH, time_count, 2) > 700:
                srcHost = host
                migrateInstance = select_instance_random(host, InstanceType.STORAGE_1)
                destHost = select_host_random(filter_host_instanceType(host_list, InstanceType.GAME_1, False))
                migrate_instance(srcHost, destHost, migrateInstance)

def storage_1_consolidation(period):
    if (time_count % period == 0):
        game_hostList = filter_host_instanceType(host_list, InstanceType.GAME_1, True)
        for host in game_hostList:
            if host.getStatisticData('future', ResourceType.BANDWIDTH, time_count, 2) < 600:
                srcHost = select_host_random(filter_host_instanceType(host_list, InstanceType.GAME_1, False))
                migrateInstance = select_instance_random(srcHost, InstanceType.STORAGE_1)
                destHost = host
                migrate_instance(srcHost, destHost, migrateInstance)

def getTotalDistance():
    totalDistance = 0

    instance_master_1 = instance_list['instance_master_1']
    instance_master_2 = instance_list['instance_master_2']

    host_1 = instance_master_1.getHost()
    host_2 = instance_master_2.getHost()

    for instanceId in instance_list:
        instance = instance_list[instanceId]
        if instance.getType() == InstanceType.MATLAB_1:
            host = instance.getHost()
            distance = host_distance_matrix[host_mapper[host_1.getId()]][host_mapper[host.getId()]]
            totalDistance += distance
            print totalDistance
        elif instance.getType() == InstanceType.MATLAB_2:
            host = instance.getHost()
            distance = host_distance_matrix[host_mapper[host_2.getId()]][host_mapper[host.getId()]]
            totalDistance += distance
            print totalDistance
    return totalDistance


############################################### experiment setup ###############################################

def setup_environment_1():
    host_1 = Host('host_1', host_list)
    host_2 = Host('host_2', host_list)
    host_3 = Host('host_3', host_list)
    host_4 = Host('host_4', host_list)

    instance_master_1 = Instance_Matlab_1('instance_master_1', InstanceType.MATLAB_1_MASTER, host_1, instance_list)
    instance_master_2 = Instance_Matlab_2('instance_master_2', InstanceType.MATLAB_2_MASTER, host_2, instance_list)

    instance_1 = Instance_Matlab_1('instance_1', InstanceType.MATLAB_1, host_1, instance_list)
    instance_2 = Instance_Matlab_1('instance_2', InstanceType.MATLAB_1, host_1, instance_list)
    instance_3 = Instance_Matlab_1('instance_3', InstanceType.MATLAB_1, host_3, instance_list)
    instance_4 = Instance_Matlab_1('instance_4', InstanceType.MATLAB_1, host_2, instance_list)
    instance_5 = Instance_Matlab_1('instance_5', InstanceType.MATLAB_1, host_2, instance_list)
    instance_6 = Instance_Matlab_1('instance_6', InstanceType.MATLAB_1, host_4, instance_list)
    instance_7 = Instance_Matlab_1('instance_7', InstanceType.MATLAB_1, host_3, instance_list)
    instance_8 = Instance_Matlab_1('instance_8', InstanceType.MATLAB_1, host_3, instance_list)
    instance_9 = Instance_Matlab_1('instance_9', InstanceType.MATLAB_1, host_3, instance_list)
    instance_10 = Instance_Matlab_1('instance_10', InstanceType.MATLAB_1, host_4, instance_list)
    instance_11 = Instance_Matlab_1('instance_11', InstanceType.MATLAB_1, host_4, instance_list)
    instance_12 = Instance_Matlab_1('instance_12', InstanceType.MATLAB_1, host_4, instance_list)

    instance_13 = Instance_Matlab_2('instance_13', InstanceType.MATLAB_2, host_1, instance_list)
    instance_14 = Instance_Matlab_2('instance_14', InstanceType.MATLAB_2, host_1, instance_list)
    instance_15 = Instance_Matlab_2('instance_15', InstanceType.MATLAB_2, host_3, instance_list)
    instance_16 = Instance_Matlab_2('instance_16', InstanceType.MATLAB_2, host_2, instance_list)
    instance_17 = Instance_Matlab_2('instance_17', InstanceType.MATLAB_2, host_2, instance_list)
    instance_18 = Instance_Matlab_2('instance_18', InstanceType.MATLAB_2, host_4, instance_list)
    instance_19 = Instance_Matlab_2('instance_19', InstanceType.MATLAB_2, host_3, instance_list)
    instance_20 = Instance_Matlab_2('instance_20', InstanceType.MATLAB_2, host_3, instance_list)
    instance_21 = Instance_Matlab_2('instance_21', InstanceType.MATLAB_2, host_3, instance_list)
    instance_22 = Instance_Matlab_2('instance_22', InstanceType.MATLAB_2, host_4, instance_list)
    instance_23 = Instance_Matlab_2('instance_23', InstanceType.MATLAB_2, host_4, instance_list)
    instance_24 = Instance_Matlab_2('instance_24', InstanceType.MATLAB_2, host_4, instance_list)

def setup_environment_2():
    host_1 = Host('host_1', host_list)
    host_2 = Host('host_2', host_list)
    host_3 = Host('host_3', host_list)

    instance_1 = Instance_Game_1('instance_1', InstanceType.GAME_1, host_1, instance_list)
    instance_2 = Instance_Game_1('instance_2', InstanceType.GAME_1, host_1, instance_list)
    instance_3 = Instance_Game_1('instance_3', InstanceType.GAME_1, host_1, instance_list)
    instance_4 = Instance_Game_1('instance_4', InstanceType.GAME_1, host_1, instance_list)
    instance_5 = Instance_Game_1('instance_5', InstanceType.GAME_1, host_1, instance_list)
    instance_6 = Instance_Game_1('instance_6', InstanceType.GAME_1, host_1, instance_list)
    instance_7 = Instance_Game_1('instance_7', InstanceType.GAME_1, host_1, instance_list)
    instance_8 = Instance_Game_1('instance_8', InstanceType.GAME_1, host_2, instance_list)
    instance_9 = Instance_Game_1('instance_9', InstanceType.GAME_1, host_2, instance_list)
    instance_10 = Instance_Game_1('instance_10', InstanceType.GAME_1, host_2, instance_list)
    instance_11 = Instance_Game_1('instance_11', InstanceType.GAME_1, host_2, instance_list)
    instance_12 = Instance_Game_1('instance_12', InstanceType.GAME_1, host_2, instance_list)
    instance_13 = Instance_Game_1('instance_13', InstanceType.GAME_1, host_2, instance_list)
    instance_14 = Instance_Game_1('instance_14', InstanceType.GAME_1, host_2, instance_list)
    instance_15 = Instance_Game_1('instance_15', InstanceType.GAME_1, host_2, instance_list)

    instance_16 = Instance_Storage_1('instance_16', InstanceType.STORAGE_1, host_1, instance_list)
    instance_17 = Instance_Storage_1('instance_17', InstanceType.STORAGE_1, host_1, instance_list)
    instance_18 = Instance_Storage_1('instance_18', InstanceType.STORAGE_1, host_1, instance_list)
    instance_19 = Instance_Storage_1('instance_19', InstanceType.STORAGE_1, host_1, instance_list)
    instance_20 = Instance_Storage_1('instance_20', InstanceType.STORAGE_1, host_1, instance_list)
    instance_21 = Instance_Storage_1('instance_21', InstanceType.STORAGE_1, host_1, instance_list)
    instance_22 = Instance_Storage_1('instance_22', InstanceType.STORAGE_1, host_1, instance_list)
    instance_23 = Instance_Storage_1('instance_23', InstanceType.STORAGE_1, host_2, instance_list)
    instance_24 = Instance_Storage_1('instance_24', InstanceType.STORAGE_1, host_2, instance_list)
    instance_25 = Instance_Storage_1('instance_25', InstanceType.STORAGE_1, host_2, instance_list)
    instance_26 = Instance_Storage_1('instance_26', InstanceType.STORAGE_1, host_2, instance_list)
    instance_27 = Instance_Storage_1('instance_27', InstanceType.STORAGE_1, host_2, instance_list)
    instance_28 = Instance_Storage_1('instance_28', InstanceType.STORAGE_1, host_2, instance_list)
    instance_29 = Instance_Storage_1('instance_29', InstanceType.STORAGE_1, host_2, instance_list)
    instance_30 = Instance_Storage_1('instance_30', InstanceType.STORAGE_1, host_2, instance_list)

def display(host_list):
    print '\n'
    for hostId in host_list:
        print '###########' + hostId + '###########'
        instanceList = host_list[hostId].getInstance(InstanceType.ALL)
        for instance in instanceList:
            print instance.getId() + '\t' + str(instance.getType())
    print '\n'


if __name__ == '__main__':
    setup_environment_1()
    display(host_list)

    host1_cpuUtil = []
    host2_cpuUtil = []
    host3_cpuUtil = []
    host4_cpuUtil = []
    total_distance = []
    time = []

    while time_count < 100:
        host1_cpuUtil.append(host_list['host_1'].getStatisticData('history', ResourceType.CPU_UTIL, time_count, 1))
        host2_cpuUtil.append(host_list['host_2'].getStatisticData('history', ResourceType.CPU_UTIL, time_count, 1))
        host3_cpuUtil.append(host_list['host_3'].getStatisticData('history', ResourceType.CPU_UTIL, time_count, 1))
        host4_cpuUtil.append(host_list['host_4'].getStatisticData('history', ResourceType.CPU_UTIL, time_count, 1))
        total_distance.append(getTotalDistance())
        time.append(time_count)
        if time_count > 23:
            #matlab_1_consolidate(4)
            #matlab_2_consolidate(4)
            matlab_1_consolidate_comparison(8)
            #matlab_2_consolidate_comparison(4)
        time_count += 1
    display(host_list)
    plt.plot(time, host1_cpuUtil)
    plt.plot(time, host2_cpuUtil)
    plt.plot(time, host3_cpuUtil)
    plt.plot(time, host4_cpuUtil)
    plt.plot(time, total_distance)
    plt.show()

    #setup_environment_2()
    #
    #display(host_list)
    #host1_bandwidth = []
    #host2_bandwidth = []
    #host3_bandwidth = []
    #time = []
    #while time_count < 80:
    #    #plot the host bandwidth pic
    #    host1_bandwidth.append(host_list['host_1'].getStatisticData('history', ResourceType.BANDWIDTH, time_count, 1))
    #    host2_bandwidth.append(host_list['host_2'].getStatisticData('history', ResourceType.BANDWIDTH, time_count, 1))
    #    host3_bandwidth.append(host_list['host_3'].getStatisticData('history', ResourceType.BANDWIDTH, time_count, 1))
    #    time.append(time_count)
    #    if time_count > 23:
    #        game_1_guarantee_qos(1)
    #        storage_1_consolidation(2)
    #    time_count += 1
    #display(host_list)
    #
    #plt.plot(time, host1_bandwidth)
    #plt.plot(time, host2_bandwidth)
    #plt.plot(time, host3_bandwidth)
    #plt.show()
































