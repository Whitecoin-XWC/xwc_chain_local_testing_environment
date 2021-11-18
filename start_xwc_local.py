import os.path
import re
import sys
import subprocess
import threading
import time
import json
import requests

GENESIS_FILE = "data/my-genesis.json"
PRIV_FILE = "data/priv.keys"
WALLET_FILE = "data/my-wallet.json"
XWC_NODE_LOG = "data/xwc_node.log"
XWC_CLI_LOG = "data/xwc_cli.log"
XWC_NODE_RPC_ADDR = "127.0.0.1:8090"
XWC_CLI_RPC_ADDR = "127.0.0.1:29000"
XWC_WALLET_PASSWORD = "12345678"

MINING_PARAM = ["miner0", "miner1", "miner2", "miner3", "miner4", "miner5", "miner6", "miner7", "miner8",
                "miner9", "miner10", "miner11", "miner12", "miner13", "miner14", "miner15", "miner16",
                "miner17", "miner18", "miner19", "miner20", "miner21", "miner22", "miner23", "miner24"]


def run_xwc_node():
    subprocess.run(f"xwc_node.exe --data-dir=data --rpc-endpoint={XWC_NODE_RPC_ADDR} "
                   f"--genesis-json={GENESIS_FILE} --p2p-endpoint=127.0.0.1:3456 > {XWC_NODE_LOG} 2>&1",
                   shell=True,
                   stdout=subprocess.PIPE)


def run_xwc_cli(chainID):
    subprocess.run(f"xwc_cli.exe --wallet-file={WALLET_FILE} --server-rpc-endpoint=ws://{XWC_NODE_RPC_ADDR} "
                   f"--rpc-endpoint={XWC_CLI_RPC_ADDR} --chain-id={chainID} > {XWC_CLI_LOG} 2>&1",
                   shell=True,
                   stdout=subprocess.PIPE)


def rpc_request(url, method, args):
    args_j = json.dumps(args)
    payload = "{\r\n \"id\": 1,\r\n \"method\": \"%s\",\r\n \"params\": %s\r\n}" % (method, args_j)
    headers = {
        'content-type': "text/plain",
        'cache-control': "no-cache",
    }
    # logging.debug(self.baseUrl)
    for i in range(5):
        try:
            print("[HTTP POST] %s" % payload)
            response = requests.request("POST", f"http://{url}", data=payload, headers=headers)
            rep = response.json()
            if response.status_code != 200:
                print("response code error", response.status_code)
                continue
            return json.loads(response.text)

        except Exception as ex:
            print(f"Retry: {payload}")
            time.sleep(5)
            continue
    return None


def get_block_height():
    block_num = 0
    try:
        resp = rpc_request(XWC_CLI_RPC_ADDR, 'network_get_info', [])
        if resp:
            block_num = int(resp['result']['current_block_height'])
    except:
        pass
    return block_num


class XwcNodeMock:
    def __init__(self):
        self.xwc_privkeys = None
        self.miner_privkeys = {}
        self.wallfacer_privkeys = {}
        self.chainID = None
        self.threadPool = []

    def generate_genesis(self):
        """
        running command to generate genesis.json and save the private key
        :return:
        """
        if os.path.isfile(GENESIS_FILE):
            print(f"{GENESIS_FILE} has been created already! If you want to recreate, "
                  f"please delete the 'data' folder!")
            return True

        print("Generating genesis.json...")
        out = subprocess.run(f"xwc_node.exe --data-dir=data --create-genesis-json={GENESIS_FILE}", shell=True,
                             stdout=subprocess.PIPE)

        if out.returncode != 0:
            print(f"failed to generate genesis! returncode = {out.returncode}")
            return False

        # write the output into the file
        with open(f"{PRIV_FILE}", 'w') as f:
            output = out.stdout.decode().replace("\r", "")
            f.write(output)
            f.flush()

            # fetch the private keys:
            lines = output.split("\n")
            for each in lines:
                if each.startswith('xwc'):
                    self.xwc_privkeys = each[3:]
                elif each.startswith('miner'):
                    _tmp = re.split(r'[\s,]', each)
                    self.miner_privkeys[_tmp[0]] = _tmp[2]
                elif each.startswith("wallfacer"):
                    _tmp = re.split(r'[\s,]', each)
                    self.wallfacer_privkeys[_tmp[0]] = _tmp[2]

        print("The file 'genesis.json' has been finished!")
        return True

    @staticmethod
    def deploy_config():
        """
        copy the config.ini
        :return:
        """

        print("deploying config.ini...")
        out = subprocess.run("copy /Y config.ini data\config.ini", shell=True,
                             stdout=subprocess.PIPE)

        if out.returncode != 0:
            print(f"failed to generate genesis! returncode = {out.returncode}")
            return False

        print("The file 'config.ini' has been deployed!")
        return True

    def import_miner_keys(self):
        print("Start importing miner keys...")
        for miner in self.miner_privkeys:
            print(f"importing private key for {miner}!")
            _cmd = f"import_key {miner} {self.miner_privkeys[miner]}"
            res = rpc_request(XWC_CLI_RPC_ADDR, "import_key", [miner, self.miner_privkeys[miner]])
            if res is None:
                print(f"Failed to run cmd '_cmd'")
        print("importing miner keys finished!")

    def starting_node(self):
        print("starting XWC node...")
        t = threading.Thread(target=run_xwc_node, args=())
        t.start()
        self.threadPool.append(t)
        time.sleep(5)

        # get the chain ID if necessary(the chainID doesn't exist when running the first time):
        try:
            with open(XWC_NODE_LOG, 'r') as nodelog:
                search_obj = re.search('Chain ID is (.*)', nodelog.read())
                if search_obj:
                    self.chainID = search_obj.group(1)
        except Exception as e:
            print(e)
            return

        # starting xwc_cli and starting miners
        t = threading.Thread(target=run_xwc_cli, args=(self.chainID,))
        t.start()
        self.threadPool.append(t)
        time.sleep(5)

        # set_password or unlock
        with open(XWC_CLI_LOG, 'r') as cliLog:
            _line = cliLog.readlines()[-1]
            if _line.startswith("locked"):
                out = rpc_request(XWC_CLI_RPC_ADDR, "unlock", [XWC_WALLET_PASSWORD])
            elif _line.startswith("new"):
                out = rpc_request(XWC_CLI_RPC_ADDR, "set_password", [XWC_WALLET_PASSWORD])
                out = rpc_request(XWC_CLI_RPC_ADDR, "unlock", [XWC_WALLET_PASSWORD])

            if out is None:
                print("failed to open xwc_cli wallet!")

        # register miners
        self.import_miner_keys()

        # start mining
        out = rpc_request(XWC_CLI_RPC_ADDR, "start_mining", [MINING_PARAM])
        if out is None:
            print("failed to start mining!")

        out = rpc_request(XWC_CLI_RPC_ADDR, "start_miner", ["true"])
        if out is None:
            print("failed to set start_miner to true!")

        print("XWC node has been started!")

    def wait(self):
        for t in self.threadPool:
            t.join()


if __name__ == '__main__':
    print("Starting the local XWC testing environment!")
    mock = XwcNodeMock()
    mock.generate_genesis()
    mock.deploy_config()
    mock.starting_node()

    while True:
        blockHeight = get_block_height()
        print(f"Current block height = {blockHeight}")
        time.sleep(6)
