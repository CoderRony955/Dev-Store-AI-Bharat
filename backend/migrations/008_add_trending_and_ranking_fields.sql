-- Migration: Add trending_score and category_rank fields
-- Description: Add fields for trending algorithm and category-based rankings
-- Date: 2026-03-06

-- Add trending_score to resources table
-- This is a calculated float used for the Unified Ranking Algorithm
-- Combines recent activity, downloads, and engagement metrics
ALTER TABLE resources ADD COLUMN IF NOT EXISTS trending_score FLOAT DEFAULT 0.0;

-- Add category_rank to resources table
-- Represents the resource's position within its type (e.g., #1 in Models)
ALTER TABLE resources ADD COLUMN IF NOT EXISTS category_rank INTEGER DEFAULT NULL;

-- Add boilerplate_download_count to track successful boilerplate downloads
-- This is separate from general download_count which may track other metrics
ALTER TABLE resources ADD COLUMN IF NOT EXISTS boilerplate_download_count INTEGER DEFAULT 0;

-- Create index for trending queries
CREATE INDEX IF NOT EXISTS idx_resources_trending ON resources(trending_score DESC);

-- Create composite index for category-based ranking queries
CREATE INDEX IF NOT EXISTS idx_resources_category_rank ON resources(type, category_rank);

-- Create index for boilerplate downloads
CREATE INDEX IF NOT EXISTS idx_resources_boilerplate_downloads ON resources(boilerplate_download_count DESC);

-- Add comments for documentation
COMMENT ON COLUMN resources.trending_score IS 'Calculated trending score combining recent activity, downloads, and engagement (0-1)';
COMMENT ON COLUMN resources.category_rank IS 'Position within resource type category (1 = top ranked in category)';
COMMENT ON COLUMN resources.boilerplate_download_count IS 'Total number of successful boilerplate code downloads';

-- Add trending_score to resource_rankings table for historical tracking
ALTER TABLE resource_rankings ADD COLUMN IF NOT EXISTS trending_score FLOAT DEFAULT 0.0;

-- Add category_rank to resource_rankings for historical tracking
ALTER TABLE resource_rankings ADD COLUMN IF NOT EXISTS category_rank INTEGER DEFAULT NULL;

-- Update comments
COMMENT ON COLUMN resource_rankings.trending_score IS 'Historical trending score for the date';
COMMENT ON COLUMN resource_rankings.category_rank IS 'Historical category rank position for the date';
