from config import *
from agent import Agent
from shepherd import Shepherd
from visualization import *
import numpy as np
from utils import calculate_gcm
import time

def main():
    start_time = time.time() # 记录开始时间
    
    # 初始化
    agents = [Agent(np.random.uniform(L/2, L, 2)) for _ in range(N)]
    shepherd = Shepherd()
    
     # 初始化轨迹记录容器
    agent_trajectories = {id(agent): [agent.position.copy()] for agent in agents}
    shepherd_trajectory = [shepherd.position.copy()]
    # 记录初始位置
    start_positions = [agent.position.copy() for agent in agents]
    # 记录是否成功
    success = False
    
    # 模拟循环
    for step in range(MAX_STEPS):
        # 更新羊群
        for agent in agents:
            agent.update(agents, shepherd.position)
            agent_trajectories[id(agent)].append(agent.position.copy())
        
        # 更新牧羊犬
        shepherd.update(agents)
        shepherd_trajectory.append(shepherd.position.copy())
            
        # 检查终止条件
        gcm = calculate_gcm(agents)
        if np.linalg.norm(gcm - TARGET) < TARGET_RADIUS:  # 检查全局质心与目标的距离
            success = True
            print(f"任务完成！步数: {step}")
            break
     # 记录结束位置
    end_positions = [agent.position.copy() for agent in agents]
    
    # 输出运行时间
    print(f"程序运行时间: {time.time() - start_time}s")
    
    # 生成最终轨迹图
    if success:
        plot_trajectories(
            start_positions,
            end_positions,
            list(agent_trajectories.values()),
            shepherd_trajectory
        )
    else:
        print("任务失败！")
        
    
    print("程序结束")

if __name__ == "__main__":
    main()