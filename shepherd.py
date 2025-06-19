from utils import *
from config import *
import agent

# 牧羊犬 
class Shepherd:
    def __init__(self):
        self.position = np.array([L/4, 3*L/4])  # 位置（初始为地图左上方）
        self.mode = 'driving'  # 行为模式（初始为驱赶）
        self.direction = np.array([1, 0])  # 移动方向（初始为右）
        
    def update(self, agents):
        # 移动逻辑（含盲区检测）
        if not self._safe_to_move(agents):
            self.mode = 'stationary'
            self.direction = np.array([0, 0]) + epsilon * np.random.randn(2) # 静止状态
        else:
            gcm = calculate_gcm(agents)
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
            self.direction = normalize_vector(target - self.position) + epsilon * np.random.randn(2)
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

    # 移动判断
    def _safe_to_move(self, agents):
        for agent in agents:
            if np.linalg.norm(self.position - agent.position) < 3 * r_a:
                return False
        return True