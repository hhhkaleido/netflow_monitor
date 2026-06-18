import csv
import os
from scapy.all import PcapReader, IP, TCP, UDP

def extract_pcap_to_csv(pcap_filepath, csv_filepath):
    print(f"[*] 正在打开 pcap 文件: {pcap_filepath}")
    
    if not os.path.exists(pcap_filepath):
        print(f"[!] 错误: 找不到文件 {pcap_filepath}")
        return

    # 用于聚合会话的字典
    # 键 (Key): (源IP, 目的IP, 协议, 源端口, 目的端口)
    # 值 (Value): {'bytes': 总字节数, 'start_time': 最早时间, 'end_time': 最晚时间}
    sessions = {}
    packet_count = 0

    print("[*] 正在解析数据包并聚合会话，这可能需要几秒钟...")
    
    # 使用 PcapReader 迭代读取，避免大文件撑爆内存
    with PcapReader(pcap_filepath) as pcap_reader:
        for pkt in pcap_reader:
            packet_count += 1
            
            # 我们只处理包含 IP 层的数据包
            if IP in pkt:
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                proto = pkt[IP].proto
                pkt_len = len(pkt)
                timestamp = float(pkt.time)

                sport = 0
                dport = 0

                # 提取端口信息 (仅限 TCP 和 UDP)
                if TCP in pkt:
                    sport = pkt[TCP].sport
                    dport = pkt[TCP].dport
                elif UDP in pkt:
                    sport = pkt[UDP].sport
                    dport = pkt[UDP].dport
                else:
                    # 对于 ICMP 等其他协议，端口设为 0
                    pass

                # 生成会话唯一标识 (5元组)
                session_key = (src_ip, dst_ip, proto, sport, dport)

                if session_key not in sessions:
                    sessions[session_key] = {
                        'bytes': 0, 
                        'start_time': timestamp, 
                        'end_time': timestamp
                    }

                # 累加数据和更新时间
                sessions[session_key]['bytes'] += pkt_len
                sessions[session_key]['end_time'] = timestamp

    print(f"[*] 共读取了 {packet_count} 个数据包，合并为 {len(sessions)} 个独立会话。")
    print(f"[*] 正在导出为 CSV 文件: {csv_filepath}")

    # 将聚合后的数据写入 CSV
    with open(csv_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 写入表头，完美契合 C 语言程序的解析要求
        writer.writerow(['Source', 'Destination', 'Protocol', 'SrcPort', 'DstPort', 'DataSize', 'Duration'])

        for key, data in sessions.items():
            src_ip, dst_ip, proto, sport, dport = key
            
            # 计算持续时间 (如果只有一个包，持续时间就是 0)
            duration = data['end_time'] - data['start_time']
            
            # 写入一行数据
            writer.writerow([src_ip, dst_ip, proto, sport, dport, data['bytes'], round(duration, 6)])

    print("[+] 提取与转换完成！你的 C 程序现在可以享用这份新鲜的数据了。")

if __name__ == "__main__":
    # 配置文件路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 【路径修正】向上回退一级找到项目根目录
    project_root = os.path.dirname(current_dir)
    pcap_file = os.path.join(project_root, "data", "my_traffic.pcap")
    csv_file = os.path.join(project_root, "data", "network_data2.csv")
    
    extract_pcap_to_csv(pcap_file, csv_file)