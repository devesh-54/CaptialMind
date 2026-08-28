import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = 'https://zjvvbteptuqufobeykop.supabase.co';
const SUPABASE_KEY = 'sb_publishable_XToGIQhvkRliU_AqbR-WsQ_vez8nkrb';

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export async function fetchSupabaseStreamEvents() {
  try {
    const { data, error } = await supabase
      .from('streamed_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(100);

    if (error) {
      console.warn('Supabase fetch notice:', error.message);
      return null;
    }
    return data;
  } catch (err) {
    console.warn('Supabase client offline/restricted, using SSE local stream:', err);
    return null;
  }
}
