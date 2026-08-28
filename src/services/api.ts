const API_BASE_URL = 'http://localhost:8000';

export async function fetchCommandCenterData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/command-center`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API offline, falling back to local dataset:', err);
  }
  return null;
}

export async function triggerSimulatedEvent(eventType: string, description: string, delayDays = 0, outflowLakhs = 0) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/simulate-event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: eventType,
        description: description,
        receivable_delay_days: delayDays,
        extra_outflow_lakhs: outflowLakhs
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to trigger event on backend:', err);
  }
  return null;
}

export async function runWhatIfSimulation(delayDays: number, cashDropLakhs: number) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/what-if`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        receivable_delay_days: delayDays,
        cash_drop_lakhs: cashDropLakhs
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to run what-if simulation:', err);
  }
  return null;
}

export function subscribeToSSEStream(onMessage: (data: any) => void): () => void {
  try {
    const eventSource = new EventSource(`${API_BASE_URL}/api/stream`);

    eventSource.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        onMessage(parsed);
      } catch (err) {
        console.error('Error parsing SSE event:', err);
      }
    };

    return () => {
      eventSource.close();
    };
  } catch (err) {
    console.warn('SSE subscription failed:', err);
    return () => {};
  }
}
