import csv
import os
import webbrowser
import networkx as nx
from pyvis.network import Network
import math

def visualize_target_subgraph(csv_filepath, target_ip, output_html="subgraph.html"):
    print(f"[*] 正在读取数据文件: {csv_filepath}")
    
    if not os.path.exists(csv_filepath):
        print(f"[!] 错误: 找不到文件 {csv_filepath}")
        return False

    # 1. 构建无向图 (Undirected Graph)
    G = nx.Graph()
    
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row['Source']
            dst = row['Destination']
            flow = int(row['DataSize'])
            
            if G.has_edge(src, dst):
                G[src][dst]['weight'] += flow
            else:
                G.add_edge(src, dst, weight=flow)

    if target_ip not in G:
        print(f"[!] 错误: 目标节点 {target_ip} 不在当前网络数据中！")
        return False

    # 2. 寻找包含目标 IP 的连通子图
    connected_nodes = nx.node_connected_component(G, target_ip)
    sub_G = G.subgraph(connected_nodes).copy()
    
    # 3. 美化节点和边
    for node in sub_G.nodes():
        degree = sub_G.degree(node)
        # 基础大小 10，每多一点连接数按对数缓慢增加
        node_size = 10 + math.log10(degree + 1) * 8 
        sub_G.nodes[node]['size'] = node_size
        sub_G.nodes[node]['label'] = node
        sub_G.nodes[node]['title'] = f"IP: {node}\n连接数: {degree}" 

        if node == target_ip:
            sub_G.nodes[node]['color'] = '#FF3B30'
            sub_G.nodes[node]['size'] = node_size + 10 # 目标节点稍微大一点
        else:
            sub_G.nodes[node]['color'] = '#0071E3'

    for u, v, data in list(sub_G.edges(data=True)):
        flow = data['weight']
        del data['weight'] # 必须删除，防止撑爆画布
        data['title'] = f"数据流量: {flow} Bytes"
        data['width'] = max(0.5, math.log10(flow + 1) * 0.8)
        data['color'] = '#CCCCCC' 

    # 4. 使用 pyvis 进行渲染
    print(f"[*] 正在生成可视化 HTML 文件...")
    net = Network(height="100vh", width="100%", bgcolor="#FFFFFF", font_color="#000000", notebook=False)
    net.from_nx(sub_G)
    net.toggle_physics(True)

    # 5. 保存图表
    html_path = os.path.abspath(output_html)
    net.save_graph(html_path)

    # ==========================================
    # 6. 核心修改：向生成的 HTML 中注入悬浮信息面板
    # ==========================================
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 构造极简风的 HTML/CSS 卡片代码
    info_panel_html = f"""
    <div style="position: absolute; top: 30px; left: 30px; background-color: rgba(255, 255, 255, 0.95); 
                padding: 20px 30px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.12); 
                font-family: 'Microsoft YaHei', -apple-system, sans-serif; z-index: 9999; 
                border: 1px solid rgba(0,0,0,0.05); backdrop-filter: blur(10px);">
        <h3 style="margin: 0 0 15px 0; color: #1D1D1F; font-size: 18px; font-weight: 600;">🎯 子图网络分析</h3>
        <p style="margin: 8px 0; color: #515154; font-size: 14px;">
            <span style="display:inline-block; width: 70px; color: #86868B;">核心 IP</span> 
            <strong style="color: #FF3B30;">{target_ip}</strong>
        </p>
        <p style="margin: 8px 0; color: #515154; font-size: 14px;">
            <span style="display:inline-block; width: 70px; color: #86868B;">节点数量</span> 
            <strong>{sub_G.number_of_nodes()}</strong> 个
        </p>
        <p style="margin: 8px 0; color: #515154; font-size: 14px;">
            <span style="display:inline-block; width: 70px; color: #86868B;">连线数量</span> 
            <strong>{sub_G.number_of_edges()}</strong> 条
        </p>
    </div>
    """

    # 找到 <body> 标签，把我们的卡片插进去
    html_content = html_content.replace('<body>', f'<body>\n{info_panel_html}')

    # 重新覆盖写入
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] 可视化文件已生成: {html_path}")
    webbrowser.open(f"file://{html_path}")
    return True

if __name__ == "__main__":
    # 【路径修正】定位到上一级 data 目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    test_csv = os.path.join(project_root, "data", "network_data.csv")
    test_ip = "124.88.91.115"  # 替换为你想要查询的 IP
    visualize_target_subgraph(test_csv, test_ip, "target_subgraph.html")