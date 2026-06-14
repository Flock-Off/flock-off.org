const URL  = process.env.NEXT_PUBLIC_SUPABASE_URL!
const ANON = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export async function sbFetch(path: string) {
  const res = await fetch(`${URL}/rest/v1/${path}`, {
    headers: {
      apikey: ANON,
      Authorization: `Bearer ${ANON}`,
      'Content-Type': 'application/json',
      Prefer: 'return=representation',
    },
    cache: 'no-store',
  })
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`)
  return res.json()
}

export async function sbCount(table: string): Promise<number> {
  const res = await fetch(`${URL}/rest/v1/${table}?select=*`, {
    method: 'HEAD',
    headers: {
      apikey: ANON,
      Authorization: `Bearer ${ANON}`,
      Prefer: 'count=exact',
    },
    cache: 'no-store',
  })
  const range = res.headers.get('content-range') ?? ''
  return parseInt(range.split('/')[1] ?? '0', 10)
}
