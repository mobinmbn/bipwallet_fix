""" Create and manage machine-payable web services.
"""
from ...two1.sell.machine import Two1Machine, Two1MachineNative, Two1MachineVirtual
from ...two1.sell.composer import Two1ComposerContainers
from ...two1.sell.exceptions.exceptions_sell import Two1SellNotSupportedException


def get_manager(sysdata):
    """ Return a manager for the 21 agent.

    Constucts a manager consisting of a platform-dependent
    machine layer and a service composer layer.

    Args:
        sysdata (two1.sell.util.client_helpers.PlatformDescription): A PlatformDescription as returned by
                                                                     two1.sell.util.client_helpers.get_platform
    """
    if sysdata.detected_os == "Darwin":
        return Two1Manager(Two1MachineVirtual(), Two1ComposerContainers())
    elif sysdata.detected_os == "Linux" and sysdata.is_supported:
        return Two1Manager(Two1MachineNative(), Two1ComposerContainers())
    else:
        raise Two1SellNotSupportedException


class Two1Manager:
    """ Two1Manager manages the machine and composer layers that make up
    the 21 agent.

    Two1Manager provides an API for creating and managing machine-payable
    microservices.  A pluggable networking layer enables peer discovery on
    the various 21 marketplace networks.

    """

    def __init__(self, machine, composer):
        self.machine = machine
        self.composer = composer

    # machine layer

    def start_networking(self):
        """ Start the pluggable networking layer.
        """
        return self.machine.start_networking()

    def stop_networking(self):
        """ Start the pluggable networking layer.
        """
        return self.machine.stop_networking()

    def status_networking(self):
        """ Start the pluggable networking layer.

        Returns: True if ZeroTier One service is running.
        """
        return self.machine.status_networking()

    def get_market_address(self):
        """ Check if connected to 21mkt network.
        """
        return self.machine.host

    def get_server_port(self):
        """ Return the 21 server port.
        """
        return self.machine.port

    def connect_market(self, client, network="21mkt"):
        """ Connect to 21mkt network.
        Args:
            client: Client to join network
            network: Network to join
        """
        return self.machine.connect_market(client, network)

    def create_machine(self, vm_name=Two1MachineVirtual.DEFAULT_VM_NAME,
                       vdisk_size=Two1MachineVirtual.DEFAULT_VDISK_SIZE,
                       vm_memory=Two1MachineVirtual.DEFAULT_VM_MEMORY,
                       service_port=Two1Machine.DEFAULT_SERVICE_PORT):
        """ Create the virtual machine.

        Args:
            vm_name: Name of the VM to create.
            vdisk_size: Size of disk for the VM in MB.
            vm_memory: Size of memory for the VM in MB
            service_port: Port on which the router container will listen.
        """
        return self.machine.create_machine(vm_name, vdisk_size, vm_memory,
                                           service_port)

    def read_machine_config(self, *args):
        """Read machine config from file.
        """
        return self.machine.read_machine_config(*args)

    def write_machine_config(self, *args):
        """ Write machine config to file.
        """
        return self.machine.write_machine_config(*args)

    def delete_machine(self):
        """ Delete the virtual machine.
        """
        return self.machine.delete_machine()

    def start_machine(self):
        """ Start the virtual machine.
        """
        return self.machine.start_machine()

    def start_docker(self):
        """ Start the docker service.
        """
        return self.machine.start_docker()

    def status_docker(self):
        """ Get the docker service status
        """
        return self.machine.status_docker()

    def stop_machine(self):
        """ Stop the virtual machine.
        """
        return self.machine.stop_machine()

    def status_machine(self):
        """ Get the virtual machine status.
        """
        return self.machine.status_machine()

    # composer layer

    def read_server_config(self, *args):
        """Reads configuration of containerized servers.
        """
        return self.composer.read_server_config(*args)

    def initialize_server(self, *args):
        """ Initialize micropayments server config files.
        """
        return self.composer.initialize_server(*args)

    def start_services(self, *args):
        """ Start services.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.start_services(*args)

    def stop_services(self, *args):
        """ Stop services.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.stop_services(*args)

    def force_stop_services(self, *args, **kwargs):
        """ Silently force stops all services.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.silently_force_stop_all_services(*args, **kwargs)

    def status_services(self, *args):
        """ Get status of all services.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.status_services(*args)

    def status_router(self, *args):
        """ Get router status.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.status_router(*args)

    def status_payments_server(self, *args):
        """ Get payments status.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.status_payments_server(*args)

    def get_running_services(self):
        """ Get list of running services.
        """
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.get_running_services()

    def publish_service(self, *args, **kwargs):
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.publish_service(*args, **kwargs)

    def get_services_mnemonic(self, *args, **kwargs):
        return self.composer.get_services_mnemonic(*args, **kwargs)

    def get_available_services(self, *args, **kwargs):
        return self.composer.ServiceManager.available_services(*args, **kwargs)

    def get_image(self, *args, **kwargs):
        return self.composer.ServiceManager.get_image(*args, **kwargs)

    def pull_image(self, *args, **kwargs):
        self.composer.connect(self.machine.env(),
                              self.machine.host,
                              self.machine.MACHINE_CONFIG_FILE)
        return self.composer.pull_image(*args, **kwargs)

    def add_service(self, *args, **kwargs):
        return self.composer.ServiceManager.add_service(*args, **kwargs)

    def remove_service(self, *args, **kwargs):
        return self.composer.ServiceManager.remove_service(*args, **kwargs)

    def available_user_services(self, *args, **kwargs):
        return self.composer.ServiceManager.available_user_services(*args, **kwargs)

    def available_21_services(self, *args, **kwargs):
        return self.composer.ServiceManager.available_21_services(*args, **kwargs)
