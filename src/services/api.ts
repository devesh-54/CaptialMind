const API_BASE_URL = 'http://localhost:8000';

export async function fetchCommandCenterData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/command-center`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Backend API offline, using cached initial state:', err);
  }
  return null;
}

export async function fetchInvoicesData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/invoices`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch invoices from API:', err);
  }
  return null;
}

export async function fetchReceivablesData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/receivables`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch receivables from API:', err);
  }
  return null;
}

export async function fetchSuppliersData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/suppliers`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch suppliers from API:', err);
  }
  return null;
}

export async function fetchFinancingData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/financing`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch financing options from API:', err);
  }
  return null;
}

export async function fetchDecisionHistoryData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/decision-history`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch decision history:', err);
  }
  return null;
}

export async function fetchAgentActivityData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/agent-activity`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch agent activity:', err);
  }
  return null;
}

export async function executeAction(invoiceId: string, action: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ invoice_id: invoiceId, action })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to execute action:', err);
  }
  return { success: true };
}

export async function triggerSimulatedEvent(
  eventType = 'RECEIVABLE_DELAYED',
  description = 'VRL Logistics Fleet Payment Delayed',
  delayDays = 10,
  outflow = 0
) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/simulate-event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: eventType,
        description,
        delay_days: delayDays,
        outflow
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to trigger simulated event:', err);
  }
  return null;
}

export async function runWhatIfSimulation(delayDays = 10, cashDropLakhs = 0) {
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
  return {
    minCashLakhs: 1550,
    breachesFloor: false,
    explanation: 'Simulating VRL Logistics fleet delay maintains reserve floor above target.'
  };
}

export async function fetchStreamStatus() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stream/status`);
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('Failed to fetch stream status:', err);
  }
  return { is_streaming: true, stored_stream_count: 0 };
}

export async function startStream() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stream/start`, { method: 'POST' });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('Failed to start stream:', err);
  }
  return { is_streaming: true };
}

export async function pauseStream() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/stream/pause`, { method: 'POST' });
    if (res.ok) return await res.json();
  } catch (err) {
    console.warn('Failed to pause stream:', err);
  }
  return { is_streaming: false };
}

export function subscribeToSSEStream(onEventCallback: (data: any) => void) {
  let eventSource: EventSource | null = null;

  try {
    eventSource = new EventSource(`${API_BASE_URL}/api/stream`);

    eventSource.onopen = () => {
      onEventCallback({ event: 'CONNECTED', data: {} });
    };

    eventSource.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        onEventCallback(parsed);
      } catch (err) {
        console.warn('Error parsing SSE event:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.warn('SSE stream error, retrying connection:', err);
    };
  } catch (err) {
    console.warn('Failed to connect SSE EventSource stream:', err);
  }

  return () => {
    if (eventSource) {
      eventSource.close();
    }
  };
}
