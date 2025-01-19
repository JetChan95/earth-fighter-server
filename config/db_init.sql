-- 清空 earth_fighter 数据库中的所有表
USE earth_fighter;

-- 获取数据库中的所有表名
SET @tables = NULL;
SELECT GROUP_CONCAT(table_name) INTO @tables
FROM information_schema.tables
WHERE table_schema = 'earth_fighter';

-- 删除所有表
SET @drop_tables = CONCAT('DROP TABLE IF EXISTS ', @tables);
PREPARE stmt FROM @drop_tables;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 创建数据库
CREATE DATABASE IF NOT EXISTS earth_fighter;

-- 使用 earth_fighter 数据库
USE earth_fighter;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    u_id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    u_name VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 组织表
CREATE TABLE IF NOT EXISTS organizations (
    c_id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    c_name VARCHAR(255) NOT NULL,
    c_type VARCHAR(255) NOT NULL,
    creator_id INT UNSIGNED NOT NULL,  -- 新增创建者字段，引用 users 表的 u_id
    invite_code VARCHAR(255) NOT NULL,  -- 新增邀请码字段
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (creator_id) REFERENCES users(u_id)  -- 添加外键约束
);

-- 用户组织关系表
CREATE TABLE IF NOT EXISTS user_org_relations (
    u_id INT UNSIGNED,
    c_id INT UNSIGNED,
    state VARCHAR(255),
    join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    break_time TIMESTAMP,
    PRIMARY KEY (u_id, c_id),
    FOREIGN KEY (u_id) REFERENCES users(u_id),
    FOREIGN KEY (c_id) REFERENCES organizations(c_id)
);

-- 角色表
CREATE TABLE IF NOT EXISTS roles (
    role_id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    role_name VARCHAR(255) NOT NULL,
    role_description TEXT,
    is_deleted BOOLEAN DEFAULT FALSE
    -- 其他角色相关的字段
);

-- 用户角色关系表
CREATE TABLE IF NOT EXISTS user_role (
    user_id INT UNSIGNED NOT NULL,
    role_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(u_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    task_id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    publisher_id INT UNSIGNED,
    receiver_id INT UNSIGNED,
    task_state TINYINT UNSIGNED DEFAULT 0,
    publish_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_limit INT,
    completion_time TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    c_id INT UNSIGNED,
    task_desc TEXT,
    FOREIGN KEY (publisher_id) REFERENCES users(u_id),
    FOREIGN KEY (receiver_id) REFERENCES users(u_id),
    FOREIGN KEY (c_id) REFERENCES organizations(c_id)
);
