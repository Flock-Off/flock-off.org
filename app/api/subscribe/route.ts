import { NextRequest, NextResponse } from 'next/server'

const SUPABASE_URL  = process.env.NEXT_PUBLIC_SUPABASE_URL!
const SUPABASE_ANON = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export async function POST(req: NextRequest) {
  const { email } = await req.json()

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return NextResponse.json({ error: 'Invalid email' }, { status: 400 })
  }

  const res = await fetch(`${SUPABASE_URL}/rest/v1/email_subscribers`, {
    method: 'POST',
    headers: {
      apikey:          SUPABASE_ANON,
      Authorization:   `Bearer ${SUPABASE_ANON}`,
      'Content-Type':  'application/json',
      Prefer:          'return=minimal',
    },
    body: JSON.stringify({ email }),
  })

  if (res.status === 409) {
    return NextResponse.json({ error: 'Already subscribed' }, { status: 409 })
  }
  if (!res.ok) {
    return NextResponse.json({ error: 'Failed to subscribe' }, { status: 500 })
  }

  return NextResponse.json({ ok: true })
}
