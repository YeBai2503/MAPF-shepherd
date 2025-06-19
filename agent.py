import numpy as np
from config import *
from utils import *

# 智能体(羊)
class Agent:
    def __init__(self, position):
        self.position = np.array(position, dtype=float) # 位置
        self.direction = np.random.randn(2)  # 移动方向
        
    def update(self, agents, shepherd_pos):
        # 计算牧羊犬的距离
        dist_to_shepherd = np.linalg.norm(self.position - shepherd_pos)
        # 计算各作用力
        repulsion = self._calculate_repulsion(agents) # 羊群排斥力
        if(dist_to_shepherd < r_s):
            attraction = self._calculate_attraction(agents) # 羊群吸引力
            shepherd_repulsion = self._calculate_shepherd_repulsion(shepherd_pos) # 牧羊犬排斥力
        else:
            attraction = np.zeros(2)
            shepherd_repulsion = np.zeros(2)
        
        # 合成新方向(公式4.2)
        new_direction = (
            h * self.direction + # 惯性
            c * attraction + # 羊群吸引力(n个最近邻的LCM吸引力)
            rho_a * repulsion + # 羊群排斥力(距离在r_a内的羊的排斥力)
            rho_s * shepherd_repulsion + # 牧羊犬排斥力
            epsilon * np.random.randn(2) # 随机噪声
        )
        self.direction = normalize_vector(new_direction)
        self.position += self.direction * v_a


    # 羊群排斥力计算
    def _calculate_repulsion(self, agents):
        # 距离在r_a内的羊邻居
        neighbors = get_neighbors_within_ra(self.position, agents)
        # 计算排斥力
        repulsion = np.zeros(2)
        for neighbor in neighbors:
            repulsion += normalize_vector(self.position - neighbor.position)
        return normalize_vector(repulsion)

    # 计算向邻居质心的吸引力
    def _calculate_attraction(self, agents):
        # 检测邻居(n个最近邻)
        neighbors = get_neighbors(self.position, agents, n_neighbors)
        # 计算最近邻质心
        gcm = calculate_gcm(neighbors)
        # 计算吸引力
        attraction = normalize_vector(gcm - self.position)
        return attraction
    
    # 计算牧羊犬排斥力
    def _calculate_shepherd_repulsion(self, shepherd_pos):
        shepherd_repulsion = normalize_vector(self.position - shepherd_pos)
        return shepherd_repulsion
    
    # 计算羊与某一点的距离
    def distance(self, position):
        return np.linalg.norm(self.position - position)