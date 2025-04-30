# modules/parser/subnet_parser.py

class Subnet:
    def __init__(
        self, subnet_id, name, cidr_block, vcn_id, compartment_id,
        dns_label, prohibit_internet_ingress, prohibit_public_ip_on_vnic,
        tags=None, resource_type=None, resource_name=None, index=None
    ):
        self.id = subnet_id
        self.name = name
        self.index = index 
        self.cidr_block = cidr_block
        self.vcn_id = vcn_id
        self.compartment_id = compartment_id
        self.dns_label = dns_label
        self.prohibit_internet_ingress = prohibit_internet_ingress
        self.prohibit_public_ip_on_vnic = prohibit_public_ip_on_vnic
        self.tags = tags or {}
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.index = index
        self.instances = []
        self.load_balancers = []

    def add_instance(self, instance):
        self.instances.append(instance)

    def add_load_balancer(self, load_balancer):
        self.load_balancers.append(load_balancer)

    @classmethod
    def from_tfstate(cls, resource_block):
        values = resource_block.get("values", {})
        return cls(
            subnet_id=values.get("id"),
            name=values.get("display_name"),
            cidr_block=values.get("cidr_block"),
            vcn_id=values.get("vcn_id"),
            compartment_id=values.get("compartment_id"),
            dns_label=values.get("dns_label"),
            prohibit_internet_ingress=values.get("prohibit_internet_ingress"),
            prohibit_public_ip_on_vnic=values.get("prohibit_public_ip_on_vnic"),
            tags=values.get("freeform_tags", {}),
            resource_type=resource_block.get("type"),
            resource_name=resource_block.get("name"),
            index=resource_block.get("index")
        )

    def pretty_print(self):
        print(f"\n  [Subnet: {self.name}]")
        print(f"    - Type               : {self.resource_type}")
        print(f"    - Name               : {self.resource_name}")
        print(f"    - Index              : {self.index}")
        print(f"    - ID                 : {self.id}")
        print(f"    - CIDR Block         : {self.cidr_block}")
        print(f"    - VCN ID             : {self.vcn_id}")
        print(f"    - DNS Label          : {self.dns_label}")
        print(f"    - Public IP Allowed  : {not self.prohibit_public_ip_on_vnic}")
        print(f"    - Internet Ingress   : {not self.prohibit_internet_ingress}")
        print(f"    - Compartment        : {self.compartment_id}")
        if self.tags:
            print(f"    - Tags:")
            for k, v in self.tags.items():
                print(f"        {k:<15}: {v}")
        if self.instances:
            print("    - Instances:")
            for instance in self.instances:
                instance.pretty_print()
        if self.load_balancers:
            print("    - LoadBalancers:")
            for lb in self.load_balancers:
                lb.pretty_print()
        else:
            print("    - No LoadBalancers associated.")

    # subnet_parser.py

    def to_dict(self):
        return {
            "id": self.id,
            "index": self.index,
            "display_name": self.name,
            "cidr_block": self.cidr_block,
            "vcn_id": self.vcn_id,
            "dns_label": self.dns_label,
            "prohibit_internet_ingress": self.prohibit_internet_ingress,
            "prohibit_public_ip_on_vnic": self.prohibit_public_ip_on_vnic,
            "compartment_id": self.compartment_id,
            "tags": self.tags,
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "instances": [instance.to_dict() for instance in self.instances],
            "load_balancers": [lb.to_dict() for lb in self.load_balancers]
        }
