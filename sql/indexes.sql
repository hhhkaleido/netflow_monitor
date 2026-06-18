USE netflow_monitor;

CREATE INDEX idx_src_ip ON traffic_log(src_ip);
CREATE INDEX idx_dst_ip ON traffic_log(dst_ip);
CREATE INDEX idx_dst_port ON traffic_log(dst_port);
CREATE INDEX idx_protocol ON traffic_log(protocol);
CREATE INDEX idx_created_at ON traffic_log(created_at);
CREATE INDEX idx_src_ip_created_at ON traffic_log(src_ip, created_at);

-- src_ip_aly indexes are created inline in schema.sql:
-- PRIMARY KEY (src_ip)
-- INDEX idx_src_ip_hash_ip (src_ip_hash, src_ip)
-- INDEX idx_total_bytes (total_bytes)
