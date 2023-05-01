# define label here
import enum
import datetime
import math

f = enum.Enum('小防御', ('8','9','10','11','13', '15', '16', '17', '19','21','23'))

s = enum.Enum('小生命', ('100','115','129','143','167', '191', '215', '209','239','269','299'))

g = enum.Enum('小攻击', ('7','8','9', '11', '12','14','16','18','19'))

_f = enum.Enum('大防御', ('3.1','3.5','3.9','4.1','4.4', '4.7','5.1','5.3','5.8','6.6','7.3'))

_s = enum.Enum('大生命', ('2.5','2.8','3.2','3.3','3.5','3.7','4.1','4.2','4.7','5.3','5.8'))

_g = enum.Enum('大攻击', ('2.5','2.8','3.2','3.3','3.5','3.7','4.1','4.2','4.7','5.3','5.8'))

j = enum.Enum('元素精通', ('10','11','13','14','15','16','17','19','21','23'))

c = enum.Enum('元素充能效率', ('2.7','3.1','3.5','3.6','3.9','4.1','4.5','4.7','5.2','5.8','6.5'))

b = enum.Enum('暴击率', ('1.6','1.9','2.1','2.2', '2.3','2.5','2.7','2.8','3.1','3.5','3.9'))

_b = enum.Enum('暴击伤害', ('3.3','3.7','4.2','4.4','4.7','5.0','5.4','5.6','6.2','7.0','7.8'))

mapping = {'小防御':f, '小生命':s, '小攻击':g, '大防御':_f, '大生命':_s, '大攻击':_g, '元素精通':j, '元素充能效率':c, '暴击率':b, '暴击伤害':_b} # 用于记录变化的词条
mapping_enum = {'小防御':0,'小生命':1,'小攻击':2,'大防御':3,'大生命':4,'大攻击':5,'元素精通':6,'元素充能效率':7,'暴击率':8,'暴击伤害':9}         # 哈希表，快速查询

sequence = [f,s,g,_f,_s,_g,j,c,b,_b]                                                                                                       # 词条顺序
end_points = [[16,23], [209, 299], [14,19],[5.1,7.3],[4.1,5.8],[4.1,5.8],[41,58],[4.5,6.5],[2.7,3.9],[5.4,7.8]]                            # 五星圣遗物的各词条最大最小值
op = [int, int, int, float, float, float, int, float, float, float]                                                                        # 各个词条的数据类型
pre_sum = [0]                                                                                                                              # 前缀和
for i in sequence:
    pre_sum.append(pre_sum[-1]+len(i))

def get_bias(main_index, a, b):
    if a.endswith('%'):
        bias = str(round(abs(op[main_index](a[:-1]) - op[main_index](b[:-1])),1)) + "%"
    else:
        bias = str(round(abs(op[main_index](a) - op[main_index](b)),1))
    print('差值', bias)
    return bias
    
def append_data_wo_time(data, citiao_mem, result, text):
    text.append(f"{result[0][1]}增加了{result[1][1]}")
    data.append({'ori':citiao_mem.copy(), 'label':result[1][0]})
    print('增加数据', data[-1])

append_func = append_data_wo_time                     

def nearest(term_index, term, val):
    res = 1e5
    for _val in term:
        _val = op[term_index](_val.name)
        res = _val if abs(op[term_index](res) - op[term_index](val)) > abs(_val - op[term_index](val)) else res
    return res

def get_index(name, val, data=None, ori=None, text=None):
    if name.__contains__('元素伤害加成'):
        return [10,0]

    if val.endswith("%"):
        val = val[:-1]
        if name.__contains__('防御'):
            citiao = '大防御'
        elif name.__contains__('生命'):
            citiao = '大生命'
        elif name.__contains__('攻击'):
            citiao = '大攻击'
        elif name.__contains__('暴击率'):
            citiao = '暴击率'
        elif name.__contains__('暴击伤害'):
            citiao = '暴击伤害'
        elif name.__contains__('充能效率'):
            citiao = '元素充能效率'

    else:
        if name.__contains__('防御'):
            citiao = '小防御'
        elif name.__contains__('生命'):
            citiao = '小生命'         # 去掉逗号和句号
            val = val.replace('.', '')
            val = val.replace(',', '')
        elif name.__contains__('攻击'):
            citiao = '小攻击'
        elif name.__contains__('精通'):
            citiao = '元素精通'
    
    term_index = mapping_enum[citiao]
    term = mapping[citiao]
    
    if data is not None and not hasattr(term, val):     
        val = op[term_index](val)
        while val > end_points[term_index][1]:
            times = sum([val / end_points[term_index][0], val / end_points[term_index][1]]) / 2 if val > end_points[term_index][1] else 1 # 说明多次强化在一个词条上
            tmp = round(op[term_index](val) / times, 1) if op[term_index] is not int else round(op[term_index](val) / times)
            tmp = nearest(term_index, term, tmp)
            val -= tmp
            append_func(data, ori, [[term_index, citiao], [pre_sum[term_index] + (term[str(tmp)].value), str(tmp)]], text)
        
        val = str(nearest(term_index, term, val))
        
    return [[term_index, citiao], [pre_sum[term_index] + (term[val].value), val]] if data is not None else [term_index,None]



if __name__ == "__main__":
    print(get_index('防御力', '7.3%'))
    print(get_index('防御','8'))
    print(get_index('防御','21'))
    print(get_index('防御','23'))
    print(get_index('生命','100'))
    print(get_index('生命','115'))
    print(get_index('生命','117'))
    print(get_index('生命','128'))
    text = []
    print(get_index("生命",'717', data=[], ori=[5, 7, 1, 3, 0], text=text))
    print(text)
    
