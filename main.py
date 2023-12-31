import logging
import pathlib
from typing import List
import requests
import cloudflare


class App:
    def __init__(self, adlist_name: str, adlist_url: str):
        self.adlist_name = adlist_name
        self.adlist_url = adlist_url
        self.name_prefix = f"[AdBlock-{adlist_name}]"
        self.logger = logging.getLogger("main")
        self.whitelist = self.loadWhitelist()

    def loadWhitelist(self):
        return open("whitelist.txt", "r").read().split("\n")

    def run(self):
        self.download_file()
        domains = self.convert_to_domain_list(self.adlist_name)

        # check if the list is already in Cloudflare
        cf_lists = cloudflare.get_lists(self.name_prefix)

        self.logger.info(f"Number of lists in Cloudflare: {len(cf_lists)}")

        # compare the lists size
        if len(domains) == sum([l["count"] for l in cf_lists]):
            self.logger.warning("Lists are the same size, skipping")

        else:

            #delete the policy

            cf_policies = cloudflare.get_firewall_policies(self.name_prefix)            
            if len(cf_policies)>0:
                cloudflare.delete_firewall_policy(cf_policies[0]["id"])

            # delete the lists
            for l in cf_lists:
                self.logger.info(f"Deleting list {l['name']}")
                cloudflare.delete_list(l["id"])

            cf_lists = []

            # chunk the domains into lists of 1000 and create them
            for chunk in self.chunk_list(domains, 1000):
                list_name = f"{self.name_prefix} {len(cf_lists) + 1}"

                self.logger.info(f"Creating list {list_name}")

                _list = cloudflare.create_list(list_name, chunk)

                cf_lists.append(_list)

        # get the gateway policies
        cf_policies = cloudflare.get_firewall_policies(self.name_prefix)

        self.logger.info(f"Number of policies in Cloudflare: {len(cf_policies)}")

        # setup the gateway policy
        if len(cf_policies) == 0:
            self.logger.info("Creating firewall policy")

            cf_policies = cloudflare.create_gateway_policy(f"{self.name_prefix} Block Ads", [l["id"] for l in cf_lists])

        elif len(cf_policies) != 1:
            self.logger.error("More than one firewall policy found")

            raise Exception("More than one firewall policy found")

        else:
            self.logger.info("Updating firewall policy")

            cloudflare.update_gateway_policy(f"{self.name_prefix} Block Ads", cf_policies[0]["id"], [l["id"] for l in cf_lists])

        self.logger.info("Done")

    def is_valid_hostname(self, hostname):
        import re
        if len(hostname) > 255:
            return False
        hostname = hostname.rstrip(".")
        allowed = re.compile('^[a-z0-9]([a-z0-9\-\_]{0,61}[a-z0-9])?$',re.IGNORECASE)
        labels = hostname.split(".")
        
        # the TLD must not be all-numeric
        if re.match(r"^[0-9]+$", labels[-1]):
            return False
        
        return all(allowed.match(x) for x in labels)



    def download_file(self):
        self.logger.info(f"Downloading file from {self.adlist_url}")

        r = requests.get(self.adlist_url, allow_redirects=True)

        path = pathlib.Path("tmp/" + self.adlist_name)
        open(path, "wb").write(r.content)

        self.logger.info(f"File size: {path.stat().st_size}")

    def convert_to_domain_list(self, file_name: str):
        with open("tmp/"+file_name, "r") as f:
            data = f.read()

        # check if the file is a hosts file or a list of domain
        is_hosts_file = False
        for ip in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]:
            if ip in data:
                is_hosts_file = True
                break

        domains = []
        for line in data.splitlines():

            
            # skip comments and empty lines
            if line.startswith("#") or line.startswith(";") or line == "\n" or line == "":
                continue

            if is_hosts_file:
                # remove the ip address and the trailing newline
                domain = line.split()[1].rstrip()

                # skip the localhost entry
                if domain == "localhost":
                    continue

            else:
                domain = line.rstrip()

            #Check whitelist
            if domain in self.whitelist:
                continue
            

            domains.append(domain)

        self.logger.info(f"Number of domains: {len(domains)}")

        return domains


        self.logger.info(f"Number of domains: {len(domains)}")
        print (domains)
        return domains

    def chunk_list(self, _list: List[str], n: int):
        for i in range(0, len(_list), n):
            yield _list[i : i + n]


if __name__ == "__main__":

    import configparser

    config = configparser.ConfigParser()
    config.read('config.ini')

    for list in config["Lists"]:
        print ("Setting list " +  list)
        app = App(list, config["Lists"][list])
        app.run()
