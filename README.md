# start_xwc_local.py

A python script for easily setting up an isolated one-node XWC chain locally.

# Dependencies

* Python 3.9

* Using packages: os, re, sys, subprocess, threading, time, json, requests

  

# Usage

* Go into the folder that the scripts and binaries are restored.
* Run the python script by command "python start_xwc_local.py"
* Check the output, if the chain blocks are generated, everything works well.
* The log files "xwc_cli.log" and "xwc_node.log" can be used for debugging issues.
* the xwc wallets RPC service listens on 127.0.0.1:29000



# Example

Once the xwc node is running, the command can be executed via RPC, an RPC request looks as below:

​		curl -l -H "Content-Type:application/json" -H "Accept:application/json" -X POST  -d "{\"id\":1, \"method\":\"network_get_info\", \"params\":[]}" http://127.0.0.1:29000

