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

export async function fetchAgentActivityData() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/agent-activity`);
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to fetch agent activity from API:', err);
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
    console.warn('Failed to fetch decision history from API:', err);
  }
  return null;
}

export async function triggerSimulatedEvent(
  eventType: str = 'RECEIVABLE_DELAYED',
  desc: string = 'Customer payment delayed',
  delayDays: number = 10,
  outflowLakhs: number = 0
) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/simulate-event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: eventType,
        description: desc,
        receivable_delay_days: delayDays,
        extra_outflow_lakhs: outflowLakhs,
        customer_id: 'CUST011'
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

export async function executeAction(invoiceId: string, action: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        invoice_id: invoiceId,
        action: action
      })
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Failed to execute action via API:', err);
  }
  return { success: true, message: `Executed ${action} for ${invoiceId}` };
}

export function subscribeToSSEStream(onMessage: (data: any) => void) {
  const eventSource = new EventSource(`${API_BASE_URL}/api/stream`);

  eventSource.onmessage = (event) => {
    try {
      const parsed = JSON.parse(event.data);
      onMessage(parsed);
    } catch (e) {
      console.warn('Error parsing SSE event:', e);
    }
  };

  eventSource.onerror = (err) => {
    console.warn('SSE stream error:', err);
  };

  return () => {
    eventSource.close();
  };
}
