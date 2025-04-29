class VCN:
    def __init__(self, vcn_id, name, cidr_blocks, compartment_id, dns_label, tags=None, resource_type=None, resource_name=None):
        self.id = vcn_id
        self.name = name
        self.cidr_blocks = cidr_blocks
        self.compartment_id = compartment_id
        self.dns_label = dns_label
        self.tags = tags or {}

        # 새로 추가된 필드
        self.resource_type = resource_type  # e.g. oci_core_vcn
        self.resource_name = resource_name  # e.g. vcn

        self.subnets = []

    @classmethod
    def from_tfstate(cls, resource_block):
        values = resource_block.get("values", {})
        return cls(
            vcn_id=values.get("id"),
            name=values.get("display_name"),
            cidr_blocks=values.get("cidr_blocks", []),
            compartment_id=values.get("compartment_id"),
            dns_label=values.get("dns_label"),
            tags=values.get("freeform_tags", {}),
            resource_type=resource_block.get("type"),
            resource_name=resource_block.get("name")
        )

    def add_subnet(self, subnet):
        self.subnets.append(subnet)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cidr_blocks": self.cidr_blocks,
            "compartment_id": self.compartment_id,
            "dns_label": self.dns_label,
            "tags": self.tags,
            "subnet_count": len(self.subnets),
            "resource_type": self.resource_type,
            "resource_name": self.resource_name,
            "subnets": [s.to_dict() for s in self.subnets]  # ✅ 여기가 핵심
        }

    def pretty_print(self):
        print(f"\n[VCN: {self.name}]")
        print(f"  - Type          : {self.resource_type}")
        print(f"  - Name          : {self.resource_name}")
        print(f"  - ID            : {self.id}")
        print(f"  - CIDR Blocks   : {', '.join(self.cidr_blocks)}")
        print(f"  - DNS Label     : {self.dns_label}")
        print(f"  - Compartment   : {self.compartment_id}")
        print(f"  - Subnet Count  : {len(self.subnets)}")
        if self.tags:
            print(f"  - Tags:")
            for k, v in self.tags.items():
                print(f"      {k:<12}: {v}")
