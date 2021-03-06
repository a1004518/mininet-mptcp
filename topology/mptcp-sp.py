#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.link import TCLink
import time
import subprocess
import os,signal
import sys
#    ___r1____
#   /          \0  1
# h1            r3---h2
#             
#   
max_queue_size = 20 
#os.system('sysctl -w net.mptcp.mptcp_path_manager=fullmesh ')
#os.system('modprobe mptcp_rr && sysctl -w net.mptcp.mptcp_scheduler=roundrobin ')
#os.system('modprobe mptcp_olia && sysctl -w net.ipv4.tcp_congestion_control=olia ')
#os.system('echo 3 | sudo tee /sys/module/mptcp_fullmesh/parameters/num_subflows') 
net = Mininet( cleanup=True )
h1 = net.addHost('h1',ip='10.0.1.1')
r1 = net.addHost('r1',ip='10.0.1.2')
r3 = net.addHost('r3',ip='10.0.5.1')
h2 = net.addHost('h2',ip='10.0.5.2')
c0 = net.addController('c0')

net.addLink(h1,r1,intfName1='h1-eth0',intfName2='r1-eth0',cls=TCLink , bw=2, delay='20ms', max_queue_size=max_queue_size)
net.addLink(r1,r3,intfName1='r1-eth1',intfName2='r3-eth0',cls=TCLink , bw=2, delay='20ms', max_queue_size=max_queue_size)
net.addLink(r3,h2,intfName1='r3-eth1',intfName2='h2-eth0',cls=TCLink , bw=2, delay='10ms', max_queue_size=max_queue_size)
net.build()
h1.cmd("ifconfig h1-eth0 10.0.1.1/24")
h1.cmd("route add default gw 10.0.1.2 dev h1-eth0")

r1.cmd("ifconfig r1-eth0 10.0.1.2/24")
r1.cmd("ifconfig r1-eth1 10.0.2.1/24")
r1.cmd("ip route add to 10.0.1.0/24 via 10.0.1.1")
r1.cmd("ip route add to 10.0.2.0/24 via 10.0.2.2")
r1.cmd("ip route add to 10.0.5.0/24 via 10.0.2.2")
r1.cmd('sysctl net.ipv4.ip_forward=1')

r3.cmd("ifconfig r3-eth0 10.0.2.2/24")
r3.cmd("ifconfig r3-eth1 10.0.5.1/24")
r3.cmd("ip route add to 10.0.1.0/24 via 10.0.2.1")
r3.cmd("ip route add to 10.0.2.0/24 via 10.0.2.1")
r3.cmd("ip route add to 10.0.5.0/24 via 10.0.5.2")
r3.cmd('sysctl net.ipv4.ip_forward=1')

h2.cmd("ifconfig h2-eth0 10.0.5.2/24")
h2.cmd("route add default gw 10.0.5.1")

net.start()
time.sleep(1)
p2 = h2.popen("./tcpudp/mytcpserver -h10.0.5.2 -p1234")
p1=h1.popen("./tcpudp/fileclient -h10.0.5.2 -p1234")
while 1:
    time.sleep(1)
    ret=subprocess.Popen.poll(p1)
    if ret is None:
    	continue
    else:
    	break
time.sleep(10)
os.killpg(os.getpgid(p2.pid),signal.SIGTERM)
p2.wait()
net.stop()

