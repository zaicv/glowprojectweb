-- Chat Folders Database Schema
-- Run this in your Supabase SQL editor to create the tables

-- Create chat_folders table
CREATE TABLE IF NOT EXISTS chat_folders (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT DEFAULT 'Star',
  color TEXT DEFAULT 'bg-blue-50 border-blue-200 text-blue-700 dark:bg-blue-950 dark:border-blue-800 dark:text-blue-300',
  is_expanded BOOLEAN DEFAULT true,
  sort_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add folder_id and is_pinned columns to chat_threads table if they don't exist
ALTER TABLE chat_threads 
ADD COLUMN IF NOT EXISTS folder_id UUID REFERENCES chat_folders(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_folders_user_id ON chat_folders(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_folders_sort_order ON chat_folders(sort_order);
CREATE INDEX IF NOT EXISTS idx_chat_threads_folder_id ON chat_threads(folder_id);
CREATE INDEX IF NOT EXISTS idx_chat_threads_is_pinned ON chat_threads(is_pinned);
CREATE INDEX IF NOT EXISTS idx_chat_threads_sort_order ON chat_threads(sort_order);

-- Enable Row Level Security (RLS)
ALTER TABLE chat_folders ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for chat_folders
CREATE POLICY "Users can view their own folders" ON chat_folders
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own folders" ON chat_folders
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own folders" ON chat_folders
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own folders" ON chat_folders
  FOR DELETE USING (auth.uid() = user_id);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_folder_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at for folders
CREATE TRIGGER update_chat_folders_updated_at
  BEFORE UPDATE ON chat_folders
  FOR EACH ROW
  EXECUTE FUNCTION update_folder_updated_at_column();

-- Create function to update thread updated_at when folder_id changes
CREATE OR REPLACE FUNCTION update_thread_on_folder_change()
RETURNS TRIGGER AS $$
BEGIN
  NEW.date_modified = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to update thread when folder_id or is_pinned changes
CREATE TRIGGER update_thread_on_folder_change
  BEFORE UPDATE ON chat_threads
  FOR EACH ROW
  WHEN (OLD.folder_id IS DISTINCT FROM NEW.folder_id OR OLD.is_pinned IS DISTINCT FROM NEW.is_pinned)
  EXECUTE FUNCTION update_thread_on_folder_change();
