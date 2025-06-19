import numpy as np
from config import *

# 计算全局质心
def calculate_gcm(agents):
    return np.mean([a.position for a in agents], axis=0)
    # positions = np.array([a.position for a in agents])
    # return np.mean(positions, axis=0)

# 向量归一化
def normalize_vector(v):
    norm = np.linalg.norm(v)
    if norm < 1e-8:  
        return np.zeros_like(v)
    return v / norm

# 盲区判断（仅适用于当前π/2的盲区）
def judge_blind_zone(direction, agent_direction):
    dot = direction[0]*agent_direction[0] + direction[1]*agent_direction[1]
    # 点积不为负时，夹角最大90度
    if dot >= 0:
        return True # 看得见
    # 点积为负时，夹角最大135度
    if dot * dot  < 0.5 * (direction[0]**2 + direction[1]**2) * (agent_direction[0]**2 + agent_direction[1]**2):
        return True # 看得见
    return False # 看不见

# 返回最近的n个邻居（向量化计算优化版）
def get_neighbors(position, agents, n):
    distances = [np.linalg.norm(position - a.position) for a in agents]
    return sorted(agents, key=lambda x: distances)[:n]
    # positions = np.array([a.position for a in agents])
    # distances = np.linalg.norm(positions - position, axis=1)
    # indices = np.argsort(distances)[:n+1]
    # return [agents[i] for i in indices]

# 返回距离在 r_a 内的邻居的索引（向量化计算优化版）
def get_neighbors_within_ra(position, agents):
    # 将所有羊的位置提取到一个NumPy数组中
    positions = np.array([a.position for a in agents])
    # 计算每个羊到指定羊的距离
    distances = np.linalg.norm(positions - position, axis=1)
    # 返回距离小于r_a的邻居列表
    return np.where(distances <= r_a)[0]


# 更新羊群（向量化计算版）
def vectorized_update(agents, shepherd_pos):
    positions = np.array([a.position for a in agents])
    directions = np.array([a.direction for a in agents])
    
    # 所有agent到牧羊犬的距离
    dist_to_shepherd = np.linalg.norm(positions - shepherd_pos, axis=1)
    
    # 初始化方向
    new_directions = h * directions
    
    # 排斥力
    for i in range(len(agents)):
        # 找出r_a范围内的邻居索引
        neighbors_idx = get_neighbors_within_ra(positions[i], agents)
        repulsion = np.zeros(2)
        for idx in neighbors_idx:
            diff = positions[i] - positions[idx]
            norm = np.linalg.norm(diff)
            if norm > 1e-8:
                repulsion += diff / norm
        
        # 归一化
        repulsion_norm = np.linalg.norm(repulsion)
        if repulsion_norm > 1e-8:
            repulsion = repulsion / repulsion_norm
            
        # 添加到方向
        new_directions[i] += rho_a * repulsion
    
    # 羊群吸引力和牧羊犬排斥力
    for i in range(len(agents)):
        if dist_to_shepherd[i] < r_s:
            neighbors = get_neighbors(positions[i], agents, n_neighbors)
            gcm = calculate_gcm(neighbors) # n个最近邻居的质心
            attraction = gcm - positions[i]
            attraction_norm = np.linalg.norm(attraction)
            if attraction_norm > 1e-8:
                attraction = attraction / attraction_norm
                new_directions[i] += c * attraction
            
            # 牧羊犬排斥力
            shepherd_repulsion = positions[i] - shepherd_pos
            repulsion_norm = np.linalg.norm(shepherd_repulsion)
            if repulsion_norm > 1e-8:
                shepherd_repulsion = shepherd_repulsion / repulsion_norm
                new_directions[i] += rho_s * shepherd_repulsion
    
    # 随机移动
    new_directions += epsilon * np.random.randn(*directions.shape)
    
    # 归一化方向
    for i in range(len(new_directions)):
        norm = np.linalg.norm(new_directions[i])
        if norm > 1e-8:
            new_directions[i] = new_directions[i] / norm
    
    # 更新位置
    new_positions = positions + new_directions * v_a
    
    # 更新至agent
    for i, agent in enumerate(agents):
        agent.position = new_positions[i]
        agent.direction = new_directions[i]


