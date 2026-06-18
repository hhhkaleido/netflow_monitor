CREATE DATABASE IF NOT EXISTS netflow_monitor
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE netflow_monitor;

CREATE TABLE IF NOT EXISTS traffic_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    src_ip VARCHAR(45) NOT NULL,
    src_port INT,
    dst_ip VARCHAR(45) NOT NULL,
    dst_port INT,
    protocol VARCHAR(10),
    packet_size INT,
    duration FLOAT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS src_ip_aly (
    src_ip VARCHAR(45) NOT NULL,
    src_ip_hash BIGINT UNSIGNED NOT NULL,
    count BIGINT NOT NULL DEFAULT 0,
    total_bytes BIGINT NOT NULL DEFAULT 0,

    PRIMARY KEY (src_ip),
    INDEX idx_src_ip_hash_ip (src_ip_hash, src_ip),
    INDEX idx_total_bytes (total_bytes)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
