from modules.oci_parser.vcn_parser import VCN
from modules.oci_parser.subnet_parser import Subnet
from modules.oci_parser.instance_parser import Instance
from modules.oci_parser.load_balancer import LoadBalancer, BackendSet, Backend, Listener
from modules.oci_parser.nsg import NSG, NSGSecurityRule

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


def oci_parser(tfstate):
    vcns = parse_vcns(tfstate)
    subnets = parse_subnets(tfstate)
    instances = parse_instances(tfstate)
    load_balancers = parse_load_balancers(tfstate)
    backend_sets = parse_backend_sets(tfstate)
    backends = parse_backends(tfstate, backend_sets)
    listeners = parse_listeners(tfstate)
    nsgs = parse_nsgs(tfstate)
    return vcns, subnets, instances, load_balancers, backends, backend_sets, listeners, nsgs
