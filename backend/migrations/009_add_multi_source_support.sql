-- Migration: Add multi-source support fields
-- Date: 2026-03-07
-- Description: Add source, language, private, and gated fields for GitHub/HuggingFace/Kaggle support

-- Add new columns
ALTER TABLE resources 
ADD COLUMN IF NOT EXISTS source VARCHAR(50) NOT NULL DEFAULT 'github',
ADD COLUMN IF NOT EXISTS language VARCHAR(100),
ADD COLUMN IF NOT EXISTS private BOOLEAN,
ADD COLUMN IF NOT EXISTS gated BOOLEAN;

-- Create indexes for filtering
CREATE INDEX IF NOT EXISTS idx_resources_source ON resources(source);
CREATE INDEX IF NOT EXISTS idx_resources_language ON resources(language) WHERE language IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_resources_private ON resources(private) WHERE private IS NOT NULL;

-- Update existing records based on source_url
UPDATE resources 
SET source = CASE 
    WHEN source_url LIKE '%github.com%' THEN 'github'
    WHEN source_url LIKE '%huggingface.co%' THEN 'huggingface'
    WHEN source_url LIKE '%kaggle.com%' THEN 'kaggle'
    ELSE 'github'
END
WHERE source = 'github';  -- Only update default values

-- Add check constraint for valid sources
ALTER TABLE resources 
ADD CONSTRAINT chk_resources_source 
CHECK (source IN ('github', 'huggingface', 'kaggle'));

-- Add comments
COMMENT ON COLUMN resources.source IS 'Data source: github, huggingface, or kaggle';
COMMENT ON COLUMN resources.language IS 'Programming language (primarily for GitHub resources)';
COMMENT ON COLUMN resources.private IS 'Privacy status (primarily for HuggingFace resources)';
COMMENT ON COLUMN resources.gated IS 'Access restriction status (primarily for HuggingFace resources)';
