from config import *
from agent import Agent
from shepherd import Shepherd
from visualization import Visualizer
import numpy as np
from utils import calculate_gcm
import time

def main():
    start_time = time.time() # 记录开始时间
    
    # 初始化
    agents = [Agent(np.random.uniform(L/2, L, 2)) for _ in range(N)]
    shepherd = Shepherd()
    
    # 初始化可视化器
    visualizer = Visualizer()
    
    # 记录初始位置
    start_positions = [agent.position.copy() for agent in agents]
    # 记录初始状态
    visualizer.record_step(agents, shepherd.position)
    # 记录是否成功
    success = False
    
    # 模拟循环
    for step in range(MAX_STEPS):
        # 更新羊群
        for agent in agents:
            agent.update(agents, shepherd.position)
        
        # 更新牧羊犬
        shepherd.update(agents)
        
        # 记录每一步状态
        visualizer.record_step(agents, shepherd.position)
            
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
    
    # 生成效果图
    filename = "result"
    if success:
        # 静态轨迹图
        print("生成轨迹图中...")
        visualizer.plot_static_trajectories(start_positions, end_positions, filename + ".png")
        
        # gif动画
        show_animation = input("是否查看动画？(y/n): ").strip().lower() == 'y'
        if show_animation:
            # 采样率设置（加速生成）
            total_frames = len(visualizer.agent_positions_history)
            
            if total_frames > 500:
                sample_rate = int(np.ceil(total_frames / 500))
                print(f"————————帧数过多，采样率已设置为{sample_rate}————————")
            else:
                sample_rate = 1
                
            visualizer.create_animation(filename + ".gif", sample_rate)
    else:
        print("任务失败！")
        
    
    print("程序结束")

if __name__ == "__main__":
    main()