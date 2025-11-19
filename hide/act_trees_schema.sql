-- ACT Trees Database Schema
-- Run this in your Supabase SQL editor to create the table

CREATE TABLE IF NOT EXISTS act_trees (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  nodes JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_act_trees_user_id ON act_trees(user_id);
CREATE INDEX IF NOT EXISTS idx_act_trees_updated_at ON act_trees(updated_at);

-- Enable Row Level Security (RLS)
ALTER TABLE act_trees ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own trees" ON act_trees
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own trees" ON act_trees
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own trees" ON act_trees
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own trees" ON act_trees
  FOR DELETE USING (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_act_trees_updated_at
  BEFORE UPDATE ON act_trees
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
