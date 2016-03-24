import argparse
from threading import Thread
import subprocess
from queue import Queue
from ipaddress import IPv4Interface


def pinger(queue, args):
    """Pings subnet"""
    while True:
        ip = queue.get()
        if ip is None:
            break

        ret = subprocess.call(["ping", "-c", "1", ip],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT)
        print_ip_mesgs(ret, ip, args)
        queue.task_done()


def cli_parse():
    parser = argparse.ArgumentParser(description='Will ping all address in given subnet in parallel')
    parser.add_argument('subnet', help='Input network subnet ie(192.168.0.1/24)')
    parser.add_argument('-v', '--verbose', help='display what hosts are not responding', action='store_true')

    args = parser.parse_args()

    return vars(args)


def print_ip_mesgs(success, ip, args):
    if success == 0:
        print("%s: is alive" % ip)
        print
    elif args.get('verbose'):
        print("%s: did not respond" % ip)
        print


def check_subnet(subnet):
    try:
        return IPv4Interface(subnet)
    except Exception as e:
        print(str(e))
        exit(0)


def get_hosts_from_subnet(subnet):
    return [ip for ip in subnet.network.hosts()]


def spawn_thread_pool(num_threads, queue, args):
    for num in range(num_threads):
        worker = Thread(target=pinger, args=(queue, args), daemon=True)
        worker.start()


def place_work_in_queue(ips, queue):
    for ip in ips:
        queue.put(str(ip))


def wait_for_worker_threads(queue):
    queue.join()


def create_queue():
    return Queue()


def main():
    args = cli_parse()
    subnet = check_subnet(args['subnet'])

    ips = get_hosts_from_subnet(subnet)
    queue = create_queue()

    spawn_thread_pool(len(ips), queue, args)
    place_work_in_queue(ips, queue)
    wait_for_worker_threads(queue)


if __name__ == '__main__':
    main()
