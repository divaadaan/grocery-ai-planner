-- backend/database/init.sql
-- Initial database setup for Grocery AI Planner

-- Create database if it doesn't exist (handled by Docker)
-- This script runs after database creation

-- Enable UUID extension for future use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE postal_code_status AS ENUM ('pending', 'active', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE scrape_job_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance (these will be created by SQLAlchemy too, but ensuring they exist)

-- Sample data for development/testing
INSERT INTO postal_codes (postal_code, status, last_updated) VALUES 
('M5V3A8', 'active', NOW()),
('K1A0A9', 'pending', NOW()),
('V6B1A1', 'active', NOW())
ON CONFLICT (postal_code) DO NOTHING;

-- Sample stores for testing
INSERT INTO stores (name, chain, address, postal_code, website, is_active) VALUES 
('Metro Downtown', 'Metro', '123 King St W, Toronto, ON M5V 3A8', 'M5V3A8', 'https://metro.ca', true),
('Loblaws City Market', 'Loblaws', '456 Queen St W, Toronto, ON M5V 2B4', 'M5V3A8', 'https://loblaws.ca', true),
('No Frills College', 'No Frills', '789 College St, Toronto, ON M6G 1C5', 'M5V3A8', 'https://nofrills.ca', true)
ON CONFLICT DO NOTHING;

-- Sample categories for offers
INSERT INTO current_offers (store_id, product_name, brand, category, price, unit, start_date, end_date, is_featured_deal) VALUES 
(1, 'Bananas', 'Fresh', 'produce', 1.99, 'lb', CURRENT_DATE, CURRENT_DATE + INTERVAL '7 days', true),
(1, 'Chicken Breast', 'Fresh', 'meat', 9.99, 'lb', CURRENT_DATE, CURRENT_DATE + INTERVAL '3 days', true),
(1, 'Milk 2%', 'Natrel', 'dairy', 4.99, '2L', CURRENT_DATE, CURRENT_DATE + INTERVAL '5 days', false),
(2, 'Ground Beef', 'Fresh', 'meat', 6.99, 'lb', CURRENT_DATE, CURRENT_DATE + INTERVAL '2 days', true),
(2, 'Bread Whole Wheat', 'Wonder', 'bakery', 2.99, 'loaf', CURRENT_DATE, CURRENT_DATE + INTERVAL '4 days', false),
(3, 'Pasta Penne', 'Barilla', 'pantry', 1.49, '500g', CURRENT_DATE, CURRENT_DATE + INTERVAL '10 days', true)
ON CONFLICT DO NOTHING;

-- Create a sample user for testing
INSERT INTO users (email, postal_code, budget, household_size, dietary_restrictions, food_preferences) VALUES 
('test@example.com', 'M5V3A8', 150.00, 2, '[]', '{"likes": ["italian", "mexican"], "dislikes": ["spicy"], "allergies": []}')
ON CONFLICT (email) DO NOTHING;