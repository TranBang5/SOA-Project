-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS pastebin;
USE pastebin;

-- Create Paste table
CREATE TABLE IF NOT EXISTS paste (
    id VARCHAR(16) PRIMARY KEY,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    views INT DEFAULT 0,
    INDEX idx_expires_at (expires_at),
    INDEX idx_created_at (created_at)
);

-- Create Analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    month DATE NOT NULL,
    total_views INT DEFAULT 0,
    total_pastes INT DEFAULT 0,
    UNIQUE INDEX idx_month (month)
);

-- Insert some sample data
INSERT INTO paste (id, content, created_at, expires_at, views) VALUES
('sample1', 'This is a sample paste that never expires.\nIt contains multiple lines\nof text.', 
 NOW(), NULL, 5),
('sample2', 'This is a temporary paste that expires in 24 hours.', 
 NOW(), DATE_ADD(NOW(), INTERVAL 24 HOUR), 2),
('sample3', 'Another sample paste with some code:\n\nfunction hello() {\n    console.log("Hello, World!");\n}', 
 NOW(), NULL, 10);

-- Insert sample analytics data
INSERT INTO analytics (month, total_views, total_pastes) VALUES
(DATE_FORMAT(NOW(), '%Y-%m-01'), 17, 3),
(DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH), '%Y-%m-01'), 25, 5); 