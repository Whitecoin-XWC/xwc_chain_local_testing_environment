# start_xwc_local.py

A python script for easily setting up an isolated one-node XWC chain locally.

# Dependencies
* windows
* Python 3.9
* Using packages: os, re, sys, subprocess, threading, time, json, requests
  

# Usage

* Downloads the source code 'start_xwc_local.py' and two binaries 'xwc_cli.exe' and 'xwc_node.exe' in the release attachment. The whole program should look like this:
  ![image](https://user-images.githubusercontent.com/92837072/142399292-23a633c6-3784-4dae-b1d0-ddf85a4045c3.png)

* Go into the folder that the scripts and binaries are restored.
* Run the python script by command "python start_xwc_local.py"
* Check the output, the chain blocks should be generated constantly if everything works well.

  ![image](https://user-images.githubusercontent.com/92837072/142399639-57e4172e-a256-454b-aeab-1438e813a15c.png)

* The log files "xwc_cli.log" and "xwc_node.log" can be used for debugging issues.
* By default, the xwc wallet RPC service listens on 127.0.0.1:29000.


# Example

Once the xwc node is running, the command can be executed via RPC, an RPC request looks as below:

```shell
curl -l -H "Content-Type:application/json" -H "Accept:application/json" -X POST  -d "{\"id\":1, \"method\":\"network_get_info\", \"params\":[]}" http://127.0.0.1:29000
```
