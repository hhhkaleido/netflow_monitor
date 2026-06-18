import csv
import os
import webbrowser
import networkx as nx
import json
import math

def visualize_target_subgraph_3d(csv_filepath, target_ip, output_html="subgraph_3d.html"):
    print(f"[*] 正在读取数据文件: {csv_filepath}")
    
    if not os.path.exists(csv_filepath):
        print(f"[!] 错误: 找不到文件 {csv_filepath}")
        return False

    # 1. 构建无向图
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

    # 2. 寻找连通子图
    connected_nodes = nx.node_connected_component(G, target_ip)
    sub_G = G.subgraph(connected_nodes).copy()
    print(f"[*] 成功提取子图: 包含 {sub_G.number_of_nodes()} 个节点, {sub_G.number_of_edges()} 条边")

    # 3. 将图数据转化为 3D 引擎所需的 JSON 格式
    nodes_data = []
    for node in sub_G.nodes():
        nodes_data.append({
            "id": node,
            "degree": sub_G.degree(node)
        })

    links_data = []
    for u, v, data in sub_G.edges(data=True):
        links_data.append({
            "source": u,
            "target": v,
            "flow": data['weight']
        })

    graph_data_json = json.dumps({"nodes": nodes_data, "links": links_data})

    # 4. 生成包含 Three.js 和 3d-force-graph 的 HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>3D Wireframe Subgraph</title>
        <style>
            body {{ margin: 0; padding: 0; background-color: #FFFFFF; overflow: hidden; font-family: 'Microsoft YaHei', sans-serif; }}
            #info-panel {{
                position: absolute; top: 20px; left: 20px; color: #333;
                background: rgba(255, 255, 255, 0.9); padding: 15px 25px;
                border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border: 1px solid #ddd; pointer-events: none; z-index: 10;
            }}
            #loading {{
                position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                font-size: 18px; color: #666; font-weight: bold; z-index: 5;
            }}
        </style>
        <!-- 使用更稳定的 CDN 源 (unpkg 或 jsdelivr) -->
        <script src="https://unpkg.com/three@0.137.0/build/three.min.js"></script>
        <script src="https://unpkg.com/3d-force-graph@1.73.3/dist/3d-force-graph.min.js"></script>
    </head>
    <body>
        <div id="loading">📡 正在加载 3D 渲染引擎，请稍候... (如果长时间卡住，请检查网络或代理设置)</div>
        <div id="3d-graph"></div>
        
        <div id="info-panel">
            <h3 style="margin-top:0;">🌐 3D 拓扑分析</h3>
            <p>🎯 核心 IP: <strong style="color: #FF3B30;">{target_ip}</strong></p>
            <p>📦 节点数量: <strong>{sub_G.number_of_nodes()}</strong></p>
            <p>🔗 连线数量: <strong>{sub_G.number_of_edges()}</strong></p>
            <p style="font-size:12px; color:#888; margin-bottom:0;">操作指南：<br>1. 左键空白处拖拽：旋转视角<br>2. 滚轮：放大/缩小<br>3. 左键拖拽节点：单独移动并固定该节点</p>
        </div>

        <script>
            // 【增强】错误捕获器，如果有错直接弹窗，不再死白
            window.onerror = function(msg, url, lineNo) {{
                alert("JS 运行报错了: " + msg + "\\n请检查网络是否屏蔽了 CDN。");
                return false;
            }};

            const gData = {graph_data_json};
            const targetIp = "{target_ip}";

            // 成功执行到这里，说明引擎加载成功，隐藏提示语
            document.getElementById('loading').style.display = 'none';

            const Graph = ForceGraph3D()
                (document.getElementById('3d-graph'))
                .graphData(gData)
                .backgroundColor('#FFFFFF') 
                .nodeThreeObject(node => {{
                    // 根据度数计算球体半径，目标节点固定偏大
                    const radius = node.id === targetIp ? 8 : Math.max(2, Math.log10(node.degree + 1) * 4);
                    // 线框球体
                    const geometry = new THREE.SphereGeometry(radius, 8, 8);
                    const material = new THREE.MeshBasicMaterial({{
                        color: node.id === targetIp ? 0xFF3B30 : 0x000000, 
                        wireframe: true,
                        transparent: true,
                        opacity: 0.7
                    }});
                    return new THREE.Mesh(geometry, material);
                }})
                .nodeLabel(node => `IP: ${{node.id}}<br>连接数: ${{node.degree}}`)
                .linkLabel(link => `<span style="color: #FF5722; font-weight: bold; background: white; padding: 2px;">流量: ${{link.flow}} Bytes</span>`)
                .linkColor(() => '#0071E3')
                .linkWidth(link => Math.max(0.2, Math.log10(link.flow + 1) * 0.3))
                // 布局完成后冻结节点位置
                .onEngineStop(() => {{
                    const currentNodes = Graph.graphData().nodes;
                    currentNodes.forEach(node => {{
                        node.fx = node.x;
                        node.fy = node.y;
                        node.fz = node.z;
                    }});
                }});
        </script>
    </body>
    </html>
    """

    print(f"[*] 正在渲染 3D WebGL 模型...")
    html_path = os.path.abspath(output_html)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] 3D 可视化文件已生成: {html_path}")
    webbrowser.open(f"file://{html_path}")
    return True

if __name__ == "__main__":
    # 【路径修正】定位到上一级 data 目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    test_csv = os.path.join(project_root, "data", "network_data.csv")
    test_ip = "112.65.219.203"  # 确保这个 IP 存在于你的数据集中
    
    visualize_target_subgraph_3d(test_csv, test_ip, "subgraph_3d.html")