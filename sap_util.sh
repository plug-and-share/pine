#!/bin/bash

VM="$1"
IP=$(arp -an | grep "`virsh dumpxml $VM | grep "mac address" | sed "s/.*'\(.*\)'.*/\1/g"`" | awk '{gsub(/[\(\)]/,"",$2); print $2}')
echo $IP
cat /home/vipro/.ssh/id_rsa.pub | ssh -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null cupid@$IP 'cat >> /home/cupid/.ssh/authorized_keys'
