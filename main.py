import json
import os
from modules.parser.vcn_parser import VCN
from modules.parser.subnet_parser import Subnet
from modules.parser.instance_parser import Instance
from modules.parser.load_balancer import LoadBalancer, BackendSet, Backend, Listener
from modules.parser.nsg import NSG, NSGSecurityRule
from dotenv import load_dotenv
from tabulate import tabulate

# from parser import parse_load_balancers, parse_backend_sets, parse_backends


# ✅ diagrams 관련 import
from diagrams import Diagram, Cluster
from diagrams.generic.network import Firewall  # 대체 클래스 사용
from diagrams.generic.compute import Rack

from diagrams import Diagram, Cluster
from diagrams.generic.compute import Rack
from diagrams.onprem.network import Haproxy  # Load Balancer 역할 대체
from diagrams.generic.network import Subnet as SubnetIcon
from diagrams import Edge
# from diagrams.generic.blank import Note

DEBUG = False
CHUNK_SIZE = 2

load_dotenv()
tfstate_path = os.getenv("TFSTATE_PATH")
diagram_filename = os.getenv("DIAGRAM_FILENAME")

def parse_vcns(tfstate_data):
    vcn_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "oci_core_vcn":
                vcn = VCN.from_tfstate(resource)
                vcn_list.append(vcn)

    return vcn_list

def parse_subnets(tfstate_data):
    subnet_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "oci_core_subnet":
                subnet = Subnet.from_tfstate(resource)
                subnet_list.append(subnet)

    return subnet_list

def parse_instances(tfstate_data):
    instance_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "oci_core_instance":
                instance = Instance.from_tfstate(resource)
                instance_list.append(instance)

    return instance_list

def parse_load_balancers(tfstate_data):
    load_balancer_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            # print(f"Checking resource: {resource}")  # 디버깅 출력
            if resource.get("type") == "oci_load_balancer":
                load_balancer = LoadBalancer.from_tfstate(resource)
                load_balancer_list.append(load_balancer)

    return load_balancer_list

def parse_backend_sets(tfstate_data):
    backend_set_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            # print(f"Checking resource: {resource}")  # 디버깅 출력
            if resource.get("type") == "oci_load_balancer_backend_set":  # 수정된 부분
                backend_set = BackendSet.from_tfstate(resource)
                backend_set_list.append(backend_set)

    return backend_set_list

def parse_backends(tfstate_data, backend_sets):
    backend_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            # 디버깅 출력
            # print(f"Checking resource: {resource}")  # 리소스 확인
            if resource.get("type") == "oci_load_balancer_backend":  # Backend 리소스 타입 확인
                # BackendSet 이름을 찾기
                backendset_name = None
                for backend_set in backend_sets:
                    if backend_set.name in resource['values']['backendset_name']:
                        backendset_name = backend_set.name
                        break
                
                # Backend 객체 생성
                backend = Backend.from_tfstate(resource, backendset_name)  # BackendSet 이름 전달
                backend_list.append(backend)

                # Backend 객체가 잘 생성되었는지 확인
                # print(f"Created Backend: {backend.name} (ID: {backend.id}, BackendSet: {backend.backendset_name})")

    return backend_list

def parse_listeners(tfstate_data):
    listener_list = []
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "oci_load_balancer_listener":
                listener = Listener.from_tfstate(resource)
                listener_list.append(listener)

    return listener_list

def parse_nsgs(tfstate_data):
    NSG.reset()  # 이전 상태 클리어
    nsgs = {}
    root_module = tfstate_data.get("values", {}).get("root_module", {})
    modules = [root_module] + root_module.get("child_modules", [])

    # 먼저 NSG 객체들을 생성
    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "oci_core_network_security_group":
                nsg = NSG.from_tfstate(resource)
                nsgs[nsg.id] = nsg

    # NSG 규칙들을 파싱하여 해당하는 NSG에 추가
    for module in modules:
        for resource in module.get("resources", []):
            if resource.get("type") == "oci_core_network_security_group_security_rule":
                values = resource.get("values", {})

                if values.get("direction") == "INGRESS" :
                    direction = "IN"
                else : 
                    direction = "E"

                rule = NSGSecurityRule(
                    id=values.get("id"),
                    # direction=values.get("direction"),
                    direction=direction,
                    protocol=values.get("protocol"),
                    source=values.get("source"),
                    destination=values.get("destination"),
                    description=values.get("description"),
                    tcp_options=values.get("tcp_options", [{}])[0] if values.get("tcp_options") else None
                )
                nsg_id = values.get("network_security_group_id")
                if nsg_id in nsgs:
                    nsgs[nsg_id].add_security_rule(rule)

    return list(nsgs.values())

def print_nsg_table(nsgs):
    table_data = []
    for nsg in nsgs:
        for rule in nsg.security_rules:
            table_data.append([
                nsg.name,
                rule.id,
                rule.direction,
                rule.protocol,
                rule.source,
                rule.destination,
                rule.description
            ])
    headers = ["NSG Name", "Rule ID", "Direction", "Protocol", "Source", "Destination", "Description"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def classify_subnet(subnet_name):
    name = subnet_name.lower()
    if "gw" in name:
        return "gw"
    elif "lb" in name:
        return "lb"
    elif "app" in name or "pub" in name or "did" in name or "bfs" in name:
        return "app"
    elif "node" in name or "priv" in name or "no" in name:
        return "private"
    else:
        return "etc"

def resolve_nsg_name(source: str) -> str:
    if source and source.startswith("ocid1.networksecuritygroup"):
        return NSG.get_name_by_id(source)
    return source

def chunked(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def render_diagram(vcns, nsgs):
    from diagrams import Edge
    from diagrams.generic.compute import Rack
    from diagrams.generic.network import Subnet as SubnetIcon
    from diagrams.generic.network import Firewall

    graph_attr = {
        "splines": "ortho",
        "nodesep": "0.1",  # 수직
        "ranksep": "1.5",  # 수평
        "rankdir": "LR",
    }

    def chunked(items, size):
        return [items[i:i + size] for i in range(0, len(items), size)]

    with Diagram("OCI Architecture", direction="LR", show=False, filename=diagram_filename, graph_attr=graph_attr):
    #with Diagram("OCI Architecture", direction="LR", show=False, filename="diagrams/oci_architecture_grid", graph_attr=graph_attr):
        gw_first_nodes = []  # 🔥 GW 그룹의 첫 번째 Node를 저장

        for vcn in vcns:
            with Cluster(f"VCN: {vcn.name}"):

                # 역할별로 서브넷 분류
                subnet_groups = {
                    "gw": [],
                    "app": [],
                    "lb": [],
                    "private": []
                }

                for subnet in vcn.subnets:
                    role = classify_subnet(subnet.name)
                    if role in subnet_groups:
                        subnet_groups[role].append(subnet)

                # 역할별 클러스터 생성
                for role in ["gw", "app", "lb", "private"]:
                    if not subnet_groups[role]:
                        continue

                    with Cluster(role.upper()):
                        previous_last_rack = None  # 🔥 직전 서브넷의 마지막 인스턴스 기억

                        for subnet in subnet_groups[role]:
                            with Cluster(f"{subnet.name}\n{subnet.cidr_block}", graph_attr={"rank": "same"}):
                                instance_racks = []

                                if role == "lb":
                                    # 🔥 LoadBalancer 전용 처리
                                    for lb in subnet.load_balancers:
                                        lines = [f"LB: {lb.name}"]
                                        if lb.ip_address:
                                            lines.append(f"{lb.ip_address}")
                                        label = "\n".join(lines)
                                        instance_racks.append(Rack(label))

                                else:
                                    for instance in subnet.instances:
                                        lines = [f"{instance.name}", f"{instance.private_ip}"]
                                        if instance.public_ip:
                                            lines.append(f"pub: {instance.public_ip}")
                                        if instance.nsg_ids:
                                            readable_nsgs = [NSG.get_name_by_id(nsg_id) for nsg_id in instance.nsg_ids]
                                            lines.append(f"nsg: {', '.join(readable_nsgs)}")
                                        if instance.ocpus and instance.memory:
                                            lines.append(f"{instance.ocpus}M {instance.memory}GB")
                                        if instance.boot_volume_size:
                                            lines.append(f"BVol: {instance.boot_volume_size}GB")
                                        label = "\n".join(lines)
                                        instance_racks.append(Rack(label))

                                                                    # 🔥 GW 역할이면 기억해놓기 (각 Subnet에서 첫 번째 Node만)
                                    if role == "gw" and instance_racks:
                                        gw_first_nodes.append(instance_racks[0])

                                chunks = chunked(instance_racks, CHUNK_SIZE)

                                if chunks:
                                    first_row = chunks[0]  # 첫 번째 줄
                                    current_first_rack = first_row[0]  # (0,0) 인스턴스
                                    current_last_rack = first_row[-1]  # (0, CHUNK_SIZE-1) 인스턴스

                                    # 🔥 이전 서브넷의 마지막 → 현재 서브넷의 첫번째 연결
                                    if previous_last_rack:
                                        # previous_last_rack >> Edge(color="blue", style="dashed") >> current_first_rack
                                        previous_last_rack >> Edge(color="transparent") >> current_first_rack

                                    previous_last_rack = current_last_rack

                                # 🔥 같은 서브넷 내에서는 인스턴스끼리 연결
                                for row in chunks:
                                    if len(row) == 2:
                                        row[0] >> Edge(color="transparent") >> row[1]
                                    elif len(row) == 1:
                                        row[0]

        # NSG 정보는 VCN 외부에 별도 표시
        # nsg_info = Firewall("\n".join([
        #     f"[{nsg.name}]\n" + "\n".join([
        #         f"  {rule.direction:<2} {rule.source:<18} {rule.get_port_range_str()}"
        #         for rule in nsg.security_rules
        #         if rule.source is not None
        #     ]) + "\n"
        #     for nsg in nsgs
        # ]).rstrip())
        nsg_info = Firewall("\n".join([
            f"[{nsg.name}]\n" + "\n".join([
                f"  {rule.direction:<2} {resolve_nsg_name(rule.source):<18} {rule.get_port_range_str()}"
                for rule in nsg.security_rules
                if rule.source is not None
            ]) + "\n"
            for nsg in nsgs
        ]).rstrip())

        
        if gw_first_nodes:
            # nsg_info >> Edge(color="red", style="bold") >> gw_first_nodes[0]
            nsg_info >> Edge(color="transparent", minlen="2") >> gw_first_nodes[0]

def main():
    tfstate_path = os.getenv("TFSTATE_PATH")	
    #tfstate_path = os.path.join("data", "v2-heal.json")

    if not os.path.exists(tfstate_path):
        print(f"❌ tfstate 파일이 존재하지 않습니다: {tfstate_path}")
        return

    with open(tfstate_path, "r") as f:
        tfstate = json.load(f)

    vcns = parse_vcns(tfstate)
    subnets = parse_subnets(tfstate)
    instances = parse_instances(tfstate)
    load_balancers = parse_load_balancers(tfstate)
    backend_sets = parse_backend_sets(tfstate)
    backends = parse_backends(tfstate, backend_sets)
    listeners = parse_listeners(tfstate)
    nsgs = parse_nsgs(tfstate)

    # VCN 연결
    vcn_map = {vcn.id: vcn for vcn in vcns}
    for subnet in subnets:
        if subnet.vcn_id in vcn_map:
            vcn_map[subnet.vcn_id].add_subnet(subnet)

    # Subnet 연결
    subnet_map = {subnet.id: subnet for subnet in subnets}
    for instance in instances:
        if instance.subnet_id in subnet_map:
            subnet_map[instance.subnet_id].add_instance(instance)

    # LoadBalancer와 BackendSet 연결
    load_balancer_map = {lb.id: lb for lb in load_balancers}
    for backend_set in backend_sets:
        if backend_set.load_balancer_id in load_balancer_map:
            load_balancer_map[backend_set.load_balancer_id].add_backend_set(backend_set)

    # Backend 연결
    backend_map = {backend.id: backend for backend in backends}
    for backend_set in backend_sets:
        for backend in backend_map.values():
            if backend.backendset_name == backend_set.name:  # BackendSet 이름으로 매칭
                backend_set.add_backend(backend)
                # print(f"Added Backend ID: {backend.id} to BackendSet: {backend_set.name}")  # Backend ID 출력

    # LoadBalancer와 Listener 연결
    for listener in listeners:
        if listener.load_balancer_id in load_balancer_map:
            load_balancer_map[listener.load_balancer_id].add_listener(listener)

    # LoadBalancer를 Subnet에 연결
    for load_balancer in load_balancers:
        print(f"Checking LoadBalancer: {load_balancer.name} (ID: {load_balancer.id}, Subnet ID: {load_balancer.subnet_id})")  # LoadBalancer 정보 출력
        if load_balancer.subnet_id in subnet_map:
            print(f"Found matching Subnet ID: {load_balancer.subnet_id} in subnet_map")  # 서브넷 ID 확인
            subnet_map[load_balancer.subnet_id].add_load_balancer(load_balancer)
        else:
            print(f"No matching Subnet found for LoadBalancer ID: {load_balancer.id} with Subnet ID: {load_balancer.subnet_id}")  # 매칭되지 않는 경우 출력

    # LoadBalancer를 Subnet에 연결
    # for load_balancer in load_balancers:
    #     if load_balancer.subnet_id in subnet_map:
    #         subnet_map[load_balancer.subnet_id].add_load_balancer(load_balancer)


####################################################################################

    # print(f"\n✅ 총 {len(vcns)}개의 VCN, {len(subnets)}개의 Subnet, {len(instances)}개의 Instance, {len(load_balancers)}개의 LoadBalancer, {len(backend_sets)}개의 BackendSet가 파싱되었습니다.\n")

    # # VCN 및 Subnet 출력
    for vcn in vcns:
        if DEBUG:
            print(json.dumps(vcn.to_dict(), indent=2))
        else:
            vcn.pretty_print()
            for subnet in vcn.subnets:
                subnet.pretty_print()

####################################################################################                
    render_diagram(vcns, nsgs)

    # NSG와 규칙을 표로 출력
    # print_nsg_table(nsgs)

if __name__ == "__main__":
    main()
