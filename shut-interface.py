from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_send_config
from nornir.plugins.functions.text import print_result

def get_facts(task):
    r = task.run(netmiko_send_command, command_string="show interfaces", use_genie=True)
    task.host["facts"] = r.result
    outer = task.host["facts"]
    for intf in outer.keys():
        int_stats = outer[intf]
        innever = int_stats["last_input"]
        if "never" in innever:
            shut_commands=[
                    'interface ' + str(intf),
                    'Description Shutdown via Nornir',
                    'no ipv6 address',
                    'shutdown'
]
            resulter= task.run(netmiko_send_config,name="Shutting Interface",config_commands=shut_commands)




def main() -> None:
    nr = InitNornir(config_file="config.yaml")
    result = nr.run(task=get_facts)
    print_result(result)
    #import ipdb;
    #ipdb.set_trace()

if __name__ == '__main__':
    main()
