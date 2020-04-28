from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_config
from nornir_scrapli.tasks import send_command, send_configs


def underlay(task):
    ipvzero = str(f"{task.host.hostname}")
    num = ipvzero[-2:]
    loopback_ip = "2001:db8:acad:{fname}::{fname}/64".format(fname= num)

    loopback_commands = [
            'ipv6 unicast-routing',
            'interface loop0',
            'ipv6 address ' + loopback_ip,
            'ipv6 ospf 1 area 0'
]
    deploy_loopback = task.run(send_configs, name="Loopback Automation", configs = loopback_commands)
    ospf_commands = [
            'ipv6 router ospf 1',
            'router-id {rid}.{rid}.{rid}.{rid}'.format(rid=num)
]
    deploy_ospf = task.run(send_configs,name="Automating OSPF RIDs", configs = ospf_commands)
    interface_commands = [
            'interface range e0/1-3',
            'ipv6 address fe80::{lastnum}'.format(lastnum=num) + ' link-local',
            'ipv6 ospf 1 area 0'
]
    deploy_interface = task.run(send_configs,name="Automating OSPF Interfaces", configs = interface_commands)
    bgp_rid_commands = [
            'router bgp ' + str(task.host['asn']),
            'bgp router-id {rid}.{rid}.{rid}.{rid}'.format(rid=num)
]

    deploy_rid = task.run(send_configs,name="Automating BGP RIDs", configs = bgp_rid_commands)
    for i in range(1,51):
        if str(i).zfill(2) == str(num):
            continue
        bgp_commands = [
                'router bgp ' + str(task.host['asn']),
                'neighbor 2001:db8:acad:' + str(i) + "::" + str(i) + ' remote-as ' + str(task.host['asn']),
                'neighbor 2001:db8:acad:' + str(i) + "::" + str(i) + ' update-source loopback0',
                'neighbor 2001:db8:acad:' + str(i) + "::" + str(i) + ' password cisco',
                'neighbor 2001:db8:acad:' + str(i) + "::" + str(i) + ' timers 10 30',
                'address-family ipv6',
                'neighbor 2001:db8:acad:' + str(i) + "::" + str(i) + ' activate'
]
        deploy_bgp = task.run(send_configs,name="Automating IPv6 BGP Configurations", configs = bgp_commands)


def main() -> None:
    nr = InitNornir(config_file="config.yaml")
    result = nr.run(task=underlay)
    print_result(result)

if __name__ == '__main__':
        main()
