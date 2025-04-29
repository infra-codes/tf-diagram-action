class LoadBalancer:
    def __init__(self, id, name, subnet_id=None, ip_address=None):
        self.id = id
        self.name = name
        self.subnet_id = subnet_id
        self.ip_address = ip_address
        self.backend_sets = []
        self.listeners = []

    @staticmethod
    def from_tfstate(resource):
        ip_addresses = resource['values'].get('ip_addresses', [])
        ip_address = ip_addresses[0] if ip_addresses else None
        return LoadBalancer(
            resource['values']['id'],
            resource['values']['display_name'],
            resource['values'].get('subnet_ids', [None])[0],
            ip_address=ip_address  # 🔥 여기서 채워주기
        )

    def add_backend_set(self, backend_set):
        self.backend_sets.append(backend_set)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def pretty_print(self):
        print(f"LoadBalancer: {self.name} (ID: {self.id}, Subnet ID: {self.subnet_id})")
        if self.backend_sets:
            print("  BackendSets:")
            for backend_set in self.backend_sets:
                backend_set.pretty_print()
        else:
            print("  No BackendSets associated.")
        if self.listeners:
            print("  Listeners:")
            for listener in self.listeners:
                listener.pretty_print()
        else:
            print("  No Listeners associated.")

class BackendSet:
    def __init__(self, id, name, load_balancer_id):
        self.id = id
        self.name = name
        self.load_balancer_id = load_balancer_id
        self.backends = []

    @staticmethod
    def from_tfstate(resource):
        backend_set = BackendSet(
            resource['values']['id'],
            resource['values']['name'],
            resource['values']['load_balancer_id']
        )
        # Backend 추가 로직
        for backend in resource['values'].get('backend', []):
            backend_set.add_backend(Backend.from_tfstate(backend))
        return backend_set

    def add_backend(self, backend):
        self.backends.append(backend)

    def pretty_print(self):
        print(f"  BackendSet: {self.name} (ID: {self.id})")
        if self.backends:
            print("    Backends:")
            for backend in self.backends:
                backend.pretty_print()
        else:
            print("    No Backends associated.")

class Backend:
    def __init__(self, id, name, backendset_name):
        self.id = id
        self.name = name
        self.backendset_name = backendset_name

    @staticmethod
    def from_tfstate(resource, backendset_name):
        return Backend(
            resource['values']['id'],
            resource['values']['name'],
            backendset_name
        )

    def pretty_print(self):
        print(f"    Backend: {self.name} (ID: {self.id}, BackendSet: {self.backendset_name})")

class Listener:
    def __init__(self, id, name, port, protocol, load_balancer_id):
        self.id = id
        self.name = name
        self.port = port
        self.protocol = protocol
        self.load_balancer_id = load_balancer_id

    @staticmethod
    def from_tfstate(resource):
        return Listener(
            resource['values']['id'],
            resource['values']['name'],
            resource['values']['port'],
            resource['values']['protocol'],
            resource['values']['load_balancer_id']
        )

    def pretty_print(self):
        print(f"    Listener: {self.name} (ID: {self.id}, Port: {self.port}, Protocol: {self.protocol})")
