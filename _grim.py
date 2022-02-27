import json
from web3 import Web3, constants

def topic_to_address(value):
    return Web3.toChecksumAddress('{0:#0{1}x}'.format(int(value, 16), 42))

# For faster execution, these files were generated using Beefy's Validator node over IPC
# web3_provider = Web3.IPCProvider('/home/beefy/.opera/opera.ipc')
web3_provider = Web3.HTTPProvider('https://rpc.ftm.tools')
rpc = Web3(web3_provider)

transfer_topic = ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef']

# List of Grim vaults targeted by whitehat transactions. Includes deployment block, explained below
vaults = {
    'G-3POOL-V2' : {'address': '0x9f490db207c362211b0ec5ab80382618e1488030', 'startBlock': 19551914},
    'G-BTC-FTM-f': {'address': '0xb94638010b971acd2481b136aa1ea2f069583f51', 'startBlock': 21479899},
    'G-BTC-FUS-U': {'address': '0x0489a43bd99f329b4bdb80ce866f3e95397aad41', 'startBlock': 17883906},
    'G-BTC-i'    : {'address': '0x0d6fa7a96699bc678bcb398967140559bc507ae6', 'startBlock': 22655890},
    'G-DAI-FTM-k': {'address': '0xafe94ae69f838f5d65e4068c9f6996d21e2787f4', 'startBlock': 24770656},
    'G-DAI-USD-j': {'address': '0xd4c100449748c0c9b181fe88e86243451edfdff0', 'startBlock': 22664353},
    'G-FTM-BNB-2': {'address': '0xc6ac0dd798da6a7d41a7e4717c04ca1297d58b15', 'startBlock': 7711437},
    'G-FTM-LIN-0': {'address': '0x594bf11801148753511e14c160e430fbf5ccdffb', 'startBlock': 18788684},
    'G-HTZ-ETH-O': {'address': '0x0af7bfae990a09674f78fd56dd76e471556386ec', 'startBlock': 16312516},
    'G-HTZ-FTM-O': {'address': '0x67d8c630aa346f1eb5bd71da3d4e00889bb545da', 'startBlock': 16301693},
    'G-ICE-USD-j': {'address': '0x58fad0583afb7efd1ca3b18e929107d93415599f', 'startBlock': 22664969},
    'G-MEM-MIM-i': {'address': '0xddcc8125195d64d77c794c4dbcbbaf6e80b9f2b8', 'startBlock': 22655223},
    'G-MEMO-i'   : {'address': '0xd1e4c9fce27a1de7139e89688189ed4a27e79d8d', 'startBlock': 22654090},
    'G-OLI-FTM-R': {'address': '0x8ff61b93e2f6e3cb29c4af0c656530f8a140624e', 'startBlock': 17170995},
    'G-SCA-FTM-i': {'address': '0xacfaf0b9b6b97b8122ed449a2e7705956ad264b2', 'startBlock': 22649073},
    'G-SHA-FTM-B': {'address': '0x62a6fe5edc535892cab6a65b23c097c3c6c5b45b', 'startBlock': 11766164},
    'G-SIN-USD-a': {'address': '0xdbc946e585f26576adf993554474cee7bdd05caf', 'startBlock': 19392122},
    'G-SPIRIT-i' : {'address': '0x077b4b9149c6df3ba9c7e49720b6b1943dfc2a34', 'startBlock': 22649073},
    'G-SUS-FTM-O': {'address': '0x81348439f77cea7ef61fe73749bde625e28a8392', 'startBlock': 18786956},
    'G-TOM-FTM-8': {'address': '0xfdc10560bd833b763352c481f5785dd69c803429', 'startBlock': 9393907},
    'G-TSH-FTM-8': {'address': '0xc7abe55e5532dda1943bbe5a94bd837dcd96e233', 'startBlock': 9393957},
    'G-USD-FTM-f': {'address': '0x7768ead8156cb6c8d96f9dc7699ceb2032a59ecc', 'startBlock': 21479548},
    'G-WIN-FTM-U': {'address': '0x4391fe69a4eb15a6a2d75b38d8d3c3adae0b7605', 'startBlock': 17880608},
    'G-YEL-FTM'  : {'address': '0x4d0caf7b36b958736f2529c9d0e547ce22656d4e', 'startBlock': 16560082},
    'G-ZOO-BRU-N': {'address': '0x9a57b392cba70b9aed9d3c0f4c7b43b049615cd4', 'startBlock': 15084004},
    'XGinSpirit' : {'address': '0x53abd9f4b30f7d1a1bcf918055b53e749afdc775', 'startBlock': 16005278}
}

# Earliest deployment block of affected Grim vaults
start_block = min([vault['startBlock'] for vault in vaults.values()])
# The end block of all whitehat attempts
end_block = 25436197

vault_addresses = list(map(Web3.toChecksumAddress, [vault['address'] for vault in vaults.values()]))
# Reverse mapping for identification
vault_map = dict(zip(vault_addresses, vaults.keys()))

# Global list of holders
all_holders = {address: {} for address in vault_addresses}

# Chunk our logs into 10000 blocks. Adjust based on your RPC's capabilities
block_range = range(start_block, end_block, 10000)
for current_block in block_range:
    print(f'Blocks {current_block} to {current_block + block_range.step - 1}')
    logs = rpc.eth.get_logs({'fromBlock': current_block, 'toBlock': current_block + block_range.step - 1, 'address': vault_addresses, 'topics': transfer_topic})

    for log in logs:
        vault = log.address
        addr_from = topic_to_address(log.topics[1].hex())
        addr_to = topic_to_address(log.topics[2].hex())
        value = int(log.data, 16)

        if not value:
            # Don't bother evaluating if there's no change in value
            continue

        if addr_from != constants.ADDRESS_ZERO:
            all_holders[vault][addr_from] -= value

        if addr_to != constants.ADDRESS_ZERO:
            try:
                all_holders[vault][addr_to] += value
            except KeyError:
                all_holders[vault][addr_to] = value

for vault_address, balances in all_holders.items():
    holders = {address: balance for address, balance in balances.items() if balance}
    vault_id = vault_map[vault_address]

    with open(f'{vault_id}.json', 'w') as outfile:
        json.dump(holders, outfile)
