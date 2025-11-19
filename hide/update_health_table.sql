-- Add new fields to the health table
ALTER TABLE public.health 
ADD COLUMN glow_process integer DEFAULT 0,
ADD COLUMN gentle_movement integer DEFAULT 0,
ADD COLUMN day_complete boolean DEFAULT false;

-- Update existing records to have default values
UPDATE public.health 
SET glow_process = 0, 
    gentle_movement = 0, 
    day_complete = false 
WHERE glow_process IS NULL OR gentle_movement IS NULL OR day_complete IS NULL;

