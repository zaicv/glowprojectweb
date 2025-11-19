-- Consciousness States Database Schema
-- Run this in your Supabase SQL editor to create the table

CREATE TABLE IF NOT EXISTS consciousness_states (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  thread_id UUID REFERENCES chat_threads(id) ON DELETE SET NULL,
  message_id UUID REFERENCES chat_messages(id) ON DELETE SET NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  state_type TEXT NOT NULL CHECK (state_type IN ('chaos', 'glow', 'neutral')),
  intensity FLOAT NOT NULL DEFAULT 0.5 CHECK (intensity >= 0 AND intensity <= 1),
  sentiment_score FLOAT CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
  context TEXT,
  chaos_indicators JSONB DEFAULT '[]'::jsonb,
  glow_indicators JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_consciousness_states_user_id ON consciousness_states(user_id);
CREATE INDEX IF NOT EXISTS idx_consciousness_states_timestamp ON consciousness_states(timestamp);
CREATE INDEX IF NOT EXISTS idx_consciousness_states_state_type ON consciousness_states(state_type);
CREATE INDEX IF NOT EXISTS idx_consciousness_states_thread_id ON consciousness_states(thread_id);

-- Enable Row Level Security (RLS)
ALTER TABLE consciousness_states ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own consciousness states" ON consciousness_states
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own consciousness states" ON consciousness_states
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own consciousness states" ON consciousness_states
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own consciousness states" ON consciousness_states
  FOR DELETE USING (auth.uid() = user_id);

-- Create function to get recent states for a user (useful for visualization)
CREATE OR REPLACE FUNCTION get_user_consciousness_states(
  p_user_id UUID,
  p_limit INTEGER DEFAULT 100,
  p_start_time TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  timestamp TIMESTAMP WITH TIME ZONE,
  state_type TEXT,
  intensity FLOAT,
  sentiment_score FLOAT,
  context TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    cs.id,
    cs.timestamp,
    cs.state_type,
    cs.intensity,
    cs.sentiment_score,
    cs.context
  FROM consciousness_states cs
  WHERE cs.user_id = p_user_id
    AND (p_start_time IS NULL OR cs.timestamp >= p_start_time)
  ORDER BY cs.timestamp DESC
  LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to get state statistics for a user
CREATE OR REPLACE FUNCTION get_consciousness_statistics(
  p_user_id UUID,
  p_start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW() - INTERVAL '30 days'
)
RETURNS TABLE (
  total_states BIGINT,
  chaos_count BIGINT,
  glow_count BIGINT,
  neutral_count BIGINT,
  avg_intensity FLOAT,
  avg_sentiment FLOAT,
  chaos_percentage FLOAT,
  glow_percentage FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*)::BIGINT as total_states,
    COUNT(*) FILTER (WHERE state_type = 'chaos')::BIGINT as chaos_count,
    COUNT(*) FILTER (WHERE state_type = 'glow')::BIGINT as glow_count,
    COUNT(*) FILTER (WHERE state_type = 'neutral')::BIGINT as neutral_count,
    AVG(intensity)::FLOAT as avg_intensity,
    AVG(sentiment_score)::FLOAT as avg_sentiment,
    (COUNT(*) FILTER (WHERE state_type = 'chaos')::FLOAT / NULLIF(COUNT(*), 0) * 100)::FLOAT as chaos_percentage,
    (COUNT(*) FILTER (WHERE state_type = 'glow')::FLOAT / NULLIF(COUNT(*), 0) * 100)::FLOAT as glow_percentage
  FROM consciousness_states
  WHERE user_id = p_user_id
    AND timestamp >= p_start_time;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

