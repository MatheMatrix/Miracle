from OpenFlow import libopenflow as of
from coreapps import arp_server as arp_server
from database import flow_database as flow_database
from threading import Timer
from database import timer_list as timer_list

"""
TODO:switch the packets by mactoport table.
Author:Licheng
Time:2014/5/7

"""

mactoport = {} #src_mac :in_port = dst_mac :out_port
MAC_TIMEOUT = 600

#____________________________________________________________

def __init__():
	pass

def switch(pkt,dpid,*args):
	rmsg = pkt
	pkt_in_msg = pkt.payload
	pkt_parsed = pkt.payload.payload
		
	mactoport_add(src_mac = pkt_parsed.src, in_port = pkt_in_msg.in_port)
	if pkt_parsed.dst == "ff:ff:ff:ff:ff:ff":
		if pkt_parsed.payload.type == 0x0806:   #all ARP will be ARP REQUEST first.
			return arp_server.arp_reply_handler(pkt)
		else:
			pkt_out = of.ofp_header()/of.ofp_pktout_header()/of.ofp_action_output()
			pkt_out.payload.payload.port = 0xfffb
			pkt_out.payload.buffer_id = pkt_in_msg.buffer_id
			pkt_out.payload.in_port = pkt_in_msg.in_port
			pkt_out.payload.actions_len = 8
			pkt_out.length = len(pkt_out)
			return pkt_out
	else:
		if pkt_parsed.dst in mactoport:
			out_port = mactoport[pkt_parsed.dst]
		else:
			out_port = 0xfffb
		flow_mod = of.create_flow(pkt, out_port)
		flow_database.flow_add(flow_mod,dpid) 
		return flow_mod

def mactoport_delete(*src_mac):
	del mactoport[src_mac]

def mactoport_add(*src_mac,**in_port):
	if src_mac not in mactoport:
		mactoport[src_mac] = in_port
		#mac_timer =Timer(MAC_TIMEOUT,mactoport_delete,src_mac)
		#mac_timer.start() 
		#timer_list.timer_list.append(mac_timer)

