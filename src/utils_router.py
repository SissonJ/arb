from logging import exception
from typing import List

def find_cycles( pair_list, start_addr, find_addr ):
    cycles_list = []
    temp = []
    for pairs in pair_list:
        if( pairs.token0_addr == start_addr ):
            temp = find_cycles_recursive(pair_list, pairs, find_addr, pairs.token1_addr, [], cycles_list)
            if not temp:
                continue
            cycles_list.append(temp)
            temp = []
        if( pairs.token1_addr == start_addr ):
            temp = find_cycles_recursive(pair_list, pairs, find_addr, pairs.token0_addr, [], cycles_list)
            if not temp:
                continue
            cycles_list.append(temp)
            temp = []
    return cycles_list

def find_cycles_recursive(pair_list, pair, find_addr, current_addr, addr_list: List, cycles_list: List):
    if( (pair.token0_addr == find_addr or pair.token1_addr == find_addr) and not not addr_list ):
        addr_list.append(pair)
        return addr_list
    if( pair in addr_list ):
        return []
    temp = []
    for pairs in pair_list:
        if( not pairs == pair ):
            if( pairs.token0_addr == current_addr ):
                addr_list.append(pair)
                temp = find_cycles_recursive( pair_list, pairs, find_addr, pairs.token1_addr, addr_list, cycles_list )
                if ( not temp or temp in cycles_list ):
                    continue
                return temp
            if( pairs.token1_addr == current_addr ):
                addr_list.append(pair)
                temp = find_cycles_recursive( pair_list, pairs, find_addr, pairs.token0_addr, addr_list, cycles_list )
                if ( not temp or temp in cycles_list ):
                    continue
                return temp
    return []

class TestPair:
  id: int
  token0_addr: int
  token1_addr: int

  def __init__(self, id, token0_addr, token1_addr):
    self.id = id
    self.token0_addr = token0_addr
    self.token1_addr = token1_addr

def testRouter():
  pair_list = []
  pair_list.append(TestPair(1,0,1))
  pair_list.append(TestPair(2,1,2))
  pair_list.append(TestPair(3,2,3))
  pair_list.append(TestPair(4,2,4))
  pair_list.append(TestPair(5,4,8))
  pair_list.append(TestPair(6,5,4))
  pair_list.append(TestPair(7,0,5))
  pair_list.append(TestPair(8,0,4))
  pair_list.append(TestPair(9,0,6))
  pair_list.append(TestPair(10,6,7))
  pair_list.append(TestPair(11,7,0))
  res = find_cycles(pair_list, 0, 0)
  print(res)
  for cycles in res:
    for pairs in cycles:
        print(pairs.id)
    print()
  #print(res[0][0][1][1][0])
  #for testPairs in res[0][0][1][1][0]:
  #  print(testPairs.id)
  #pass

testRouter()