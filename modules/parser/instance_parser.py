class Instance:
    def __init__(
        self,
        instance_id: str,
        index: str,
        display_name: str,
        subnet_id: str,
        private_ip: str,
        public_ip: str,
        shape: str,
        state: str,
        nsg_ids: list = None,
        tags: dict = None,
        ocpus: float = None,
        memory: int = None,
        boot_volume_size: int = None,
    ):
        self.id = instance_id
        self.index = index
        self.name = display_name
        self.subnet_id = subnet_id
        self.private_ip = private_ip
        self.public_ip = public_ip
        self.shape = shape
        self.state = state
        self.nsg_ids = nsg_ids or []
        self.tags = tags or {}
        self.ocpus = ocpus
        self.memory = memory
        self.boot_volume_size = boot_volume_size

    @classmethod
    def from_tfstate(cls, resource_block: dict):
        values = resource_block.get("values", {})
        vnic = values.get("create_vnic_details", [{}])[0]
        
        shape_config = values.get("shape_config", [{}])[0]
        ocpus = shape_config.get("ocpus")
        memory = shape_config.get("memory_in_gbs")

        boot_volume_size = None
        if 'source_details' in values:
            for source in values['source_details']:
                if 'boot_volume_size_in_gbs' in source:
                    boot_volume_size = int(source['boot_volume_size_in_gbs'])

        return cls(
            instance_id=values.get("id"),
            index=resource_block.get("index"),
            display_name=values.get("display_name"),
            subnet_id=vnic.get("subnet_id"),
            private_ip=vnic.get("private_ip"),
            public_ip=values.get("public_ip"),
            shape=values.get("shape"),
            state=values.get("state"),
            nsg_ids=vnic.get("nsg_ids", []),
            tags=vnic.get("freeform_tags", {}),
            ocpus=ocpus,
            memory=memory,
            boot_volume_size=boot_volume_size,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "index": self.index,
            "name": self.name,
            "subnet_id": self.subnet_id,
            "private_ip": self.private_ip,
            "public_ip": self.public_ip,
            "shape": self.shape,
            "state": self.state,
            "nsg_ids": self.nsg_ids,
            "tags": self.tags,
            "ocpus": self.ocpus,
            "memory": self.memory,
            "boot_volume_size": self.boot_volume_size,
        }

    def pretty_print(self):
        print(f"    [Instance: {self.index}]")
        print(f"      - Name            : {self.name}")
        print(f"      - State           : {self.state}")
        print(f"      - Shape           : {self.shape}")
        print(f"      - Subnet ID       : {self.subnet_id}")
        print(f"      - Private IP      : {self.private_ip}")
        if self.public_ip:
            print(f"      - Public IP       : {self.public_ip}")
        if self.tags:
            print(f"      - Tags:")
            for k, v in self.tags.items():
                print(f"          {k:<15}: {v}")
        if self.nsg_ids:
            print(f"      - NSG IDs         :")
            for nsg in self.nsg_ids:
                print(f"          - {nsg}")
        print(f"      - OCPUs           : {self.ocpus}")
        print(f"      - Memory (GB)     : {self.memory}")
        print(f"      - Boot Volume Size : {self.boot_volume_size} GB")
