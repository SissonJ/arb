from logging import exception
from typing import List

def find_cycles( pair_list, start_addr, find_addr ):
    cycles_list = []
    temp = []
    for pairs in pair_list:
        if( pairs.token0_addr == start_addr ):
            while not temp == 0:
                temp = find_cycles_recursive(pair_list, pairs, find_addr, pairs.token1_addr, [], cycles_list)
                if temp == 0:
                    continue
                cycles_list.append(temp)
            temp = []
        if( pairs.token1_addr == start_addr ):
            while not temp == 0:
                temp = find_cycles_recursive(pair_list, pairs, find_addr, pairs.token0_addr, [], cycles_list)
                if temp == 0:
                    continue
                cycles_list.append(temp)
            temp = []
    return cycles_list

def find_cycles_recursive(pair_list, pair, find_addr, current_addr, addr_list: List, cycles_list: List):
    if( (pair.token0_addr == find_addr or pair.token1_addr == find_addr) and not len(addr_list) == 0 ):
        addr_list.append(pair)
        return addr_list
    if( pair in addr_list ):
        return 0
    temp = []
    for pairs in pair_list:
        if( not pairs == pair ):
            if( pairs.token0_addr == current_addr ):
                addr_list.append(pair)
                temp = find_cycles_recursive( pair_list, pairs, find_addr, pairs.token1_addr, addr_list, cycles_list )
                if ( temp == 0 or temp in cycles_list ):
                    continue
                return temp
            if( pairs.token1_addr == current_addr ):
                addr_list.append(pair)
                temp = find_cycles_recursive( pair_list, pairs, find_addr, pairs.token0_addr, addr_list, cycles_list )
                if ( temp == 0 or temp in cycles_list ):
                    continue
                return temp
    return 0