import asyncio
from tracemalloc import start
from env import endpoint
from config import sscrtAdresses

from Pair import Pair
from secret_sdk.client.lcd.lcdclient import AsyncLCDClient
from utils_async import generateTxEncryptionKeysAsync
from utils_router import find_cycles

SIENNA_FACTORY = "secret18sq0ux28kt2z7dlze2mu57d3ua0u5ayzwp6v2r"
SSWAP_FACTORY = "secret1fjqlk09wp7yflxx7y433mkeskqdtw3yqerkcgp"

async def main():
    client = AsyncLCDClient(endpoint, "secret-4")
    sienna_code_hash = await client.wasm.contract_hash(SIENNA_FACTORY)
    sswap_code_hash = await client.wasm.contract_hash(SSWAP_FACTORY)
    nonceDict, keyDict = await generateTxEncryptionKeysAsync(client)
    print("here")
    sienna_factory_info = await client.wasm.contract_query(
        SIENNA_FACTORY,
        {"list_exchanges":{"pagination":{"start":1,"limit":30}}},
        sienna_code_hash,
        nonceDict["first"],
        keyDict["first"]
    )
    print("here")
    sswap_factory_info = await client.wasm.contract_query(
        SSWAP_FACTORY,
        {"pairs":{"limit":30}},
        sswap_code_hash,
        nonceDict["second"],
        keyDict["second"]
    )
    pair_list = []
    for pair in sienna_factory_info["list_exchanges"]["exchanges"]:
        pair_list.append( Pair(pair, "", "sienna") )
    for pair in sswap_factory_info["pairs"]:
        code_hash = await client.wasm.contract_hash(pair["contract_addr"])
        pair_list.append( Pair(pair, code_hash, "sswap") )
    start_addr = sscrtAdresses["SSCRT_ADDRESS"]
    current_addr = sscrtAdresses["SSCRT_ADDRESS"]
    dex = ""
    #adjacency_list = []
    #index = 0
    #for pair0 in pair_list:
    #    adjacency_list.append([])
    #    for pair1 in pair_list:
    #        if( not pair0.pair_addr == pair1.pair_addr and (pair0.token0_addr == pair1.token0_addr or pair0.token0_addr == pair1.token1_addr or pair0.token1_addr == pair1.token0_addr or pair0.token1_addr == pair1.token1_addr)):
    #            adjacency_list[index].append(pair1.pair_addr)
    #        else:
    #            adjacency_list[index].append(0)
    #    index = index + 1
    #print(adjacency_list[0])
    cycles_list = find_cycles(pair_list, start_addr, start_addr)
    #print(cycles_list)
    index = 0
    for cycles in cycles_list:
        if ( cycles is None ):
            continue
        print(index)
        index = index + 1
        for pair in cycles:
            #print(pair.pair_addr)
            print(pair)
            #print(await pair.query_pair(client))
        
    await client.session.close()
    return 0

#asyncio.run(main())