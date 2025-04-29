class NSGSecurityRule:
    def __init__(self, id, direction, protocol, source, destination, description=None, tcp_options=None):
        self.id = id
        self.direction = direction
        self.protocol = protocol
        self.source = source
        self.destination = destination
        self.description = description
        self.tcp_options = tcp_options or {}
        
    def get_port_range_str(self):
        if not self.tcp_options:
            return ""
        dest_ports = self.tcp_options.get("destination_port_range", [])
        src_ports = self.tcp_options.get("source_port_range", [])
        port_info = []
        
        if dest_ports:
            for port_range in dest_ports:
                # if port_range.get("min") == port_range.get("max"):
                #     port_info.append(f"port {port_range['min']}")
                # else:
                    port_info.append(f"ports {port_range['min']}-{port_range['max']}")
                    
        if src_ports:
            for port_range in src_ports:
                # if port_range.get("min") == port_range.get("max"):
                #     port_info.append(f"src port {port_range['min']}")
                # else:
                    port_info.append(f"src ports {port_range['min']}-{port_range['max']}")
                    
        return " ".join(port_info) if port_info else ""


class NSG:
    _id_name_map = {}

    def __init__(self, id, name, security_rules=None):
        self.id = id
        self.name = name
        self.security_rules = security_rules if security_rules else []
        NSG._id_name_map[self.id] = self.name

    def add_security_rule(self, rule):
        if isinstance(rule, NSGSecurityRule):
            self.security_rules.append(rule)

    @classmethod
    def get_name_by_id(cls, nsg_id):
        return cls._id_name_map.get(nsg_id, nsg_id[-6:])

    @classmethod
    def reset(cls):
        cls._id_name_map = {}

    @classmethod
    def from_tfstate(cls, resource):
        values = resource.get("values", {})
        security_rules = []
        for rule in values.get("security_rules", []):
            security_rules.append(NSGSecurityRule(
                id=rule.get("id"),
                direction=rule.get("direction"),
                protocol=rule.get("protocol"),
                source=rule.get("source"),
                destination=rule.get("destination"),
                description=rule.get("description"),
                tcp_options=rule.get("tcp_options", [{}])[0] if rule.get("tcp_options") else None
            ))
        return cls(
            id=values.get("id"),
            name=values.get("display_name"),
            security_rules=security_rules
        )
