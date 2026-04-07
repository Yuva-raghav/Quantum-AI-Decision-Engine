const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function parseErrorPayload(payload) {
  if (!payload) return ''

  if (typeof payload === 'string') return payload

  if (typeof payload.detail === 'string') return payload.detail

  if (Array.isArray(payload.detail)) {
    return payload.detail
      .map((entry) => {
        if (typeof entry === 'string') return entry
        if (entry && typeof entry.msg === 'string') return entry.msg
        return JSON.stringify(entry)
      })
      .join(' | ')
  }

  return JSON.stringify(payload)
}

async function post(path, body) {
  const response = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    let message = ''

    try {
      const json = await response.json()
      message = parseErrorPayload(json)
    } catch {
      message = await response.text()
    }

    throw new Error(message || `Request failed: ${response.status}`)
  }

  return response.json()
}

export async function compareProblem(prompt) {
  return post('/compare', { message: prompt })
}

export { API_URL }
