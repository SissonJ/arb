from logging import exception
from typing import List

def find_cycles( pair_list, start_addr ):
    cycles_list = []
    for pairs in pair_list:
        if( pairs.token0_addr == start_addr or pairs.token1_addr == start_addr):
            cycles_list.append(find_cycles_recursive(pair_list, pairs, start_addr, []))
    return cycles_list

def find_cycles_recursive(pair_list, pair, start_addr, addr_list: List):
    if( (pair.token0_addr == start_addr or pair.token1_addr == start_addr) and not len(addr_list) == 0 ):
        addr_list.append(pair)
        return addr_list
    try:
        if( addr_list.index(pair) ):
            return 0
    except Exception as e:
        pass
    #print(addr_list)
    for pairs in pair_list:
        if( not pairs == pair ):
            if( (not pair.token1_addr == start_addr and (pair.token1_addr == pairs.token0_addr or pair.token1_addr == pairs.token1_addr)) or (not pair.token0_addr == start_addr and (pair.token0_addr == pairs.token0_addr or pair.token0_addr == pairs.token1_addr))):
                addr_list.append(pair)
                temp = find_cycles_recursive(pair_list, pairs, start_addr, addr_list)
                if ( temp == 0 ):
                    continue
                return temp
    return None