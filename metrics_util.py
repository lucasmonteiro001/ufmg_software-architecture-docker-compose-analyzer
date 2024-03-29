import pandas as pd
import yaml
from collections import namedtuple

MAX = 1000000

_Max_service = namedtuple('Services', ['repo', 'num_servicos'])
_Max_networks = namedtuple('Networks', ['repo', 'num_redes'])
_Max_port = namedtuple('Ports', ['repo', 'num_portas'])
_Max_depends = namedtuple('Dependencies', ['repo', 'num_dependencias'])


class MetricsUtil(object):
    @staticmethod
    def get_metrics(file_list):

        max_service = _Max_service(repo=None, num_servicos=0)
        max_redes = _Max_networks(repo=None, num_redes=0)
        max_ports = _Max_port(repo=None, num_portas=0)
        max_dependencies = _Max_depends(repo=None, num_dependencias=0)

        errors = list()
        file_data = dict()
        service_data = dict()

        cont_file = 0
        cont_service = 0
        cont_max = 0

        # parses each file
        for file_path in file_list:

            try:
                # print cont_max
                # print "\t" + file_path

                if cont_max >= MAX:
                    break

                cont_max += 1

                with open(file_path, "r") as stream:
                    yaml_file = yaml.load(stream)

                # if there is any service
                if yaml_file.get("services"):
                    services = yaml_file.get("services")
                    version_number = yaml_file.get("version")

                    if version_number > 0:
                        version_number = int(float(version_number))

                    number_of_networks = len(yaml_file.get("networks") or [])
                else:
                    services = yaml_file
                    version_number = 0
                    number_of_networks = 0

                number_of_services = len(services)

                file_data["f: ({})".format(cont_file)] = pd.Series(
                    [number_of_services, version_number, number_of_networks],
                    ["#services", "version_number", "#networks"])

                if len(services) > max_service.num_servicos:
                    max_service = _Max_service(repo=file_path, num_servicos=len(services))

                if number_of_networks > max_redes.num_redes:
                    max_redes = _Max_networks(repo=file_path, num_redes=number_of_networks)

                # loop through services
                for s in services:

                    # remove data that was stored for unprocessed file
                    try:
                        # if the file has no service key
                        if yaml_file.get(s):
                            service = yaml_file.get(s)
                        else:
                            service = services[s]

                        ports = service.get("ports") or []
                        number_of_ports = len(ports)

                        depends_on = service.get("depends_on") or []
                        number_of_depends_on = len(depends_on)

                        volumes = service.get("volumes") or []
                        number_of_volumes = len(volumes)

                        if number_of_ports > max_ports.num_portas:
                            max_ports = _Max_port(repo=file_path, num_portas=number_of_ports)

                        if number_of_depends_on > max_dependencies.num_dependencias:
                            max_dependencies = _Max_depends(repo=file_path, num_dependencias=number_of_depends_on)

                        service_data["s: ({})".format(cont_service)] = pd.Series(
                            [number_of_ports, number_of_depends_on, number_of_volumes],
                            ["#ports", "#depends_on", "#volumes"])

                        cont_service += 1

                    except Exception:
                        # remove data that was stored for unprocessed file
                        try:
                            del service_data["s: ({})".format(cont_service)]
                        except Exception:
                            pass

                        raise "error"

                cont_file += 1

            except Exception:
                # print "error: " + file_path
                # errors.append(file_path)

                # remove data that was stored for unprocessed file
                try:
                    del file_data["f: ({})".format(cont_file)]

                except Exception:
                    pass


        print max_service
        print max_redes
        print max_ports
        print max_dependencies

        # save error logs
        with open("errors.txt", "w") as f:
            for l in errors:
                f.write(l)
                f.write("\n")

        return file_data, service_data
