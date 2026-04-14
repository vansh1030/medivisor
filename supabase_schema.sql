-- Drop the table if it exists to ensure a clean slate (optional, but good for testing)
-- DROP TABLE IF EXISTS public.predictions_log;

CREATE TABLE IF NOT EXISTS public.predictions_log (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamptz DEFAULT now() NOT NULL,
  age integer NOT NULL,
  gender varchar(50) NOT NULL,
  bmi numeric NOT NULL,
  smoking_history boolean NOT NULL,
  family_history boolean NOT NULL,
  wheezing boolean NOT NULL,
  shortness_of_breath boolean NOT NULL,
  predicted_risk varchar(50) NOT NULL
);

-- Enable Row Level Security (RLS) as a best practice
ALTER TABLE public.predictions_log ENABLE ROW LEVEL SECURITY;

-- Allow insert access for the table, since our backend logic will insert data.
-- (If you use the Supabase Service Role Key on the backend, RLS is bypassed. 
-- But if configuring via standard anon key, this allows inserts).
CREATE POLICY "Allow public inserts" ON public.predictions_log 
FOR INSERT TO anon, authenticated 
WITH CHECK (true);

-- Allow admins (or anyone) to select (read) the data for dashboard purposes
CREATE POLICY "Allow public select" ON public.predictions_log 
FOR SELECT TO anon, authenticated
USING (true);
