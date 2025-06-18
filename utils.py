import numpy as np
from config import *

# 计算全局质心
def calculate_gcm(agents):
    return np.mean([a.position for a in agents], axis=0)

# 向量归一化
def normalize_vector(v):
    norm = np.linalg.norm(v)
    if norm < 1e-8:  
        return np.zeros_like(v)
    return v / norm

# 返回最近的n个邻居
def get_neighbors(position, agents, n):
    distances = [np.linalg.norm(position - a.position) for a in agents]
    return sorted(agents, key=lambda x: distances)[:n]

# 返回距离在 r_a 内的邻居
def get_neighbors_within_ra(position, agents):
    neighbors = []
    for a in agents:
        distance = np.linalg.norm(position - a.position)
        if 0 < distance <= r_a:
            neighbors.append(a)
    return neighbors
