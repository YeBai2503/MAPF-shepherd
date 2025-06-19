from utils import *
from config import *
import agent

# 牧羊犬 
class Shepherd:
    def __init__(self):
        self.position = np.array([L/4, 3*L/4])  # 位置（初始为地图左上方）
        self.mode = 'driving'  # 行为模式（初始为驱赶）
        self.direction = np.array([0, 0])  # 移动方向（初始为右）
        
    def update(self, all_agents, gcm):
        agents = [] # 可见羊(不在盲区)
        # 移动逻辑（含盲区检测）
        if not self._need_to_move(all_agents, agents, gcm):
            self.mode = 'stationary'
            self.direction = np.array([0, 0]) + epsilon * np.random.randn(2) # 静止状态
        else:
            N = len(agents)
            f_N = r_a * N **(2/3)  # 计算f_N
            # 驱赶模式：移动到群体后方(Pd点)
            if all(agent.distance(gcm) < f_N for agent in agents):
                self.mode = 'driving'
                target = self._calculate_driving_position(gcm, N)
            # 收集模式：移动到最远个体后方（Pc点）
            else:
                self.mode = 'collecting'
                furthest = max(agents, key=lambda agent: np.linalg.norm(agent.position - gcm))
                target = self._calculate_collecting_position(gcm, furthest.position)
            # 更新移动方向
            self.direction = normalize_vector(target - self.position) + epsilon * np.random.randn(2)

            # 模型优化：羊数量较大时检测移动方向是否穿过羊群
            if(N>75):
                direction_to_gcm = normalize_vector(gcm - self.position) # 到羊群质心的方向
                if np.sum((self.position - target)**2) > np.sum((self.position - gcm)**2) + np.sum((target - gcm)**2):
                    # 两个预选的垂直方向（逆时针90度和顺时针90度）
                    pre1 = np.array([-direction_to_gcm[1], direction_to_gcm[0]])  
                    pre2 = np.array([direction_to_gcm[1], -direction_to_gcm[0]])  
                    # 选择self.direction一侧的垂直方向
                    if np.dot(pre1, self.direction) > 0:
                        self.direction = pre1
                    else:
                        self.direction = pre2

        # 更新位置
        self.position += self.direction * v_s

    # 计算驱赶模式的目标位置（Pd点）
    def _calculate_driving_position(self, gcm, N):
        direction_from_target = normalize_vector(gcm - TARGET)
        return gcm + direction_from_target * r_a * np.sqrt(N)

    # 计算收集模式的目标位置（Pc点）
    def _calculate_collecting_position(self, gcm, agent_pos):
        direction_from_gcm = normalize_vector(agent_pos - gcm)
        return agent_pos + direction_from_gcm * r_a

    # 盲区和移动判断
    def _need_to_move(self, agents, visible_agents, gcm):
        # 如果无方向，则设置为质心方向
        if np.allclose(self.direction, 0, 1e-8):
            self.direction = normalize_vector(gcm - self.position)

        # 找出在盲区内的羊
        for agent in agents:
            agent_direction = agent.position - self.position  # 牧羊犬到羊的向量
            # 盲区判断
            if judge_blind_zone(self.direction, agent_direction):
                visible_agents.append(agent)
        
        # 检查可见羊的距离是否都小于3*r_a
        if not visible_agents:
            return False  # 没有可见的羊
        positions = np.array([agent.position for agent in visible_agents])
        distances = np.linalg.norm(positions - self.position, axis=1)
        return not np.any(distances < 3 * r_a)
        # for agent in agents:
        #     if np.linalg.norm(self.position - agent.position) < 3 * r_a:
        #         return False
        # return True

    