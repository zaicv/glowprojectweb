-- Create RPC function to calculate sleep debt
CREATE OR REPLACE FUNCTION calculate_sleep_debt(
  user_id_param UUID,
  days_back INTEGER DEFAULT 14
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
  total_sleep_needed NUMERIC;
  total_sleep_actual NUMERIC;
  sleep_debt NUMERIC;
  target_hours_per_night NUMERIC := 8; -- Default target sleep hours
BEGIN
  -- Calculate total sleep needed (target hours × number of days)
  total_sleep_needed := target_hours_per_night * days_back;
  
  -- Calculate total sleep actually got from past days
  SELECT COALESCE(SUM(hours_sleep), 0)
  INTO total_sleep_actual
  FROM health
  WHERE user_id = user_id_param
    AND date >= CURRENT_DATE - INTERVAL '1 day' * days_back
    AND date < CURRENT_DATE;
  
  -- Calculate sleep debt
  sleep_debt := total_sleep_needed - total_sleep_actual;
  
  -- Return sleep debt (positive means debt, negative means surplus)
  RETURN GREATEST(sleep_debt, 0);
END;
$$;
