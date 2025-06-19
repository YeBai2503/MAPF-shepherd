import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import matplotlib.patches as mpatches
from config import *

class Visualizer:
    def __init__(self):
        self.agent_positions_history = []  # 每一步所有羊的位置
        self.shepherd_positions_history = []  # 每一步牧羊犬的位置
        
    """记录每个时间步的位置"""
    def record_step(self, agents, shepherd_position):
        self.agent_positions_history.append([agent.position.copy() for agent in agents])
        self.shepherd_positions_history.append(shepherd_position.copy())
    
    """绘制静态轨迹图"""
    def plot_static_trajectories(self, start_positions, end_positions, save_file):
        plt.figure(figsize=(10, 8))
        
        # 获取所有羊的轨迹
        agent_trajectories = self._get_agent_trajectories()
        
        # 计算坐标边界值
        bounds = self._calculate_bounds()
        
        # 羊群轨迹（灰色细线）
        for trajectory in agent_trajectories:
            plt.plot([pos[0] for pos in trajectory], [pos[1] for pos in trajectory], 
                         color="gray", linewidth=0.5, alpha=0.5)
        
        # 起始/结束位置（红色圆圈）
        for start, end in zip(start_positions, end_positions):
            plt.scatter(start[0], start[1], s=30, facecolors="none", 
                           edgecolors="red", linewidths=0.8, marker="o")
            plt.scatter(end[0], end[1], s=30, facecolors="none",
                           edgecolors="red", linewidths=0.8, marker="o")
        
        # 牧羊犬轨迹（蓝色粗线）
        plt.plot([pos[0] for pos in self.shepherd_positions_history], [pos[1] for pos in self.shepherd_positions_history], 
                     color="blue", linewidth=1.5, alpha=0.8)

        # 目的地
        plt.scatter(TARGET[0], TARGET[1], s=TARGET_RADIUS, marker="x", color="green")
        
        # 设置图形参数
        plt.title("Path of Agent and Shepherd")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.axis('equal')
        plt.xlim(bounds['x_min'], bounds['x_max'])
        plt.ylim(bounds['y_min'], bounds['y_max'])
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        plt.show()

    """绘制动画(可设置采样率sample_rate加速生成,默认帧间隔时间interval为50ms)"""
    def create_animation(self, save_file=None, sample_rate=1, interval=50):
        # 采样以减少帧数
        total_frames = len(self.agent_positions_history)
        if sample_rate > 1:
            sampled_indices = list(range(0, total_frames, sample_rate))
            # 确保包含最后一帧
            if sampled_indices[-1] != total_frames - 1:
                sampled_indices.append(total_frames - 1)  
                
            agent_history_sampled = [self.agent_positions_history[i] for i in sampled_indices]
            shepherd_history_sampled = [self.shepherd_positions_history[i] for i in sampled_indices]
        else:
            agent_history_sampled = self.agent_positions_history
            shepherd_history_sampled = self.shepherd_positions_history
        
        # 创建图形和轴
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 设置坐标范围
        bounds = self._calculate_bounds()
        ax.set_xlim(bounds['x_min'], bounds['x_max'])
        ax.set_ylim(bounds['y_min'], bounds['y_max'])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Shepherding Simulation')
        ax.grid(True, linestyle="--", alpha=0.3)
        ax.set_aspect('equal')
        
        # 绘制目的区域
        target_circle = mpatches.Circle(TARGET, TARGET_RADIUS, color='green', alpha=0.2)
        ax.add_patch(target_circle)
        ax.plot(TARGET[0], TARGET[1], 'gx')
        
        # 创建散点图和线的容器
        agents_scatter = ax.scatter([], [], s=30, c='black', alpha=0.7) # 黑色圆点
        shepherd_scatter = ax.scatter([], [], s=50, c='blue', marker='s') # 蓝色方形
        
        # 轨迹线
        agent_lines = []
        for _ in range(len(agent_history_sampled[0])):
            line, = ax.plot([], [], 'gray', alpha=0.3, linewidth=0.5)
            agent_lines.append(line)
        shepherd_line, = ax.plot([], [], 'blue', alpha=0.7, linewidth=1.5)
        
        # 显示帧数
        time_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                          verticalalignment='top')
        
        def init():
            # 初始化所有图形元素
            agents_scatter.set_offsets(np.empty((0, 2)))
            shepherd_scatter.set_offsets(np.empty((0, 2)))
            
            for line in agent_lines:
                line.set_data([], [])
            shepherd_line.set_data([], [])
            time_text.set_text('')
            
            return [agents_scatter, shepherd_scatter, shepherd_line, time_text] + agent_lines
        
        def update(frame):
            # 更新散点位置
            agents_scatter.set_offsets(agent_history_sampled[frame])
            shepherd_scatter.set_offsets([shepherd_history_sampled[frame]])
            
            # 更新轨迹线
            for i, line in enumerate(agent_lines):
                agent_pos_history = [step_pos[i] for step_pos in agent_history_sampled[:frame+1]]
                line.set_data([p[0] for p in agent_pos_history], [p[1] for p in agent_pos_history])
            
            shepherd_line.set_data([p[0] for p in shepherd_history_sampled[:frame+1]], 
                                  [p[1] for p in shepherd_history_sampled[:frame+1]])
            
            # 更新帧数显示
            frame_idx = frame * sample_rate if sample_rate > 1 else frame
            time_text.set_text('Step: ' + str(frame_idx))
            
            return [agents_scatter, shepherd_scatter, shepherd_line, time_text] + agent_lines
        
        # 创建动画
        print("正在生成动画，请稍候...")
        ani = animation.FuncAnimation(
            fig, update, frames=len(agent_history_sampled),
            init_func=init, blit=True, interval=interval
        )
        
        # 保存gif文件
        if save_file:
            print(f"正在保存动画至 {save_file}...")
            ani.save(save_file, writer='pillow', fps=20)
            print(f"动画已保存至 {save_file}!")
            
        plt.show()
        return ani

    """构建每只羊的轨迹"""
    def _get_agent_trajectories(self):
        n_agents = len(self.agent_positions_history[0])
        return [[step_pos[i] for step_pos in self.agent_positions_history] 
                for i in range(n_agents)]
    
    """计算坐标轴的边界值"""
    def _calculate_bounds(self):
        min_x = 9999999
        max_x = -9999999
        min_y = 9999999
        max_y = -9999999
        
        # 所有羊的位置
        for step_positions in self.agent_positions_history:
            for pos in step_positions:
                min_x = min(min_x, pos[0])
                max_x = max(max_x, pos[0])
                min_y = min(min_y, pos[1])
                max_y = max(max_y, pos[1])
        
        # 牧羊犬位置
        for pos in self.shepherd_positions_history:
            min_x = min(min_x, pos[0])
            max_x = max(max_x, pos[0])
            min_y = min(min_y, pos[1])
            max_y = max(max_y, pos[1])
        
        # 目标位置
        min_x = min(min_x, TARGET[0])
        max_x = max(max_x, TARGET[0])
        min_y = min(min_y, TARGET[1])
        max_y = max(max_y, TARGET[1])
        
        # 计算边距（0.1倍）
        margin_x = 0.1 * (max_x - min_x) if max_x - min_x != 0 else 1
        margin_y = 0.1 * (max_y - min_y) if max_y - min_y != 0 else 1
        
        return {
            'x_min': min_x - margin_x, 'x_max': max_x + margin_x,
            'y_min': min_y - margin_y, 'y_max': max_y + margin_y
        }
    